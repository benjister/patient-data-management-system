from flask import Flask, render_template, request, redirect, url_for, session
import csv
import bcrypt

app = Flask(__name__)
app.secret_key = 'Passphrase@alx'

users = {
    "admin": {"password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()), "role": "admin"},
    "user": {"password": bcrypt.hashpw("userpass".encode('utf-8'), bcrypt.gensalt()), "role": "user"}
}

def load_patient_data():
    try:
        with open('patient_data.csv', mode='r') as f:
            reader = csv.reader(f)
            return list(reader)
    except FileNotFoundError:
        return []

def save_patient_data(data):
    try:
        with open('patient_data.csv', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    except Exception as e:
        print(f"Error saving data: {e}")

@app.route('/')
def index():
    error = request.args.get('error')
    message = request.args.get('message')
    return render_template('login.html', error=error, message=message)

@app.route('/search')
def search():
    query = request.args.get('search')
    if query:
        patient_list = load_patient_data()
        search_results = [patient for patient in patient_list if query.lower() in patient[0].lower()]
        return render_template('patients.html', patients=search_results)
    else:
        return redirect(url_for('patients'))

@app.route('/patients')
def patients():
    if 'username' not in session:
        return redirect(url_for('index'))
    patient_list = load_patient_data()
    return render_template('patients.html', patients=patient_list)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    if username in users and bcrypt.checkpw(password, users[username]['password']):
        session['username'] = username
        session['role'] = users[username]['role']
        return redirect(url_for('patients'))
    else:
        error = "Invalid username or password. Please try again."
        return redirect(url_for('index', error=error))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        if username not in users:
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            users[username] = {"password": hashed_password, "role": "user"}
            message = "Successfully signed up! Please log in."
            return redirect(url_for('index', message=message))
        else:
            error = "Username already exists. Please choose a different username."
            return redirect(url_for('index', error=error))
    return render_template('signup.html')

@app.route('/patient_form')
def patient_form():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        diagnosis = request.form['diagnosis']
        
        patient_data = [name, age, gender, diagnosis]
        patient_list = load_patient_data()
        patient_list.append(patient_data)
        save_patient_data(patient_list)
        
        return redirect(url_for('patients'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    patient_list = load_patient_data()
    del patient_list[index - 1]
    save_patient_data(patient_list)
    return redirect(url_for('patients'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if 'username' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        patient_list = load_patient_data()
        patient = patient_list[index - 1]
        return render_template('edit.html', patient=patient, index=index)
    elif request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        diagnosis = request.form['diagnosis']
        
        patient_list = load_patient_data()
        patient_list[index - 1] = [name, age, gender, diagnosis]
        save_patient_data(patient_list)
        
        return redirect(url_for('patients'))

@app.route('/export')
def export():
    if 'username' not in session:
        return redirect(url_for('index'))
    patient_list = load_patient_data()
    response = make_response('\n'.join([','.join(patient) for patient in patient_list]))
    response.headers["Content-Disposition"] = "attachment; filename=patient_data.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)
