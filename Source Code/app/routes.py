from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import db, Applicant_Details, ML_Model, Approval_Prediction
from app.utils import preprocess_and_predict
from datetime import datetime

# Initialize main blueprint
main = Blueprint('main', __name__)

# --- MAIN ROUTES ---

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
def dashboard():
    # Get stats for all queries (public / no authentication)
    total_queries = Approval_Prediction.query.count()
    approved_queries = Approval_Prediction.query.filter_by(prediction_result=1).count()
    rejected_queries = Approval_Prediction.query.filter_by(prediction_result=0).count()
    active_model = ML_Model.query.filter_by(is_active=True).first()
    
    # Recent 5 predictions
    recent_predictions = Approval_Prediction.query.order_by(Approval_Prediction.predicted_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        total_queries=total_queries,
        approved_queries=approved_queries,
        rejected_queries=rejected_queries,
        active_model=active_model,
        recent_predictions=recent_predictions
    )

@main.route('/predict', methods=['GET', 'POST'])
def predict():
    # Check if there is an active ML Model
    active_model = ML_Model.query.filter_by(is_active=True).first()
    
    if request.method == 'POST':
        try:
            # Retrieve applicant details from form
            gender = request.form.get('gender')
            own_car = request.form.get('own_car')
            own_realty = request.form.get('own_realty')
            cnt_children = int(request.form.get('cnt_children', 0))
            amt_income_total_raw = request.form.get('amt_income_total', '0')
            amt_income_total = float(str(amt_income_total_raw).replace(',', ''))
            name_income_type = request.form.get('name_income_type')
            name_education_type = request.form.get('name_education_type')
            name_family_status = request.form.get('name_family_status')
            name_housing_type = request.form.get('name_housing_type')
            
            # Days birth & days employed conversions
            age_years = float(request.form.get('age', 30))
            days_birth = int(-age_years * 365.25)
            
            employment_status = request.form.get('employment_status')
            if employment_status == 'Unemployed':
                days_employed = 365243 # Standard Kaggle code representing unemployed/pensioner
            else:
                exp_years = float(request.form.get('experience', 0))
                days_employed = int(-exp_years * 365.25)
                
            flag_mobil = int(request.form.get('flag_mobil', 1))
            flag_work_phone = int(request.form.get('flag_work_phone', 0))
            flag_phone = int(request.form.get('flag_phone', 0))
            flag_email = int(request.form.get('flag_email', 0))
            occupation_type = request.form.get('occupation_type')
            
            # Save applicant details to database (user_id is None)
            applicant = Applicant_Details(
                user_id=None,
                gender=gender,
                own_car=own_car,
                own_realty=own_realty,
                cnt_children=cnt_children,
                amt_income_total=amt_income_total,
                name_income_type=name_income_type,
                name_education_type=name_education_type,
                name_family_status=name_family_status,
                name_housing_type=name_housing_type,
                days_birth=days_birth,
                days_employed=days_employed,
                flag_mobil=flag_mobil,
                flag_work_phone=flag_work_phone,
                flag_phone=flag_phone,
                flag_email=flag_email,
                occupation_type=occupation_type
            )
            
            db.session.add(applicant)
            db.session.commit()
            
            # Run prediction logic using active model or fallback model path
            model_path = active_model.model_path if active_model else 'models/best_model.pkl'
            prediction_label, probability = preprocess_and_predict(applicant, model_path)
            
            # Save prediction record
            prediction = Approval_Prediction(
                user_id=None,
                applicant_id=applicant.id,
                model_used_id=active_model.id if active_model else 1,
                prediction_result=int(prediction_label),
                prediction_probability=float(probability)
            )
            db.session.add(prediction)
            db.session.commit()
            
            flash('Prediction generated successfully!', 'success')
            return redirect(url_for('main.result', prediction_id=prediction.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.predict'))
            
    return render_template('index.html', active_model=active_model)

@main.route('/result/<int:prediction_id>')
def result(prediction_id):
    prediction = Approval_Prediction.query.get_or_404(prediction_id)
    return render_template('result.html', prediction=prediction)

@main.route('/history')
def history():
    # Fetch all queries since there's no auth filtering
    predictions = Approval_Prediction.query.order_by(Approval_Prediction.predicted_at.desc()).all()
    return render_template('history.html', predictions=predictions)

@main.route('/models', methods=['GET'])
def models_dashboard():
    models = ML_Model.query.order_by(ML_Model.accuracy.desc()).all()
    return render_template('models.html', models=models)

@main.route('/models/toggle/<int:model_id>', methods=['POST'])
def toggle_model(model_id):
    model = ML_Model.query.get_or_404(model_id)
    
    # Deactivate all models
    ML_Model.query.update({ML_Model.is_active: False})
    
    # Activate selected model
    model.is_active = True
    db.session.commit()
    
    flash(f'{model.model_name} activated for predictions.', 'success')
    return redirect(url_for('main.models_dashboard'))
