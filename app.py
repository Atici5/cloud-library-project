from flask import Flask, request, redirect, url_for, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'shelfly_global_key'

# Database Connection
server = 'library-server-atici.database.windows.net'
database = 'LibraryDB'
username = 'adminuser'
password = 'FinalProject123!'
driver = '{ODBC Driver 17 for SQL Server}'

ADMIN_PASSWORD = "atici123"

def get_db_connection():
    return pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        error = "Invalid password!"
    return f"""
    <html>
    <head>
        <title>Shelfly | Admin Login</title>
        <style>
            body {{ background: #000; color: white; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-box {{ background: #111; padding: 40px; border-radius: 20px; border: 1px solid #333; text-align: center; width: 300px; }}
            input {{ width: 100%; padding: 12px; margin: 20px 0; border-radius: 8px; border: 1px solid #444; background: #222; color: white; box-sizing: border-box; }}
            .btn {{ background: #e50914; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }}
            .btn:hover {{ background: #b20710; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2 style="letter-spacing: 3px;">SHELFLY</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="Admin Password" required>
                <input type="submit" value="Sign In" class="btn">
            </form>
            <p style="color:#e50914; font-size: 13px;">{error if error else ""}</p>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    is_admin = session.get('logged_in')
    
    if request.method == 'POST' and is_admin:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO BooksV2 (title, author, image_url, summary) VALUES (?, ?, ?, ?)', 
                           (request.form['title'], request.form['author'], request.form['image_url'], request.form['summary']))
            conn.commit()
            conn.close()
        except: pass
        return redirect(url_for('home'))

    books_html = ""
    total_books = 0
    try: