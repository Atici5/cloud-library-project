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

# Veritabanında Kitaplar tablosu yoksa otomatik oluştur
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Books' and xtype='U')
        CREATE TABLE Books (
            id INT IDENTITY(1,1) PRIMARY KEY,
            title NVARCHAR(100),
            author NVARCHAR(100)
        )
    ''')
    conn.commit()
    conn.close()
except Exception as e:
    print("Tablo oluşturma hatası:", e)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Forma kitap yazıp gönder (Ekleme işlemi)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Books (title, author) VALUES (?, ?)', (title, author))
            conn.commit()
            conn.close()
        except Exception as e:
            return f"Veri ekleme hatası: {e}"
        return redirect(url_for('home'))

    # Sayfa açıldığında kitapları listele (Okuma işlemi)
    books_html = ""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title, author FROM Books')
        rows = cursor.fetchall()
        for row in rows:
            books_html += f"<li style='margin-bottom: 5px;'>📚 <b>{row.title}</b> - <i>{row.author}</i></li>"
        conn.close()
    except Exception as e:
        books_html = f"<p>Kitaplar çekilirken hata oluştu: {e}</p>"

    # Uygulamanın HTML Arayüzü
    html_template = f"""
    <html>
    <head><title>Cloud Library App</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">☁️ Cloud Library Application</h2>
            <p style="color: green;"><b>✓ Connected to Azure SQL Database Successfully!</b></p>
            
            <hr style="border: 1px solid #ddd;">

            <h3 style="color: #555;">Yeni Kitap Ekle</h3>
            <form method="POST">
                <input type="text" name="title" placeholder="Kitap Adı" required style="padding: 8px; margin-right: 10px;">
                <input type="text" name="author" placeholder="Yazar Adı" required style="padding: 8px; margin-right: 10px;">
                <input type="submit" value="Kitabı Kaydet" style="padding: 8px 15px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;">
            </form>

            <h3 style="color: #555;">Kütüphanedeki Kitaplar</h3>
            <ul style="list-style-type: none; padding: 0;">
                {books_html if books_html else "<p>Henüz kitap eklenmedi. Kütüphane boş.</p>"}
            </ul>
        </div>
    </body>
    </html>
    """
    return html_template

if __name__ == '__main__':
    app.run(debug=True)