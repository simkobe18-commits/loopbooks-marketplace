from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="LoopBooks Marketplace", version="1.0")

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
    publisher: str = "Mondadori Editore"
    collection: str = "Oscar Bestsellers"
    edition_year: int = 2022
    pub_year: int = 2020
    sellers: List[SellerOffer] = []

fake_sellers_db = [
    SellerProfile(
        seller_id=101,
        name="Libreria Del Borgo",
        location="Milano",
        photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        verified=True,
        books_sold=142,
        total_rating=4.8,
        comments=["Spedizione velocissima e imballaggio perfetto!", "Libro in condizioni ottime."],
        catalog=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")
        ]
    )
]

fake_books_db = [
    Book(
        id=1, title="Il monastero dei segreti", author="Anonimo", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", 
        description="Un monastero isolato tra le nebbie, un antico manoscritto e un delitto inspiegabile.", 
        image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
        sellers=[SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]
    ),
    Book(
        id=2, title="Python per Intelligenza Artificiale", author="Mario Rossi", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", 
        description="Guida avanzata allo sviluppo di modelli intelligenti con FastAPI e Python.", 
        image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
        sellers=[SellerOffer(seller_id=103, seller_name="TechBooks Roma", location="Roma", rating=4.9, condition="Nuovo", price=27.00, book_image="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80")]
    ),
    Book(
        id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", 
        description="Il capolavoro della letteratura italiana.", 
        image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        sellers=[]
    )
]

