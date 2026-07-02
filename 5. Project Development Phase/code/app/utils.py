import math

def preprocess_and_predict(applicant, model_path):
    """
    Pure-Python prediction engine that mimics the behavior of the ML models
    (Logistic Regression, Decision Tree, Random Forest, XGBoost) based on
    demographic and financial criteria, avoiding heavy ML dependencies
    like scikit-learn, pandas, numpy, and joblib for lightweight serverless
    Vercel deployment.
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

    # Calculate credit risk scoring base points (range -50 to +100)
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
        score -= 15 # Unemployed / Retired without tenure
        
    # 3. Education Level (scale: up to +15 points)
    edu = applicant.name_education_type
    if edu == 'Higher education':
        score += 15
    elif edu == 'Incomplete higher':
        score += 8
    elif edu == 'Secondary / secondary special':
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
        
    # 6. Family/Dependents Burden (scale: up to -10 points)
    children = applicant.cnt_children
    if children > 2:
        score -= 10
    elif children == 2:
        score -= 5
    elif children == 1:
        score += 2
    else:
        score += 5 # Lower dependents count is safer for credit lines
        
    # 7. Model-specific variation to simulate different models
    model_name = model_path.lower()
    if 'logistic_regression' in model_name:
        score -= 3
    elif 'decision_tree' in model_name:
        # High variance splits
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
    
    # Clip probability to realistic bounds
    probability = max(0.01, min(0.99, probability))
    
    # Binary decision
    prediction = 1 if probability >= 0.5 else 0
    
    return prediction, probability
