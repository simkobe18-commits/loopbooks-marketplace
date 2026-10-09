from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Loopbooks Marketplace", version="1.0")

class SellerOffer(BaseModel):
    seller_id: int
    seller_name: str
    location: str
    rating: float
    condition: str
    price: float
    book_image: str

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    avg_price: float
    publisher: str
    collection: str
    isbn: str
    edition_year: int
    pub_year: int
    description: str
    image_url: str
    sellers: List[SellerOffer]

# Database unificato con libri completi di dettagli e venditori
fake_books_db = [
    Book(
        id=1,
        title="Il monastero dei segreti",
        author="Anonimo",
        genre="Gialli/Thriller/Noir",
        avg_price=14.50,
        publisher="Mondadori",
        collection="Oscar Bestsellers",
        isbn="9788804712345",
        edition_year=2022,
        pub_year=2020,
        description="Un monastero isolato tra le nebbie, un antico manoscritto e un delitto inspiegabile.",
        image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"),
            SellerOffer(seller_id=102, seller_name="BookLovers Store", location="Bologna", rating=4.5, condition="Buone", price=11.00, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")
        ]
    ),
    Book(
        id=2,
        title="Python per Intelligenza Artificiale",
        author="Mario Rossi",
        genre="Scienze/Tecnologia/Natura",
        avg_price=28.00,
        publisher="Hoepli",
        collection="Tech & Code",
        isbn="9788803987654",
        edition_year=2024,
        pub_year=2023,
        description="Guida avanzata allo sviluppo di modelli intelligenti con FastAPI e Python.",
        image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=103, seller_name="TechBooks Italia", location="Roma", rating=4.9, condition="Nuovo", price=28.00, book_image="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80")
        ]
    ),
    Book(
        id=3,
        title="I Promessi Sposi",
        author="Alessandro Manzoni",
        genre="Classici",
        avg_price=10.00,
        publisher="Einaudi",
        collection="Classici Letteratura",
        isbn="9788801234567",
        edition_year=2021,
        pub_year=1840,
        description="Il capolavoro della letteratura italiana ambientato sul lago di Como.",
        image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=9.50, book_image="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80")
        ]
    )
]

user_library = []

# --- 1. HOME PAGE & VETRINA ---
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
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-color); color: var(--text-color); }
            header { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0)); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }
            .logo-area { display: flex; align-items: center; gap: 10px; font-size: 1.5rem; font-weight: 700; color: #fff; text-decoration: none; }
            .nav-center { display: flex; gap: 30px; align-items: center; }
            .nav-center a { color: var(--text-color); text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: color 0.3s; }
            .nav-center a:hover { color: #fff; }
            .profile-icon { width: 36px; height: 36px; background: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; }
            
            .hero { height: 65vh; background: linear-gradient(to right, rgba(20,20,20,0.9), rgba(20,20,20,0.4)), url('https://images.unsplash.com/photo-1507842229443-77783618cdc3?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover; display: flex; flex-direction: column; justify-content: center; padding: 0 50px; margin-top: 60px; }
            .hero h1 { font-size: 3rem; max-width: 600px; margin-bottom: 10px; line-height: 1.2; }
            .hero p { font-size: 1.2rem; max-width: 500px; color: #b3b3b3; margin-bottom: 25px; }
            .search-bar { display: flex; gap: 10px; max-width: 600px; }
            .search-bar input { flex: 1; padding: 12px 16px; border-radius: 4px; border: 1px solid #333; background: rgba(0,0,0,0.6); color: white; font-size: 1rem; }
            .search-bar button { padding: 0 20px; background: #fff; color: #000; font-weight: 600; border: none; border-radius: 4px; cursor: pointer; }
            
            .container { padding: 20px 50px 60px 50px; }
            h2.section-title { font-size: 1.3rem; margin: 35px 0 15px 0; font-weight: 600; color: #fff; }
            
            .carousel-container { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 15px; scroll-behavior: smooth; }
            .carousel-container::-webkit-scrollbar { height: 6px; }
            .carousel-container::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
            
            .book-card { min-width: 200px; max-width: 200px; background: var(--card-bg); border-radius: 8px; overflow: hidden; flex-shrink: 0; transition: transform 0.3s; cursor: pointer; text-decoration: none; color: inherit; display: block; }
            .book-card:hover { transform: scale(1.05); }
            .book-card img { width: 100%; height: 260px; object-fit: cover; }
            .book-info { padding: 12px; }
            .book-info h3 { margin: 0 0 4px 0; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .book-info p { margin: 0; color: #888; font-size: 0.8rem; }
            .price { color: var(--blue-glow); font-weight: 600; margin-top: 8px; font-size: 0.9rem; }
            
            .merch-section { background: linear-gradient(135deg, #1f1f1f, #111); border: 1px solid #333; border-radius: 12px; padding: 25px 30px; margin-top: 40px; display: flex; justify-content: space-between; align-items: center; }
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo-area"><span>📖 Loopbooks</span></a>
            <div class="nav-center">
                <a href="/sell">METTI IN VENDITA</a>
                <a href="/library">LA MIA BIBLIOTECA</a>
                <a href="#search-section">CERCA LIBRO</a>
            </div>
            <div class="profile-icon">SC</div>
        </header>

        <section class="hero" id="search-section">
            <h1>Un monastero, un segreto, un crimine.</h1>
            <p>Scopri il mistero tra migliaia di libri garantiti e venditori verificati.</p>
            <div class="search-bar">
                <input type="text" id="search-input" placeholder="Cerca per nome o codice ISBN...">
                <button onclick="filterBooks()">Trova il mio libro</button>
            </div>
        </section>

        <div class="container">
            <h2 class="section-title">Libri di tendenza (Top 10)</h2>
            <div class="carousel-container" id="trending-carousel"></div>

            <h2 class="section-title">Grandi classici</h2>
            <div class="carousel-container" id="classics-carousel"></div>

            <h2 class="section-title">Narrativa e Letteratura</h2>
            <div class="carousel-container" id="narrative-carousel"></div>

            <h2 class="section-title">Saggistica e Cultura</h2>
            <div class="carousel-container" id="essays-carousel"></div>

            <div class="merch-section">
                <div>
                    <h3>📦 Oggettistica per Consegne e Packaging</h3>
                    <p style="color: #aaa; margin: 5px 0 0 0; font-size: 0.9rem;">Scopri scatole e buste protettive per spedire in sicurezza.</p>
                </div>
                <a href="/sell" style="background: #e50914; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600;">Esplora</a>
            </div>
        </div>

        <script>
            async function loadHome() {
                const res = await fetch('/api/books');
                const books = await res.json();
                populate('trending-carousel', books);
                populate('classics-carousel', books.filter(b => b.genre === 'Classici'));
                populate('narrative-carousel', books.filter(b => b.genre.includes('Gialli') || b.genre.includes('Narrativa')));
                populate('essays-carousel', books.filter(b => b.genre.includes('Scienze')));
            }

            function populate(elemId, list) {
                const container = document.getElementById(elemId);
                container.innerHTML = '';
                if(list.length === 0) {
                    container.innerHTML = '<p style="color:#666; font-size:0.85rem;">Nessun libro disponibile.</p>';
                    return;
                }
                list.forEach(b => {
                    container.innerHTML += `
                        <a href="/book/${b.id}" class="book-card">
                            <img src="${b.image_url}" alt="${b.title}">
                            <div class="book-info">
                                <h3>${b.title}</h3>
                                <p>${b.author}</p>
                                <div class="price">€ ${b.avg_price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }

            async function filterBooks() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const res = await fetch('/api/books');
                const books = await res.json();
                const filtered = books.filter(b => b.title.toLowerCase().includes(query) || b.isbn.includes(query));
                populate('trending-carousel', filtered);
            }

            loadHome();
        </script>
    </body>
    </html>
    """

# --- 2. PAGINA INFO LIBRO (DETTAGLIO PRODOTTO) ---
@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int):
    book = next((b for b in fake_books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Libro non trovato")
    
    sellers_html = ""
    for s in book.sellers:
        sellers_html += f"""
        <div style="background:#1f1f1f; padding:15px; border-radius:8px; display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div style="display:flex; gap:15px; align-items:center;">
                <img src="{s.book_image}" style="width:50px; height:70px; object-fit:cover; border-radius:4px;">
                <div>
                    <h4 style="margin:0 0 4px 0;"><a href="/seller/{s.seller_id}" style="color:#00d2ff; text-decoration:none;">{s.seller_name}</a> <span style="font-size:0.8rem; color:#aaa;">({s.location})</span></h4>
                    <p style="margin:0; font-size:0.85rem; color:#888;">Condizione: <b>{s.condition}</b> | Valutazione: ⭐ {s.rating}</p>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:15px;">
                <span style="font-size:1.1rem; font-weight:bold; color:#00d2ff;">€ {s.price:.2f}</span>
                <button onclick="alert('Aggiunto al carrello!')" style="background:#e50914; color:#fff; border:none; padding:8px 12px; border-radius:4px; font-weight:600; cursor:pointer;">Carrello</button>
                <button onclick="alert('Aggiunto ai preferiti!')" style="background:#333; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">❤️</button>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>{book.title} - Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #141414; color: #e5e5e5; }}
            header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(0,0,0,0.9); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }}
            .container {{ padding: 120px 50px 60px 50px; max-width: 1000px; margin: auto; }}
            .detail-grid {{ display: grid; grid-template-columns: 300px 1fr; gap: 30px; margin-bottom: 40px; }}
            .detail-img {{ width: 100%; border-radius: 8px; object-fit: cover; height: 400px; }}
            .analytics-box {{ background: #1f1f1f; padding: 20px; border-radius: 8px; margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" style="color:#fff; text-decoration:none; font-weight:700; font-size:1.5rem;">📖 Loopbooks</a>
            <a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a>
        </header>

        <div class="container">
            <div class="detail-grid">
                <div><img src="{book.image_url}" class="detail-img"></div>
                <div>
                    <h1 style="margin-top:0;">{book.title}</h1>
                    <p style="color: #aaa; font-size: 1.1rem;">di <b>{book.author}</b></p>
                    <p><b>Genere:</b> {book.genre}</p>
                    <p><b>Prezzo medio di vendita:</b> <span style="color:#00d2ff; font-weight:bold;">€ {book.avg_price:.2f}</span></p>
                    <p><b>Editore:</b> {book.publisher} | <b>Collana:</b> {book.collection}</p>
                    <p><b>Codice EAN-ISBN:</b> {book.isbn}</p>
                    <p><b>Anno Edizione:</b> {book.edition_year} | <b>Pubblicazione:</b> {book.pub_year}</p>
                    <p style="margin-top: 15px; color: #ccc;">{book.description}</p>
                </div>
            </div>

            <div class="analytics-box">
                <h3 style="margin-top:0; color:#fff;">Analitica: Andamento Prezzi e Vendite nel tempo</h3>
                <canvas id="trendChart" height="90"></canvas>
            </div>

            <h3 style="color:#fff; margin-bottom: 15px;">Tutti i venditori per questo libro ({len(book.sellers)})</h3>
            <div>{sellers_html}</div>
        </div>

        <script>
            const ctx = document
