import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
import joblib

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Create directories if they don't exist
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

# 1. Dataset Generation (Synthetic)
def generate_synthetic_data(num_records=1000):
    print("Generating synthetic datasets...")
    np.random.seed(42)
    
    # Generate Application Records
    ids = np.arange(5000000, 5000000 + num_records)
    genders = np.random.choice(['M', 'F'], size=num_records, p=[0.4, 0.6])
    own_car = np.random.choice(['Y', 'N'], size=num_records, p=[0.35, 0.65])
    own_realty = np.random.choice(['Y', 'N'], size=num_records, p=[0.7, 0.3])
    cnt_children = np.random.choice([0, 1, 2, 3], size=num_records, p=[0.7, 0.2, 0.08, 0.02])
    
    # Incomes correlated with education/job type roughly
    income_base = np.random.lognormal(mean=11.8, sigma=0.5, size=num_records)
    amt_income_total = np.round(income_base / 1000) * 1000
    
    income_types = np.random.choice(
        ['Working', 'Commercial associate', 'Pensioner', 'State servant', 'Student'],
        size=num_records, p=[0.55, 0.22, 0.15, 0.078, 0.002]
    )
    
    education_types = np.random.choice(
        ['Secondary / secondary special', 'Higher education', 'Incomplete higher', 'Lower secondary', 'Academic degree'],
        size=num_records, p=[0.71, 0.24, 0.035, 0.014, 0.001]
    )
    
    family_statuses = np.random.choice(
        ['Married', 'Single / not married', 'Civil marriage', 'Separated', 'Widow'],
        size=num_records, p=[0.68, 0.14, 0.08, 0.06, 0.04]
    )
    
    housing_types = np.random.choice(
        ['House / apartment', 'With parents', 'Rented apartment', 'Municipal apartment', 'Office apartment', 'Co-op apartment'],
        size=num_records, p=[0.89, 0.05, 0.03, 0.017, 0.01, 0.003]
    )
    
    # Days birth (Age 21 to 65 represented in negative days)
    ages = np.random.randint(21, 66, size=num_records)
    days_birth = -ages * 365
    
    # Days employed
    days_employed = []
    for i in range(num_records):
        if income_types[i] == 'Pensioner':
            days_employed.append(365243) # Unemployed/retired flag
        else:
            max_work_years = ages[i] - 18
            work_years = np.random.randint(0, max_work_years + 1)
            days_employed.append(-work_years * 365)
    days_employed = np.array(days_employed)
    
    flag_mobil = np.ones(num_records, dtype=int)
    flag_work_phone = np.random.choice([0, 1], size=num_records, p=[0.78, 0.22])
    flag_phone = np.random.choice([0, 1], size=num_records, p=[0.7, 0.3])
    flag_email = np.random.choice([0, 1], size=num_records, p=[0.9, 0.1])
    
    occupations = ['Laborers', 'Core staff', 'Sales staff', 'Managers', 'Drivers', 'High skill tech staff',
                   'Accountants', 'Medicine staff', 'Cooking staff', 'Security staff', 'Cleaning staff',
                   'Private service staff', 'Low-skill Laborers', 'Waiters/barmen staff', 'Secretaries',
                   'HR staff', 'Realty agents', 'IT staff']
    
    occupation_types = []
    for i in range(num_records):
        if income_types[i] == 'Pensioner':
            occupation_types.append('') # Pensioners usually have no occupation type in Kaggle
        else:
            occupation_types.append(np.random.choice(occupations))
            
    df_app = pd.DataFrame({
        'ID': ids,
        'CODE_GENDER': genders,
        'FLAG_OWN_CAR': own_car,
        'FLAG_OWN_REALTY': own_realty,
        'CNT_CHILDREN': cnt_children,
        'AMT_INCOME_TOTAL': amt_income_total,
        'NAME_INCOME_TYPE': income_types,
        'NAME_EDUCATION_TYPE': education_types,
        'NAME_FAMILY_STATUS': family_statuses,
        'NAME_HOUSING_TYPE': housing_types,
        'DAYS_BIRTH': days_birth,
        'DAYS_EMPLOYED': days_employed,
        'FLAG_MOBIL': flag_mobil,
        'FLAG_WORK_PHONE': flag_work_phone,
        'FLAG_PHONE': flag_phone,
        'FLAG_EMAIL': flag_email,
        'OCCUPATION_TYPE': occupation_types
    })
    df_app.to_csv('data/application_record.csv', index=False)
    
    # Generate Credit Records
    credit_data = []
    for cid in ids:
        history_len = np.random.randint(1, 36) # Credit history 1 to 36 months
        months = np.arange(-history_len + 1, 1)
        
        # Determine client quality class
        # Add slight correlation with income and education
        base_prob = 0.90 # 90% good by default
        idx = np.where(ids == cid)[0][0]
        if amt_income_total[idx] < 120000:
            base_prob -= 0.15
        if education_types[idx] == 'Secondary / secondary special':
            base_prob -= 0.05
        if own_car[idx] == 'Y':
            base_prob += 0.05
            
        base_prob = np.clip(base_prob, 0.5, 0.98)
        
        # Good/Bad client profile
        is_bad_client = np.random.rand() > base_prob
        
        for m in months:
            if is_bad_client:
                # Higher chance of past due status
                status = np.random.choice(['C', '0', '1', '2', '3', '4', '5'], p=[0.2, 0.4, 0.2, 0.1, 0.05, 0.03, 0.02])
            else:
                # Mostly Paid off (C) or No loan (X) or 1-29 days past due (0)
                status = np.random.choice(['C', 'X', '0', '1'], p=[0.5, 0.2, 0.28, 0.02])
            credit_data.append([cid, m, status])
            
    df_credit = pd.DataFrame(credit_data, columns=['ID', 'MONTHS_BALANCE', 'STATUS'])
    df_credit.to_csv('data/credit_record.csv', index=False)
    print("Synthetic datasets successfully created in /data.")

