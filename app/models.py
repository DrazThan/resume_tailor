from app import db
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class User(UserMixin, Base):
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Resume(Base):
    content = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('resumes', lazy=True))

class JobDescription(Base):
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('job_descriptions', lazy=True))

class TailoredResume(Base):
    original_resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    questions = db.Column(db.JSON)
    token_count = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    original_resume = db.relationship('Resume', backref=db.backref('tailored_resumes', lazy=True))
    job_description = db.relationship('JobDescription', backref=db.backref('tailored_resumes', lazy=True))
    user = db.relationship('User', backref=db.backref('tailored_resumes', lazy=True))