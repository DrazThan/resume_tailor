from app import db
from datetime import datetime, timezone

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Resume(Base):
    content = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.JSON)

class JobDescription(Base):
    content = db.Column(db.Text, nullable=False)

class TailoredResume(Base):
    original_resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    questions = db.Column(db.JSON)
    token_count = db.Column(db.Integer)

    original_resume = db.relationship('Resume', backref=db.backref('tailored_resumes', lazy=True))
    job_description = db.relationship('JobDescription', backref=db.backref('tailored_resumes', lazy=True))