import pandas as pd
import joblib

def preprocess_and_predict(applicant, model_path):
    """
    Takes an applicant database model record, converts it into the exact DataFrame 
    format expected by the ML Pipeline, loads the specified model, and returns 
    the prediction class and probability of approval.
    """
    # Preprocess Days Birth -> Age in years
    age_years = -applicant.days_birth / 365.25
    
    # Preprocess Days Employed -> Years employed
    if applicant.days_employed == 365243:
        years_employed = 0.0
    else:
        years_employed = -applicant.days_employed / 365.25
        
    # Construct feature dictionary mapping exactly to columns in training
    input_data = {
        'CODE_GENDER': applicant.gender,
        'FLAG_OWN_CAR': applicant.own_car,
        'FLAG_OWN_REALTY': applicant.own_realty,
        'CNT_CHILDREN': applicant.cnt_children,
        'AMT_INCOME_TOTAL': applicant.amt_income_total,
        'NAME_INCOME_TYPE': applicant.name_income_type,
        'NAME_EDUCATION_TYPE': applicant.name_education_type,
        'NAME_FAMILY_STATUS': applicant.name_family_status,
        'NAME_HOUSING_TYPE': applicant.name_housing_type,
        'FLAG_WORK_PHONE': applicant.flag_work_phone,
        'FLAG_PHONE': applicant.flag_phone,
        'FLAG_EMAIL': applicant.flag_email,
        'OCCUPATION_TYPE': applicant.occupation_type if applicant.occupation_type else 'Other',
        'age_years': age_years,
        'years_employed': years_employed
    }
    
    # Create single-row pandas DataFrame
    df = pd.DataFrame([input_data])
    
    # Load serialized pipeline
    pipeline = joblib.load(model_path)
    
    # Run prediction
    prediction = pipeline.predict(df)[0]
    
    # Get probability score for class 1 (Approved / Good)
    if hasattr(pipeline, "predict_proba"):
        probability = pipeline.predict_proba(df)[0][1]
    else:
        # Fallback if model doesn't support probability
        probability = 1.0 if prediction == 1 else 0.0
        
    return prediction, probability
