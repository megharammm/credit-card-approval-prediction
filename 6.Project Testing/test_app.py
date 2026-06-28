import os
import sys
import unittest

# Add root folder to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db

class CreditValetTest(unittest.TestCase):
    def setUp(self):
        # Configure app for testing with an in-memory DB
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            
    def test_auth_pages_load(self):
        # Check if auth pages load correctly
        r1 = self.client.get('/login')
        self.assertEqual(r1.status_code, 200)
        
        r2 = self.client.get('/register')
        self.assertEqual(r2.status_code, 200)

    def test_unauthenticated_redirect(self):
        # Predict page should redirect unauthenticated users to login
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])

    def test_dashboard_redirect(self):
        # Accessing home root should redirect to login when unauthenticated
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])

if __name__ == '__main__':
    unittest.main()
