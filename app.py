from flask import Flask, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Veritabanı Bağlantı Bilgileri
server = 'library-server-atici.database.windows.net'
database = 'LibraryDB'
username = 'adminuser'
password = 'FinalProject123!'
driver = '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    return conn

# Yeni ve Gelişmiş Tabloyu Oluştur (BooksV2)
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BooksV2' and xtype='U')
        CREATE TABLE BooksV2 (
            id INT IDENTITY(1,1) PRIMARY KEY,
            title NVARCHAR(100),
            author NVARCHAR(100),
            image_url NVARCHAR(MAX),
            summary NVARCHAR(MAX)
        )
    ''')
    conn.commit()
    conn.close()
except Exception as e:
    print("Tablo oluşturma hatası:", e)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
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
            return f"Veri ekleme hatası: {e}"
        return redirect(url_for('home'))

    books_html = ""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title, author, image_url, summary FROM BooksV2')
        rows = cursor.fetchall()
        for row in rows:
            # Resim linki boşsa varsayılan bir kapak resmi koy
            img_src = row.image_url if row.image_url else "https://via.placeholder.com/200x300?text=Kapak+Yok"
            books_html += f"""
            <div style="width: 220px; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: white; margin-bottom: 20px; transition: transform 0.2s;">
                <img src="{img_src}" alt="Kapak" style="width: 100%; height: 320px; object-fit: cover;">
                <div style="padding: 15px;">
                    <h4 style="margin: 0 0 5px 0; color: #222; font-size: 16px;">{row.title}</h4>
                    <p style="margin: 0 0 10px 0; color: #555; font-size: 14px;"><i>{row.author}</i></p>
                    <hr style="border: 0.5px solid #eee;">
                    <p style="margin: 10px 0 0 0; font-size: 12px; color: #666; line-height: 1.4;">{row.summary}</p>
                </div>
            </div>
            """
        conn.close()
    except Exception as e:
        books_html = f"<p>Kitaplar çekilirken hata oluştu: {e}</p>"

    html_template = f"""
    <html>
    <head>
        <title>Cloud Library Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .header-box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            input, textarea {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-family: inherit; }}
            .btn {{ padding: 12px 20px; background-color: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }}
            .btn:hover {{ background-color: #0056b3; }}
            .grid {{ display: flex; flex-wrap: wrap; gap: 25px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-box" style="text-align: center;">
                <h1 style="color: #333; margin-top: 0;">📚 Cloud Library Pro</h1>
                <p style="color: #28a745; margin-bottom: 0;"><b>✓ Azure SQL Database Bağlantısı Aktif</b></p>
            </div>

            <div class="header-box" style="background: #e9ecef; border-left: 5px solid #007bff;">
                <h3 style="margin-top: 0;">✨ Yeni Kitap Ekle</h3>
                <form method="POST">
                    <input type="text" name="title" placeholder="Kitap Adı" required>
                    <input type="text" name="author" placeholder="Yazar Adı" required>
                    <input type="text" name="image_url" placeholder="Kapak Fotoğrafı İnternet Linki (Örn: https://.../resim.jpg)" required>
                    <textarea name="summary" placeholder="Kitap Özeti (Kısa bir açıklama yazın)" rows="3" required></textarea>
                    <input type="submit" value="Kütüphaneye Ekle" class="btn">
                </form>
            </div>

            <h2 style="color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px;">📖 Kütüphanedeki Kitaplar</h2>
            <div class="grid">
                {books_html if books_html else "<p style='color:#777;'>Henüz kitap eklenmedi. İlk kitabı sen ekle!</p>"}
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

if __name__ == '__main__':
    app.run(debug=True)