import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def get_summary():
    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query('SELECT * FROM expenses', conn)
    conn.close()

    if len(df) == 0:
        return{
            'total' : 0,
            'count' : 0,
            'average' : 0,
            'highest' : 0,
            'lowest' : 0
        }
    summary = {
        'total' : round(df['amount'].sum(), 2),
        'count' : len(df),
        'average' : round(df['amount'].mean(), 2),
        'highest' : round(df['amount'].max(), 2),
        'lowest' : round(df['amount'].min(), 2)
    }
    return summary

def get_category_chart():
    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query('SELECT * FROM expenses', conn)
    conn.close()

    if len(df) == 0:
        return None
    
    category_totals = df.groupby('category')['amount'].sum()

    plt.figure(figsize=(7,5))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    plt.pie(
        category_totals.values,
        labels=category_totals.index,
        autopct='%1.1f%%',
        colors=colors[:len(category_totals)],
        startangle=140
    )
    plt.title('Spending by Category', fontsize=16, fontweight='bold')
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return chart_url

def get_monthly_chart():
    """Generate bar chart of spending by month"""
    try:
        conn = sqlite3.connect('expenses.db')
        df = pd.read_sql_query('SELECT * FROM expenses', conn)
        conn.close()

        if len(df) == 0:
            return None

        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Create a column like "2025-01" for grouping
        df['month'] = df['date'].dt.strftime('%Y-%m')

        # Group by month and sum amounts
        monthly_totals = df.groupby('month')['amount'].sum()

        # Create bar chart
        plt.figure(figsize=(8, 5))
        bars = plt.bar(
            range(len(monthly_totals)),
            monthly_totals.values,
            color='#3498db'
        )

        # Add month labels on x-axis
        plt.xticks(range(len(monthly_totals)), monthly_totals.index, rotation=45)

        # Add amount labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'Rs.{int(height)}',
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        plt.title('Monthly Spending', fontsize=16, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Amount (Rs.)')
        plt.tight_layout()

        # Convert chart to image string
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return chart_url

    except Exception as e:
        print(f"ERROR in monthly chart: {e}")
        plt.close()
        return None