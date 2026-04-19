# 💰 Smart Expense Tracker

A full-stack expense tracking web application with **Machine Learning** based spending prediction and **anomaly detection** for unusual spending patterns. Built to solve real-world personal finance problems.

**🔗 Live Demo:** https://smart-expense-tracker-ifij.onrender.com/

---

## ✨ Features

### 📝 Core Tracking
- **CRUD Operations:** Add, edit, and delete daily expenses.
- **Categorization:** Classify spending into Food, Transport, Shopping, Entertainment, Bills, or Other.
- **Smart Filtering:** Filter records by specific categories or custom date ranges.
- **Budget Management:** Set a monthly budget and track it with a dynamic, color-coded progress bar (Green/Yellow/Red alerts).

### 📊 Analytics Dashboard
- **Data Processing:** Uses Pandas to aggregate and process database records.
- **Visualizations:** Auto-generated Matplotlib charts.
  - Pie Chart: Category-wise spending breakdown.
  - Bar Chart: Month-over-month spending trends.
- **Summary Stats:** Instantly view Total, Average, Highest, and Lowest expenses.

### 🤖 Machine Learning & Intelligence
- **Spending Prediction:** Uses Scikit-Learn (`LinearRegression`) to analyze past monthly totals and predict next month's spending.
- **Model Accuracy:** Calculates and displays the R² score of the prediction model.
- **Anomaly Detection:** Uses the Interquartile Range (IQR) statistical method and Median checks to flag unusually high individual expenses or abnormal monthly totals.

### 💻 UI/UX
- **Fully Responsive:** Custom CSS ensures the app works perfectly on desktops, tablets, and mobile phones.
- **Flash Messages:** Real-time success/error notifications for user actions.
- **Clean Interface:** Modern, professional design without bloated external CSS frameworks.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Data Science & ML:** Pandas, Scikit-Learn (Linear Regression), NumPy
- **Data Visualization:** Matplotlib
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Deployment:** Gunicorn, Render

---

## 🚀 How To Run Locally

### Prerequisites
Make sure you have Python 3.11+ installed on your machine.

### Installation

1. **Clone the repository**
git clone https://github.com/YOUR_USERNAME/smart-expense-tracker.git
cd smart-expense-tracker

2. Install the required dependencies
pip install -r requirements.txt

3. Run the application
python app.py

4. Open in your browser
Navigate to http://127.0.0.1:5000
Note: The SQLite database (expenses.db) will be created automatically when you first run the app.

📁 Project Structure
smart-expense-tracker/
│
├── app.py                 # Main Flask application (routes & backend logic)
├── analytics.py           # Pandas data processing & Matplotlib chart generation
├── ml_model.py            # Scikit-Learn linear regression & IQR anomaly detection
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment configuration for Render
├── .python-version        # Specifies Python version for cloud deployment
│
├── templates/             # Jinja2 HTML Templates
│   ├── base.html          # Base layout (navbar, footer, flash messages)
│   ├── index.html         # Dashboard (expenses table, filters, budget bar)
│   ├── analytics.html     # Analytics dashboard with charts
│   ├── predictions.html   # ML predictions & anomaly alerts
│   ├── budget.html        # Budget setting form
│   └── add/edit.html      # Expense forms
│
└── static/                
    └── style.css          # Custom responsive styling

    
🧠 How The Intelligence Works
1. Spending Prediction (Linear Regression):
The app queries the SQLite database, groups expenses by month using Pandas, and feeds the monthly totals into a Scikit-Learn LinearRegression model. The model calculates the line of best fit (y=mx+c) to predict the subsequent month's total spending.

2. Anomaly Detection (Robust Statistics):
Instead of using a simple Mean (which is skewed by outliers), the app uses the Median and Interquartile Range (IQR).

It calculates Q1 and Q3 for each category.
It defines an upper threshold (Q3+1.5×IQR).
Any expense crossing this mathematical threshold is flagged as an anomaly, warning the user of unusual spending behavior.
👤 Author
Tushar Yadav

GitHub: @tusharyadav869
LinkedIn: https://www.linkedin.com/in/tushar-yadav-733a86313/
