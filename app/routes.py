from flask import jsonify, request, current_app
from flask_login import login_user, login_required, current_user, logout_user
from app import db, limiter
from app.models import User, Resume, JobDescription, TailoredResume
from app.services.claude_service import ClaudeService
import logging

claude_service = ClaudeService()

@app.errorhandler(Exception)
def handle_exception(e):
    current_app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/v1/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    try:
        data = request.json
        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Invalid registration data"}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400

        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": "Failed to register user"}), 500

@app.route('/api/v1/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Invalid login data"}), 400

        user = User.query.filter_by(username=data['username']).first()
        if user is None or not user.check_password(data['password']):
            return jsonify({"error": "Invalid username or password"}), 401

        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({"error": "Failed to log in"}), 500

@app.route('/api/v1/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/v1/resumes', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def create_resume():
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        new_resume = Resume(content=data['content'], user_id=current_user.id)
        db.session.add(new_resume)
        db.session.commit()

        analysis = claude_service.analyze_resume(data['content'])
        new_resume.analysis = analysis
        db.session.commit()

        current_app.logger.info(f"Resume created and analyzed with id: {new_resume.id}")
        return jsonify({
            "message": "Resume created and analyzed successfully",
            "id": new_resume.id,
            "created_at": new_resume.created_at,
            "analysis": analysis
        }), 201
    except ValueError as ve:
        current_app.logger.error(f"ValueError in create_resume: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating resume: {str(e)}")
        return jsonify({"error": "Failed to create resume"}), 500

@app.route('/api/v1/tailor_resume', methods=['POST'])
@login_required
@limiter.limit("3 per minute")
def tailor_resume():
    try:
        data = request.json
        if not data or 'resume_id' not in data or 'job_id' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        resume = Resume.query.get(data['resume_id'])
        job = JobDescription.query.get(data['job_id'])

        if not resume or not job:
            return jsonify({"error": "Resume or Job Description not found"}), 404

        if resume.user_id != current_user.id or job.user_id != current_user.id:
            return jsonify({"error": "Unauthorized access"}), 403

        tailored_result = claude_service.tailor_resume(resume.content, job.content)

        tailored_resume = TailoredResume(
            original_resume_id=resume.id,
            job_description_id=job.id,
            content=tailored_result['tailored_resume'],
            questions=tailored_result.get('questions', []),
            token_count=tailored_result.get('token_count', 0),
            user_id=current_user.id
        )
        db.session.add(tailored_resume)
        db.session.commit()

        current_app.logger.info(f"Resume tailored successfully with id: {tailored_resume.id}")
        return jsonify({
            "message": "Resume tailored successfully",
            "id": tailored_resume.id,
            "content": tailored_resume.content,
            "questions": tailored_resume.questions,
            "token_count": tailored_resume.token_count
        }), 201
    except ValueError as ve:
        current_app.logger.error(f"ValueError in tailor_resume: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error tailoring resume: {str(e)}")
        return jsonify({"error": "Failed to tailor resume"}), 500

@app.route('/api/v1/resumes', methods=['GET'])
@login_required
def get_user_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": resume.id,
        "content": resume.content,
        "created_at": resume.created_at,
        "analysis": resume.analysis
    } for resume in resumes]), 200

@app.route('/api/v1/job_descriptions', methods=['GET'])
@login_required
def get_user_job_descriptions():
    job_descriptions = JobDescription.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": job.id,
        "content": job.content,
        "created_at": job.created_at
    } for job in job_descriptions]), 200

@app.route('/api/v1/tailored_resumes', methods=['GET'])
@login_required
def get_user_tailored_resumes():
    tailored_resumes = TailoredResume.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": tailored.id,
        "content": tailored.content,
        "questions": tailored.questions,
        "token_count": tailored.token_count,
        "created_at": tailored.created_at
    } for tailored in tailored_resumes]), 200