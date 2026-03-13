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
            # KİTAP EKLEME TABLO ADI: Books
            cursor.execute('INSERT INTO Books (title, author, image_url, summary) VALUES (?, ?, ?, ?)', 
                           (request.form['title'], request.form['author'], request.form['image_url'], request.form['summary']))
            conn.commit()
            conn.close()
        except: pass
        return redirect(url_for('home'))

    books_html = ""
    total_books = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # KİTAP LİSTELEME TABLO ADI: Books
        cursor.execute('SELECT id, title, author, image_url FROM Books')
        rows = cursor.fetchall()
        total_books = len(rows)
        for row in rows:
            del_btn = f'<form action="/delete/{row.id}" method="POST" style="position:absolute; top:10px; right:10px; z-index:5;"><button type="submit" class="del-btn" title="Delete Book">×</button></form>' if is_admin else ""
            books_html += f"""
            <div class="book-card" data-title="{row.title.lower()}">
                {del_btn}
                <a href="/book/{row.id}" style="text-decoration:none; color:inherit;">
                    <img src="{row.image_url}" class="book-img">
                    <div class="book-info">
                        <div class="book-title">{row.title}</div>
                        <div class="book-author">{row.author}</div>
                    </div>
                </a>
            </div>
            """
        conn.close()
    except: pass

    # SAĞ ÜSTTEKİ BUTON VE ADMİN PANELİ
    admin_section = f"""
    <div class="admin-panel">
        <h3 style="color: #e50914; margin-top:0;">✨ Admin Dashboard</h3>
        <form method="POST" class="add-form">
            <input type="text" name="title" placeholder="Book Title" required>
            <input type="text" name="author" placeholder="Author" required>
            <input type="text" name="image_url" placeholder="Cover Image URL" required>
            <input type="text" name="summary" placeholder="Summary" required>
            <button type="submit" class="add-btn">Add to Collection</button>
        </form>
        <a href="/logout" style="color:#666; font-size:12px; text-decoration:none; display:inline-block; margin-top:15px;">Secure Logout</a>
    </div>
    """ if is_admin else '<a href="/login" class="staff-btn">Staff Access</a>'

    return f"""
    <html>
    <head>
        <title>Shelfly | Digital Library Archive</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ background: #050505; color: white; font-family: 'Inter', sans-serif; margin: 0; padding: 40px 20px; }}
            
            .staff-btn {{ position: absolute; top: 30px; right: 40px; color: #444; font-size: 12px; font-weight: bold; letter-spacing: 1px; text-decoration: none; text-transform: uppercase; transition: color 0.3s; z-index: 100; }}
            .staff-btn:hover {{ color: #e50914; }}

            .container {{ max-width: 1200px; margin: auto; position: relative; }}
            h1 {{ font-size: 55px; text-align: center; color: #e50914; letter-spacing: 10px; margin-bottom: 5px; font-weight: 700; }}
            .stats {{ text-align: center; color: #666; margin-bottom: 35px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
            
            .search-box {{ width: 100%; max-width: 450px; margin: 0 auto 50px auto; display: block; padding: 16px 25px; border-radius: 30px; border: 1px solid #222; background: #111; color: white; text-align: center; font-size: 16px; outline: none; transition: 0.3s; }}
            .search-box:focus {{ border-color: #e50914; box-shadow: 0 0 20px rgba(229, 9, 20, 0.2); }}

            .grid {{ display: flex; flex-wrap: wrap; gap: 30px; justify-content: center; }}
            
            .book-card {{ width: 210px; position: relative; border-radius: 12px; background: #111; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); border: 1px solid #1a1a1a; }}
            .book-card:hover {{ transform: scale(1.08); box-shadow: 0 15px 40px rgba(0,0,0,0.9), 0 0 25px rgba(229, 9, 20, 0.3); z-index: 10; border-color: #333; }}
            .book-img {{ width: 100%; height: 310px; object-fit: cover; border-radius: 12px 12px 0 0; }}
            .book-info {{ padding: 15px; text-align: center; }}
            .book-title {{ font-weight: 700; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }}
            .book-author {{ font-size: 12px; color: #777; }}
            
            .del-btn {{ background: rgba(229, 9, 20, 0.9); color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; font-size: 18px; transition: 0.2s; }}
            .del-btn:hover {{ transform: scale(1.1); background: #ff0000; }}
            
            .admin-panel {{ background: #0f0f0f; padding: 35px; border-radius: 20px; border: 1px solid #222; margin-bottom: 60px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .add-form {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 25px; }}
            .add-form input {{ padding: 14px; background: #1a1a1a; border: 1px solid #333; color: white; border-radius: 8px; font-family: inherit; }}
            .add-btn {{ grid-column: span 2; padding: 16px; background: #e50914; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }}
            .add-btn:hover {{ background: #b20710; }}
        </style>
    </head>
    <body>
        {admin_section}
        <div class="container">
            <h1>SHELFLY</h1>
            <div class="stats">Curating <b>{total_books}</b> Masterpieces in our Archive</div>
            
            <input type="text" id="searchInput" class="search-box" placeholder="Search the collection..." onkeyup="searchBooks()">

            <div class="grid" id="bookGrid">
                {books_html if books_html else "<p style='color:#444; text-align:center; width:100%;'>No books found in the archive.</p>"}
            </div>
        </div>

        <script>
            function searchBooks() {{
                let input = document.getElementById('searchInput').value.toLowerCase();
                let cards = document.getElementsByClassName('book-card');
                for (let card of cards) {{
                    let title = card.getAttribute('data-title');
                    card.style.display = title.includes(input) ? "block" : "none";
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # DETAY SAYFASI TABLO ADI: Books
        cursor.execute('SELECT title, author, image_url, summary FROM Books WHERE id = ?', (book_id,))
        row = cursor.fetchone()
        conn.close()
        return f"""
        <html>
        <head>
            <title>{row.title} | Details</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{ background: #050505; color: white; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
                .container {{ max-width: 1000px; display: flex; gap: 60px; padding: 50px; background: #111; border-radius: 30px; border: 1px solid #222; align-items: center; position: relative; box-shadow: 0 30px 60px rgba(0,0,0,0.8); }}
                .cover {{ width: 380px; border-radius: 15px; box-shadow: 0 25px 50px rgba(0,0,0,0.7); flex-shrink: 0; }}
                .back-btn {{ position: absolute; top: -50px; left: 0; color: #e50914; text-decoration: none; font-weight: bold; font-size: 14px; letter-spacing: 1px; transition: 0.3s; }}
                .back-btn:hover {{ color: white; padding-left: 5px; }}
                .info {{ flex-grow: 1; }}
                h1 {{ font-size: 52px; margin: 0; line-height: 1.1; }}
                h3 {{ color: #e50914; margin: 15px 0 35px 0; font-weight: 400; font-size: 22px; opacity: 0.9; }}
                p {{ font-size: 19px; line-height: 1.8; color: #ccc; text-align: justify; }}
            </style>
        </head>
        <body>
            <div style="position: relative;">
                <a href="/" class="back-btn">← BACK TO COLLECTION</a>
                <div class="container">
                    <img src="{row.image_url}" class="cover">
                    <div class="info">
                        <h1>{row.title}</h1>
                        <h3>{row.author}</h3>
                        <p>{row.summary}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except: return redirect(url_for('home'))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if session.get('logged_in'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Books WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)