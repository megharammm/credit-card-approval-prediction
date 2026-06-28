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
            
    def test_public_pages_load(self):
        # Check that dashboard (index) loads directly
        r1 = self.client.get('/')
        self.assertEqual(r1.status_code, 200)
        
        # Check that predict form loads directly
        r2 = self.client.get('/predict')
        self.assertEqual(r2.status_code, 200)

        # Check that history logs page loads directly
        r3 = self.client.get('/history')
        self.assertEqual(r3.status_code, 200)

        # Check that models dashboard loads directly
        r4 = self.client.get('/models')
        self.assertEqual(r4.status_code, 200)

if __name__ == '__main__':
    unittest.main()
