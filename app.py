from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Supabase Configuration
SUPABASE_URL = "https://nacmsiwwgpnovyzvpeqo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hY21zaXd3Z3Bub3Z5enZwZXFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE4NjUzMTcsImV4cCI6MjA3NzQ0MTMxN30.DD89PSVYlxnwEaExUOmAX49T-3gyyxWMqA-ztNb6dJM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------- ROUTES ----------

@app.route('/')
def home():
    return redirect(url_for('login'))


# Register with email + password
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing = supabase.table('auth_users').select('*').eq('email', email).execute()
        if existing.data:
            msg = "Email already registered!"
        else:
            supabase.table('auth_users').insert({'email': email, 'password': password}).execute()
            msg = "Registration successful! Please log in."
    return render_template('register.html', msg=msg)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        result = supabase.table('auth_users').select('*').eq('email', email).eq('password', password).execute()

        if result.data:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            msg = "Invalid email or password!"
    return render_template('login.html', msg=msg)


# Dashboard: accepts first/last/username/password, shows table
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))

    msg = ""
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']

        supabase.table('user_info').insert({
            'firstname': firstname,
            'lastname': lastname,
            'username': username,
            'password': password
        }).execute()

        msg = "Data saved successfully!"

    # Fetch all stored data
    users = supabase.table('user_info').select('*').execute().data
    return render_template('dashboard.html', email=session['email'], users=users, msg=msg)


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
