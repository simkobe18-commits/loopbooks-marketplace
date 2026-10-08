from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="LoopBooks Marketplace", version="1.0")

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    price: float
    condition: str
    isbn: str
    description: str
    image_url: str

# Database esteso per popolare i vari caroselli
fake_books_db = [
    # Top 10 / Tendenza
    Book(id=1, title="Il monastero dei segreti", author="Anonimo", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", description="Un monastero isolato...", image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"),
    Book(id=2, title="Python per Intelligenza Artificiale", author="Mario Rossi", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", description="Guida avanzata...", image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"),
    # Grandi Classici
    Book(id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", description="Il capolavoro della letteratura italiana.", image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80"),
    Book(id=4, title="La Divina Commedia", author="Dante Alighieri", genre="Classici", price=18.50, condition="Ottime", isbn="9788807654321", description="Un viaggio attraverso Inferno, Purgatorio e Paradiso.", image_url="https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=600&q=80"),
    # Narrativa e Letteratura
    Book(id=5, title="Cronache del Tempo Sospeso", author="Elena Bianchini", genre="Narrativa e Letteratura", price=15.00, condition="Nuovo", isbn="9788809876543", description="Romanzo contemporaneo intenso.", image_url="https://images.unsplash.com/photo-1495640388908-05fa85288e61?auto=format&fit=crop&w=600&q=80"),
    # Saggistica e Cultura
    Book(id=6, title="Storia delle Civiltà Moderne", author="Giovanni Treccani", genre="Saggistica e Cultura", price=32.00, condition="Ottime", isbn="9788801112223", description="Analisi storica e culturale profonda.", image_url="https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=600&q=80"),
    # Crescita Personale e Lifestyle
    Book(id=7, title="Il Potere dell'Abitudine", author="Charles Duhigg", genre="Crescita Personale", price=19.90, condition="Nuovo", isbn="9788803334445", description="Come cambiare abitudini nella vita e nel lavoro.", image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"),
    # Passioni, Hobby e Creatività
    Book(id=8, title="Cucina Botanica", author="Carlotta Perego", genre="Cucina", price=22.00, condition="Nuovo", isbn="9788805556667", description="Ricette vegetali semplici e gustose.", image_url="https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=600&q=80"),
    # Bambini e Ragazzi (Young Adult)
    Book(id=9, title="Le Avventure di Oz", author="L. Frank Baum", genre="Young Adult", price=12.00, condition="Buone", isbn="9788807778889", description="Un classico fantastico per ragazzi.", image_url="https://images.unsplash.com/photo-1513001900722-370f803f498d?auto=format&fit=crop&w=600&q=80")
]

user_library = []

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loopbooks - Marketplace</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-color: #141414;
                --card-bg: #1f1f1f;
                --text-color: #e5e5e5;
                --accent-color: #e50914;
                --accent-hover: #b20710;
                --blue-glow: #00d2ff;
            }
            body {
                margin: 0;
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 50px;
                background: linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0));
                position: fixed;
                top: 0;
                width: 100%;
                box-sizing: border-box;
                z-index: 1000;
            }
            .logo-area {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.5rem;
                font-weight: 700;
                color: #fff;
                text-decoration: none;
            }
            .nav-center {
                display: flex;
                gap: 30px;
                align-items: center;
            }
            .nav-center a {
                color: var(--text-color);
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                letter-spacing: 0.5px;
                transition: color 0.3s;
            }
            .nav-center a:hover {
                color: #fff;
            }
            .profile-area {
                display: flex;
                align-items: center;
            }
            .profile-icon {
                width: 36px;
                height: 36px;
                background: #333;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                font-weight: bold;
                cursor: pointer;
            }
            .hero {
                height: 65vh;
                background: linear-gradient(to right, rgba(20,20,20,0.9), rgba(20,20,20,0.4)), url('https://images.unsplash.com/photo-1507842229443-77783618cdc3?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 0 50px;
                margin-top: 60px;
            }
            .hero h1 {
                font-size: 3rem;
                max-width: 600px;
                margin-bottom: 10px;
                line-height: 1.2;
            }
            .hero p {
                font-size: 1.2rem;
                max-width: 500px;
                color: #b3b3b3;
                margin-bottom: 25px;
            }
            .search-bar {
                display: flex;
                gap: 10px;
                max-width: 600px;
            }
            .search-bar input {
                flex: 1;
                padding: 12px 16px;
                border-radius: 4px;
                border: 1px solid #333;
                background: rgba(0,0,0,0.6);
                color: white;
                font-size: 1rem;
            }
            .search-bar button {
                padding: 0 20px;
                background: #fff;
                color: #000;
                font-weight: 600;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .container {
                padding: 20px 50px 60px 50px;
            }
            h2.section-title {
                font-size: 1.3rem;
                margin: 35px 0 15px 0;
                font-weight: 600;
                color: #fff;
            }
            /* Caroselli Orizzontali a Scorrimento */
            .carousel-container {
                display: flex;
                gap: 20px;
                overflow-x: auto;
                padding-bottom: 15px;
                scroll-behavior: smooth;
            }
            .carousel-container::-webkit-scrollbar {
                height: 6px;
            }
            .carousel-container::-webkit-scrollbar-thumb {
                background: #333;
                border-radius: 3px;
            }
            .book-card {
                min-width: 200px;
                max-width: 200px;
                background: var(--card-bg);
                border-radius: 8px;
                overflow: hidden;
                flex-shrink: 0;
                transition: transform 0.3s;
                cursor: pointer;
            }
            .book-card:hover {
                transform: scale(1.05);
            }
            .book-card img {
                width: 100%;
                height: 260px;
                object-fit: cover;
            }
            .book-info {
                padding: 12px;
            }
            .book-info h3 {
                margin: 0 0 4px 0;
                font-size: 0.95rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .book-info p {
                margin: 0;
                color: #888;
                font-size: 0.8rem;
            }
            .price {
                color: var(--blue-glow);
                font-weight: 600;
                margin-top: 8px;
                font-size: 0.9rem;
            }
            /* Sezione Oggettistica Consegne */
            .merch-section {
                background: linear-gradient(135deg, #1f1f1f, #111);
                border: 1px solid #333;
                border-radius: 12px;
                padding: 25px 30px;
                margin-top: 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .merch-content h3 { margin: 0 0 8px 0; font-size: 1.2rem; color: #fff; }
            .merch-content p { margin: 0; color: #aaa; font-size: 0.9rem; }
            .merch-btn { background: var(--accent-color); color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: background 0.3s; }
            .merch-btn:hover { background: var(--accent-hover); }
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo-area">
                <span>📖 Loopbooks</span>
            </a>
            <div class="nav-center">
                <a href="/sell">METTI IN VENDITA</a>
                <a href="/library">LA MIA BIBLIOTECA</a>
                <a href="#search-section">CERCA LIBRO</a>
            </div>
            <div class="profile-area">
                <div class="profile-icon">SC</div>
            </div>
        </header>

        <section class="hero" id="search-section">
            <h1>Un monastero, un segreto, un crimine.</h1>
            <p>Scopri il mistero tra migliaia di libri garantiti e venditori verificati.</p>
            <div class="search-bar">
                <input type="text" id="search-input" placeholder="Cerca per nome o codice ISBN...">
                <button onclick="alert('Ricerca avviata!')">Trova il mio libro</button>
            </div>
        </section>

        <div class="container">
            <!-- Sezioni in evidenza -->
            <h2 class="section-title">Libri di tendenza (Top 10)</h2>
            <div class="carousel-container" id="trending-carousel"></div>

            <h2 class="section-title">Visualizzati di recente</h2>
            <div class="carousel-container" id="recent-carousel"></div>

            <h2 class="section-title">Grandi classici</h2>
            <div class="carousel-container" id="classics-carousel"></div>

            <h2 class="section-title">Nuove uscite</h2>
            <div class="carousel-container" id="new-carousel"></div>

            <!-- Caroselli a scorrimento per categorie -->
            <h2 class="section-title">Preferiti</h2>
            <div class="carousel-container" id="favorites-carousel"></div>

            <h2 class="section-title">Narrativa e Letteratura</h2>
            <div class="carousel-container" id="narrative-carousel"></div>

            <h2 class="section-title">Saggistica e Cultura</h2>
            <div class="carousel-container" id="essays-carousel"></div>

            <h2 class="section-title">Crescita Personale e Lifestyle</h2>
            <div class="carousel-container" id="lifestyle-carousel"></div>

            <h2 class="section-title">Passioni, Hobby e Creatività</h2>
            <div class="carousel-container" id="hobby-carousel"></div>

            <h2 class="section-title">Bambini e Ragazzi (Young Adult)</h2>
            <div class="carousel-container" id="ya-carousel"></div>

            <!-- Sezione dedicata: Oggettistica per consegne -->
            <div class="merch-section">
                <div class="merch-content">
                    <h3>📦 Oggettistica per Consegne e Packaging</h3>
                    <p>Scopri scatole protettive, buste imbottite e materiali ecologici ideali per spedire i tuoi libri in sicurezza.</p>
                </div>
                <a href="#" class="merch-btn">Esplora Catalogo</a>
            </div>
        </div>

        <script>
            async function loadHomeContent() {
                const response = await fetch('/api/books');
                const books = await response.json();

                populateCarousel('trending-carousel', books);
                populateCarousel('recent-carousel', books.slice().reverse());
                populateCarousel('classics-carousel', books.filter(b => b.genre === 'Classici'));
                populateCarousel('new-carousel', books);
                populateCarousel('favorites-carousel', books.slice(0, 3));
                populateCarousel('narrative-carousel', books.filter(b => b.genre.includes('Narrativa')));
                populateCarousel('essays-carousel', books.filter(b => b.genre.includes('Saggistica')));
                populateCarousel('lifestyle-carousel', books.filter(b => b.genre.includes('Crescita')));
                populateCarousel('hobby-carousel', books.filter(b => b.genre.includes('Cucina') || b.genre.includes('Hobby')));
                populateCarousel('ya-carousel', books.filter(b => b.genre.includes('Young Adult')));
            }

            function populateCarousel(elementId, booksList) {
                const container = document.getElementById(elementId);
                if (!container) return;
                container.innerHTML = '';
                
                if (booksList.length === 0) {
                    container.innerHTML = '<p style="color: #666; font-size: 0.85rem;">Nessun elemento disponibile in questa sezione.</p>';
                    return;
                }

                booksList.forEach(book => {
                    container.innerHTML += `
                        <div class="book-card">
                            <img src="${book.image_url}" alt="${book.title}">
                            <div class="book-info">
                                <h3>${book.title}</h3>
                                <p>${book.author}</p>
                                <div class="price">€ ${book.price.toFixed(2)}</div>
                            </div>
                        </div>
                    `;
                });
            }

            loadHomeContent();
        </script>
    </body>
    </html>
    """

@app.get("/api/books", response_model=List[Book])
def get_books():
    return fake_books_db

@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Metti in Vendita - Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background: #141414; color: #fff; padding: 40px; }
            .form-container { max-width: 600px; margin: auto; background: #1f1f1f; padding: 30px; border-radius: 8px; }
            input, select, textarea { width: 100%; padding: 10px; margin: 10px 0 20px 0; background: #333; border: none; color: #fff; border-radius: 4px; box-sizing: border-box; }
            button { background: #e50914; color: white; padding: 12px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>Metti in Vendita</h2>
            <form action="/api/sell" method="POST">
                <label>Codice ISBN (Autocompilazione assistita IA):</label>
                <input type="text" name="isbn" placeholder="Es. 9788804712345" required>
                
                <label>Prezzo di Vendita (€):</label>
                <input type="number" step="0.01" name="price" required>

                <label>Condizioni del libro:</label>
                <select name="condition">
                    <option value="Nuovo">Nuovo</option>
                    <option value="Ottime">Ottime</option>
                    <option value="Buone">Buone</option>
                    <option value="Discrete">Discrete</option>
                </select>

                <button type="submit">Conferma Inserzione</button>
            </form>
            <p><a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/api/sell")
def post_sell(isbn: str = Form(...), price: float = Form(...), condition: str = Form(...)):
    new_book = Book(
        id=len(fake_books_db) + 1,
        title=f"Libro ISBN {isbn}",
        author="Autore Verificato",
        genre="Narrativa e Letteratura",
        price=price,
        condition=condition,
        isbn=isbn,
        description="Inserito tramite flusso guidato con supporto IA.",
        image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
    )
    fake_books_db.append(new_book)
    return HTMLResponse("<html><body style='background:#141414;color:#fff;text-align:center;padding-top:50px;'><h2>Annuncio pubblicato con successo!</h2><a href='/' style='color:#00d2ff;'>Torna alla Home</a></body></html>")

@app.get("/library", response_class=HTMLResponse)
def library_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>La Mia Biblioteca - Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background: #141414; color: #fff; padding: 40px; }
            .container { max-width: 900px; margin: auto; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #1f1f1f; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-card h3 { margin: 0; color: #888; font-size: 0.9rem; }
            .stat-card p { font-size: 1.5rem; font-weight: bold; margin: 10px 0 0 0; color: #00d2ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>La Mia Biblioteca (Dashboard)</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>Magazzino (Libri)</h3>
                    <p>2</p>
                </div>
                <div class="stat-card">
                    <h3>Guadagno Totale Netto</h3>
                    <p>€ 42.50</p>
                </div>
                <div class="stat-card">
                    <h3>Valore Magazzino</h3>
                    <p>€ 35.00</p>
                </div>
            </div>
            <p><a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a></p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
