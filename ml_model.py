import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_spending():
    """Predict next month's spending using Linear Regression"""
    
    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query('SELECT * FROM expenses', conn)
    conn.close()

    if len(df) == 0:
        return {
            'status': 'error',
            'message': 'No expenses found. Add some expenses first!'
        }

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Group by month
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly = df.groupby('month')['amount'].sum().reset_index()

    # Need at least 2 months of data
    if len(monthly) < 2:
        return {
            'status': 'error',
            'message': 'Need at least 2 months of data to predict. Add more expenses!'
        }

    # Prepare data for ML
    X = np.array(range(1, len(monthly) + 1)).reshape(-1, 1)
    y = monthly['amount'].values

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next month
    next_month_num = len(monthly) + 1
    prediction = model.predict([[next_month_num]])[0]

    # Make sure prediction is not negative
    if prediction < 0:
        prediction = 0

    # Calculate accuracy (R² score)
    score = model.score(X, y)

    # Get month names for display
    month_names = monthly['month'].tolist()
    month_amounts = monthly['amount'].tolist()

    return {
        'status': 'success',
        'prediction': round(prediction, 2),
        'score': round(score * 100, 1),
        'month_names': month_names,
        'month_amounts': month_amounts,
        'next_month': next_month_num
    }


def detect_anomalies():
    """Find unusual spending patterns"""

    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query('SELECT * FROM expenses', conn)
    conn.close()

    if len(df) < 3:
        return []

    alerts = []

    # ========================================
    # CHECK 1: Unusual INDIVIDUAL expenses
    # ========================================
    categories = df['category'].unique()

    for cat in categories:
        cat_expenses = df[df['category'] == cat]
        cat_amounts = cat_expenses['amount']

        if len(cat_amounts) < 3:
            continue

        # Use MEDIAN instead of MEAN
        # Median is not affected by outliers
        median = cat_amounts.median()
        
        # Use IQR (Interquartile Range) method
        q1 = cat_amounts.quantile(0.25)
        q3 = cat_amounts.quantile(0.75)
        iqr = q3 - q1

        # If IQR is 0 (all same values), use median-based threshold
        if iqr == 0:
            upper_limit = median * 3
        else:
            upper_limit = q3 + 1.5 * iqr

        # Also flag if expense is more than 3x the median
        simple_limit = median * 3

        # Use the LOWER of the two thresholds (catches more anomalies)
        threshold = min(upper_limit, simple_limit)

        # Make sure threshold is reasonable
        if threshold <= 0:
            threshold = median * 3

        for index, row in cat_expenses.iterrows():
            amount = row['amount']
            if amount > threshold:
                alerts.append({
                    'type': 'single',
                    'message': f"₹{amount} on {cat} is unusually HIGH (your typical {cat} expense is around ₹{round(median, 2)})",
                    'detail': f"{row['description']} | {row['date']}"
                })

    # ========================================
    # CHECK 2: Unusual MONTHLY totals
    # ========================================
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly = df.groupby('month')['amount'].sum()

    if len(monthly) >= 3:
        median_monthly = monthly.median()
        
        q1 = monthly.quantile(0.25)
        q3 = monthly.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            upper_limit = median_monthly * 2
            lower_limit = median_monthly * 0.3
        else:
            upper_limit = q3 + 1.5 * iqr
            lower_limit = q1 - 1.5 * iqr

        # Also use simple 2x median check
        simple_upper = median_monthly * 2
        upper_threshold = min(upper_limit, simple_upper)

        for month, total in monthly.items():
            if total > upper_threshold:
                alerts.append({
                    'type': 'monthly',
                    'message': f"Month {month}: ₹{total} is unusually HIGH (your typical monthly spending is around ₹{round(median_monthly, 2)})",
                    'detail': f"This is ₹{round(total - median_monthly, 2)} more than your typical month"
                })
            elif iqr > 0 and total < lower_limit:
                alerts.append({
                    'type': 'monthly',
                    'message': f"Month {month}: ₹{total} is unusually LOW (your typical monthly spending is around ₹{round(median_monthly, 2)})",
                    'detail': f"This is ₹{round(median_monthly - total, 2)} less than your typical month"
                })

    return alerts