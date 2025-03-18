from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    position = db.Column(db.String(50))
    age = db.Column(db.Integer)
    matches = db.Column(db.Integer)
    starts = db.Column(db.Integer)
    mins = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    passes_attempted = db.Column(db.Integer)
    perc_passes_completed = db.Column(db.Float)
    penalty_goals = db.Column(db.Integer)
    penalty_attempted = db.Column(db.Integer)
    xg = db.Column(db.Float)
    xa = db.Column(db.Float)
    yellow_cards = db.Column(db.Integer)
    red_cards = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'team': self.team,
            'nationality': self.nationality,
            'position': self.position,
            'age': self.age,
            'matches': self.matches,
            'starts': self.starts,
            'mins': self.mins,
            'goals': self.goals,
            'assists': self.assists,
            'passes_attempted': self.passes_attempted,
            'perc_passes_completed': self.perc_passes_completed,
            'penalty_goals': self.penalty_goals,
            'penalty_attempted': self.penalty_attempted,
            'xg': self.xg,
            'xa': self.xa,
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards
        } 