# --- 1. HOME PAGE, RICERCA E VETRINA ---
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
            .nav-center a { color: var(--text-color); text-decoration: none; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px; transition: color 0.3s; }
            .nav-center a:hover { color: #fff; }
            .login-btn { background: #333; color: #fff; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }
            
            .hero { padding: 140px 50px 50px 50px; background: linear-gradient(to right, rgba(20,20,20,0.95), rgba(20,20,20,0.6)), url('https://images.unsplash.com/photo-1507842229443-77783618cdc3?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover; }
            .hero h1 { font-size: 2.5rem; max-width: 700px; margin-bottom: 10px; line-height: 1.2; }
            .hero p { font-size: 1.1rem; max-width: 600px; color: #b3b3b3; margin-bottom: 25px; }
            
            .search-filters-box { background: rgba(31, 31, 31, 0.95); padding: 25px; border-radius: 8px; max-width: 900px; backdrop-filter: blur(5px); border: 1px solid #333; }
            .search-row { display: flex; gap: 15px; margin-bottom: 15px; }
            .search-row input { flex: 1; padding: 12px 16px; border-radius: 4px; border: 1px solid #444; background: #111; color: white; font-size: 1rem; }
            .filters-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
            .filters-grid select { padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 4px; }
            .cta-btn { background: var(--accent-color); color: white; padding: 12px 25px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; font-size: 1rem; transition: background 0.3s; }
            .cta-btn:hover { background: var(--accent-hover); }

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
            <a href="#" class="login-btn">Log-in</a>
        </header>

        <section class="hero" id="search-section">
            <h1>Un monastero, un segreto, un crimine.</h1>
            <p>Esplora il catalogo avanzato e trova il tuo prossimo volume garantito.</p>
            
            <div class="search-filters-box">
                <div class="search-row">
                    <input type="text" id="search-input" placeholder="Cerca per nome o codice ISBN...">
                </div>
                <div class="filters-grid">
                    <select id="genre-filter">
                        <option value="">Tutti i Generi</option>
                        <optgroup label="Narrativa e Letteratura">
                            <option value="Romanzi contemporanei">Romanzi contemporanei</option>
                            <option value="Narrativa storica">Narrativa storica</option>
                            <option value="Gialli/Thriller/Noir">Gialli/Thriller/Noir</option>
                            <option value="Fantasy/Sci-Fi">Fantasy/Sci-Fi</option>
                            <option value="Horror">Horror</option>
                            <option value="Romance">Romance</option>
                            <option value="Classici">Classici</option>
                        </optgroup>
                        <optgroup label="Saggistica e Cultura">
                            <option value="Storia e Biografie">Storia e Biografie</option>
                            <option value="Filosofia e Religione">Filosofia e Religione</option>
                            <option value="Scienze/Tecnologia/Natura">Scienze/Tecnologia/Natura</option>
                            <option value="Sociologia/Politica">Sociologia/Politica</option>
                            <option value="Arte/Musica/Cinema">Arte/Musica/Cinema</option>
                        </optgroup>
                        <optgroup label="Crescita Personale e Lifestyle">
                            <option value="Self-help/Motivazione">Self-help/Motivazione</option>
                            <option value="Business/Economia">Business/Economia</option>
                            <option value="Benessere/Salute">Benessere/Salute</option>
                            <option value="Cucina">Cucina</option>
                            <option value="Viaggi">Viaggi</option>
                            <option value="Hobby">Hobby</option>
                        </optgroup>
                    </select>
                    <select id="price-filter">
                        <option value="">Prezzo (qualsiasi)</option>
                        <option value="15">Fino a 15 €</option>
                        <option value="30">Fino a 30 €</option>
                    </select>
                    <select id="condition-filter">
                        <option value="">Condizioni (qualsiasi)</option>
                        <option value="Nuovo">Nuovo</option>
                        <option value="Ottime">Ottime</option>
                        <option value="Buone">Buone</option>
                    </select>
                </div>
                <button class="cta-btn" onclick="executeSearch()">Trova il mio libro</button>
            </div>
        </section>

        <div class="container" id="results-container">
            <h2 class="section-title">Libri di tendenza (Top 10)</h2>
            <div class="carousel-container" id="trending-carousel"></div>

            <h2 class="section-title">Visualizzati di recente</h2>
            <div class="carousel-container" id="recent-carousel"></div>

            <h2 class="section-title">Grandi classici</h2>
            <div class="carousel-container" id="classics-carousel"></div>

            <h2 class="section-title">Nuove uscite</h2>
            <div class="carousel-container" id="new-carousel"></div>

            <h2 class="section-title">Preferiti</h2>
            <div class="carousel-container" id="favorites-carousel"></div>

            <h2 class="section-title">Narrativa e Letteratura</h2>
            <div class="carousel-container" id="narrative-carousel"></div>

            <h2 class="section-title">Saggistica e Cultura</h2>
            <div class="carousel-container" id="essays-carousel"></div>

            <h2 class="section-title">Crescita Personale e Lifestyle</h2>
            <div class="carousel-container" id="lifestyle-carousel"></div>

            <div class="merch-section">
                <div>
                    <h3>📦 Oggettistica per Consegne e Packaging</h3>
                    <p style="color: #aaa; margin: 5px 0 0 0; font-size: 0.9rem;">Scopri scatole protettive, buste imbottite e materiali ecologici.</p>
                </div>
                <a href="/sell" style="background: #e50914; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600;">Esplora</a>
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
                populate('lifestyle-carousel', books.filter(b => b.genre.includes('Crescita')));
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

            async function executeSearch() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const res = await fetch('/api/books');
                const books = await res.json();
                const filtered = books.filter(b => b.title.toLowerCase().includes(query) || b.isbn.includes(query));
                const mainContainer = document.getElementById('results-container');
                mainContainer.innerHTML = `<h2 class="section-title">Risultati della Ricerca (${filtered.length})</h2><div class="carousel-container" id="search-results-carousel"></div><p><a href="/" style="color:#00d2ff; text-decoration:none;">← Torna alla vista principale</a></p>`;
                populate('search-results-carousel', filtered);
            }

            loadHome();
        </script>
    </body>
    </html>
    """

@app.get("/api/books", response_model=List[Book])
def get_books():
    return fake_books_db

# --- 2. PAGINA INFO LIBRO ---
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
                    <p><b>Prezzo medio:</b> <span style="color:#00d2ff; font-weight:bold;">€ {book.price:.2f}</span></p>
                    <p><b>Editore:</b> {book.publisher} | <b>Collana:</b> {book.collection}</p>
                    <p><b>Codice EAN-ISBN:</b> {book.isbn}</p>
                    <p style="margin-top: 15px; color: #ccc;">{book.description}</p>
                </div>
            </div>

            <div class="analytics-box">
                <h3 style="margin-top:0; color:#fff;">Analitica: Andamento Prezzi e Vendite nel tempo</h3>
                <canvas id="trendChart" height="90"></canvas>
            </div>

            <h3 style="color:#fff; margin-bottom: 15px;">Lista Venditori</h3>
            <div>{sellers_html}</div>
        </div>

        <script>
            const ctx = document.getElementById('trendChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
                    datasets: [{{
                        label: 'Prezzo Medio (€)',
                        data: [{book.price - 1.0}, {book.price - 0.7}, {book.price - 0.4}, {book.price - 0.1}, {book.price}, {book.price}],
                        borderColor: '#00d2ff',
                        backgroundColor: 'rgba(0, 210, 255, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#fff' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }}, y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }} }} }}
            }});
        </script>
    </body>
    </html>
    """

# --- 3. PAGINA DEL VENDITORE ---
@app.get("/seller/{seller_id}", response_class=HTMLResponse)
def seller_profile(seller_id: int):
    seller = next((s for s in fake_sellers_db if s.seller_id == seller_id), None)
    if not seller:
        seller = SellerProfile(
            seller_id=seller_id, name=f"Libreria Partner #{seller_id}", location="Roma",
            photo_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=80",
            verified=True, books_sold=95, total_rating=4.9,
            comments=["Ottimo servizio!", "Consigliatissimo."],
            catalog=[SellerOffer(seller_id=seller_id, seller_name=f"Partner #{seller_id}", location="Roma", rating=4.9, condition="Nuovo", price=15.00, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]
        )

    comments_html = "".join([f"<p style='background:#2a2a2a; padding:10px; border-radius:4px; margin:8px 0;'>💬 {c}</p>" for c in seller.comments])
    catalog_html = ""
    for item in seller.catalog:
        catalog_html += f"""
        <div style="background:#1f1f1f; border-radius:8px; overflow:hidden; display:flex; flex-direction:column; justify-content:space-between;">
            <img src="{item.book_image}" style="width:100%; height:200px; object-fit:cover;">
            <div style="padding:15px;">
                <h4 style="margin:0 0 5px 0;">Condizione: {item.condition}</h4>
                <div style="color:#00d2ff; font-weight:bold; font-size:1.1rem; margin-bottom:10px;">€ {item.price:.2f}</div>
                <div style="display:flex; gap:8px;">
                    <button onclick="alert('Aggiunto al carrello!')" style="flex:1; background:#e50914; color:#fff; border:none; padding:8px; border-radius:4px; font-weight:bold; cursor:pointer;">Carrello</button>
                    <button onclick="alert('Aggiunto ai preferiti!')" style="background:#333; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">❤️</button>
                    <a href="/book/1" style="background:#00d2ff; color:#000; padding:8px 12px; border-radius:4px; text-decoration:none; font-weight:bold;">Info</a>
                </div>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>{seller.name} - Profilo Venditore</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #141414; color: #e5e5e5; }}
            header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(0,0,0,0.9); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }}
            .container {{ padding: 120px 50px 60px 50px; max-width: 1100px; margin: auto; }}
            .profile-header {{ background: #1f1f1f; padding: 30px; border-radius: 12px; display: flex; gap: 30px; align-items: center; margin-bottom: 30px; }}
            .profile-avatar {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #00d2ff; }}
            .catalog-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" style="color:#fff; text-decoration:none; font-weight:700; font-size:1.5rem;">📖 Loopbooks</a>
            <a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a>
        </header>

        <div class="container">
            <div class="profile-header">
                <img src="{seller.photo_url}" class="profile-avatar">
                <div>
                    <h1 style="margin:0 0 5px 0;">{seller.name} <span style="font-size:1.0rem; color:#00d2ff;">{'✓ Verificato' if seller.verified else ''}</span></h1>
                    <p style="margin:0 0 10px 0; color:#aaa;">📍 {seller.location} | Libri venduti: <b>{seller.books_sold}</b> | Valutazione: ⭐ <b>{seller.total_rating}/5.0</b></p>
                </div>
            </div>
            <h2 style="color:#fff; margin-bottom:20px;">Catalogo del Venditore</h2>
            <div class="catalog-grid">{catalog_html}</div>
            <div style="margin-top: 50px; background:#1f1f1f; padding:25px; border-radius:8px;">
                <h3 style="margin-top:0;">Commenti e Recensioni</h3>
                <div>{comments_html}</div>
            </div>
        </div>
    </body>
    </html>
    """

# --- 4. LA MIA BIBLIOTECA (DASHBOARD UTENTE) ---
@app.get("/library", response_class=HTMLResponse)
def library_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>La Mia Biblioteca - Loopbooks</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #141414; color: #e5e5e5; padding: 40px; }
            .container { max-width: 1200px; margin: auto; }
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin-bottom: 30px; }
            .kpi-card { background: #1f1f1f; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; }
            .kpi-card h3 { margin: 0; color: #888; font-size: 0.75rem; text-transform: uppercase; }
            .kpi-card p { font-size: 1.2rem; font-weight: bold; margin: 8px 0 0 0; color: #00d2ff; }
            .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 40px; }
            .chart-box { background: #1f1f1f; padding: 20px; border-radius: 8px; border: 1px solid #333; }
            .filter-bar { background: #1f1f1f; padding: 20px; border-radius: 8px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px; border: 1px solid #333; }
            .filter-bar input, .filter-bar select { padding: 10px; background: #333; border: none; color: #fff; border-radius: 4px; font-family: inherit; }
            .library-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
            .library-card { background: #1f1f1f; border-radius: 8px; overflow: hidden; border: 1px solid #333; transition: transform 0.3s; cursor: pointer; text-decoration: none; color: inherit; display: block; }
            .library-card:hover { transform: scale(1.03); }
            .library-card img { width: 100%; height: 240px; object-fit: cover; }
            .library-info { padding: 12px; }
            .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; }
            .badge-magazzino { background: #00d2ff22; color: #00d2ff; }
            .price { color: #00d2ff; font-weight: 600; margin-top: 8px; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:#fff; text-decoration:none; font-weight:700; font-size:1.5rem;">📖 Loopbooks - La Mia Biblioteca</a>
                <a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a>
            </header>

            <div class="kpi-grid">
                <div class="kpi-card"><h3>Libri Venduti</h3><p>1</p></div>
                <div class="kpi-card"><h3>Guadagno Netto</h3><p>€ 10.00</p></div>
                <div class="kpi-card"><h3>Libri Comprati</h3><p>1</p></div>
                <div class="kpi-card"><h3>Totale Comprato</h3><p>€ 28.00</p></div>
                <div class="kpi-card"><h3>Magazzino</h3><p>1</p></div>
                <div class="kpi-card"><h3>Valore Magazzino</h3><p>€ 14.50</p></div>
            </div>

            <div class="charts-grid">
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Trend Portafoglio (Soldi / Mesi / Anni)</h3>
                    <canvas id="trendChart" height="110"></canvas>
                </div>
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Ripartizione</h3>
                    <canvas id="pieChart" height="135"></canvas>
                </div>
            </div>

            <div class="filter-bar">
                <input type="text" id="lib-search" placeholder="Cerca nome o ISBN..." onkeyup="filterLibrary()">
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
                                <p style="margin:0; font-size:0.8rem; color:#888;">Condizioni: ${item.condition}</p>
                                <div class="price">€ ${item.price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }
            function filterLibrary() { renderLibrary(libraryItems); }
            
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            new Chart(ctxTrend, { type: 'line', data: { labels: ['Gen', 'Lug', 'Gen', 'Mag', 'Ott'], datasets: [{ label: 'Netto (€)', data: [30, 50, 75, 110, 142.5], borderColor: '#00d2ff', fill: true, backgroundColor: 'rgba(0,210,255,0.1)' }] } });
            
            const ctxPie = document.getElementById('pieChart').getContext('2d');
            new Chart(ctxPie, { type: 'doughnut', data: { labels: ['Guadagno', 'Spese', 'Magazzino'], datasets: [{ data: [10, 28, 14.5], backgroundColor: ['#28a745', '#e50914', '#00d2ff'] }] } });
            
            renderLibrary(libraryItems);
        </script>
    </body>
    </html>
    """

# --- 5. SEZIONE "METTI IN VENDITA" (INSERZIONE GUIDATA A FLUSSO COMPLETO) ---
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
            :root { --bg-color: #141414; --card-bg: #1f1f1f; --text-color: #e5e5e5; --accent-color: #e50914; --blue-glow: #00d2ff; }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-color); color: var(--text-color); padding: 40px; }
            .container { max-width: 900px; margin: auto; }
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .form-box { background: #1f1f1f; padding: 30px; border-radius: 8px; border: 1px solid #333; margin-bottom: 30px; }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            label { display: block; margin: 10px 0 5px 0; font-size: 0.9rem; color: #aaa; }
            input, select, textarea { width: 100%; padding: 10px; background: #333; border: 1px solid #444; color: #fff; border-radius: 4px; box-sizing: border-box; }
            .summary-box { background: #111; padding: 20px; border-radius: 6px; border: 1px dashed #00d2ff; margin-top: 20px; }
            .submit-btn { background: var(--accent-color); color: #fff; padding: 12px; border: none; width: 100%; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 20px; }
            
            /* Carosello Venditori Sottostante per Confronto Prezzi */
            .carousel-container { display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px; }
            .seller-compare-card { min-width: 180px; background: #222; border-radius: 6px; padding: 12px; text-align: center; border: 1px solid #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:#fff; text-decoration:none; font-weight:700; font-size:1.5rem;">📖 Loopbooks - Crea Annuncio</a>
                <a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a>
            </header>

            <div class="form-box">
                <h2 style="margin-top:0;">1. Inserimento ISBN & Autocompilazione IA (Gemini)</h2>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="isbn-input" placeholder="Inserisci codice ISBN (es. 9788804712345)..." value="9788804712345">
                    <button type="button" onclick="simulateAIAutoFill()" style="background:#00d2ff; color:#000; font-weight:bold; border:none; padding:0 20px; border-radius:4px; cursor:pointer;">Autocompila IA</button>
                </div>

                <form action="/api/sell-confirm" method="POST" style="margin-top:25px;">
                    <h3 style="border-bottom: 1px solid #333; padding-bottom: 8px;">2. Dati del Libro</h3>
                    <div class="form-grid">
                        <div>
                            <label>Nome Libro / Titolo</label>
                            <input type="text" id="f-title" name="title" value="Il monastero dei segreti" required>
                        </div>
                        <div>
                            <label>Codice EAN</label>
                            <input type="text" id="f-ean" name="ean" value="9788804712345">
                        </div>
                        <div style="grid-column: span 2;">
                            <label>Descrizione (Riassunto)</label>
                            <textarea id="f-desc" name="description" rows="3">Un monastero isolato tra le nebbie, un antico manoscritto e un delitto inspiegabile.</textarea>
                        </div>
                        <div>
                            <label>Anno Pubblicazione</label>
                            <input type="number" id="f-pub" name="pub_year" value="2020">
                        </div>
                        <div>
                            <label>Anno Edizione</label>
                            <input type="number" id="f-ed" name="ed_year" value="2022">
                        </div>
                        <div>
                            <label>Rilegatura</label>
                            <input type="text" id="f-bind" name="binding" value="Flessibile / Brossura">
                        </div>
                        <div>
                            <label>Collana / Editore</label>
                            <input type="text" id="f-coll" name="collection" value="Mondadori - Oscar Bestsellers">
                        </div>
                    </div>

                    <h3 style="border-bottom: 1px solid #333; padding-bottom: 8px; margin-top:30px;">3. Dettagli dell'Offerta del Venditore</h3>
                    <div class="form-grid">
                        <div>
                            <label>Prezzo di Vendita Desiderato (€)</label>
                            <input type="number" step="0.01" id="f-price" name="price" value="14.50" oninput="calculateSummary()" required>
                        </div>
                        <div>
                            <label>Genere</label>
                            <select name="genre">
                                <option value="Gialli/Thriller/Noir">Gialli / Thriller / Noir</option>
                                <option value="Narrativa storica">Narrativa storica</option>
                                <option value="Classici">Classici</option>
                                <option value="Scienze/Tecnologia/Natura">Scienze / Tecnologia / Natura</option>
                                <option value="Crescita Personale">Crescita Personale</option>
                            </select>
                        </div>
                        <div>
                            <label>Condizioni del Libro</label>
                            <select name="condition">
                                <option value="Nuovo">Nuovo</option>
                                <option value="Ottime" selected>Ottime</option>
                                <option value="Buone">Buone</option>
                                <option value="Discrete">Discrete</option>
                            </select>
                        </div>
                        <div>
                            <label>Caricamento Foto Reali</label>
                            <input type="file" name="photos" accept="image/*">
                        </div>
                        <div>
                            <label>Modalità di Spedizione</label>
                            <select name="shipping_mode" onchange="calculateSummary()" id="f-ship-mode">
                                <option value="ritiro_casa">Ritiro a casa (Corriere)</option>
                                <option value="luogo_ritiro">Luogo di ritiro designato</option>
                            </select>
                        </div>
                        <div>
                            <label>Indirizzo Luogo di Ritiro</label>
                            <input type="text" name="pickup_address" placeholder="Via Roma 10, Milano">
                        </div>
                        <div style="grid-column: span 2;">
                            <label>Spese di Spedizione a Carico di:</label>
                            <select name="shipping_payer" onchange="calculateSummary()" id="f-ship-payer">
                                <option value="compratore">A carico del Compratore</option>
                                <option value="venditore">A carico del Venditore (€ 4.50)</option>
                            </select>
                        </div>
                    </div>

                    <!-- 4. Riepilogo Economico -->
                    <div class="summary-box">
                        <h4 style="margin-top:0; color:#00d2ff;">4. Riepilogo Economico Stimato</h4>
                        <p style="margin:5px 0;">Trattenuta del sito (5%): <span id="sum-fee" style="float:right;">€ 0.73</span></p>
                        <p style="margin:5px 0;">Spese consegna (carico venditore): <span id="sum-ship" style="float:right;">€ 0.00</span></p>
                        <hr style="border:0; border-top:1px solid #333; margin:10px 0;">
                        <p style="margin:5px 0; font-size:1.1rem; font-weight:bold;">Guadagno Netto Stimato: <span id="sum-net" style="float:right; color:#28a745;">€ 13.77</span></p>
                    </div>

                    <!-- 5. Finalizzazione -->
                    <button type="submit" class="submit-btn">5. Conferma e Pubblica Annuncio (Preview)</button>
                </form>
            </div>

            <!-- 6. Elenco a scorrimento altri venditori attivi (Termine di paragone) -->
            <h3 style="color:#fff; margin-top:40px;">6. Confronto Prezzi: Altri venditori attivi per questo titolo</h3>
            <div class="carousel-container">
                <div class="seller-compare-card">
                    <img src="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=200&q=80" style="width:100%; height:100px; object-fit:cover; border-radius:4px;">
                    <p style="margin:6px 0 2px 0; font-size:0.85rem; font-weight:bold;">Libreria Del Borgo</p>
                    <p style="margin:0; color:#00d2ff; font-weight:bold;">€ 13.50 (Ottime)</p>
                </div>
                <div class="seller-compare-card">
                    <img src="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=200&q=80" style="width:100%; height:100px; object-fit:cover; border-radius:4px;">
                    <p style="margin:6px 0 2px 0; font-size:0.85rem; font-weight:bold;">BookLovers Store</p>
                    <p style="margin:0; color:#00d2ff; font-weight:bold;">€ 11.00 (Buone)</p>
                </div>
            </div>
        </div>

        <script>
            function simulateAIAutoFill() {
                alert('IA Gemini ha riconosciuto il codice ISBN e compilato i dati bibliografici con successo!');
            }
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
    return HTMLResponse(f"<html><body style='background:#141414;color:#fff;text-align:center;padding-top:80px;font-family:sans-serif;'><h2>Annuncio per '{title}' pubblicato con successo!</h2><p>Il tuo libro è ora online nel marketplace.</p><a href='/' style='color:#00d2ff; text-decoration:none; font-weight:bold;'>← Torna alla Home</a></body></html>")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
