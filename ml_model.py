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
        cat_data = df[df['category'] == cat]['amount']

        if len(cat_data) < 3:
            continue

        mean = cat_data.mean()
        std = cat_data.std()

        if std == 0:
            continue

        for index, row in df[df['category'] == cat].iterrows():
            amount = row['amount']
            if amount > mean + 2 * std:
                alerts.append({
                    'type': 'single',
                    'message': f"₹{amount} on {cat} is unusually HIGH (your average {cat} expense is ₹{round(mean, 2)})",
                    'detail': f"{row['description']} | {row['date']}"
                })

    # ========================================
    # CHECK 2: Unusual MONTHLY totals
    # ========================================
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly = df.groupby('month')['amount'].sum()

    if len(monthly) >= 3:
        mean_monthly = monthly.mean()
        std_monthly = monthly.std()

        if std_monthly > 0:
            for month, total in monthly.items():
                if total > mean_monthly + 1.5 * std_monthly:
                    alerts.append({
                        'type': 'monthly',
                        'message': f"Month {month}: ₹{total} is unusually HIGH (your average monthly spending is ₹{round(mean_monthly, 2)})",
                        'detail': f"This is ₹{round(total - mean_monthly, 2)} more than your average month"
                    })
                elif total < mean_monthly - 1.5 * std_monthly:
                    alerts.append({
                        'type': 'monthly',
                        'message': f"Month {month}: ₹{total} is unusually LOW (your average monthly spending is ₹{round(mean_monthly, 2)})",
                        'detail': f"This is ₹{round(mean_monthly - total, 2)} less than your average month"
                    })

    return alerts