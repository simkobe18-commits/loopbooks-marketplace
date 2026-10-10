from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="LoopBooks Marketplace - Dark Fantasy Edition", version="2.1")

class SellerOffer(BaseModel):
    seller_id: int
    seller_name: str
    location: str
    rating: float
    condition: str
    price: float
    book_image: str

class SellerProfile(BaseModel):
    seller_id: int
    name: str
    location: str
    photo_url: str
    verified: bool
    books_sold: int
    total_rating: float
    comments: List[str]
    catalog: List[SellerOffer]

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
    publisher: str = "Scriptorium Monasticum"
    collection: str = "Codices Arcani"
    edition_year: int = 1492
    pub_year: int = 1485
    sellers: List[SellerOffer] = []

fake_sellers_db = [
    SellerProfile(
        seller_id=101,
        name="Abbazia di San Sisto",
        location="Milano Monastica",
        photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        verified=True,
        books_sold=342,
        total_rating=4.9,
        comments=["Pergamena preservata con cura mirabile.", "Spedizione celere attraverso le nebbie."],
        catalog=[
            SellerOffer(seller_id=101, seller_name="Abbazia di San Sisto", location="Milano Monastica", rating=4.9, condition="Ottime", price=14.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")
        ]
    )
]

fake_books_db = [
    Book(
        id=1, title="Il monastero dei segreti", author="Frater Aegidius", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", 
        description="Un monastero isolato tra le nebbie perpetue, un antico manoscritto cifrato e un delitto che sfida la ragione divina.", 
        image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
        sellers=[SellerOffer(seller_id=101, seller_name="Abbazia di San Sisto", location="Milano Monastica", rating=4.9, condition="Ottime", price=14.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]
    ),
    Book(
        id=2, title="Trattato di Alchimia e Sette Arti", author="Magister Cornelius", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", 
        description="Formule segrete, trasmutazioni dei metalli e codici segreti per l'intelletto.", 
        image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
        sellers=[SellerOffer(seller_id=103, seller_name="Scriptorium di Roma", location="Roma Sotterranea", rating=4.9, condition="Nuovo", price=27.00, book_image="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80")]
    ),
    Book(
        id=3, title="Cronache del Regno Sotterraneo", author="Dante da Norcia", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", 
        description="Il viaggio nei gironi dimenticati della mente e della terra.", 
        image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        sellers=[]
    )
]

# --- 1. HOME PAGE CON HERO 3D E TUTTI I CAROSELLI ---
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loopbooks - Dark Gothic Edition</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-deep: #0a0807;
                --bg-card: #14100e;
                --text-main: #d1c7bd;
                --text-muted: #8c7e72;
                --gold-candle: #c5a059;
                --gold-glow: rgba(197, 160, 89, 0.25);
                --shadow-gothic: 0 10px 30px rgba(0, 0, 0, 0.8);
                --border-sepia: #2d221b;
            }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-deep); color: var(--text-main); overflow-x: hidden; }
            
            header { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(10, 8, 7, 0.95); border-bottom: 1px solid var(--border-sepia); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; backdrop-filter: blur(8px); }
            .logo-area { display: flex; align-items: center; gap: 12px; font-family: 'Cinzel', serif; font-size: 1.6rem; font-weight: 700; color: var(--gold-candle); text-decoration: none; text-shadow: 0 0 10px var(--gold-glow); }
            .nav-center { display: flex; gap: 30px; align-items: center; }
            .nav-center a { color: var(--text-main); text-decoration: none; font-family: 'Cinzel', serif; font-weight: 600; font-size: 0.85rem; letter-spacing: 1px; transition: color 0.3s; }
            .nav-center a:hover { color: var(--gold-candle); text-shadow: 0 0 8px var(--gold-glow); }
            .login-btn { background: #1a1410; border: 1px solid var(--gold-candle); color: var(--gold-candle); padding: 8px 18px; border-radius: 2px; text-decoration: none; font-family: 'Cinzel', serif; font-weight: 600; font-size: 0.85rem; transition: all 0.3s; }
            .login-btn:hover { background: var(--gold-candle); color: #0a0807; box-shadow: 0 0 15px var(--gold-glow); }

            .hero-section {
                padding: 160px 50px 80px 50px;
                background: linear-gradient(135deg, rgba(10,8,7,0.95) 0%, rgba(26,18,11,0.85) 100%), url('https://images.unsplash.com/photo-1507842229443-77783618cdc3?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover;
                border-bottom: 2px solid var(--border-sepia);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 50px;
                box-shadow: inset 0 -40px 50px rgba(10,8,7,0.9);
            }
            .hero-content { max-width: 600px; }
            .hero-content h1 {
                font-family: 'Cinzel', serif;
                font-size: 3rem;
                font-weight: 900;
                color: #f3e5ab;
                margin: 0 0 20px 0;
                line-height: 1.15;
                text-shadow: 0 0 25px rgba(197, 160, 89, 0.4);
            }
            .hero-content p { font-size: 1.1rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 30px; }
            .hero-cta {
                display: inline-block;
                background: linear-gradient(135deg, #c5a059, #8c6d33);
                color: #0a0807;
                padding: 14px 30px;
                font-family: 'Cinzel', serif;
                font-weight: 700;
                text-decoration: none;
                border-radius: 2px;
                box-shadow: 0 0 20px rgba(197, 160, 89, 0.3);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .hero-cta:hover { transform: translateY(-3px); box-shadow: 0 0 30px rgba(197, 160, 89, 0.6); }

            /* HERO 3D BOOK */
            .book-3d-wrapper { perspective: 1200px; display: flex; justify-content: center; align-items: center; padding: 20px; }
            .book-3d {
                width: 220px; height: 330px; position: relative;
                transform-style: preserve-3d; transform: rotateY(-25deg) rotateX(10deg);
                transition: transform 0.6s ease; box-shadow: -25px 25px 40px rgba(0,0,0,0.9);
            }
            .book-3d:hover { transform: rotateY(0deg) rotateX(0deg) scale(1.02); }
            .book-cover {
                position: absolute; width: 100%; height: 100%;
                background: url('https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80') no-repeat center center/cover;
                border-radius: 3px 6px 6px 3px; border: 1px solid rgba(197, 160, 89, 0.4); box-sizing: border-box;
            }
            .book-spine {
                position: absolute; top: 0; left: 0; width: 35px; height: 100%;
                background: linear-gradient(90deg, #120e0b, #261c14);
                transform-origin: left; transform: rotateY(-90deg);
                border: 1px solid rgba(197, 160, 89, 0.2);
                display: flex; align-items: center; justify-content: center;
                writing-mode: vertical-rl; text-orientation: upright;
                font-family: 'Cinzel', serif; font-size: 0.65rem; color: var(--gold-candle); letter-spacing: 2px;
            }
            .book-pages {
                position: absolute; top: 3px; right: -15px; width: 15px; height: calc(100% - 6px);
                background: linear-gradient(90deg, #d1c7bd, #b3a496, #807264);
                transform: rotateY(90deg); border-radius: 0 2px 2px 0;
            }

            .container { padding: 40px 50px; }
            h2.section-title { font-family: 'Cinzel', serif; font-size: 1.5rem; margin: 40px 0 20px 0; font-weight: 700; color: #f3e5ab; border-bottom: 1px solid var(--border-sepia); padding-bottom: 8px; text-shadow: 0 0 10px rgba(197,160,89,0.2); }
            
            .carousel-container { display: flex; gap: 25px; overflow-x: auto; padding-bottom: 20px; scroll-behavior: smooth; }
            .carousel-container::-webkit-scrollbar { height: 6px; }
            .carousel-container::-webkit-scrollbar-thumb { background: var(--border-sepia); border-radius: 3px; }
            
            .book-card {
                min-width: 210px; max-width: 210px; background: var(--bg-card);
                border-radius: 4px; overflow: hidden; flex-shrink: 0; border: 1px solid var(--border-sepia);
                transition: transform 0.3s, border-color 0.3s, box-shadow 0.3s; cursor: pointer; text-decoration: none; color: inherit; display: block;
            }
            .book-card:hover { transform: translateY(-5px); border-color: var(--gold-candle); box-shadow: 0 10px 25px rgba(0,0,0,0.9), 0 0 15px var(--gold-glow); }
            .book-card img { width: 100%; height: 260px; object-fit: cover; filter: sepia(20%) contrast(110%); }
            .book-info { padding: 15px; }
            .book-info h3 { margin: 0 0 5px 0; font-family: 'Cinzel', serif; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #f3e5ab; }
            .book-info p { margin: 0; color: var(--text-muted); font-size: 0.8rem; }
            .price { color: var(--gold-candle); font-weight: 600; margin-top: 10px; font-size: 0.95rem; font-family: 'Cinzel', serif; text-shadow: 0 0 8px var(--gold-glow); }
            
            .merch-section { background: linear-gradient(135deg, #14100e, #0a0807); border: 1px solid var(--border-sepia); border-radius: 6px; padding: 30px; margin-top: 50px; display: flex; justify-content: space-between; align-items: center; box-shadow: var(--shadow-gothic); }
            .merch-section h3 { font-family: 'Cinzel', serif; color: #f3e5ab; margin: 0 0 5px 0; }
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo-area"><span>🕯️ Loopbooks</span></a>
            <div class="nav-center">
                <a href="/sell">METTI IN VENDITA</a>
                <a href="/library">LA MIA BIBLIOTECA</a>
                <a href="/search">CERCA LIBRO</a>
            </div>
            <a href="#" class="login-btn">Log-in Scriptorium</a>
        </header>

        <section class="hero-section">
            <div class="hero-content">
                <h1>Il monastero dei segreti</h1>
                <p>Esplora il catalogo avanzato illuminato da luci soffuse e pergamene antiche. Scopri volumi introvabili custoditi nelle biblioteche più recondite del mondo.</p>
                <a href="/search" class="hero-cta">Esplora il Scriptorium</a>
            </div>
            <div class="book-3d-wrapper">
                <div class="book-3d">
                    <div class="book-spine">MONASTERO DEI SEGRETI</div>
                    <div class="book-pages"></div>
                    <div class="book-cover"></div>
                </div>
            </div>
        </section>

        <div class="container">
            <h2 class="section-title">Volumi di Tendenza (Top 10)</h2>
            <div class="carousel-container" id="trending-carousel"></div>

            <h2 class="section-title">Visualizzati di recente</h2>
            <div class="carousel-container" id="recent-carousel"></div>

            <h2 class="section-title">Grandi Classici e Codici</h2>
            <div class="carousel-container" id="classics-carousel"></div>

            <h2 class="section-title">Nuove Scoperte</h2>
            <div class="carousel-container" id="new-carousel"></div>

            <h2 class="section-title">Preferiti del Custode</h2>
            <div class="carousel-container" id="favorites-carousel"></div>

            <h2 class="section-title">Narrativa e Letteratura</h2>
            <div class="carousel-container" id="narrative-carousel"></div>

            <h2 class="section-title">Saggistica e Alchimia</h2>
            <div class="carousel-container" id="essays-carousel"></div>

            <h2 class="section-title">Crescita Personale e Spiritualità</h2>
            <div class="carousel-container" id="lifestyle-carousel"></div>

            <div class="merch-section">
                <div>
                    <h3>📦 Custodie, Ceralacca e Packaging Antico</h3>
                    <p style="color: var(--text-muted); margin: 0; font-size: 0.9rem;">Proteggi i tuoi preziosi manoscritti con scatole rinforzate e sigilli in ceralacca.</p>
                </div>
                <a href="/sell" style="background: transparent; border: 1px solid var(--gold-candle); color: var(--gold-candle); padding: 10px 20px; border-radius: 2px; text-decoration: none; font-family: 'Cinzel', serif; font-weight: 600;">Esplora</a>
            </div>
        </div>

        <script>
            async function loadHome() {
                const res = await fetch('/api/books');
                const books = await res.json();
                populate('trending-carousel', books);
                populate('recent-carousel', books.slice().reverse());
                populate('classics-carousel', books.filter(b => b.genre === 'Classici'));
                populate('new-carousel', books);
                populate('favorites-carousel', books.slice(0, 2));
                populate('narrative-carousel', books.filter(b => b.genre.includes('Gialli')));
                populate('essays-carousel', books.filter(b => b.genre.includes('Scienze')));
                populate('lifestyle-carousel', books.filter(b => b.genre.includes('Crescita') || b.genre.includes('Classici')));
            }

            function populate(elemId, list) {
                const container = document.getElementById(elemId);
                if(!container) return;
                container.innerHTML = '';
                list.forEach(b => {
                    container.innerHTML += `
                        <a href="/book/${b.id}" class="book-card">
                            <img src="${b.image_url}" alt="${b.title}">
                            <div class="book-info">
                                <h3>${b.title}</h3>
                                <p>${b.author}</p>
                                <div class="price">€ ${b.price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }
            loadHome();
        </script>
    </body>
    </html>
    """

# --- 2. PAGINA DEDICATA "CERCA LIBRO" CON ALBERATURA COMPLETA ---
@app.get("/search", response_class=HTMLResponse)
def search_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Cerca Libro - Scriptorium Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root { --bg-deep: #0a0807; --bg-card: #14100e; --text-main: #d1c7bd; --text-muted: #8c7e72; --gold-candle: #c5a059; --gold-glow: rgba(197, 160, 89, 0.25); --border-sepia: #2d221b; }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-deep); color: var(--text-main); padding: 40px; }
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 1px solid var(--border-sepia); padding-bottom: 20px; }
            .container { max-width: 1000px; margin: auto; }
            
            .search-filters-box { background: var(--bg-card); padding: 35px; border-radius: 6px; border: 1px solid var(--border-sepia); margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
            .search-filters-box h2 { font-family: 'Cinzel', serif; font-size: 1.6rem; color: #f3e5ab; margin-top: 0; margin-bottom: 8px; text-shadow: 0 0 10px var(--gold-glow); }
            .search-filters-box p.search-subtitle { font-size: 0.95rem; color: var(--text-muted); margin-top: 0; margin-bottom: 25px; }
            .search-row { display: flex; gap: 15px; margin-bottom: 20px; }
            .search-row input { flex: 1; padding: 12px 16px; border-radius: 2px; border: 1px solid var(--border-sepia); background: #0a0807; color: white; font-size: 1rem; }
            .filters-grid { display: grid; grid-template-columns: 2fr 1.5fr 1fr; gap: 15px; margin-bottom: 20px; align-items: center; }
            .filters-grid select { padding: 10px; background: #0a0807; border: 1px solid var(--border-sepia); color: var(--text-main); border-radius: 2px; font-family: inherit; }
            .slider-container { background: #0a0807; padding: 8px 12px; border-radius: 2px; border: 1px solid var(--border-sepia); display: flex; flex-direction: column; }
            .slider-container label { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 4px; }
            .slider-container input[type=range] { width: 100%; accent-color: var(--gold-candle); cursor: pointer; }
            .cta-btn { background: linear-gradient(135deg, #c5a059, #8c6d33); color: #0a0807; padding: 12px 25px; border: none; border-radius: 2px; font-family: 'Cinzel', serif; font-weight: 700; cursor: pointer; width: 100%; font-size: 1rem; box-shadow: 0 0 15px var(--gold-glow); }
            
            .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; }
            .book-card { background: var(--bg-card); border-radius: 4px; overflow: hidden; border: 1px solid var(--border-sepia); text-decoration: none; color: inherit; display: block; transition: transform 0.3s, border-color 0.3s; }
            .book-card:hover { transform: translateY(-3px); border-color: var(--gold-candle); box-shadow: 0 5px 20px rgba(0,0,0,0.8), 0 0 10px var(--gold-glow); }
            .book-card img { width: 100%; height: 240px; object-fit: cover; filter: sepia(20%) contrast(110%); }
            .book-info { padding: 15px; }
            .book-info h3 { margin: 0 0 4px 0; font-family: 'Cinzel', serif; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #f3e5ab; }
            .price { color: var(--gold-candle); font-weight: 600; margin-top: 8px; font-size: 0.95rem; font-family: 'Cinzel', serif; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:var(--gold-candle); text-decoration:none; font-family:'Cinzel',serif; font-weight:700; font-size:1.5rem;">🕯️ Loopbooks</a>
                <a href="/" style="color: var(--text-muted); text-decoration: none; font-family:'Cinzel',serif; font-size:0.9rem;">← Torna al Scriptorium</a>
            </header>

            <div class="search-filters-box">
                <h2>Cerca il tuo libro</h2>
                <p class="search-subtitle">Esplora il catalogo avanzato e trova il tuo prossimo volume garantito.</p>
                <div class="search-row">
                    <input type="text" id="search-input" placeholder="Cerca per nome o codice ISBN...">
                </div>
                <div class="filters-grid">
                    <select id="genre-filter">
                        <option value="">Tutti i Generi (Alberatura Completa)</option>
                        <optgroup label="Narrativa e Letteratura">
                            <option value="Romanzi contemporanei">└ Romanzi contemporanei</option>
                            <option value="Narrativa storica">└ Narrativa storica</option>
                            <option value="Gialli/Thriller/Noir">└ Gialli/Thriller/Noir</option>
                            <option value="Fantasy/Sci-Fi">└ Fantasy/Sci-Fi</option>
                            <option value="Horror">└ Horror</option>
                            <option value="Romance">└ Romance</option>
                            <option value="Classici">└ Classici</option>
                        </optgroup>
                        <optgroup label="Saggistica e Cultura">
                            <option value="Storia e Biografie">└ Storia e Biografie</option>
                            <option value="Filosofia e Religione">└ Filosofia e Religione</option>
                            <option value="Scienze/Tecnologia/Natura">└ Scienze/Tecnologia/Natura</option>
                            <option value="Sociologia/Politica">└ Sociologia/Politica</option>
                            <option value="Arte/Musica/Cinema">└ Arte/Musica/Cinema</option>
                        </optgroup>
                        <optgroup label="Crescita Personale e Lifestyle">
                            <option value="Self-help/Motivazione">└ Self-help/Motivazione</option>
                            <option value="Business/Economia">└ Business/Economia</option>
                            <option value="Benessere/Salute">└ Benessere/Salute</option>
                            <option value="Cucina">└ Cucina</option>
                            <option value="Viaggi">└ Viaggi</option>
                            <option value="Hobby">└ Hobby</option>
                        </optgroup>
                        <optgroup label="Fumetti e Grafica">
                            <option value="Fumetti">└ Fumetti</option>
                            <option value="Manga">└ Manga</option>
                            <option value="Graphic Novel">└ Graphic Novel</option>
                            <option value="Libri illustrati">└ Libri illustrati</option>
                            <option value="Design">└ Design</option>
                        </optgroup>
                        <optgroup label="Altri settori">
                            <option value="Sport e Giochi">└ Sport e Giochi</option>
                            <option value="Esoterismo e Astrologia">└ Esoterismo e Astrologia</option>
                        </optgroup>
                        <optgroup label="Bambini e Ragazzi / Young Adult">
                            <option value="Prima infanzia 0-3 anni">└ Prima infanzia 0-3 anni</option>
                            <option value="4-8 anni">└ 4-8 anni</option>
                            <option value="9-13 anni">└ 9-13 anni</option>
                            <option value="Young Adult">└ Young Adult 14+</option>
                        </optgroup>
                    </select>

                    <select id="condition-filter">
                        <option value="">Condizioni (Tutte)</option>
                        <option value="Nuovo">Nuovo</option>
                        <option value="Ottime">Ottime</option>
                        <option value="Buone">Buone</option>
                        <option value="Discrete">Discrete</option>
                        <option value="Antico / Raro">Antico / Raro</option>
                    </select>

                    <div class="slider-container">
                        <label for="price-slider">Prezzo massimo: <span id="price-val">50</span> €</label>
                        <input type="range" id="price-slider" min="5" max="100" value="50" oninput="document.getElementById('price-val').innerText = this.value">
                    </div>
                </div>
                <button class="cta-btn" onclick="executeSearch()">Cerca nel Catalogo</button>
            </div>

            <h3 id="results-title" style="font-family:'Cinzel',serif; color:#f3e5ab; margin-bottom:20px;">Tutti i volumi disponibili</h3>
            <div class="results-grid" id="search-results"></div>
        </div>

        <script>
            async function loadAllBooks() {
                const res = await fetch('/api/books');
                const books = await res.json();
                renderResults(books);
            }

            function renderResults(list) {
                const container = document.getElementById('search-results');
                container.innerHTML = '';
                if(list.length === 0) {
                    container.innerHTML = '<p style="color:var(--text-muted);">Nessun manoscritto trovato con i filtri selezionati.</p>';
                    return;
                }
                list.forEach(b => {
                    container.innerHTML += `
                        <a href="/book/${b.id}" class="book-card">
                            <img src="${b.image_url}" alt="${b.title}">
                            <div class="book-info">
                                <h3>${b.title}</h3>
                                <p style="margin:0; font-size:0.8rem; color:var(--text-muted);">${b.author}</p>
                                <div class="price">€ ${b.price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }

            async function executeSearch() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const genre = document.getElementById('genre-filter').value;
                const maxPrice = parseFloat(document.getElementById('price-slider').value);
                const condition = document.getElementById('condition-filter').value;

                const res = await fetch('/api/books');
                const books = await res.json();

                const filtered = books.filter(b => {
                    const matchText = b.title.toLowerCase().includes(query) || b.isbn.includes(query);
                    const matchGenre = !genre || b.genre === genre;
                    const matchPrice = b.price <= maxPrice;
                    const matchCond = !condition || b.condition === condition;
                    return matchText && matchGenre && matchPrice && matchCond;
                });

                document.getElementById('results-title').innerText = `Risultati della Ricerca (${filtered.length})`;
                renderResults(filtered);
            }

            loadAllBooks();
        </script>
    </body>
    </html>
    """

@app.get("/api/books", response_model=List[Book])
def get_books():
    return fake_books_db

# --- 3. PAGINA INFO LIBRO CON GRAFICO CHART.JS ---
@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int):
    book = next((b for b in fake_books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Manoscritto non trovato")
    
    sellers_html = ""
    for s in book.sellers:
        sellers_html += f"""
        <div style="background:#14100e; padding:15px; border-radius:4px; border:1px solid #2d221b; display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div style="display:flex; gap:15px; align-items:center;">
                <img src="{s.book_image}" style="width:50px; height:70px; object-fit:cover; border-radius:2px;">
                <div>
                    <h4 style="margin:0 0 4px 0; font-family:'Cinzel',serif;"><a href="/seller/{s.seller_id}" style="color:#c5a059; text-decoration:none;">{s.seller_name}</a> <span style="font-size:0.8rem; color:#8c7e72;">({s.location})</span></h4>
                    <p style="margin:0; font-size:0.85rem; color:#8c7e72;">Condizione: <b>{s.condition}</b> | Valutazione: ⭐ {s.rating}</p>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:15px;">
                <span style="font-size:1.1rem; font-weight:bold; color:#c5a059; font-family:'Cinzel',serif;">€ {s.price:.2f}</span>
                <button onclick="alert('Manoscritto aggiunto al carrello monastico!')" style="background:#c5a059; color:#0a0807; border:none; padding:8px 14px; border-radius:2px; font-weight:bold; cursor:pointer; font-family:'Cinzel',serif;">Ottieni</button>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>{book.title} - Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0a0807; color: #d1c7bd; }}
            header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(10,8,7,0.95); border-bottom: 1px solid #2d221b; position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }}
            .container {{ padding: 120px 50px 60px 50px; max-width: 1000px; margin: auto; }}
            .detail-grid {{ display: grid; grid-template-columns: 300px 1fr; gap: 30px; margin-bottom: 40px; }}
            .detail-img {{ width: 100%; border-radius: 4px; object-fit: cover; height: 400px; border: 1px solid #2d221b; }}
            .analytics-box {{ background: #14100e; padding: 20px; border-radius: 6px; border: 1px solid #2d221b; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" style="color:#c5a059; text-decoration:none; font-family:'Cinzel',serif; font-weight:700; font-size:1.5rem;">🕯️ Loopbooks</a>
            <a href="/search" style="color: #8c7e72; text-decoration: none; font-family:'Cinzel',serif;">← Torna a Cerca Libro</a>
        </header>

        <div class="container">
            <div class="detail-grid">
                <div><img src="{book.image_url}" class="detail-img"></div>
                <div>
                    <h1 style="margin-top:0; font-family:'Cinzel',serif; color:#f3e5ab; text-shadow:0 0 10px rgba(197,160,89,0.2);">{book.title}</h1>
                    <p style="color: #8c7e72; font-size: 1.1rem;">custodito da <b>{book.author}</b></p>
                    <p><b>Genere:</b> {book.genre}</p>
                    <p><b>Prezzo di stima:</b> <span style="color:#c5a059; font-weight:bold; font-family:'Cinzel',serif;">€ {book.price:.2f}</span></p>
                    <p><b>Scriptorium:</b> {book.publisher} | <b>Collana:</b> {book.collection}</p>
                    <p><b>Codice ISBN:</b> {book.isbn}</p>
                    <p style="margin-top: 15px; color: #b3a496; line-height:1.6;">{book.description}</p>
                </div>
            </div>

            <div class="analytics-box">
                <h3 style="margin-top:0; color:#f3e5ab; font-family:'Cinzel',serif;">Andamento Storico dei Codici</h3>
                <canvas id="trendChart" height="90"></canvas>
            </div>

            <h3 style="color:#f3e5ab; margin-bottom: 15px; font-family:'Cinzel',serif;">Scribes & Venditori Monastici</h3>
            <div>{sellers_html}</div>
        </div>

        <script>
            const ctx = document.getElementById('trendChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
                    datasets: [{{
                        label: 'Valore Storico (€)',
                        data: [{book.price - 1.0}, {book.price - 0.7}, {book.price - 0.4}, {book.price - 0.1}, {book.price}, {book.price}],
                        borderColor: '#c5a059',
                        backgroundColor: 'rgba(197, 160, 89, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#d1c7bd' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#8c7e72' }}, grid: {{ color: '#2d221b' }} }}, y: {{ ticks: {{ color: '#8c7e72' }}, grid: {{ color: '#2d221b' }} }} }} }}
            }});
        </script>
    </body>
    </html>
    """

# --- 4. PAGINA DEL VENDITORE ---
@app.get("/seller/{seller_id}", response_class=HTMLResponse)
def seller_profile(seller_id: int):
    seller = SellerProfile(
        seller_id=seller_id, name=f"Abbazia di San Sisto", location="Milano Monastica",
        photo_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=80",
        verified=True, books_sold=342, total_rating=4.9,
        comments=["Pergamena preservata con cura mirabile.", "Spedizione celere attraverso le nebbie."],
        catalog=[SellerOffer(seller_id=seller_id, seller_name="Abbazia di San Sisto", location="Milano Monastica", rating=4.9, condition="Ottime", price=14.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]
    )

    comments_html = "".join([f"<p style='background:#14100e; padding:12px; border-radius:4px; border:1px solid #2d221b; margin:8px 0; color:#d1c7bd;'>🕯️ {c}</p>" for c in seller.comments])
    catalog_html = ""
    for item in seller.catalog:
        catalog_html += f"""
        <div style="background:#14100e; border-radius:4px; border:1px solid #2d221b; overflow:hidden; display:flex; flex-direction:column; justify-content:space-between;">
            <img src="{item.book_image}" style="width:100%; height:200px; object-fit:cover; filter:sepia(20%);">
            <div style="padding:15px;">
                <h4 style="margin:0 0 5px 0; font-family:'Cinzel',serif; color:#f3e5ab;">Condizione: {item.condition}</h4>
                <div style="color:#c5a059; font-weight:bold; font-size:1.1rem; margin-bottom:10px; font-family:'Cinzel',serif;">€ {item.price:.2f}</div>
                <div style="display:flex; gap:8px;">
                    <button onclick="alert('Aggiunto al carrello!')" style="flex:1; background:#c5a059; color:#0a0807; border:none; padding:8px; border-radius:2px; font-weight:bold; cursor:pointer; font-family:'Cinzel',serif;">Ottieni</button>
                    <a href="/book/1" style="background:#1a1410; border:1px solid #c5a059; color:#c5a059; padding:8px 12px; border-radius:2px; text-decoration:none; font-family:'Cinzel',serif; font-size:0.85rem;">Codice</a>
                </div>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>{seller.name} - Scriptorius</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0a0807; color: #d1c7bd; }}
            header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(10,8,7,0.95); border-bottom: 1px solid #2d221b; position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }}
            .container {{ padding: 120px 50px 60px 50px; max-width: 1100px; margin: auto; }}
            .profile-header {{ background: #14100e; padding: 30px; border-radius: 6px; border: 1px solid #2d221b; display: flex; gap: 30px; align-items: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
            .profile-avatar {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #c5a059; }}
            .catalog-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" style="color:#c5a059; text-decoration:none; font-family:'Cinzel',serif; font-weight:700; font-size:1.5rem;">🕯️ Loopbooks</a>
            <a href="/search" style="color: #8c7e72; text-decoration: none; font-family:'Cinzel',serif;">← Torna a Cerca Libro</a>
        </header>

        <div class="container">
            <div class="profile-header">
                <img src="{seller.photo_url}" class="profile-avatar">
                <div>
                    <h1 style="margin:0 0 5px 0; font-family:'Cinzel',serif; color:#f3e5ab;">{seller.name} <span style="font-size:1.0rem; color:#c5a059;">{'✓ Custode Verificato' if seller.verified else ''}</span></h1>
                    <p style="margin:0 0 10px 0; color:#8c7e72;">📍 {seller.location} | Codici trascritti: <b>{seller.books_sold}</b> | Reputazione: ⭐ <b>{seller.total_rating}/5.0</b></p>
                </div>
            </div>
            <h2 style="color:#f3e5ab; margin-bottom:20px; font-family:'Cinzel',serif;">Codici Custoditi</h2>
            <div class="catalog-grid">{catalog_html}</div>
            <div style="margin-top: 50px; background:#14100e; padding:25px; border-radius:6px; border:1px solid #2d221b;">
                <h3 style="margin-top:0; font-family:'Cinzel',serif; color:#f3e5ab;">Testimonianze dei Pellegrini</h3>
                <div>{comments_html}</div>
            </div>
        </div>
    </body>
    </html>
    """

# --- 5. LA MIA BIBLIOTECA (DASHBOARD COMPLETA CON KPI E GRAFICI) ---
@app.get("/library", response_class=HTMLResponse)
def library_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>La Mia Biblioteca - Scriptorius</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0a0807; color: #d1c7bd; padding: 40px; }
            .container { max-width: 1200px; margin: auto; }
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid #2d221b; padding-bottom: 20px; }
            .kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin-bottom: 30px; }
            .kpi-card { background: #14100e; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #2d221b; box-shadow: 0 5px 20px rgba(0,0,0,0.8); }
            .kpi-card h3 { margin: 0; color: #8c7e72; font-size: 0.75rem; text-transform: uppercase; font-family: 'Cinzel', serif; }
            .kpi-card p { font-size: 1.2rem; font-weight: bold; margin: 8px 0 0 0; color: #c5a059; font-family: 'Cinzel', serif; }
            .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 40px; }
            .chart-box { background: #14100e; padding: 20px; border-radius: 6px; border: 1px solid #2d221b; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
            .filter-bar { background: #14100e; padding: 20px; border-radius: 6px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px; border: 1px solid #2d221b; }
            .filter-bar input, .filter-bar select { padding: 10px; background: #0a0807; border: 1px solid #2d221b; color: #d1c7bd; border-radius: 2px; font-family: inherit; }
            .library-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
            .library-card { background: #14100e; border-radius: 4px; overflow: hidden; border: 1px solid #2d221b; transition: transform 0.3s, border-color 0.3s; cursor: pointer; text-decoration: none; color: inherit; display: block; }
            .library-card:hover { transform: translateY(-3px); border-color: #c5a059; box-shadow: 0 5px 20px rgba(0,0,0,0.8); }
            .library-card img { width: 100%; height: 240px; object-fit: cover; filter: sepia(20%); }
            .library-info { padding: 15px; }
            .badge { display: inline-block; padding: 3px 8px; border-radius: 2px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; font-family: 'Cinzel', serif; }
            .badge-magazzino { background: rgba(197, 160, 89, 0.15); color: #c5a059; border: 1px solid rgba(197, 160, 89, 0.3); }
            .price { color: #c5a059; font-weight: 600; margin-top: 8px; font-size: 0.95rem; font-family: 'Cinzel', serif; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:#c5a059; text-decoration:none; font-family:'Cinzel',serif; font-weight:700; font-size:1.5rem;">🕯️ Loopbooks - La Mia Biblioteca</a>
                <a href="/" style="color: #8c7e72; text-decoration: none; font-family:'Cinzel',serif;">← Torna al Scriptorium</a>
            </header>

            <div class="kpi-grid">
                <div class="kpi-card"><h3>Codici Ceduti</h3><p>1</p></div>
                <div class="kpi-card"><h3>Guadagno Netto</h3><p>€ 10.00</p></div>
                <div class="kpi-card"><h3>Codici Ottenuti</h3><p>1</p></div>
                <div class="kpi-card"><h3>Totale Speso</h3><p>€ 28.00</p></div>
                <div class="kpi-card"><h3>Magazzino</h3><p>1</p></div>
                <div class="kpi-card"><h3>Valore Magazzino</h3><p>€ 14.50</p></div>
            </div>

            <div class="charts-grid">
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem; font-family:'Cinzel',serif; color:#f3e5ab;">Andamento Storico Portafoglio</h3>
                    <canvas id="trendChart" height="110"></canvas>
                </div>
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem; font-family:'Cinzel',serif; color:#f3e5ab;">Ripartizione Asset</h3>
                    <canvas id="pieChart" height="135"></canvas>
                </div>
            </div>

            <div class="filter-bar">
                <input type="text" id="lib-search" placeholder="Cerca titolo o ISBN..." onkeyup="filterLibrary()">
                <select id="lib-genre" onchange="filterLibrary()">
                    <option value="">Tutti i Generi</option>
                    <option value="Gialli/Thriller/Noir">Gialli/Thriller/Noir</option>
                </select>
                <select id="lib-cond" onchange="filterLibrary()">
                    <option value="">Condizioni</option>
                    <option value="Ottime">Ottime</option>
                </select>
                <select id="lib-price" onchange="filterLibrary()">
                    <option value="">Prezzo</option>
                    <option value="20">Fino a 20 €</option>
                </select>
                <select id="lib-type" onchange="filterLibrary()">
                    <option value="">Tipologia</option>
                    <option value="In Magazzino">In Magazzino</option>
                </select>
            </div>

            <div class="library-grid" id="library-grid"></div>
        </div>

        <script>
            const libraryItems = [
                {id: 1, title: "Il monastero dei segreti", image: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80", condition: "Ottime", price: 14.50, type: "In Magazzino", genre: "Gialli/Thriller/Noir", isbn: "9788804712345"}
            ];
            function renderLibrary(items) {
                const grid = document.getElementById('library-grid');
                grid.innerHTML = '';
                items.forEach(item => {
                    grid.innerHTML += `
                        <a href="/book/${item.id}" class="library-card">
                            <img src="${item.image}">
                            <div class="library-info">
                                <span class="badge badge-magazzino">${item.type}</span>
                                <h4>${item.title}</h4>
                                <p style="margin:0; font-size:0.8rem; color:#8c7e72;">Condizioni: ${item.condition}</p>
                                <div class="price">€ ${item.price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }
            function filterLibrary() { renderLibrary(libraryItems); }
            
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            new Chart(ctxTrend, { type: 'line', data: { labels: ['Gen', 'Lug', 'Gen', 'Mag', 'Ott'], datasets: [{ label: 'Valore Netto (€)', data: [30, 50, 75, 110, 142.5], borderColor: '#c5a059', fill: true, backgroundColor: 'rgba(197,160,89,0.1)' }] } });
            
            const ctxPie = document.getElementById('pieChart').getContext('2d');
            new Chart(ctxPie, { type: 'doughnut', data: { labels: ['Guadagno', 'Spese', 'Magazzino'], datasets: [{ data: [10, 28, 14.5], backgroundColor: ['#8c6d33', '#4a1515', '#c5a059'] }] } });
            
            renderLibrary(libraryItems);
        </script>
    </body>
    </html>
    """

# --- 6. SEZIONE "METTI IN VENDITA" CON FLUSSO GUIDATO E CALCOLI ---
@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Metti in Vendita - Scriptorius</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root { --bg-deep: #0a0807; --bg-card: #14100e; --text-main: #d1c7bd; --text-muted: #8c7e72; --gold-candle: #c5a059; --gold-glow: rgba(197, 160, 89, 0.25); --border-sepia: #2d221b; }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-deep); color: var(--text-main); padding: 40px; }
            .container { max-width: 900px; margin: auto; }
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid var(--border-sepia); padding-bottom: 20px; }
            .form-box { background: var(--bg-card); padding: 35px; border-radius: 6px; border: 1px solid var(--border-sepia); margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            label { display: block; margin: 10px 0 5px 0; font-size: 0.9rem; color: var(--text-muted); font-family: 'Cinzel', serif; }
            input, select, textarea { width: 100%; padding: 10px; background: #0a0807; border: 1px solid var(--border-sepia); color: var(--text-main); border-radius: 2px; box-sizing: border-box; }
            .summary-box { background: #0a0807; padding: 20px; border-radius: 4px; border: 1px dashed var(--gold-candle); margin-top: 25px; }
            .submit-btn { background: linear-gradient(135deg, #c5a059, #8c6d33); color: #0a0807; padding: 14px; border: none; width: 100%; font-family: 'Cinzel', serif; font-weight: 700; border-radius: 2px; cursor: pointer; font-size: 1rem; margin-top: 25px; box-shadow: 0 0 15px var(--gold-glow); }
            .carousel-container { display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px; }
            .seller-compare-card { min-width: 180px; background: var(--bg-card); border-radius: 4px; padding: 12px; text-align: center; border: 1px solid var(--border-sepia); }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:#c5a059; text-decoration:none; font-family:'Cinzel',serif; font-weight:700; font-size:1.5rem;">🕯️ Loopbooks - Trascrivi Annuncio</a>
                <a href="/" style="color: #8c7e72; text-decoration: none; font-family:'Cinzel',serif;">← Torna al Scriptorium</a>
            </header>

            <div class="form-box">
                <h2 style="margin-top:0; font-family:'Cinzel',serif; color:#f3e5ab;">1. Codice ISBN & Autocompilazione Monastica (Gemini)</h2>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="isbn-input" placeholder="Inserisci codice ISBN..." value="9788804712345">
                    <button type="button" onclick="simulateAIAutoFill()" style="background:#c5a059; color:#0a0807; font-weight:bold; border:none; padding:0 20px; border-radius:2px; cursor:pointer; font-family:'Cinzel',serif;">Evoca Dati</button>
                </div>

                <form action="/api/sell-confirm" method="POST" style="margin-top:25px;">
                    <h3 style="border-bottom: 1px solid #2d221b; padding-bottom: 8px; font-family:'Cinzel',serif; color:#f3e5ab;">2. Dati del Manoscritto</h3>
                    <div class="form-grid">
                        <div>
                            <label>Titolo del Volume</label>
                            <input type="text" id="f-title" name="title" value="Il monastero dei segreti" required>
                        </div>
                        <div>
                            <label>Codice EAN</label>
                            <input type="text" id="f-ean" name="ean" value="9788804712345">
                        </div>
                        <div style="grid-column: span 2;">
                            <label>Sommario / Descrizione</label>
                            <textarea id="f-desc" name="description" rows="3">Un monastero isolato tra le nebbie perpetue, un antico manoscritto cifrato e un delitto.</textarea>
                        </div>
                        <div>
                            <label>Anno di Composizione</label>
                            <input type="number" id="f-pub" name="pub_year" value="1485">
                        </div>
                        <div>
                            <label>Anno di Edizione</label>
                            <input type="number" id="f-ed" name="ed_year" value="1492">
                        </div>
                        <div>
                            <label>Rilegatura</label>
                            <input type="text" id="f-bind" name="binding" value="Pelle e borchie metalliche">
                        </div>
                        <div>
                            <label>Scriptorium / Collana</label>
                            <input type="text" id="f-coll" name="collection" value="Scriptorium Monasticum">
                        </div>
                    </div>

                    <h3 style="border-bottom: 1px solid #2d221b; padding-bottom: 8px; margin-top:30px; font-family:'Cinzel',serif; color:#f3e5ab;">3. Dettagli dell'Offerta Monastica</h3>
                    <div class="form-grid">
                        <div>
                            <label>Prezzo di Cessione Desiderato (€)</label>
                            <input type="number" step="0.01" id="f-price" name="price" value="14.50" oninput="calculateSummary()" required>
                        </div>
                        <div>
                            <label>Genere</label>
                            <select name="genre">
                                <option value="Gialli/Thriller/Noir">Gialli / Thriller / Noir</option>
                                <option value="Classici">Classici</option>
                            </select>
                        </div>
                        <div>
                            <label>Condizioni del Volume</label>
                            <select name="condition">
                                <option value="Ottime" selected>Ottime</option>
                                <option value="Antico / Raro">Antico / Raro</option>
                            </select>
                        </div>
                        <div>
                            <label>Sigillo Fotografico (Immagini)</label>
                            <input type="file" name="photos" accept="image/*">
                        </div>
                        <div>
                            <label>Metodo di Spedizione</label>
                            <select name="shipping_mode" onchange="calculateSummary()" id="f-ship-mode">
                                <option value="ritiro_casa">Corriere dei Pellegrini</option>
                                <option value="luogo_ritiro">Ritiro in Abbazia</option>
                            </select>
                        </div>
                        <div>
                            <label>Ubicazione del Scriptorium</label>
                            <input type="text" name="pickup_address" placeholder="Via Abbazia 3, Milano">
                        </div>
                        <div style="grid-column: span 2;">
                            <label>Oneri di Spedizione a Carico di:</label>
                            <select name="shipping_payer" onchange="calculateSummary()" id="f-ship-payer">
                                <option value="compratore">A carico dell'Acquirente</option>
                                <option value="venditore">A carico del Venditore (€ 4.50)</option>
                            </select>
                        </div>
                    </div>

                    <div class="summary-box">
                        <h4 style="margin-top:0; color:#c5a059; font-family:'Cinzel',serif;">4. Resoconto Economico Monastico</h4>
                        <p style="margin:5px 0;">Tassa del Scriptorium (5%): <span id="sum-fee" style="float:right;">€ 0.73</span></p>
                        <p style="margin:5px 0;">Oneri di spedizione (carico venditore): <span id="sum-ship" style="float:right;">€ 0.00</span></p>
                        <hr style="border:0; border-top:1px dashed #2d221b; margin:10px 0;">
                        <p style="margin:5px 0; font-size:1.1rem; font-weight:bold; font-family:'Cinzel',serif;">Guadagno Netto Stimato: <span id="sum-net" style="float:right; color:#c5a059;">€ 13.77</span></p>
                    </div>

                    <button type="submit" class="submit-btn">5. Sigilla e Pubblica Annuncio (Anteprima)</button>
                </form>
            </div>

            <h3 style="color:#f3e5ab; margin-top:40px; font-family:'Cinzel',serif;">6. Esame di Mercato: Altri Scribes per questo Codice</h3>
            <div class="carousel-container">
                <div class="seller-compare-card">
                    <img src="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=200&q=80" style="width:100%; height:100px; object-fit:cover; border-radius:2px; filter:sepia(20%);">
                    <p style="margin:6px 0 2px 0; font-size:0.85rem; font-weight:bold; font-family:'Cinzel',serif; color:#f3e5ab;">Abbazia di San Sisto</p>
                    <p style="margin:0; color:#c5a059; font-weight:bold; font-family:'Cinzel',serif;">€ 13.50 (Ottime)</p>
                </div>
            </div>
        </div>

        <script>
            function simulateAIAutoFill() { alert('L’intelligenza monastica di Gemini ha trascritto i dati con successo!'); }
            function calculateSummary() {
                const price = parseFloat(document.getElementById('f-price').value) || 0;
                const shipPayer = document.getElementById('f-ship-payer').value;
                const fee = price * 0.05;
                const shipCost = (shipPayer === 'venditore') ? 4.50 : 0.00;
                const net = price - fee - shipCost;
                document.getElementById('sum-fee').innerText = '€ ' + fee.toFixed(2);
                document.getElementById('sum-ship').innerText = '€ ' + shipCost.toFixed(2);
                document.getElementById('sum-net').innerText = '€ ' + (net > 0 ? net.toFixed(2) : '0.00');
            }
            calculateSummary();
        </script>
    </body>
    </html>
    """

@app.post("/api/sell-confirm")
def post_sell_confirm(title: str = Form(...), price: float = Form(...)):
    return HTMLResponse(f"<html><body style='background:#0a0807;color:#d1c7bd;text-align:center;padding-top:80px;font-family:Cinzel,serif;'><h2 style='color:#f3e5ab;'>Il manoscritto '{title}' è stato consacrato nel Scriptorium!</h2><p style='color:#8c7e72;'>Il tuo volume è ora visibile ai pellegrini di tutto il regno.</p><a href='/' style='color:#c5a059; text-decoration:none; font-weight:bold;'>← Ritorna al Scriptorium</a></body></html>")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
