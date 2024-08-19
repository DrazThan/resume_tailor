import os
import requests
from flask import current_app

class ClaudeService:
    def __init__(self):
        self.api_key = os.environ.get('CLAUDE_API_KEY')
        if not self.api_key:
            current_app.logger.error("CLAUDE_API_KEY not found in environment variables")
            raise ValueError("CLAUDE_API_KEY not set")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def analyze_resume(self, resume_content):
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": f"Please analyze this resume:\n\n{resume_content}\n\nProvide a JSON output with key skills and experience."
                }
            ]
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

    def tailor_resume(self, resume_content, job_description):
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": f"Please tailor this resume:\n\n{resume_content}\n\nTo this job description:\n\n{job_description}\n\nProvide the tailored resume and any questions about missing information in JSON format."
                }
            ]
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()