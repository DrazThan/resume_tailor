from app.services.resume_analyzer import ResumeAnalyzer
from app.services.job_processor import JobProcessor

class ResumeTailor:
    def __init__(self, resume_content, job_description):
        self.resume = resume_content
        self.job = job_description
        self.resume_analyzer = ResumeAnalyzer(resume_content)
        self.job_processor = JobProcessor(job_description)

    def tailor(self):
        resume_analysis = self.resume_analyzer.analyze()
        job_analysis = self.job_processor.process()

        missing_skills = set(job_analysis['required_skills']) - set(resume_analysis['skills'])
        tailored_resume = self.resume

        if missing_skills:
            tailored_resume += "\n\nAdditional Skills:\n"
            for skill in missing_skills:
                tailored_resume += f"• Familiar with {skill} and eager to apply and develop skills further\n"

        if job_analysis['required_experience'] and not any(job_analysis['required_experience'] in exp for exp in resume_analysis['experience']):
            tailored_resume += f"\n• {job_analysis['required_experience']} of relevant industry experience\n"

        return tailored_resume