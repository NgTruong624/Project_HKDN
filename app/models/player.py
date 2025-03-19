from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    position = db.Column(db.String(50))
    age = db.Column(db.Integer)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    matches = db.Column(db.Integer, nullable=True)
    starts = db.Column(db.Integer, nullable=True)
    mins = db.Column(db.Integer, nullable=True)
    goals = db.Column(db.Integer, nullable=True)
    assists = db.Column(db.Integer, nullable=True)
    passes_attempted = db.Column(db.Integer, nullable=True)
    perc_passes_completed = db.Column(db.Float, nullable=True)
    penalty_goals = db.Column(db.Integer, nullable=True)
    penalty_attempted = db.Column(db.Integer, nullable=True)
    xg = db.Column(db.Float, nullable=True)
    xa = db.Column(db.Float, nullable=True)
    yellow_cards = db.Column(db.Integer, nullable=True)
    red_cards = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'team': self.team,
            'nationality': self.nationality,
            'position': self.position,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
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