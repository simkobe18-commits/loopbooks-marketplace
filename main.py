import os
import sqlite3
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="LoopBooks Marketplace")

DB_NAME = "loopbooks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            isbn TEXT,
            price REAL,
            category TEXT,
            condition TEXT,
            thumbnail TEXT,
            seller TEXT,
            status TEXT DEFAULT 'Disponibile'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT,
            image TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ("Il Nome della Rosa", "Umberto Eco", "9788845247253", 14.50, "Narrativa", "Ottime", "https://books.google.com/books/content?id=p5n6CgAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api", "Marco R.", "Disponibile"),
            ("1984", "George Orwell", "9788804668237", 9.00, "Sci-Fi", "Buone", "https://books.google.com/books/content?id=J1w5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api", "Elena B.", "Disponibile"),
            ("Sapiens. Da animale a dio", "Yuval Noah Harari", "9788817077028", 12.00, "Saggistica", "Come nuovo", "https://books.google.com/books/content?id=Xwz7DAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api", "Simone C.", "Disponibile"),
            ("Clean Code", "Robert C. Martin", "9780132350884", 25.00, "Tecnologia", "Ottime", "https://books.google.com/books/content?id=hjEFCAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api", "TechDev", "Disponibile")
        ]
        cursor.executemany('INSERT INTO books (title, author, isbn, price, category, condition, thumbnail, seller, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_books)
    
    cursor.execute('SELECT COUNT(*) FROM packing_materials')
    if cursor.fetchone()[0] == 0:
        sample_materials = [
            ("Kit Buste Imbottite (Set 10)", 8.50, "Buste in carta kraft con protezione interna in pluriball.", "📦"),
            ("Scatola per Libri Standard", 1.20, "Cartone rinforzato per spedizioni sicure di singoli volumi.", "📦"),
            ("Rotolo Pluriball Alta Protezione", 6.00, "Altezza 50cm x 5 metri di protezione ammortizzante.", "🛡️"),
            ("Nastro Adesivo Personalizzato LoopBooks", 3.50, "Nastro resistente da 66m con sigillo di garanzia.", "🎗️")
        ]
        cursor.executemany('INSERT INTO packing_materials (name, price, description, image) VALUES (?, ?, ?, ?)', sample_materials)
    
    conn.commit()
    conn.close()

init_db()

BASE_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LoopBooks - P2P Book Marketplace</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-primary: #121212;
            --bg-secondary: #181818;
            --bg-card: #202020;
            --accent: #e50914;
            --accent-hover: #f40612;
            --text-main: #ffffff;
            --text-muted: #a0a0a0;
            --border: #333333;
            --nav-height: 70px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg-primary); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        header {
            position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
            background: rgba(18, 18, 18, 0.95); backdrop-filter: blur(10px);
            display: flex; justify-content: space-between; align-items: center;
            padding: 0 5%; z-index: 1000; border-bottom: 1px solid var(--border);
        }
        .logo { font-size: 1.6rem; font-weight: 800; color: var(--accent); letter-spacing: -0.5px; text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; gap: 25px; align-items: center; }
        .nav-links a { color: var(--text-main); text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s; }
        .nav-links a:hover, .nav-links a.active { color: var(--accent); }
        .sell-btn { background: var(--accent); padding: 8px 18px; border-radius: 6px; font-weight: 600; color: white !important; transition: background 0.2s; }
        .sell-btn:hover { background: var(--accent-hover); }

        .hamburger { display: none; cursor: pointer; font-size: 1.5rem; color: var(--text-main); }
        .mobile-menu {
            display: none; position: fixed; top: var(--nav-height); left: 0; width: 100%;
            background: var(--bg-secondary); border-bottom: 1px solid var(--border);
            padding: 20px; flex-direction: column; gap: 15px; z-index: 999;
        }
        .mobile-menu.open { display: flex; }

        main { margin-top: var(--nav-height); flex: 1; padding: 30px 5%; max-width: 1400px; width: 100%; margin-left: auto; margin-right: auto; }

        .hero {
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.15), rgba(0,0,0,0.8)), url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1200&q=80') center/cover;
            border-radius: 16px; padding: 60px 40px; margin-bottom: 40px; border: 1px solid var(--border);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4); position: relative; overflow: hidden;
        }
        .hero h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 15px; line-height: 1.2; }
        .hero p { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 25px; max-width: 600px; }

        .search-filter-bar {
            display: flex; gap: 15px; margin-bottom: 35px; flex-wrap: wrap; align-items: center;
        }
        .search-box {
            flex: 1; min-width: 280px; background: var(--bg-secondary); border: 1px solid var(--border);
            border-radius: 8px; display: flex; align-items: center; padding: 0 15px; height: 48px;
        }
        .search-box input {
            background: transparent; border: none; outline: none; color: white; width: 100%; font-size: 1rem; margin-left: 10px;
        }
        .filter-select {
            background: var(--bg-secondary); border: 1px solid var(--border); color: white;
            padding: 0 15px; height: 48px; border-radius: 8px; outline: none; cursor: pointer; font-size: 0.95rem;
        }

        .section-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }

        .books-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; margin-bottom: 50px;
        }
        .book-card {
            background: var(--bg-card); border-radius: 12px; overflow: hidden; border: 1px solid var(--border);
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease; display: flex; flex-direction: column;
        }
        .book-card:hover {
            transform: translateY(-6px); box-shadow: 0 12px 30px rgba(229, 9, 20, 0.2); border-color: var(--accent);
        }
        .book-thumb-container {
            width: 100%; height: 280px; background: var(--bg-secondary); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
        }
        .book-thumb-container img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .book-card:hover .book-thumb-container img { transform: scale(1.05); }
        .book-info { padding: 15px; display: flex; flex-direction: column; flex: 1; justify-content: space-between; }
        .book-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .book-author { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px; }
        .book-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
        .book-price { font-size: 1.2rem; font-weight: 700; color: var(--accent); }
        .btn-details {
            background: rgba(255,255,255,0.1); color: white; padding: 6px 12px; border-radius: 6px;
            text-decoration: none; font-size: 0.85rem; font-weight: 500; transition: background 0.2s;
        }
        .btn-details:hover { background: var(--accent); }

        .form-container {
            background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 16px;
            padding: 40px; max-width: 700px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 8px; font-size: 0.95rem; }
        .form-control {
            width: 100%; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px;
            padding: 12px 15px; color: white; font-size: 1rem; outline: none; transition: border-color 0.2s;
        }
        .form-control:focus { border-color: var(--accent); }
        .commission-box {
            background: rgba(229, 9, 20, 0.08); border: 1px dashed var(--accent); border-radius: 8px;
            padding: 15px; margin-top: 15px; font-size: 0.95rem;
        }
        .submit-btn {
            background: var(--accent); color: white; border: none; width: 100%; padding: 14px;
            border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: background 0.2s; margin-top: 10px;
        }
        .submit-btn:hover { background: var(--accent-hover); }

        @media (max-width: 768px) {
            .nav-links { display: none; }
            .hamburger { display: block; }
            .hero { padding: 40px 20px; text-align: center; }
            .hero h1 { font-size: 1.8rem; }
            .search-filter-bar { flex-direction: column; align-items: stretch; }
            .books-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }
            .book-thumb-container { height: 210px; }
            .form-container { padding: 20px; }
        }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo">📚 LoopBooks</a>
        <nav class="nav-links">
            <a href="/" class="active">Home</a>
            <a href="/sell">Vendi</a>
            <a href="/library">La mia biblioteca</a>
            <a href="/packing" class="sell-btn">Kit Spedizione</a>
        </nav>
        <div class="hamburger" onclick="toggleMobileMenu()">☰</div>
    </header>

    <div class="mobile-menu" id="mobileMenu">
        <a href="/">Home</a>
        <a href="/sell">Vendi</a>
        <a href="/library">La mia biblioteca</a>
        <a href="/packing">Kit Spedizione</a>
    </div>

    <main>
        {{content}}
    </main>

    <script>
        function toggleMobileMenu() {
            document.getElementById('mobileMenu').classList.toggle('open');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = None, category: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT id, title, author, price, category, condition, thumbnail, seller FROM books WHERE 1=1"
    params = []
    if q:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if category and category != "Tutti":
        query += " AND category = ?"
        params.append(category)
        
    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()

    books_html = ""
    for b in books:
        books_html += f"""
        <div class="book-card">
            <div class="book-thumb-container">
                <img src="{b[6] or 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80'}" alt="{b[1]}">
            </div>
            <div class="book-info">
                <div>
                    <div class="book-title" title="{b[1]}">{b[1]}</div>
                    <div class="book-author">{b[2]}</div>
                </div>
                <div class="book-footer">
                    <span class="book-price">€ {b[3]:.2f}</span>
                    <a href="/book/{b[0]}" class="btn-details">Dettagli</a>
                </div>
            </div>
        </div>
        """

    content = f"""
    <div class="hero">
        <h1>Il marketplace P2P per i tuoi libri</h1>
        <p>Acquista e vendi libri universitari, romanzi e rarità direttamente da lettore a lettore con massima sicurezza e spedizioni tracciate.</p>
    </div>

    <form class="search-filter-bar" method="get" action="/">
        <div class="search-box">
            <span>🔍</span>
            <input type="text" name="q" placeholder="Cerca per titolo, autore o ISBN..." value="{q or ''}">
        </div>
        <select name="category" class="filter-select" onchange="this.form.submit()">
            <option value="Tutti">Tutti i generi</option>
            <option value="Narrativa" {"selected" if category == "Narrativa" else ""}>Narrativa</option>
            <option value="Sci-Fi" {"selected" if category == "Sci-Fi" else ""}>Sci-Fi</option>
            <option value="Saggistica" {"selected" if category == "Saggistica" else ""}>Saggistica</option>
            <option value="Tecnologia" {"selected" if category == "Tecnologia" else ""}>Tecnologia</option>
        </select>
    </form>

    <div class="section-title">
        <span>Libri in Evidenza</span>
    </div>

    <div class="books-grid">
        {books_html if books_html else '<p style="color: var(--text-muted);">Nessun libro trovato.</p>'}
    </div>
    """
    return HTMLResponse(content=BASE_HTML.replace("{{content}}", content))

@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    content = """
    <div class="form-container">
        <h2 style="margin-bottom: 20px; font-size: 1.8rem;">Metti in vendita un libro</h2>
        <form action="/sell" method="post">
            <div class="form-group">
                <label>Codice ISBN (Inseriscilo per il recupero automatico)</label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="isbnInput" name="isbn" class="form-control" placeholder="es. 9788845247253">
                    <button type="button" onclick="fetchBookByISBN()" style="background: #333; color: white; border: none; padding: 0 15px; border-radius: 8px; cursor: pointer; font-weight: 600;">Cerca</button>
                </div>
            </div>
            <div class="form-group">
                <label>Titolo del Libro</label>
                <input type="text" id="titleInput" name="title" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Autore</label>
                <input type="text" id="authorInput" name="author" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Genere</label>
                <select name="category" class="form-control">
                    <option value="Narrativa">Narrativa</option>
                    <option value="Sci-Fi">Sci-Fi</option>
                    <option value="Saggistica">Saggistica</option>
                    <option value="Tecnologia">Tecnologia</option>
                    <option value="Università">Università</option>
                </select>
            </div>
            <div class="form-group">
                <label>Condizioni</label>
                <select name="condition" class="form-control">
                    <option value="Come nuovo">Come nuovo</option>
                    <option value="Ottime">Ottime</option>
                    <option value="Buone">Buone</option>
                    <option value="Discrete">Discrete</option>
                </select>
            </div>
            <div class="form-group">
                <label>Carica Foto Reale (File)</label>
                <input type="file" name="book_image" class="form-control" accept="image/*">
            </div>
            <div class="form-group">
                <label>Prezzo di Vendita (€)</label>
                <input type="number" step="0.5" id="priceInput" name="price" class="form-control" required oninput="calculateCommission()">
            </div>
            <div class="commission-box" id="commissionBox">
                Commissione LoopBooks (5%): <strong>€ 0.00</strong><br>
                Il tuo guadagno netto stimato: <strong style="color: #4ade80;">€ 0.00</strong>
            </div>
            <input type="hidden" id="thumbnailInput" name="thumbnail" value="">
            <button type="submit" class="submit-btn" style="margin-top: 25px;">Pubblica Inserzione</button>
        </form>
    </div>

    <script>
        function calculateCommission() {
            let price = parseFloat(document.getElementById('priceInput').value) || 0;
            let commission = price * 0.05;
            let net = price - commission;
            document.getElementById('commissionBox').innerHTML =
