from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from analytics import get_summary, get_category_chart, get_monthly_chart

app = Flask(__name__)

def get_db_connection():
    """Connect to the database and return connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close() 

init_db()

@app.route('/')
def home():
    conn = get_db_connection()

    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = 'SELECT * FROM expenses WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)

    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC'


    expenses = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('index.html', expenses=expenses,
                           category=category,
                           date_from=date_from,
                           date_to=date_to)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)',
            (amount, category, description, date)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()

    if request.method =='POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        conn.execute('''
            UPDATE expenses
            SET amount = ?, category = ?, description = ?, date = ?
            WHERE id = ? 
        ''', (amount, category, description, date, id))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))
    expense = conn.execute(
        'SELECT * FROM expenses WHERE id = ?', (id,)
    ).fetchone()
    conn.close()
    
    return render_template('edit.html', expense = expense)

# ANALYTICS PAGE
@app.route('/analytics')
def analytics():
    summary = get_summary()
    pie_chart = get_category_chart()
    bar_chart = get_monthly_chart()
    return render_template('analytics.html',
                           summary=summary,
                           pie_chart=pie_chart,
                           bar_chart=bar_chart
                           )

if __name__ == '__main__':
    app.run(debug=True)