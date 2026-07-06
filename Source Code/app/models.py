from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy db object
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Approval_Prediction', backref='user', lazy=True)
    applicants = db.relationship('Applicant_Details', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Applicant_Details(db.Model):
    __tablename__ = 'applicant_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Creator user

    # --- Core fields required by the rule-based approval engine ---
    age_years = db.Column(db.Float, nullable=False, default=30.0)
    monthly_salary = db.Column(db.Float, nullable=False, default=0.0)
    employment_status = db.Column(db.String(50), nullable=False, default='Salaried')
    credit_score = db.Column(db.Integer, nullable=False, default=0)          # 300-900 typical range
    existing_emi = db.Column(db.Float, nullable=False, default=0.0)          # Rs./month

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    credit_histories = db.relationship('Credit_History', backref='applicant', lazy=True, cascade="all, delete-orphan")
    predictions = db.relationship('Approval_Prediction', backref='applicant', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Applicant {self.id}>'

class Credit_History(db.Model):
    __tablename__ = 'credit_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant_details.id'), nullable=False)
    months_balance = db.Column(db.Integer, nullable=False)         # MONTHS_BALANCE
    status = db.Column(db.String(5), nullable=False)               # STATUS

    def __repr__(self):
        return f'<CreditHistory AppID:{self.applicant_id} Month:{self.months_balance} Status:{self.status}>'

class ML_Model(db.Model):
    __tablename__ = 'ml_model'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(100), unique=True, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    model_path = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Approval_Prediction', backref='ml_model', lazy=True)

    def __repr__(self):
        return f'<MLModel {self.model_name} (Active: {self.is_active})>'

class Approval_Prediction(db.Model):
    __tablename__ = 'approval_prediction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant_details.id'), nullable=False)
    model_used_id = db.Column(db.Integer, db.ForeignKey('ml_model.id'), nullable=False)

    prediction_result = db.Column(db.Integer, nullable=False)     # 1 = Approved, 0 = Rejected
    prediction_probability = db.Column(db.Float, nullable=False)  # 1.0 or 0.0 for the rule-based engine
    explanation = db.Column(db.Text, nullable=True)                # Plain-language reason for the decision
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction AppID:{self.applicant_id} Result:{self.prediction_result}>'
