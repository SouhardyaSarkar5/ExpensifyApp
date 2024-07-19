from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

def init_db():
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            budget REAL NOT NULL
        )''')
        conn.commit()

def check_db_contents():
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM expenses')
        expenses = cursor.fetchall()
        print("Expenses:", expenses)

        cursor.execute('SELECT * FROM incomes')
        incomes = cursor.fetchall()
        print("Incomes:", incomes)

check_db_contents()

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/index')
def index():
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        
        # Fetch expenses
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        expenses = cursor.fetchall()
        
        # Fetch incomes
        cursor.execute('SELECT * FROM incomes ORDER BY date DESC')
        incomes = cursor.fetchall()
        
    return render_template('index.html', expenses=expenses, incomes=incomes)

@app.route('/summary')
def summary():
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        
        # Fetch expenses grouped by date
        cursor.execute('SELECT date, SUM(amount) AS total_expense FROM expenses GROUP BY date')
        expenses_data = cursor.fetchall()
        
        # Fetch incomes grouped by date
        cursor.execute('SELECT date, SUM(amount) AS total_income FROM incomes GROUP BY date')
        incomes_data = cursor.fetchall()
        
    return render_template('summary.html', expenses_data=expenses_data, incomes_data=incomes_data)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category'].capitalize()  # Capitalize the category
        description = request.form.get('description', '')
        date = request.form['date']

        with sqlite3.connect('expenses.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)', 
                           (amount, category, description, date))
            conn.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category'].capitalize()  # Capitalize the category
        description = request.form.get('description', '')
        date = request.form['date']

        with sqlite3.connect('expenses.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO incomes (amount, category, description, date) VALUES (?, ?, ?, ?)', 
                           (amount, category, description, date))
            conn.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_income.html')

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM incomes WHERE id = ?', (income_id,))
        conn.commit()
    flash('Income deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(port=8080, debug=True)
