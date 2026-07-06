def evaluate_application(age_years, monthly_salary, credit_score, employment_status,
                          existing_emi):
    """
    Pure rule-based credit card approval engine.

    Approves the application ONLY if ALL of the following are true:
      1. Age is at least 21 years
      2. Monthly salary is Rs. 20,000 or above
      3. Credit score is 700 or above
      4. Employment status is 'Salaried' or 'Self-employed'
      5. Existing EMI is less than or equal to 40% of monthly salary

    Returns a tuple: (prediction, probability, reasons)
      prediction  : 1 if approved, 0 if rejected
      probability : 1.0 if approved, 0.0 if rejected (kept so the rest of the
                    app / database schema, which expects a probability field,
                    keeps working without changes)
      reasons     : list of dicts, one per rule, each with 'label', 'passed',
                    and 'detail' -- used to explain the decision in plain language
    """
    emi_limit = monthly_salary * 0.4 if monthly_salary else 0
    emi_ratio = (existing_emi / monthly_salary * 100) if monthly_salary else float('inf')

    checks = [
        {
            'label': 'Age is at least 21 years',
            'passed': age_years >= 21,
            'detail': f'Applicant is {age_years:.0f} years old.'
        },
        {
            'label': 'Monthly salary is Rs. 20,000 or above',
            'passed': monthly_salary >= 20000,
            'detail': f'Monthly salary is Rs. {monthly_salary:,.0f}.'
        },
        {
            'label': 'Credit score is 700 or above',
            'passed': credit_score >= 700,
            'detail': f'Credit score is {credit_score}.'
        },
        {
            'label': 'Employment status is Salaried or Self-employed',
            'passed': employment_status in ('Salaried', 'Self-employed'),
            'detail': f'Employment status is {employment_status}.'
        },
        {
            'label': 'Existing EMI is 40% or less of monthly salary',
            'passed': existing_emi <= emi_limit,
            'detail': f'Existing EMI is Rs. {existing_emi:,.0f}, which is {emi_ratio:.1f}% of salary '
                      f'(limit is Rs. {emi_limit:,.0f}).'
        }
    ]

    approved = all(c['passed'] for c in checks)
    prediction = 1 if approved else 0
    probability = 1.0 if approved else 0.0

    return prediction, probability, checks


def build_explanation(approved, checks):
    """Builds a simple, plain-language explanation string from the rule checks."""
    if approved:
        return ('This application is approved. The applicant meets every requirement: '
                'they are old enough, earn enough, have a strong credit score, are in '
                'qualifying employment, keep their EMI within a safe limit of their salary, '
                'and have no history of default.')

    failed = [c['label'][0].lower() + c['label'][1:] for c in checks if not c['passed']]
    joined = '; '.join(failed)
    plural = 's' if len(failed) > 1 else ''
    return f'This application is rejected. It does not meet the following requirement{plural}: {joined}.'
