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
        # id sütununu da çekiyoruz ki tıklama ve silme işlemi yapabilelim
        cursor.execute('SELECT id, title, author, image_url, summary FROM BooksV2')
        rows = cursor.fetchall()
        for row in rows:
            img_src = row.image_url if row.image_url else "https://via.placeholder.com/200x300?text=Kapak+Yok"
            books_html += f"""
            <div style="width: 200px; position: relative; border-radius: 10px; overflow: hidden; box-shadow: 0 6px 12px rgba(0,0,0,0.15); background: white; transition: transform 0.2s; text-align: center;">
                
                <form action="/delete/{row.id}" method="POST" style="position: absolute; top: 8px; right: 8px; margin: 0; z-index: 10;">
                    <button type="submit" style="background: rgba(220, 53, 69, 0.9); color: white; border: none; border-radius: 50%; width: 32px; height: 32px; cursor: pointer; font-weight: bold; font-size: 14px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);" title="Kitabı Sil" onclick="return confirm('Bu kitabı silmek istediğinize emin misiniz?');">X</button>
                </form>

                <a href="/book/{row.id}" style="text-decoration: none; color: inherit; display: block;">
                    <img src="{img_src}" alt="Kapak" style="width: 100%; height: 300px; object-fit: cover;">
                    <div style="padding: 10px;">
                        <h4 style="margin: 0; font-size: 15px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row.title}</h4>
                    </div>
                </a>
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
            .grid {{ display: flex; flex-wrap: wrap; gap: 25px; justify-content: flex-start; }}
            .grid > div:hover {{ transform: scale(1.03); }}
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
                    <textarea name="summary" placeholder="Kitap Özeti (Kısa bir açıklama yazın)" rows="2" required></textarea>
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


# YENİ ÖZELLİK: KİTAP DETAY SAYFASI
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title, author, image_url, summary FROM BooksV2 WHERE id = ?', (book_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return "<h3>Kitap bulunamadı!</h3><a href='/'>Ana Sayfaya Dön</a>"
            
        img_src = row.image_url if row.image_url else "https://via.placeholder.com/300x450?text=Kapak+Yok"
        
        detail_html = f"""
        <html>
        <head>
            <title>{row.title} - Detay</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                .back-btn {{ display: inline-block; margin-bottom: 30px; color: #007bff; text-decoration: none; font-weight: bold; font-size: 16px; padding: 10px 20px; border: 2px solid #007bff; border-radius: 6px; transition: 0.2s; }}
                .back-btn:hover {{ background: #007bff; color: white; }}
                .content {{ display: flex; gap: 40px; align-items: flex-start; }}
                .cover-img {{ width: 280px; border-radius: 10px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); flex-shrink: 0; }}
                .info {{ flex-grow: 1; }}
                h1 {{ margin-top: 0; color: #222; font-size: 36px; margin-bottom: 10px; }}
                h3 {{ color: #666; margin-top: 0; font-style: italic; font-weight: normal; font-size: 20px; }}
                p {{ font-size: 18px; line-height: 1.8; color: #444; margin-top: 20px; text-align: justify; padding: 20px; background: #fdfdfd; border-left: 4px solid #007bff; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-btn">← Kütüphaneye Dön</a>
                <div class="content">
                    <img src="{img_src}" alt="Kapak" class="cover-img">
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
        return detail_html
    except Exception as e:
        return f"Hata: {e}"

# YENİ ÖZELLİK: KİTAP SİLME İŞLEMİ
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM BooksV2 WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Silme hatası:", e)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)