# Clean & Preprocess Data
def load_and_preprocess_data():
    if not os.path.exists('data/application_record.csv') or not os.path.exists('data/credit_record.csv'):
        generate_synthetic_data()
        
    print("Loading datasets...")
    app_df = pd.read_csv('data/application_record.csv')
    credit_df = pd.read_csv('data/credit_record.csv')
    
    # Define Target Label
    # 0 = Bad (delinquent 30+ days: status 1, 2, 3, 4, 5)
    # 1 = Good (Approved: status 0, C, X)
    credit_df['is_bad'] = credit_df['STATUS'].isin(['1', '2', '3', '4', '5']).astype(int)
    grouped = credit_df.groupby('ID')['is_bad'].max().reset_index()
    grouped['target'] = 1 - grouped['is_bad']
    
    # Merge datasets
    merged = pd.merge(app_df, grouped[['ID', 'target']], on='ID', how='inner')
    print(f"Dataset shape after merging: {merged.shape}")
    print(f"Target distribution:\n{merged['target'].value_counts(normalize=True)}")
    
    # Feature Engineering
    merged['age_years'] = -merged['DAYS_BIRTH'] / 365.25
    merged['years_employed'] = merged['DAYS_EMPLOYED'].apply(lambda x: -x / 365.25 if x < 0 else 0.0)
    
    # Drop raw date columns, IDs, and redundant flags
    X = merged.drop(columns=['ID', 'DAYS_BIRTH', 'DAYS_EMPLOYED', 'FLAG_MOBIL', 'target'])
    y = merged['target']
    
    # Handle missing occupations
    X['OCCUPATION_TYPE'] = X['OCCUPATION_TYPE'].fillna('Other')
    
    return X, y

# Main Training Pipeline
def run_pipeline():
    X, y = load_and_preprocess_data()
    
    # Categorical and Numerical splits for column transformation
    categorical_cols = ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY', 
                        'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 
                        'NAME_FAMILY_STATUS', 'NAME_HOUSING_TYPE', 'OCCUPATION_TYPE']
    
    numerical_cols = ['CNT_CHILDREN', 'AMT_INCOME_TOTAL', 'age_years', 'years_employed',
                      'FLAG_WORK_PHONE', 'FLAG_PHONE', 'FLAG_EMAIL']
                      
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ])
        
    # Defined Models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, class_weight='balanced', random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=float(sum(y==0))/sum(y==1), random_state=42)
    }
    
    results = {}
    best_f1 = 0
    best_model_name = None
    
    print("\n--- Training Models ---")
    for name, clf in models.items():
        # Build training pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', clf)
        ])
        
        # Fit
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        
        # Evaluate
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        results[name] = {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'pipeline': pipeline
        }
        print(f"{name:20} - Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")
        
        # Save pipeline file
        clean_name = name.lower().replace(' ', '_')
        model_filename = f"models/{clean_name}_pipeline.pkl"
        joblib.dump(pipeline, model_filename)
        results[name]['path'] = model_filename
        
        # Select best model based on F1 Score
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    print(f"\nBest Model identified: {best_model_name} with F1-score: {best_f1:.4f}")
    
    # Save the best model as best_model.pkl
    best_pipeline = results[best_model_name]['pipeline']
    joblib.dump(best_pipeline, 'models/best_model.pkl')
    print("Saved best model pipeline to models/best_model.pkl")
    
    # Write metadata of ALL 4 models into the ML_Model database using SQLAlchemy
    from app import create_app
    from app.models import db, ML_Model
    
    app = create_app()
    with app.app_context():
        # Clean previous models
        db.session.query(ML_Model).delete()
        
        for name, info in results.items():
            is_active = (name == best_model_name)
            ml_model = ML_Model(
                model_name=name,
                accuracy=float(info['accuracy']),
                precision=float(info['precision']),
                recall=float(info['recall']),
                f1_score=float(info['f1_score']),
                model_path=info['path'],
                is_active=is_active
            )
            db.session.add(ml_model)
            
        # Add an entry for "Best Model" which points to best_model.pkl
        best_ml_model = ML_Model(
            model_name="Best Model (Auto)",
            accuracy=float(results[best_model_name]['accuracy']),
            precision=float(results[best_model_name]['precision']),
            recall=float(results[best_model_name]['recall']),
            f1_score=float(results[best_model_name]['f1_score']),
            model_path='models/best_model.pkl',
            is_active=False
        )
        db.session.add(best_ml_model)
        
        db.session.commit()
    print("Registered all 4 models and the 'Best Model (Auto)' metadata inside the SQLite database.")

if __name__ == '__main__':
    run_pipeline()
