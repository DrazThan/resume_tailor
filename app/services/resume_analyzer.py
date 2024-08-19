import re
from collections import Counter
import spacy

class ResumeAnalyzer:
    def __init__(self, resume_content):
        self.content = resume_content
        self.nlp = spacy.load("en_core_web_sm")

    def extract_skills(self):
        doc = self.nlp(self.content)
        skill_patterns = [
            "python", "java", "c++", "javascript", "react", "node.js", "sql", "mongodb",
            "machine learning", "data analysis", "project management"
        ]
        skills = Counter()
        for token in doc:
            if token.text.lower() in skill_patterns:
                skills[token.text.lower()] += 1
        return dict(skills)

    def extract_experience(self):
        doc = self.nlp(self.content)
        experience = []
        for ent in doc.ents:
            if ent.label_ == "DATE" and "year" in ent.text.lower():
                experience.append(ent.text)
        return experience

    def analyze(self):
        return {
            'skills': self.extract_skills(),
            'experience': self.extract_experience()
        }