import os
import json
import kaggle
from app import db
from app.models.player import Player
import pandas as pd
import traceback
import sys

def check_kaggle_credentials():
    """Check if Kaggle credentials are properly configured."""
    try:
        username = os.environ.get('KAGGLE_USERNAME')
        key = os.environ.get('KAGGLE_KEY')
        
        if not username:
            return False, "KAGGLE_USERNAME không được cấu hình trong environment variables"
        
        if not key:
            return False, "KAGGLE_KEY không được cấu hình trong environment variables"
            
        # Hiển thị thông tin (không hiển thị key đầy đủ)
        masked_key = key[:4] + "*" * (len(key) - 8) + key[-4:] if len(key) > 8 else "****"
        print(f"Kaggle config: Username={username}, Key={masked_key}")
            
        # Create kaggle.json if it doesn't exist
        kaggle_dir = os.path.expanduser('~/.kaggle')
        if not os.path.exists(kaggle_dir):
            os.makedirs(kaggle_dir)
            print(f"Đã tạo thư mục Kaggle: {kaggle_dir}")
            
        kaggle_json_path = os.path.join(kaggle_dir, 'kaggle.json')
        credentials = {
            "username": username,
            "key": key
        }
        
        # Luôn ghi lại file credentials để đảm bảo nó là mới nhất
        with open(kaggle_json_path, 'w') as f:
            json.dump(credentials, f)
        # Set appropriate permissions
        os.chmod(kaggle_json_path, 0o600)
        print(f"Đã cập nhật file credentials: {kaggle_json_path}")
            
        return True, "Kaggle credentials configured successfully"
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Kaggle credentials error: {str(e)}\n{error_traceback}")
        return False, f"Error configuring Kaggle credentials: {str(e)}"

def ensure_data_directory():
    """Ensure the data directory exists."""
    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Đã tạo thư mục data: {data_dir}")
    return data_dir

def download_epl_data():
    """Download EPL dataset from Kaggle."""
    try:
        data_dir = ensure_data_directory()
        
        # Check credentials first
        cred_success, cred_message = check_kaggle_credentials()
        if not cred_success:
            return False, cred_message
        
        print("Bắt đầu xác thực Kaggle API...")
        # Try authenticate explicitly
        try:
            kaggle.api.authenticate()
            print("Xác thực Kaggle API thành công")
        except Exception as auth_e:
            error_traceback = traceback.format_exc()
            print(f"Lỗi xác thực Kaggle API: {str(auth_e)}\n{error_traceback}")
            return False, f"Lỗi xác thực Kaggle API: {str(auth_e)}"
        
        # Dataset info - thử nhiều dataset khác nhau nếu một cái fail
        datasets = [
            "aravindanr/english-premier-league-players-dataset-2020-2021",
            "rajatrc1705/premier-league-player-statistics"
        ]
        
        download_success = False
        error_messages = []
        
        for dataset in datasets:
            try:
                print(f"Đang tải dataset từ Kaggle: {dataset}...")
                kaggle.api.dataset_download_files(
                    dataset,
                    path=data_dir,
                    unzip=True
                )
                # Kiểm tra xem file có tồn tại không
                expected_files = ['EPL_20_21.csv', 'players_stats.csv']
                for file in expected_files:
                    file_path = os.path.join(data_dir, file)
                    if os.path.exists(file_path):
                        print(f"Tải dataset thành công: {file_path}")
                        download_success = True
                        break
                
                if download_success:
                    break
            except Exception as e:
                error_message = f"Lỗi khi tải dataset {dataset}: {str(e)}"
                error_messages.append(error_message)
                print(error_message)
                continue
        
        if download_success:
            return True, "Dataset downloaded successfully"
        else:
            detailed_error = "\n".join(error_messages)
            return False, f"Không thể tải dataset từ Kaggle: {detailed_error}"
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Lỗi khi tải dataset: {str(e)}\n{error_traceback}")
        return False, f"Error downloading dataset: {str(e)}"

def update_database():
    """Update database with new data from Kaggle."""
    try:
        # First download the data
        download_success, download_message = download_epl_data()
        if not download_success:
            return False, download_message
        
        data_dir = './data'
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            return False, f"Không tìm thấy file CSV nào trong thư mục {data_dir}"
        
        print(f"Danh sách file CSV: {csv_files}")
        
        # Kiểm tra EPL_20_21.csv trước
        if 'EPL_20_21.csv' in csv_files:
            df = pd.read_csv(os.path.join(data_dir, 'EPL_20_21.csv'))
            print(f"Đã đọc file EPL_20_21.csv: {df.shape[0]} dòng, {df.shape[1]} cột")
            print(f"Các cột: {df.columns.tolist()}")
        elif 'players_stats.csv' in csv_files:
            df = pd.read_csv(os.path.join(data_dir, 'players_stats.csv'))
            print(f"Đã đọc file players_stats.csv: {df.shape[0]} dòng, {df.shape[1]} cột")
            print(f"Các cột: {df.columns.tolist()}")
        else:
            # Sử dụng file đầu tiên tìm thấy
            file_path = os.path.join(data_dir, csv_files[0])
            df = pd.read_csv(file_path)
            print(f"Đã đọc file {csv_files[0]}: {df.shape[0]} dòng, {df.shape[1]} cột")
            print(f"Các cột: {df.columns.tolist()}")
            
        # Mapping để thích ứng với các dataset khác nhau
        column_mapping = {
            # EPL_20_21.csv
            'Name': 'name',
            'Club': 'team',
            'Team': 'team',
            'Nationality': 'nationality',
            'Position': 'position',
            'Age': 'age',
            'Matches': 'matches',
            'Appearances': 'matches',
            'Starts': 'starts',
            'Mins': 'mins',
            'Minutes': 'mins',
            'Goals': 'goals',
            'Assists': 'assists',
            'Passes_Attempted': 'passes_attempted',
            'Perc_Passes_Completed': 'perc_passes_completed',
            'Penalty_Goals': 'penalty_goals',
            'Penalty_Attempted': 'penalty_attempted',
            'xG': 'xg',
            'xA': 'xa',
            'Yellow_Cards': 'yellow_cards',
            'Red_Cards': 'red_cards',
            'Height': 'height',
            'Weight': 'weight'
        }
        
        # Clear existing data
        print("Xóa dữ liệu cũ")
        Player.query.delete()
        
        # Insert new data
        print("Bắt đầu chèn dữ liệu mới")
        for _, row in df.iterrows():
            player_data = {}
            
            # Lặp qua tất cả cột có thể có trong model Player
            for column_name in df.columns:
                if column_name in column_mapping:
                    model_field = column_mapping[column_name]
                    player_data[model_field] = row[column_name]
            
            # Kiểm tra các trường bắt buộc
            if 'name' not in player_data:
                continue
                
            player = Player(**player_data)
            db.session.add(player)
        
        print("Commit dữ liệu vào database")
        db.session.commit()
        print("Cập nhật database thành công")
        return True, "Database updated successfully"
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Lỗi khi cập nhật database: {str(e)}\n{error_traceback}")
        db.session.rollback()
        return False, f"Error updating database: {str(e)}" 