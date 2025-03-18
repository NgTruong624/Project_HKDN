from app import db
from datetime import datetime

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    team = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    appearances = db.Column(db.Integer)
    season = db.Column(db.String(10))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'team': self.team,
            'nationality': self.nationality,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'goals': self.goals,
            'assists': self.assists,
            'appearances': self.appearances,
            'season': self.season,
            'last_updated': self.last_updated.isoformat()
        } 