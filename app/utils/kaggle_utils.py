import os
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
from app.models.player import Player
from app import db

def setup_kaggle():
    """Setup Kaggle API credentials"""
    api = KaggleApi()
    api.authenticate()
    return api

def ensure_data_directory():
    """Ensure the data directory exists"""
    if not os.path.exists('./data'):
        os.makedirs('./data')

def download_epl_data():
    """Download EPL player data from Kaggle"""
    try:
        ensure_data_directory()
        api = setup_kaggle()
        # Premier League Player Statistics dataset
        dataset = "rajatrc1705/premier-league-player-statistics"
        api.dataset_download_files(dataset, path='./data', unzip=True)
        return True, "Data downloaded successfully"
    except Exception as e:
        return False, str(e)

def update_database():
    """Update the database with new data from Kaggle"""
    try:
        # Ensure data is downloaded
        success, message = download_epl_data()
        if not success:
            return False, f"Failed to download data: {message}"

        # Read the downloaded data
        df = pd.read_csv('./data/EPL_20_21.csv')
        
        # Clear existing data
        Player.query.delete()
        
        # Insert new data
        for _, row in df.iterrows():
            player = Player(
                name=row['Name'],
                position=row['Position'],
                team=row['Team'],
                nationality=row['Nationality'],
                age=row['Age'],
                height=row['Height'],
                weight=row['Weight'],
                goals=row['Goals'],
                assists=row['Assists'],
                appearances=row['Appearances'],
                season='2020-21'
            )
            db.session.add(player)
        
        db.session.commit()
        return True, "Database updated successfully"
    except Exception as e:
        db.session.rollback()
        return False, str(e) 