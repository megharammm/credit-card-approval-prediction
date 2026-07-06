from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import db, Applicant_Details, ML_Model, Approval_Prediction
from app.utils import evaluate_application, build_explanation
from datetime import datetime

# Initialize main blueprint
main = Blueprint('main', __name__)

# --- MAIN ROUTES ---

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
def dashboard():
    total_queries = Approval_Prediction.query.count()
    approved_queries = Approval_Prediction.query.filter_by(prediction_result=1).count()
    rejected_queries = Approval_Prediction.query.filter_by(prediction_result=0).count()
    active_model = ML_Model.query.filter_by(is_active=True).first()

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
    active_model = ML_Model.query.filter_by(is_active=True).first()

    if request.method == 'POST':
        try:
            # --- Core fields for rule-based engine ---
            monthly_salary_raw = request.form.get('monthly_salary', '0')
            monthly_salary = float(str(monthly_salary_raw).replace(',', ''))
            
            age_years = float(request.form.get('age', 0))
            employment_status = request.form.get('employment_status')
            
            credit_score = int(request.form.get('credit_score', 0))
            existing_emi_raw = request.form.get('existing_emi', '0')
            existing_emi = float(str(existing_emi_raw).replace(',', ''))

            # Save applicant details to database
            applicant = Applicant_Details(
                user_id=None,
                age_years=age_years,
                monthly_salary=monthly_salary,
                employment_status=employment_status,
                credit_score=credit_score,
                existing_emi=existing_emi
            )

            db.session.add(applicant)
            db.session.commit()

            # Run the rule-based evaluation (see app/utils.py)
            prediction_label, probability, checks = evaluate_application(
                age_years=age_years,
                monthly_salary=monthly_salary,
                credit_score=credit_score,
                employment_status=employment_status,
                existing_emi=existing_emi
            )
            explanation = build_explanation(bool(prediction_label), checks)

            # Save prediction record
            prediction = Approval_Prediction(
                user_id=None,
                applicant_id=applicant.id,
                model_used_id=active_model.id if active_model else 1,
                prediction_result=int(prediction_label),
                prediction_probability=float(probability),
                explanation=explanation  # NOTE: add this column to Approval_Prediction
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
    predictions = Approval_Prediction.query.order_by(Approval_Prediction.predicted_at.desc()).all()
    return render_template('history.html', predictions=predictions)

@main.route('/models', methods=['GET'])
def models_dashboard():
    models = ML_Model.query.order_by(ML_Model.accuracy.desc()).all()
    return render_template('models.html', models=models)

@main.route('/models/toggle/<int:model_id>', methods=['POST'])
def toggle_model(model_id):
    model = ML_Model.query.get_or_404(model_id)
    ML_Model.query.update({ML_Model.is_active: False})
    model.is_active = True
    db.session.commit()
    flash(f'{model.model_name} activated for predictions.', 'success')
    return redirect(url_for('main.models_dashboard'))
