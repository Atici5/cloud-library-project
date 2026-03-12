from flask import Flask, request, redirect, url_for, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'shelfly_secret_key' # Oturum yönetimi için gerekli

# Veritabanı Bağlantı Bilgileri
server = 'library-server-atici.database.windows.net'
database = 'LibraryDB'
username = 'adminuser'
password = 'FinalProject123!'
driver = '{ODBC Driver 17 for SQL Server}'

# ADMİN ŞİFRESİ (Buradan değiştirebilirsin)
ADMIN_PASSWORD = "atici123"

def get_db_connection():
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    return conn

# Giriş Yapma Sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = "Hatalı şifre! Lütfen tekrar deneyin."
    
    return f"""
    <html>
    <head>
        <title>Shelfly - Admin Login</title>
        <style>
            body {{ background-color: #0f0f0f; color: white; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-box {{ background: #1a1a1a; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 300px; }}
            input {{ width: 100%; padding: 12px; margin: 20px 0; border-radius: 5px; border: 1px solid #333; background: #2a2a2a; color: white; box-sizing: border-box; }}
            .btn {{ background: #e50914; color: white; border: none; padding: 12px; width: 100%; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Shelfly Admin</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="Admin Şifresi" required>
                <input type="submit" value="Giriş Yap" class="btn">
            </form>
            <p style="color: red; font-size: 13px;">{error if error else ""}</p>
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
        title = request.form['title']
        author = request.form['author']
        image_url = request.form['image_url']
        summary = request.form['summary']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO BooksV2 (title, author, image_url, summary) VALUES (?, ?, ?, ?)', 
                           (title, author, image_url, summary))
            conn.commit()
            conn.close()
        except Exception as e:
            return f"Hata: {e}"
        return redirect(url_for('home'))

    books_html = ""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, author, image_url FROM BooksV2')
        rows = cursor.fetchall()
        for row in rows:
            delete_btn = f"""
                <form action="/delete/{row.id}" method="POST" style="position: absolute; top: 10px; right: 10px; z-index: 10;">
                    <button type="submit" style="background: rgba(229, 9, 20, 0.9); color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer;" onclick="return confirm('Silinsin mi?');">×</button>
                </form>""" if is_admin else ""
            
            books_html += f"""
            <div style="width: 200px; position: relative; border-radius: 12px; overflow: hidden; background: #1a1a1a; transition: transform 0.3s;">
                {delete_btn}
                <a href="/book/{row.id}" style="text-decoration: none; color: white;">
                    <img src="{row.image_url}" style="width: 100%; height: 300px; object-fit: cover; opacity: 0.8; transition: 0.3s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.8">
                    <div style="padding: 12px; text-align: center;">
                        <div style="font-weight: bold; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row.title}</div>
                    </div>
                </a>
            </div>
            """
        conn.close()
    except Exception as e:
        books_html = f"<p>Hata: {e}</p>"

    # Admin Paneli Kısmı
    admin_panel = ""
    if is_admin:
        admin_panel = f"""
        <div style="background: #1a1a1a; padding: 25px; border-radius: 15px; margin-bottom: 40px; border: 1px solid #333;">
            <h3 style="margin-top:0; color: #e50914;">✨ Yeni Kitap Ekle (Yönetici Paneli)</h3>
            <form method="POST" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <input type="text" name="title" placeholder="Kitap Adı" required style="padding:10px; background:#2a2a2a; color:white; border:1px solid #444; border-radius:5px;">
                <input type="text" name="author" placeholder="Yazar Adı" required style="padding:10px; background:#2a2a2a; color:white; border:1px solid #444; border-radius:5px;">
                <input type="text" name="image_url" placeholder="Kapak Linki" required style="padding:10px; background:#2a2a2a; color:white; border:1px solid #444; border-radius:5px;">
                <input type="text" name="summary" placeholder="Kısa Özet" required style="padding:10px; background:#2a2a2a; color:white; border:1px solid #444; border-radius:5px;">
                <input type="submit" value="Kütüphaneye Ekle" style="grid-column: span 2; padding:12px; background:#e50914; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">
            </form>
            <a href="/logout" style="color: #888; text-decoration: none; font-size: 12px; display: block; margin-top: 15px; text-align: center;">Güvenli Çıkış Yap</a>
        </div>
        """
    else:
        admin_panel = """<div style="text-align: right; margin-bottom: 20px;"><a href="/login" style="color: #444; text-decoration: none; font-size: 13px;">Admin Girişi</a></div>"""

    return f"""
    <html>
    <head>
        <title>Shelfly | Premium Library</title>
        <style>
            body {{ background-color: #0f0f0f; color: #ffffff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 40px 20px; }}
            .container {{ max-width: 1100px; margin: auto; }}
            .grid {{ display: flex; flex-wrap: wrap; gap: 25px; justify-content: center; }}
            .grid > div:hover {{ transform: scale(1.05); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }}
            h1 {{ font-size: 42px; text-align: center; margin-bottom: 10px; color: #e50914; letter-spacing: 2px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>S H E L F L Y</h1>
            <p style="text-align:center; color: #888; margin-bottom: 40px;">Zengin İçerikli Dijital Kütüphane Arşivi</p>
            
            {admin_panel}

            <div class="grid">
                {books_html}
            </div>
        </div>
    </body>
    </html>
    """

# DETAY SAYFASI (SİYAH TEMA)
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title, author, image_url, summary FROM BooksV2 WHERE id = ?', (book_id,))
        row = cursor.fetchone()
        conn.close()
        return f"""
        <html>
        <head>
            <title>{row.title} - Shelfly</title>
            <style>
                body {{ background-color: #0f0f0f; color: white; font-family: 'Segoe UI', sans-serif; padding: 50px; }}
                .container {{ max-width: 900px; margin: auto; display: flex; gap: 50px; background: #1a1a1a; padding: 40px; border-radius: 20px; }}
                .cover {{ width: 300px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
                .back {{ color: #e50914; text-decoration: none; font-weight: bold; display: block; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div style="max-width: 900px; margin: auto;">
                <a href="/" class="back">← Geri Dön</a>
                <div class="container">
                    <img src="{row.image_url}" class="cover">
                    <div>
                        <h1 style="font-size: 40px; margin-bottom: 0;">{row.title}</h1>
                        <h3 style="color: #888; margin-top: 5px;">{row.author}</h3>
                        <p style="font-size: 18px; line-height: 1.6; color: #ccc; margin-top: 30px;">{row.summary}</p>
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
        cursor.execute('DELETE FROM BooksV2 WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)