# Project Demonstration Walkthrough

This document guides the mentor/evaluator through demonstrating the **Credit Card Approval Prediction** web application.

---

## 💻 Running the Demonstration

### 1. Launch the Application
Start the Flask web server locally by executing:
```bash
python app.py
```
Open a browser and navigate to: **`http://127.0.0.1:5000/`**

### 2. Register & Login
- Click **Register** in the navigation bar to create a local testing account.
- Input credentials (e.g. Username: `testuser`, Email: `testuser@example.com`, Password: `Password123`) and submit.
- Sign in with the registered credentials. You will be redirected to the **Home Page (Dashboard)**.

### 3. Home Page (Dashboard)
- Review the control cards showing **Total Queries**, **Approved Profiles**, **Rejected Profiles**, and the **Active Predictor** model name.
- View recent activity in the tables.

### 4. Running a Prediction Query
- Click **New Evaluation** or select **Predict** in the navbar.
- Fill out the applicant profile form (e.g., age, income, education, car ownership, occupation).
- Dynamic UX triggers will hide/disable experience duration input if you select "Unemployed/Retired" from the dropdown.
- Click **Evaluate Credit Approval** to run inference.
- View the **Evaluation Result** page which displays the approval/rejection decision alongside the confidence percentage score.

### 5. Managing Models
- Select **Models Dashboard** in the navbar.
- Compare performance metrics (Accuracy, Precision, Recall, F1) across the trained models (XGBoost, Random Forest, Decision Tree, Logistic Regression).
- Click **Activate Model** under any model card to instantly switch the active classifier used for scoring.

---

## 📈 ML Pipeline Verification

The pipeline has been fully executed by running `train.py`. Results on the test split are:
* **Logistic Regression**: Accuracy `0.4850`, F1-score `0.5381`
* **Decision Tree**: Accuracy `0.4750`, F1-score `0.5478`
* **Random Forest**: Accuracy `0.4700`, F1-score `0.5470`
* **XGBoost**: Accuracy `0.5000`, F1-score `0.5495` (XGBoost was set as the default active model)
