# Credit Card Approval Prediction - CreditValet

An end-to-end full-stack Machine Learning application developed as a **Skill Valet Internship Project**. This system evaluates credit card applications on-the-fly using trained classification models, logs applicant data, and presents a responsive model management dashboard.

---

## 🚀 How to View & Run the Interface

The Flask application is currently **running locally in the background** on your machine.

1. **Access the Web App**: Open your web browser and go to:
   👉 [**http://127.0.0.1:5000/**](http://127.0.0.1:5000/)
2. **First-time Sign Up**: Click **Register** on the navbar to create a local testing account.
3. **Log In**: Use your credentials to sign in.
4. **Make Predictions**: Fill out the applicant evaluation form to see if they are approved or rejected.
5. **Explore Dashboards**:
   - Check the **History** tab to see previously queried applicants.
   - Go to the **Models Dashboard** to compare model performance metrics and toggle the active classifier.

*Note: If you ever close the terminal or need to restart the application, run:*
```bash
python app.py
```

---

## 🛠️ Project Architecture & Tech Stack

This project is built using:
- **Web App**: Flask (Python web framework)
- **Database**: SQLite (SQL relational database) + SQLAlchemy ORM
- **Machine Learning**: Scikit-Learn & XGBoost
- **Styling**: Modern, premium CSS (dark theme, glassmorphic layout, Outfit & Inter fonts, neon accents)

### Database Schema (ER Diagram)

The database schema matches the required ER diagram and includes 5 tables:
1. **`Users`**: Standard authentication records (`username`, `email`, `password_hash`).
2. **`Applicant_Details`**: Stores demographic, asset, and income data points of applicants.
3. **`Credit_History`**: Logs monthly delinquency status records linked to applicant entries.
4. **`ML_Model`**: Details model files and test metrics (Accuracy, Precision, Recall, F1).
5. **`Approval_Prediction`**: Logs prediction records linking Users, Applicants, and ML Models.

---

## 📂 Project Structure

```
credit-card-approval-prediction/
├── 1. Brainstorming & Ideation/          # Phase 1: Ideation PDFs
├── 2. Requirement Analysis/              # Phase 2: Analysis PDFs
├── 3. Project Design Phase/              # Phase 3: Design PDFs
├── 4. Project Planning Phase/            # Phase 4: Planning PDFs
├── 5. Project Development Phase/         # Phase 5: Coding PDFs
├── 6.Project Testing/                    # Phase 6: Testing PDFs
├── 7.Project Documentation/              # Phase 7: Docs PDFs
├── 8.Project Demonstration/              # Phase 8: Demo PDFs
├── app/
│   ├── templates/                        # HTML views (base, login, register, predict, result, history, models)
│   ├── static/                           # Assets
│   │   ├── css/style.css                 # Premium theme stylesheet
│   │   └── js/main.js                    # Dynamic form controls & UI logic
│   ├── __init__.py                       # App factory & DB initialization
│   ├── models.py                         # SQLAlchemy database models
│   ├── routes.py                         # Authentication and app page routing
│   ├── utils.py                          # Prediction helper and preprocessor
│   └── creditcard.db                     # SQLite database file (auto-generated)
├── data/                                 # Datasets
│   ├── application_record.csv            # Demographics record
│   └── credit_record.csv                 # Historic credit record
├── models/                               # Serialized model pipelines (.pkl)
│   ├── best_model.pkl                    # Active predictor
│   ├── decision_tree_pipeline.pkl
│   ├── logistic_regression_pipeline.pkl
│   ├── random_forest_pipeline.pkl
│   └── xgboost_pipeline.pkl
├── train.py                              # ML Pipeline: Preprocessing, training, and database registration
├── app.py                                # Entry point to launch Flask server
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

---

## 📈 ML Pipeline & Model Training

The ML training pipeline is implemented in [`train.py`](file:///d:/creditcard/train.py):
1. **Data Preprocessing**: Combines demographic records with credit history logs. Engineering derives `age_years` and `years_employed` while cleaning outliers.
2. **Imbalance Handling**: Class weights are applied dynamically during training to mitigate minority class issues.
3. **Pipeline Construction**: Numerical scaling and categorical one-hot encoding are integrated directly into standard scikit-learn pipeline objects to avoid train-serve skew.
4. **Models Trained**:
   - Logistic Regression
   - Decision Tree
   - Random Forest
   - XGBoost
5. **Selection**: Saves individual pipelines, detects the best model based on F1-Score, and registers their details and metrics inside SQLite.

To retrain the models and update metrics, execute:
```bash
python train.py
```

---

## ☁️ IBM Watson ML Deployment

The application is structured to facilitate clean deployment to IBM Cloud:
1. **Model Persistence**: Pipelines are saved in standard `joblib` formats which are compatible with Watson ML.
2. **Environment Variables**: Sensitive configuration parameters (like Flask `SECRET_KEY` and database URIs) leverage `os.environ` defaults, enabling secure injection in cloud runtimes.
3. **Port Binding**: The entry point binds to host `0.0.0.0` and can bind to the environment variable `PORT` if running in containerized setups like Watson Studio or Cloud Foundry.