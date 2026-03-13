import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# --- AZURE'DAN BİLGİLERİ ÇEKEN KISIM ---
# Azure'daki AZURE_SQL_CONNECTIONSTRING değerini okur
connection_string = os.getenv("AZURE_SQL_CONNECTIONSTRING")

# SQLAlchemy için bağlantı formatını ayarlar
app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc:///?odbc_connect={connection_string}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "shelfly_secret_99")

db = SQLAlchemy(app)

# --- VERİ TABANI MODELİ ---
class Book(db.Model):
    __tablename__ = 'Books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)

# Azure'daki ADMIN_PASS şifresini çeker
ADMIN_PASS = os.getenv("ADMIN_PASS", "atici123")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ANA SAYFA ---
@app.route('/')
def home():
    books = Book.query.all()
    total_books = len(books)
    is_admin = session.get('logged_in')
    
    books_html = ""
    for book in books:
        del_btn = f'<form action="/delete/{book.id}" method="POST" style="position:absolute; top:10px; right:10px;"><button type="submit" class="del-btn">×</button></form>' if is_admin else ""
        books_html += f"""
        <div class="book-card" data-title="{book.title.lower()}">
            {del_btn}
            <a href="/book/{book.id}" style="text-decoration:none; color:inherit;">
                <img src="{book.image_url}" class="book-img">
                <div class="book-info">
                    <div class="book-title">{book.title}</div>
                    <div class="book-author">{book.author}</div>
                </div>
            </a>
        </div>
        """

    admin_panel = f"""
    <div class="admin-panel">
        <h3>✨ Admin Dashboard</h3>
        <form action="/add" method="POST" class="add-form">
            <input type="text" name="title" placeholder="Book Title" required>
            <input type="text" name="author" placeholder="Author" required>
            <input type="text" name="image_url" placeholder="Cover Image URL" required>
            <input type="text" name="summary" placeholder="Summary" required>
            <button type="submit" class="add-btn">Add to Collection</button>
        </form>
        <a href="/logout" style="color:#666; font-size:12px; text-decoration:none;">Logout</a>
    </div>
    """ if is_admin else '<a href="/login" class="staff-btn">Staff Access</a>'

    return f"""
    <html>
    <head>
        <title>Shelfly | Digital Library</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ background: #050505; color: white; font-family: 'Inter', sans-serif; margin: 0; padding: 40px 20px; }}
            .staff-btn {{ position: absolute; top: 30px; right: 40px; color: #444; font-size: 12px; font-weight: bold; text-decoration: none; text-transform: uppercase; }}
            .container {{ max-width: 1200px; margin: auto; }}
            h1 {{ font-size: 55px; text-align: center; color: #e50914; letter-spacing: 10px; }}
            .grid {{ display: flex; flex-wrap: wrap; gap: 30px; justify-content: center; }}
            .book-card {{ width: 210px; position: relative; background: #111; border: 1px solid #1a1a1a; transition: 0.4s; border-radius: 12px; }}
            .book-card:hover {{ transform: scale(1.05); border-color: #e50914; }}
            .book-img {{ width: 100%; height: 310px; object-fit: cover; border-radius: 12px 12px 0 0; }}
            .book-info {{ padding: 15px; text-align: center; }}
            .del-btn {{ background: #e50914; color: white; border: none; border-radius: 50%; cursor: pointer; width: 25px; height: 25px; }}
            .admin-panel {{ background: #0f0f0f; padding: 30px; border-radius: 20px; border: 1px solid #222; margin-bottom: 50px; text-align: center; }}
            .add-form {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top:20px; }}
            .add-form input {{ padding: 12px; background: #1a1a1a; border: 1px solid #333; color: white; border-radius: 8px; }}
            .add-btn {{ grid-column: span 2; padding: 15px; background: #e50914; color: white; border: none; font-weight: bold; border-radius: 8px; cursor:pointer; }}
        </style>
    </head>
    <body>
        {admin_panel}
        <div class="container">
            <h1>SHELFLY</h1>
            <p style="text-align:center; color:#666; margin-bottom:40px;">Curating <b>{total_books}</b> Masterpieces</p>
            <div class="grid">{books_html}</div>
        </div>
    </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return f"""
    <body style="background:#000; color:white; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
        <form method="POST" style="background:#111; padding:40px; border-radius:20px; border:1px solid #333; width:300px;">
            <h2 style="text-align:center;">Admin Login</h2>
            <input type="password" name="password" placeholder="Enter Password" style="padding:12px; width:100%; margin:20px 0; background:#222; border:1px solid #444; color:white; border-radius:8px;">
            <button type="submit" style="padding:12px; width:100%; background:#e50914; color:white; border:none; font-weight:bold; border-radius:8px; cursor:pointer;">Login</button>
            <p style="text-align:center; margin-top:15px;"><a href="/" style="color:#666; font-size:12px; text-decoration:none;">← Back to Site</a></p>
        </form>
    </body>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
@login_required
def add_book():
    b = Book(title=request.form['title'], author=request.form['author'], image_url=request.form['image_url'], summary=request.form['summary'])
    db.session.add(b)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    b = Book.query.get(book_id)
    if b:
        db.session.delete(b)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    b = Book.query.get_or_404(book_id)
    return f"""
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0;">
        <div style="max-width:900px; display:flex; gap:50px; background:#111; padding:50px; border-radius:30px; border:1px solid #222; align-items:center;">
            <img src="{b.image_url}" style="width:300px; border-radius:15px; box-shadow:0 20px 50px rgba(0,0,0,0.6);">
            <div>
                <a href="/" style="color:#e50914; text-decoration:none; font-weight:bold;">← BACK TO COLLECTION</a>
                <h1 style="font-size:48px; margin:25px 0 10px 0;">{b.title}</h1>
                <h3 style="color:#e50914; margin-bottom:30px; font-weight:normal;">{b.author}</h3>
                <p style="font-size:18px; line-height:1.7; color:#ccc;">{b.summary}</p>
            </div>
        </div>
    </body>
    """

if __name__ == '__main__':
    app.run()