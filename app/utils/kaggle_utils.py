import os
import json
import kaggle
from app import db
from app.models.player import Player
import pandas as pd

def check_kaggle_credentials():
    """Check if Kaggle credentials are properly configured."""
    try:
        username = os.environ.get('KAGGLE_USERNAME')
        key = os.environ.get('KAGGLE_KEY')
        
        if not username or not key:
            return False, "Kaggle credentials not found in environment variables"
            
        # Create kaggle.json if it doesn't exist
        kaggle_dir = os.path.expanduser('~/.kaggle')
        if not os.path.exists(kaggle_dir):
            os.makedirs(kaggle_dir)
            
        kaggle_json_path = os.path.join(kaggle_dir, 'kaggle.json')
        if not os.path.exists(kaggle_json_path):
            with open(kaggle_json_path, 'w') as f:
                json.dump({
                    "username": username,
                    "key": key
                }, f)
            # Set appropriate permissions
            os.chmod(kaggle_json_path, 0o600)
            
        return True, "Kaggle credentials configured successfully"
    except Exception as e:
        return False, f"Error configuring Kaggle credentials: {str(e)}"

def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists('./data'):
        os.makedirs('./data')

def download_epl_data():
    """Download EPL dataset from Kaggle."""
    try:
        ensure_data_directory()
        
        # Check credentials first
        cred_success, cred_message = check_kaggle_credentials()
        if not cred_success:
            return False, cred_message
            
        # Authenticate with Kaggle
        kaggle.api.authenticate()
        
        # Download dataset
        kaggle.api.dataset_download_files(
            'aravindanr/english-premier-league-players-dataset-2020-2021',
            path='./data',
            unzip=True
        )
        return True, "Dataset downloaded successfully"
    except Exception as e:
        return False, f"Error downloading dataset: {str(e)}"

def update_database():
    """Update database with new data from Kaggle."""
    try:
        # First download the data
        download_success, download_message = download_epl_data()
        if not download_success:
            return False, download_message
            
        # Read the CSV file
        df = pd.read_csv('./data/EPL_20_21.csv')
        
        # Clear existing data
        Player.query.delete()
        
        # Insert new data
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
        return True, "Database updated successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating database: {str(e)}" 