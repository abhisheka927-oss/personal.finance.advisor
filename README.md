# 💰 Personal Finance Advisor Bot

An AI-powered personal finance management web application built using Flask, Python, SQLAlchemy, SQLite, and OpenAI API.

## 🚀 Features

- User Registration and Login
- Secure Password Hashing
- Income Tracking
- Expense Tracking
- Expense Categorization
- Budget Management
- Budget vs Spending Analysis
- Overspending Detection
- Savings Calculation
- Savings Rate Analysis
- Spending Analytics
- Monthly Financial Reports
- Financial Health Score
- AI-powered Financial Advisor
- Dashboard with Financial Summary
- Protected User Routes
- SQLite Database
- Environment Variable Configuration

## 🛠️ Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- HTML
- CSS
- OpenAI API
- python-dotenv
- Git & GitHub

## 📂 Project Structure

```text
Personal-Finance-Advisor-Bot/
│
├── app.py
├── models.py
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── analytics.html
│   ├── monthly_report.html
│   └── financial_health.html
│
├── static/
├── instance/
└── venv/

git clone https://github.com/abhisheka927-oss/personal.finance.advisor.git

cd personal.finance.advisor

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

OPENAI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
