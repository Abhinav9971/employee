import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Change this to a strong, random key in production

DATABASE = 'employees.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def init_db():
    """Initializes the database by creating the employees table if it doesn't exist."""
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL
            );
        ''')
        conn.commit()
        conn.close()

# Initialize the database when the application starts
init_db()

@app.route('/')
def index():
    """Displays a list of all employees."""
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=('GET', 'POST'))
def add_employee():
    """Adds a new employee to the database."""
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        salary = request.form['salary']

        if not name or not position or not department or not salary:
            flash('All fields are required!', 'error')
        else:
            try:
                salary = float(salary)
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO employees (name, position, department, salary) VALUES (?, ?, ?, ?)',
                    (name, position, department, salary)
                )
                conn.commit()
                conn.close()
                flash('Employee added successfully!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Salary must be a valid number!', 'error')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')

    return render_template('add_employee.html')

@app.route('/edit/<int:employee_id>', methods=('GET', 'POST'))
def edit_employee(employee_id):
    """Edits an existing employee's details."""
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()

    if employee is None:
        flash('Employee not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        salary = request.form['salary']

        if not name or not position or not department or not salary:
            flash('All fields are required!', 'error')
        else:
            try:
                salary = float(salary)
                conn.execute(
                    'UPDATE employees SET name = ?, position = ?, department = ?, salary = ? WHERE id = ?',
                    (name, position, department, salary, employee_id)
                )
                conn.commit()
                flash('Employee updated successfully!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Salary must be a valid number!', 'error')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:employee_id>', methods=('POST',))
def delete_employee(employee_id):
    """Deletes an employee from the database."""
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()

    if employee is None:
        flash('Employee not found!', 'error')
    else:
        conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        flash('Employee deleted successfully!', 'success')
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in production
