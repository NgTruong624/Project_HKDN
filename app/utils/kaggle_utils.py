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

def download_epl_data():
    """Download EPL player data from Kaggle"""
    api = setup_kaggle()
    # Premier League Player Statistics dataset
    dataset = "rajatrc1705/premier-league-player-statistics"
    api.dataset_download_files(dataset, path='./data', unzip=True)
    
def update_database():
    """Update the database with new data from Kaggle"""
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
            season=row['Season']
        )
        db.session.add(player)
    
    db.session.commit() 