from flask import Blueprint, render_template, request, jsonify
from app.models.player import Player
from app.utils.kaggle_utils import update_database, check_kaggle_credentials
from app.utils.sample_data import get_sample_data
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/check-credentials')
def check_credentials():
    success, message = check_kaggle_credentials()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message
    })

@main.route('/search')
def search():
    query = request.args.get('q', '')
    try:
        players = Player.query.filter(
            (Player.name.ilike(f'%{query}%')) |
            (Player.team.ilike(f'%{query}%')) |
            (Player.nationality.ilike(f'%{query}%'))
        ).all()
        return jsonify([player.to_dict() for player in players])
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/player/<int:player_id>')
def player_detail(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        return jsonify(player.to_dict())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/update-data')
def update_data():
    try:
        # Thử sử dụng Kaggle API trước
        try:
            # Check credentials
            cred_success, cred_message = check_kaggle_credentials()
            if cred_success:
                # Nếu credentials OK, thử cập nhật database bằng Kaggle API
                success, message = update_database()
                if success:
                    return jsonify({'status': 'success', 'message': message})
                else:
                    print(f"Không thể cập nhật từ Kaggle: {message}. Thử sử dụng dữ liệu mẫu...")
            else:
                print(f"Lỗi credentials: {cred_message}. Thử sử dụng dữ liệu mẫu...")
        except Exception as e:
            print(f"Lỗi khi sử dụng Kaggle API: {str(e)}. Thử sử dụng dữ liệu mẫu...")
        
        # Nếu không thể cập nhật từ Kaggle, sử dụng dữ liệu mẫu
        try:
            # Xóa dữ liệu cũ
            Player.query.delete()
            
            # Tải dữ liệu mẫu
            print("Tạo dữ liệu mẫu...")
            df = get_sample_data()
            
            # Chèn dữ liệu mẫu vào database
            print(f"Chèn {df.shape[0]} cầu thủ vào database")
            for _, row in df.iterrows():
                player = Player(
                    name=row['Name'],
                    team=row['Club'],
                    nationality=row['Nationality'],
                    position=row['Position'],
                    age=row['Age'],
                    matches=row['Matches'],
                    starts=row['Starts'],
                    mins=row['Mins'],
                    goals=row['Goals'],
                    assists=row['Assists'],
                    passes_attempted=row['Passes_Attempted'],
                    perc_passes_completed=row['Perc_Passes_Completed'],
                    penalty_goals=row['Penalty_Goals'],
                    penalty_attempted=row['Penalty_Attempted'],
                    xg=row['xG'],
                    xa=row['xA'],
                    yellow_cards=row['Yellow_Cards'],
                    red_cards=row['Red_Cards']
                )
                db.session.add(player)
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Database updated with sample data'})
        except Exception as sample_error:
            return jsonify({
                'status': 'error',
                'message': f'Không thể cập nhật database: {str(sample_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500 