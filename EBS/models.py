# models.py
from . import db
from flask_login import UserMixin

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), nullable=False)
    nominee_id = db.Column(db.Integer, db.ForeignKey('nominee.id'), nullable=False)

class Voter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    usn = db.Column(db.String(20), nullable=False, unique=True)
    otp_secret = db.Column(db.String(20))
    otp = db.Column(db.Integer)
    
    def has_voted_for_post(self, election_id, nominee_id):
        return Vote.query.filter_by(voter_id=self.id, nominee_id=nominee_id).join(Nominee).filter_by(election_id=election_id).count() > 0
    
    def has_voted(self, election_id, nominee_id=None):
        if nominee_id:
            return Vote.query.filter_by(voter_id=self.id, nominee_id=nominee_id).join(Nominee).filter(Nominee.election_id == election_id).first() is not None
        else:
            return Vote.query.join(Nominee).filter(Nominee.election_id == election_id, Vote.voter_id == self.id).first() is not None

class SuperUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Election(db.Model):
    __tablename__ = 'election'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('super_user.id'), nullable=True)

    # Establish the relationship with the Nominee model
    nominees = db.relationship('Nominee', backref='election', lazy=True)

class Nominee(db.Model):
    __tablename__ = 'nominee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), nullable=False)
    post = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)

    votes_count = db.Column(db.Integer, default=0)
    # Establish the relationship with the Vote model
    votes_count = db.Column(db.Integer, default=0)
