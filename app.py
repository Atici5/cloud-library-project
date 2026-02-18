from flask import Flask
import pyodbc

app = Flask(__name__)

# Veritabanı Bağlantı Bilgileri (Buraya kendi şifreni yaz!)
server = 'library-server-atici.database.windows.net'
database = 'LibraryDB'
username = 'adminuser'
password = 'FinalProject123!'
driver= '{ODBC Driver 17 for SQL Server}'

@app.route('/')
def home():
    try:
        # Veritabanına bağlanmayı dene
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        return "<h1>Final Project</h1><p>Status: <b>Connected to Azure SQL Database Successfully!</b></p>"
    except Exception as e:
        return f"<h1>Final Project</h1><p>Status: Connected to Web Server but Database error: {str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True)