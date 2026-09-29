from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Income, Expense, Budget
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home
@app.route("/")
def home():
    return render_template("index.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/add-income", methods=["POST"])
@login_required
def add_income():

    amount = float(request.form["amount"])
    source = request.form["source"]

    income = Income(
        amount=amount,
        source=source,
        user_id=current_user.id
    )

    db.session.add(income)
    db.session.commit()

    flash("Income added successfully!")

    return redirect(url_for("dashboard"))


@app.route("/add-expense", methods=["POST"])
@login_required
def add_expense():

    amount = float(request.form["amount"])
    category = request.form["category"]
    description = request.form["description"]

    expense = Expense(
        amount=amount,
        category=category,
        description=description,
        user_id=current_user.id
    )

    db.session.add(expense)
    db.session.commit()

    flash("Expense added successfully!")

    return redirect(url_for("dashboard"))
@app.route("/add-budget", methods=["POST"])
@login_required
def add_budget():

    category = request.form["category"]
    amount = float(request.form["amount"])

    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")

    budget = Budget(
        category=category,
        amount=amount,
        month=current_month,
        user_id=current_user.id
    )

    db.session.add(budget)
    db.session.commit()

    flash("Budget added successfully!")

    return redirect(url_for("dashboard"))

@app.route("/delete-income/<int:income_id>", methods=["POST"])
@login_required
def delete_income(income_id):
    income = Income.query.filter_by(
        id=income_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(income)
    db.session.commit()

    flash("Income deleted successfully!")
    return redirect(url_for("dashboard"))


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(expense)
    db.session.commit()

    flash("Expense deleted successfully!")
    return redirect(url_for("dashboard"))


@app.route("/delete-budget/<int:budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(budget)
    db.session.commit()

    flash("Budget deleted successfully!")
    return redirect(url_for("dashboard"))

@app.route("/ai-advisor", methods=["POST"])
@login_required
def ai_advisor():

    incomes = Income.query.filter_by(user_id=current_user.id).all()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    budgets = Budget.query.filter_by(user_id=current_user.id).all()

    total_income = sum(income.amount for income in incomes)
    total_expenses = sum(expense.amount for expense in expenses)
    savings = total_income - total_expenses

    user_question = request.form.get("question", "").strip()

    if not user_question:
        flash("Please enter a question for the AI Advisor.")
        return redirect(url_for("dashboard"))

    expense_summary = {}

    for expense in expenses:
        expense_summary[expense.category] = (
            expense_summary.get(expense.category, 0) + expense.amount
        )

    budget_summary = []

    for budget in budgets:
        spent = sum(
            expense.amount
            for expense in expenses
            if expense.category == budget.category
        )

        budget_summary.append(
            f"{budget.category}: Budget ₹{budget.amount:.2f}, "
            f"Spent ₹{spent:.2f}"
        )

    prompt = f"""
You are a personal finance education assistant.

Give general budgeting and financial-management guidance.
Do not recommend specific stocks, cryptocurrencies, trading strategies,
or other investments.

User's financial summary:

Total Income: ₹{total_income:.2f}
Total Expenses: ₹{total_expenses:.2f}
Current Savings: ₹{savings:.2f}

Expenses by category:
{expense_summary}

Budget information:
{budget_summary}

User's question:
{user_question}

Give a clear, practical answer based only on the information provided.
Do not invent financial numbers.
Keep the response easy to understand.
Mention that this is general educational guidance when appropriate.
"""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions="You are a helpful personal finance budgeting assistant.",
            input=prompt
        )

        ai_answer = response.output_text

    
    except Exception as e:
        print("AI ERROR:", type(e).__name__, str(e))
        ai_answer = "Sorry, the AI Advisor is currently unavailable. Please try again."

    return render_template(
        "dashboard.html",
        username=current_user.username,
        incomes=incomes,
        expenses=expenses,
        budgets=budgets,
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        savings_rate=(savings / total_income * 100) if total_income > 0 else 0,
        budget_analysis=[],
        ai_answer=ai_answer
    )
# Spending Analytics
@app.route("/analytics")
@login_required
def analytics():

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    category_totals = {}

    for expense in expenses:
        category_totals[expense.category] = (
            category_totals.get(expense.category, 0)
            + expense.amount
        )

    total_expenses = sum(expense.amount for expense in expenses)

    return render_template(
        "analytics.html",
        category_totals=category_totals,
        total_expenses=total_expenses
    )

# Monthly Financial Report
@app.route("/monthly-report")
@login_required
def monthly_report():

    selected_month = request.args.get(
        "month",
        datetime.now().strftime("%Y-%m")
    )

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    monthly_incomes = [
        income for income in incomes
        if income.date.strftime("%Y-%m") == selected_month
    ]

    monthly_expenses = [
        expense for expense in expenses
        if expense.date.strftime("%Y-%m") == selected_month
    ]

    total_income = sum(
        income.amount for income in monthly_incomes
    )

    total_expenses = sum(
        expense.amount for expense in monthly_expenses
    )

    savings = total_income - total_expenses

    if total_income > 0:
        savings_rate = (savings / total_income) * 100
    else:
        savings_rate = 0

    category_totals = {}

    for expense in monthly_expenses:
        category_totals[expense.category] = (
            category_totals.get(expense.category, 0)
            + expense.amount
        )

    if category_totals:
        highest_category = max(
            category_totals,
            key=category_totals.get
        )

        highest_category_amount = category_totals[
            highest_category
        ]
    else:
        highest_category = "No expenses"
        highest_category_amount = 0

    transaction_count = (
        len(monthly_incomes) + len(monthly_expenses)
    )

    return render_template(
        "monthly_report.html",
        selected_month=selected_month,
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        savings_rate=savings_rate,
        highest_category=highest_category,
        highest_category_amount=highest_category_amount,
        transaction_count=transaction_count
    )
# Financial Health
@app.route("/financial-health")
@login_required
def financial_health():

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    budgets = Budget.query.filter_by(
        user_id=current_user.id
    ).all()

    total_income = sum(
        income.amount for income in incomes
    )

    total_expenses = sum(
        expense.amount for expense in expenses
    )

    savings = total_income - total_expenses

    if total_income > 0:
        savings_rate = (savings / total_income) * 100
        expense_ratio = (total_expenses / total_income) * 100
    else:
        savings_rate = 0
        expense_ratio = 0

    score = 0

    # Savings
    if savings_rate >= 20:
        score += 40
    elif savings_rate >= 10:
        score += 25
    elif savings_rate > 0:
        score += 15

    # Expenses
    if expense_ratio <= 60:
        score += 30
    elif expense_ratio <= 80:
        score += 20
    elif expense_ratio <= 100:
        score += 10

    # Budget status
    overspent = 0

    for budget in budgets:

        spent = sum(
            expense.amount
            for expense in expenses
            if expense.category == budget.category
        )

        if spent > budget.amount:
            overspent += 1

    if not budgets:
        score += 15
    elif overspent == 0:
        score += 30
    elif overspent <= len(budgets) / 2:
        score += 15

    if score >= 75:
        status = "Healthy"
    elif score >= 50:
        status = "Moderate"
    else:
        status = "Needs Attention"

    return render_template(
        "financial_health.html",
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        savings_rate=savings_rate,
        expense_ratio=expense_ratio,
        score=score,
        status=status
    )
# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    budgets = Budget.query.filter_by(
        user_id=current_user.id
    ).all()

    total_income = sum(income.amount for income in incomes)
    total_expenses = sum(expense.amount for expense in expenses)
    savings = total_income - total_expenses

    if total_income > 0:
        savings_rate = (savings / total_income) * 100
    else:
        savings_rate = 0

    if savings < 0:
        savings_status = "Expenses are higher than income"
        savings_message = "Review your expenses and look for areas where spending can be reduced."
    elif savings_rate < 10:
        savings_status = "Low savings"
        savings_message = "Consider setting aside a small amount regularly for savings."
    elif savings_rate < 20:
        savings_status = "Moderate savings"
        savings_message = "You are saving some of your income. Continue monitoring your expenses."
    else:
        savings_status = "Good savings"
        savings_message = "You are maintaining a healthy gap between income and expenses."

    

    # Budget vs actual spending
    budget_analysis = []

    for budget in budgets:

        spent = sum(
            expense.amount
            for expense in expenses
            if expense.category == budget.category
        )

        remaining = budget.amount - spent

        if spent > budget.amount:
            status = "Overspent"
        else:
            status = "Within Budget"

        budget_analysis.append({
            "id": budget.id,
            "category": budget.category,
            "budget": budget.amount,
            "spent": spent,
            "remaining": remaining,
            "status": status
            
        })

    return render_template(
        "dashboard.html",
        username=current_user.username,
        incomes=incomes,
        expenses=expenses,
        budgets=budgets,
        budget_analysis=budget_analysis,
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        savings_status=savings_status,
        savings_message=savings_message,
        savings_rate=savings_rate
    )

# Logout
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)