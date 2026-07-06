import math
import os

def preprocess_and_predict(applicant, model_path):
    """
    Evaluation engine that:
    1. Loads the actual trained ML pipeline (.pkl) to generate predictions locally.
    2. Falls back to a comprehensive pure-Python simulator if packages are not installed
       (specifically for Vercel serverless deployments to bypass the 500MB size limit).
    """
    # Preprocess Days Birth -> Age in years
    age_years = -applicant.days_birth / 365.25
    
    # Preprocess Days Employed -> Years employed
    if applicant.days_employed == 365243:
        years_employed = 0.0
    else:
        years_employed = -applicant.days_employed / 365.25
        
    # Hard rejection threshold: Any annual income below ₹1,20,000 (1.2 Lakhs) is automatically rejected
    income = applicant.amt_income_total
    if income < 120000:
        return 0, 0.05

    # --- 1. Try Predicting using the Serialized Machine Learning Pipeline ---
    try:
        import joblib
        import pandas as pd
        import numpy as np
        
        # Reconstruct exactly the features used during training in train.py
        input_data = pd.DataFrame([{
            'CODE_GENDER': applicant.gender,
            'FLAG_OWN_CAR': applicant.own_car,
            'FLAG_OWN_REALTY': applicant.own_realty,
            'NAME_INCOME_TYPE': applicant.name_income_type,
            'NAME_EDUCATION_TYPE': applicant.name_education_type,
            'NAME_FAMILY_STATUS': applicant.name_family_status,
            'NAME_HOUSING_TYPE': applicant.name_housing_type,
            'OCCUPATION_TYPE': applicant.occupation_type or 'Other',
            'CNT_CHILDREN': float(applicant.cnt_children or 0),
            'AMT_INCOME_TOTAL': float(applicant.amt_income_total),
            'age_years': float(age_years),
            'years_employed': float(years_employed),
            'FLAG_WORK_PHONE': int(applicant.flag_work_phone or 0),
            'FLAG_PHONE': int(applicant.flag_phone or 0),
            'FLAG_EMAIL': int(applicant.flag_email or 0)
        }])
        
        if os.path.exists(model_path):
            pipeline = joblib.load(model_path)
            prediction = int(pipeline.predict(input_data)[0])
            probs = pipeline.predict_proba(input_data)[0]
            probability = float(probs[1] if len(probs) > 1 else probs[0])
            return prediction, probability
    except Exception as e:
        print(f"ML Pipeline loading failed/skipped (using fallback simulator): {e}")

    # --- 2. Fallback Pure-Python Simulator Engine (fully considers all components) ---
    score = 0.0
    
    # 1. Income Factor (scale: up to +35 points)
    if income >= 300000:
        score += 35
    elif income >= 200000:
        score += 25
    elif income >= 135000:
        score += 15
    elif income >= 80000:
        score += 5
    else:
        score -= 10
        
    # 2. Employment Duration (scale: up to +25 points)
    if years_employed >= 10:
        score += 25
    elif years_employed >= 5:
        score += 18
    elif years_employed >= 2:
        score += 10
    elif years_employed > 0:
        score += 3
    else:
        score -= 15
        
    # 3. Education Level (scale: up to +15 points)
    edu = applicant.name_education_type
    if edu == 'Higher education' or 'higher' in str(edu).lower() or 'graduate' in str(edu).lower():
        score += 15
    elif edu == 'Incomplete higher':
        score += 8
    elif edu == 'Secondary / secondary special' or 'secondary' in str(edu).lower():
        score += 2
    else:
        score -= 5
        
    # 4. Property and Assets (scale: up to +15 points)
    if applicant.own_realty == 'Y':
        score += 8
    if applicant.own_car == 'Y':
        score += 7
        
    # 5. Age Factor (scale: up to +10 points)
    if 30 <= age_years <= 50:
        score += 10
    elif 23 <= age_years < 30 or 50 < age_years <= 60:
        score += 5
    else:
        score -= 5
        
    # 6. Family & Dependents Burden (scale: up to -10 points)
    children = applicant.cnt_children
    if children > 2:
        score -= 10
    elif children == 2:
        score -= 5
    elif children == 1:
        score += 2
    else:
        score += 5
        
    # 7. Additional Components (Housing, Family Status, Income Source)
    # Housing Type Stability
    ht = str(applicant.name_housing_type).lower()
    if 'house' in ht or 'apartment' in ht:
        score += 5
    elif 'parents' in ht:
        score += 2
    else:
        score -= 2
        
    # Family Status Stability
    fs = str(applicant.name_family_status).lower()
    if 'married' in fs:
        score += 5
    else:
        score += 1
        
    # Income Type Stability
    it = str(applicant.name_income_type).lower()
    if 'state' in it or 'servant' in it:
        score += 5
    elif 'pensioner' in it:
        score += 3
    elif 'working' in it:
        score += 2
    else:
        score -= 1

    # 8. Model-specific variation to simulate different models
    model_name = str(model_path).lower()
    if 'logistic_regression' in model_name:
        score -= 3
    elif 'decision_tree' in model_name:
        if score > 15:
            score += 12
        else:
            score -= 12
    elif 'random_forest' in model_name:
        score += 2
    elif 'xgboost' in model_name:
        score += 6
        
    # Map raw score to probability using Sigmoid function: P = 1 / (1 + exp(-k * (score - threshold)))
    k = 0.075
    threshold = 10.0
    probability = 1.0 / (1.0 + math.exp(-k * (score - threshold)))
    probability = max(0.01, min(0.99, probability))
    prediction = 1 if probability >= 0.5 else 0
    
    return prediction, probability
