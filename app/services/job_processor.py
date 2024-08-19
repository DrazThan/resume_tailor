import spacy
from collections import Counter

class JobProcessor:
    def __init__(self, job_description):
        self.content = job_description
        self.nlp = spacy.load("en_core_web_sm")

    def extract_required_skills(self):
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

    def extract_required_experience(self):
        doc = self.nlp(self.content)
        for ent in doc.ents:
            if ent.label_ == "DATE" and "year" in ent.text.lower():
                return ent.text
        return None

    def process(self):
        return {
            'required_skills': self.extract_required_skills(),
            'required_experience': self.extract_required_experience()
        }