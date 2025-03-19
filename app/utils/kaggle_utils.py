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
        
        # Dataset theo URL cụ thể mà user cung cấp
        dataset = "rajatrc1705/english-premier-league202021"
        
        try:
            print(f"Đang tải dataset từ Kaggle: {dataset}...")
            kaggle.api.dataset_download_files(
                dataset,
                path=data_dir,
                unzip=True
            )
            
            # Kiểm tra các file được tải xuống
            downloaded_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if downloaded_files:
                print(f"Tải dataset thành công. Các file: {downloaded_files}")
                return True, "Dataset downloaded successfully"
            else:
                return False, "Không tìm thấy file CSV nào sau khi tải dataset"
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Lỗi khi tải dataset {dataset}: {str(e)}\n{error_traceback}")
            
            # Thử tải file bằng cách download trực tiếp
            try:
                # Thử phương pháp khác: Tạo dữ liệu mẫu
                from app.utils.sample_data import get_sample_data
                print("Không thể tải từ Kaggle API, sử dụng dữ liệu mẫu thay thế")
                get_sample_data()
                return True, "Không thể tải từ Kaggle, đã sử dụng dữ liệu mẫu thay thế"
            except Exception as sample_error:
                return False, f"Lỗi khi tải dataset và tạo dữ liệu mẫu: {str(e)}"
                
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
        
        # Chọn file đầu tiên tìm thấy
        file_path = os.path.join(data_dir, csv_files[0])
        df = pd.read_csv(file_path)
        print(f"Đã đọc file {csv_files[0]}: {df.shape[0]} dòng, {df.shape[1]} cột")
        print(f"Các cột: {df.columns.tolist()}")
            
        # Mapping để thích ứng với các dataset khác nhau
        column_mapping = {
            # Mapping cho dataset EPL 20/21
            'Name': 'name',
            'Club': 'team',
            'Team': 'team',
            'club': 'team',
            'player': 'name',
            'Apps': 'matches',
            'Nationality': 'nationality',
            'nationality': 'nationality',
            'Position': 'position',
            'position': 'position',
            'Age': 'age',
            'age': 'age',
            'Matches': 'matches',
            'matches_played': 'matches',
            'Appearances': 'matches',
            'Starts': 'starts',
            'Mins': 'mins',
            'minutes': 'mins',
            'Minutes': 'mins',
            'Goals': 'goals',
            'goals': 'goals',
            'Assists': 'assists',
            'assists': 'assists',
            'Passes_Attempted': 'passes_attempted',
            'passes': 'passes_attempted',
            'Perc_Passes_Completed': 'perc_passes_completed',
            'pass_accuracy': 'perc_passes_completed',
            'Penalty_Goals': 'penalty_goals',
            'penalties_scored': 'penalty_goals',
            'Penalty_Attempted': 'penalty_attempted',
            'penalties_taken': 'penalty_attempted',
            'xG': 'xg',
            'xA': 'xa',
            'Yellow_Cards': 'yellow_cards',
            'yellow_cards': 'yellow_cards',
            'Red_Cards': 'red_cards',
            'red_cards': 'red_cards',
            'Height': 'height',
            'height': 'height',
            'Weight': 'weight',
            'weight': 'weight'
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