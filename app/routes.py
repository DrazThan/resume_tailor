from flask import jsonify
from app import create_app

app = create_app()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Resume Tailor API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})