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

    def test_evaluate_application_approved(self):
        from app.utils import evaluate_application
        # Age 25, Salary 30k, Score 750, Salaried, EMI 5k (16.7%), No default
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=30000.0,
            credit_score=750,
            employment_status='Salaried',
            existing_emi=5000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 1)
        self.assertEqual(probability, 1.0)
        self.assertTrue(all(c['passed'] for c in checks))

    def test_evaluate_application_rejected_age(self):
        from app.utils import evaluate_application
        # Age 20 (fails age rule)
        prediction, probability, checks = evaluate_application(
            age_years=20.0,
            monthly_salary=30000.0,
            credit_score=750,
            employment_status='Salaried',
            existing_emi=5000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[0]['passed'])

    def test_evaluate_application_rejected_salary(self):
        from app.utils import evaluate_application
        # Salary 15k (fails salary rule)
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=15000.0,
            credit_score=750,
            employment_status='Salaried',
            existing_emi=1000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[1]['passed'])

    def test_evaluate_application_rejected_credit(self):
        from app.utils import evaluate_application
        # Credit Score 650 (fails credit rule)
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=30000.0,
            credit_score=650,
            employment_status='Salaried',
            existing_emi=5000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[2]['passed'])

    def test_evaluate_application_rejected_employment(self):
        from app.utils import evaluate_application
        # Employment Unemployed (fails employment status rule)
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=30000.0,
            credit_score=750,
            employment_status='Unemployed',
            existing_emi=5000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[3]['passed'])

    def test_evaluate_application_rejected_emi(self):
        from app.utils import evaluate_application
        # EMI 15k on 30k salary (50% > 40%) (fails EMI limit rule)
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=30000.0,
            credit_score=750,
            employment_status='Salaried',
            existing_emi=15000.0,
            has_loan_default=False
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[4]['passed'])

    def test_evaluate_application_rejected_default(self):
        from app.utils import evaluate_application
        # Default True (fails default rule)
        prediction, probability, checks = evaluate_application(
            age_years=25.0,
            monthly_salary=30000.0,
            credit_score=750,
            employment_status='Salaried',
            existing_emi=5000.0,
            has_loan_default=True
        )
        self.assertEqual(prediction, 0)
        self.assertEqual(probability, 0.0)
        self.assertFalse(checks[5]['passed'])

    def test_explanation_generation(self):
        from app.utils import evaluate_application, build_explanation
        # Test approved explanation
        _, _, checks_approved = evaluate_application(25, 30000, 750, 'Salaried', 5000, False)
        exp_approved = build_explanation(True, checks_approved)
        self.assertIn("approved", exp_approved)

        # Test rejected explanation
        _, _, checks_rejected = evaluate_application(20, 15000, 650, 'Unemployed', 15000, True)
        exp_rejected = build_explanation(False, checks_rejected)
        self.assertIn("rejected", exp_rejected)
        self.assertIn("age is at least 21 years", exp_rejected)
        self.assertIn("monthly salary is Rs. 20,000 or above", exp_rejected)

if __name__ == '__main__':
    unittest.main()
