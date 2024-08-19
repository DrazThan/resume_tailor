from flask import jsonify, request, current_app
from app import create_app, db
from app.models import Resume, JobDescription, TailoredResume
from app.services.claude_service import ClaudeService
import logging

app = create_app()
claude_service = ClaudeService()

@app.errorhandler(Exception)
def handle_exception(e):
    current_app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/v1/resumes', methods=['POST'])
def create_resume():
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        new_resume = Resume(content=data['content'])
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
def tailor_resume():
    try:
        data = request.json
        if not data or 'resume_id' not in data or 'job_id' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        resume = Resume.query.get(data['resume_id'])
        job = JobDescription.query.get(data['job_id'])

        if not resume or not job:
            return jsonify({"error": "Resume or Job Description not found"}), 404

        tailored_result = claude_service.tailor_resume(resume.content, job.content)

        tailored_resume = TailoredResume(
            original_resume_id=resume.id,
            job_description_id=job.id,
            content=tailored_result['tailored_resume'],
            questions=tailored_result.get('questions', []),
            token_count=tailored_result.get('token_count', 0)
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