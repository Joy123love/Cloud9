from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<User {self.username}>"

class CodingChallengesStatements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, foreign_key="CodingChallenges.id")
    keyword = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Statement {self.keyword} : {self.amount}>"

class CodingChallengesChecks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, foreign_key="CodingChallenges.id")
    check = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return f"<Check {self.check}>"

class CodingChallenges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(512))
    starting = db.Column(db.String(4086), nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Challenge {self.name}>"
