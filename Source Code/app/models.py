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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Creator user
    
    # Demographic / Personal features
    gender = db.Column(db.String(10), nullable=False)             # CODE_GENDER (M/F)
    own_car = db.Column(db.String(5), nullable=False)              # FLAG_OWN_CAR (Y/N)
    own_realty = db.Column(db.String(5), nullable=False)           # FLAG_OWN_REALTY (Y/N)
    cnt_children = db.Column(db.Integer, nullable=False)          # CNT_CHILDREN
    amt_income_total = db.Column(db.Float, nullable=False)        # AMT_INCOME_TOTAL
    name_income_type = db.Column(db.String(50), nullable=False)    # NAME_INCOME_TYPE
    name_education_type = db.Column(db.String(100), nullable=False) # NAME_EDUCATION_TYPE
    name_family_status = db.Column(db.String(50), nullable=False)  # NAME_FAMILY_STATUS
    name_housing_type = db.Column(db.String(50), nullable=False)   # NAME_HOUSING_TYPE
    days_birth = db.Column(db.Integer, nullable=False)             # DAYS_BIRTH (Age in days, negative)
    days_employed = db.Column(db.Integer, nullable=False)          # DAYS_EMPLOYED (Employment in days, negative)
    flag_mobil = db.Column(db.Integer, default=1)                 # FLAG_MOBIL
    flag_work_phone = db.Column(db.Integer, default=0)            # FLAG_WORK_PHONE
    flag_phone = db.Column(db.Integer, default=0)                 # FLAG_PHONE
    flag_email = db.Column(db.Integer, default=0)                 # FLAG_EMAIL
    occupation_type = db.Column(db.String(100), nullable=True)     # OCCUPATION_TYPE
    
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
    months_balance = db.Column(db.Integer, nullable=False)         # MONTHS_BALANCE (Month offset from current, e.g., 0, -1, -2)
    status = db.Column(db.String(5), nullable=False)               # STATUS (0, 1, 2, 3, 4, 5, C, X)

    def __repr__(self):
        return f'<CreditHistory AppID:{self.applicant_id} Month:{self.months_balance} Status:{self.status}>'

class ML_Model(db.Model):
    __tablename__ = 'ml_model'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(100), unique=True, nullable=False) # e.g. "Random Forest"
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    model_path = db.Column(db.String(255), nullable=False)         # Local file path to serialized model
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Approval_Prediction', backref='ml_model', lazy=True)

    def __repr__(self):
        return f'<MLModel {self.model_name} (Active: {self.is_active})>'

class Approval_Prediction(db.Model):
    __tablename__ = 'approval_prediction'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Who queried the prediction
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant_details.id'), nullable=False)
    model_used_id = db.Column(db.Integer, db.ForeignKey('ml_model.id'), nullable=False)
    
    prediction_result = db.Column(db.Integer, nullable=False)     # 1 = Approved, 0 = Rejected
    prediction_probability = db.Column(db.Float, nullable=False)  # Probability of approval
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction AppID:{self.applicant_id} Result:{self.prediction_result}>'
