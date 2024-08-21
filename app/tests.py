import unittest
from app import create_app, db
from app.models import User, Resume, JobDescription

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='test', email='test@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_resume_creation(self):
        u = User(username='test', email='test@example.com')
        db.session.add(u)
        db.session.commit()
        r = Resume(content='Test resume content', user_id=u.id)
        db.session.add(r)
        db.session.commit()
        self.assertIsNotNone(r.id)
        self.assertEqual(r.content, 'Test resume content')
        self.assertEqual(r.user_id, u.id)

if __name__ == '__main__':
    unittest.main()