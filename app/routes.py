from flask import Blueprint, render_template, request, jsonify
from app.models.player import Player
from app.utils.kaggle_utils import update_database, check_kaggle_credentials
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
        # First check credentials
        cred_success, cred_message = check_kaggle_credentials()
        if not cred_success:
            return jsonify({
                'status': 'error',
                'message': f'Kaggle credentials error: {cred_message}'
            }), 500

        # Then try to update database
        success, message = update_database()
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message}), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500 