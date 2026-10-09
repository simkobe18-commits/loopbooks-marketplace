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

class LibraryItem(BaseModel):
    id: int
    title: str
    image_url: str
    condition: str
    price: float
    type: str # Comprati / Venduti / In Magazzino / Preferiti
    genre: str
    isbn: str

fake_library_db = [
    LibraryItem(id=1, title="Il monastero dei segreti", image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80", condition="Ottime", price=14.50, type="In Magazzino", genre="Gialli/Thriller/Noir", isbn="9788804712345"),
    LibraryItem(id=2, title="Python per Intelligenza Artificiale", image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80", condition="Nuovo", price=28.00, type="Comprati", genre="Scienze/Tecnologia/Natura", isbn="9788803987654"),
    LibraryItem(id=3, title="I Promessi Sposi", image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80", condition="Buone", price=10.00, type="Venduti", genre="Classici", isbn="9788801234567"),
    LibraryItem(id=4, title="Il Potere dell'Abitudine", image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80", condition="Nuovo", price=19.90, type="Preferiti", genre="Crescita Personale", isbn="9788803334445")
]

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
        sellers=[]
    ),
    Book(
        id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", 
        description="Il capolavoro della letteratura italiana.", 
        image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        sellers=[]
    ),
    Book(
        id=4, title="Il Potere dell'Abitudine", author="Charles Duhigg", genre="Crescita Personale", price=19.90, condition="Nuovo", isbn="9788803334445", 
        description="Come cambiare abitudini nella vita e nel lavoro.", 
        image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
        sellers=[]
    ),
    Book(
        id=5, title="Cucina Botanica", author="Carlotta Perego", genre="Cucina", price=22.00, condition="Nuovo", isbn="9788805556667", 
        description="Ricette vegetali semplici e gustose.", 
        image_url="https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=600&q=80",
        sellers=[]
    ),
    Book(
        id=6, title="Le Avventure di Oz", author="L. Frank Baum", genre="Young Adult", price=12.00, condition="Buone", isbn="9788807778889", 
        description="Un classico fantastico per ragazzi.", 
        image_url="https://images.unsplash.com/photo-1513001900722-370f803f498d?auto=format&fit=crop&w=600&q=80",
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
                        <optgroup label="Fumetti e Grafica">
                            <option value="Fumetti">Fumetti</option>
                            <option value="Manga">Manga</option>
                            <option value="Graphic Novel">Graphic Novel</option>
                            <option value="Libri illustrati">Libri illustrati</option>
                            <option value="Design">Design</option>
                        </optgroup>
                        <optgroup label="Bambini e Ragazzi / Young Adult">
                            <option value="Prima infanzia 0-3 anni">Prima infanzia 0-3 anni</option>
                            <option value="4-8 anni">4-8 anni</option>
                            <option value="9-13 anni">9-13 anni</option>
                            <option value="Young Adult">Young Adult 14+</option>
                        </optgroup>
                    </select>

                    <select id="price-filter">
                        <option value="">Prezzo (qualsiasi)</option>
                        <option value="15">Fino a 15 €</option>
                        <option value="25">Fino a 25 €</option>
                        <option value="50">Fino a 50 €</option>
                    </select>

                    <select id="condition-filter">
                        <option value="">Condizioni (qualsiasi)</option>
                        <option value="Nuovo">Nuovo</option>
                        <option value="Ottime">Ottime</option>
                        <option value="Buone">Buone</option>
                        <option value="Discrete">Discrete</option>
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

            <h2 class="section-title">Passioni, Hobby e Creatività</h2>
            <div class="carousel-container" id="hobby-carousel"></div>

            <h2 class="section-title">Bambini e Ragazzi (Young Adult)</h2>
            <div class="carousel-container" id="ya-carousel"></div>

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
                populate('narrative-carousel', books.filter(b => b.genre.includes('Gialli') || b.genre.includes('Romanzi')));
                populate('essays-carousel', books.filter(b => b.genre.includes('Scienze')));
                populate('lifestyle-carousel', books.filter(b => b.genre.includes('Crescita')));
                populate('hobby-carousel', books.filter(b => b.genre.includes('Cucina')));
                populate('ya-carousel', books.filter(b => b.genre.includes('Young Adult')));
            }

            function populate(elemId, list) {
                const container = document.getElementById(elemId);
                if(!container) return;
                container.innerHTML = '';
                if(list.length === 0) {
                    container.innerHTML = '<p style="color:#666; font-size:0.85rem;">Nessun libro trovato.</p>';
                    return;
                }
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
                const genre = document.getElementById('genre-filter').value;
                const maxPrice = parseFloat(document.getElementById('price-filter').value) || 9999;
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

# --- 2. PAGINA INFO LIBRO (DETTAGLIO PRODOTTO) ---
@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int):
    book = next((b for b in fake_books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Libro non trovato")
    
    sellers_html = ""
    if book.sellers:
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
    else:
        sellers_html = '<p style="color: #888;">Nessun venditore attivo per questo titolo al momento.</p>'

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
                    <p><b>Prezzo medio di vendita:</b> <span style="color:#00d2ff; font-weight:bold;">€ {book.price:.2f}</span></p>
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
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ labels: {{ color: '#fff' }} }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }},
                        y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }}
                    }}
                }}
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
            .search-tools {{ background: #1f1f1f; padding: 20px; border-radius: 8px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px; }}
            .search-tools input, .search-tools select {{ padding: 10px; background: #333; border: none; color: #fff; border-radius: 4px; }}
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
                    <h1 style="margin:0 0 5px 0;">{seller.name} <span style="font-size:1rem; color:#00d2ff;">{'✓ Verificato' if seller.verified else ''}</span></h1>
                    <p style="margin:0 0 10px 0; color:#aaa;">📍 {seller.location} | Libri venduti: <b>{seller.books_sold}</b> | Valutazione complessiva: ⭐ <b>{seller.total_rating}/5.0</b></p>
                </div>
            </div>

            <div class="search-tools">
                <input type="text" placeholder="Cerca libro per nome o ISBN...">
                <select><option value="">Tutti i generi</option></select>
                <select><option value="">Prezzo</option></select>
                <select><option value="">Condizioni</option></select>
            </div>

            <h2 style="color:#fff; margin-bottom:20px;">Catalogo del Venditore</h2>
            <div class="catalog-grid">{catalog_html}</div>

            <div style="margin-top: 50px; background:#1f1f1f; padding:25px; border-radius:8px;">
                <h3 style="margin-top:0;">Commenti e Recensioni</h3>
                <div>{comments_html}</div>
                <h4 style="margin-top:20px;">Scrivi il tuo commento</h4>
                <textarea placeholder="Scrivi la tua recensione..." style="width:100%; height:80px; background:#333; border:none; color:#fff; padding:10px; border-radius:4px; box-sizing:border-box;"></textarea>
                <button onclick="alert('Commento inviato!')" style="background:#e50914; color:#fff; border:none; padding:10px 20px; margin-top:10px; border-radius:4px; font-weight:bold; cursor:pointer;">Pubblica</button>
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
            .library-info h4 { margin: 0 0 5px 0; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; }
            .badge-magazzino { background: #00d2ff22; color: #00d2ff; }
            .badge-comprati { background: #28a74522; color: #28a745; }
            .badge-venduti { background: #ffc10722; color: #ffc107; }
            .badge-preferiti { background: #e5091422; color: #e50914; }
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
                <div class="kpi-card"><h3>Magazzino (Libri)</h3><p>1</p></div>
                <div class="kpi-card"><h3>Valore Magazzino</h3><p>€ 14.50</p></div>
            </div>

            <div class="charts-grid">
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Trend Portafoglio Temporale (Soldi / Mesi / Anni)</h3>
                    <canvas id="trendChart" height="110"></canvas>
                </div>
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Ripartizione Finanziaria</h3>
                    <canvas id="pieChart" height="135"></canvas>
                </div>
            </div>

            <div class="filter-bar">
                <input type="text" id="lib-search" placeholder="Cerca per nome o ISBN..." onkeyup="filterLibrary()">
                <select id="lib-genre" onchange="filterLibrary()">
                    <option value="">Tutti i Generi</option>
                    <option value="Gialli/Thriller/Noir">Gialli/Thriller/Noir</option>
                    <option value="Scienze/Tecnologia/Natura">Scienze/Tecnologia/Natura</option>
                    <option value="Classici">Classici</option>
                    <option value="Crescita Personale">Crescita Personale</option>
                </select>
                <select id="lib-cond" onchange="filterLibrary()">
                    <option value="">Condizioni (Tutte)</option>
                    <option value="Nuovo">Nuovo</option>
                    <option value="Ottime">Ottime</option>
                    <option value="Buone">Buone</option>
                </select>
                <select id="lib-price" onchange="filterLibrary()">
                    <option value="">Prezzo Modulabile</option>
                    <option value="15">Fino a 15 €</option>
                    <option value="30">Fino a 30 €</option>
                </select>
                <select id="lib-type" onchange="filterLibrary()">
                    <option value="">Tipologia (Tutte)</option>
                    <option value="Comprati">Comprati</option>
                    <option value="Venduti">Venduti</option>
                    <option value="In Magazzino">In Magazzino</option>
                    <option value="Preferiti">Preferiti</option>
                </select>
            </div>

            <h2 style="color:#fff; margin-bottom:20px;">Catalogo Personale (<span id="lib-count">4</span>)</h2>
            <div class="library-grid" id="library-grid"></div>
        </div>

        <script>
            const libraryItems = [
                {id: 1, title: "Il monastero dei segreti", image: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80", condition: "Ottime", price: 14.50, type: "In Magazzino", genre: "Gialli/Thriller/Noir", isbn: "9788804712345"},
                {id: 2, title: "Python per Intelligenza Artificiale", image: "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80", condition: "Nuovo", price: 28.00, type: "Comprati", genre: "Scienze/Tecnologia/Natura", isbn: "9788803987654"},
                {id: 3, title: "I Promessi Sposi", image: "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80", condition: "Buone", price: 10.00, type: "Venduti", genre: "Classici", isbn: "9788801234567"},
                {id: 4, title: "Il Potere dell'Abitudine", image: "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80", condition: "Nuovo", price: 19.90, type: "Preferiti", genre: "Crescita Personale", isbn: "9788803334445"}
            ];

            function renderLibrary(items) {
                const grid = document.getElementById('library-grid');
                document.getElementById('lib-count').innerText = items.length;
                grid.innerHTML = '';
                if(items.length === 0) {
                    grid.innerHTML = '<p style="color:#888;">Nessun libro corrisponde ai criteri di ricerca.</p>';
                    return;
                }
                items.forEach(item => {
                    let badgeClass = 'badge-magazzino';
                    if(item.type === 'Comprati') badgeClass = 'badge-comprati';
                    if(item.type === 'Venduti') badgeClass = 'badge-venduti';
                    if(item.type === 'Preferiti') badgeClass = 'badge-preferiti';

                    grid.innerHTML += `
                        <a href="/book/${item.id}" class="library-card">
                            <img src="${item.image}" alt="${item.title}">
                            <div class="library-info">
                                <span class="badge ${badgeClass}">${item.type}</span>
                                <h4>${item.title}</h4>
                                <p style="margin:0; font-size:0.8rem; color:#888;">Condizioni: ${item.condition}</p>
                                <div class="price">€ ${item.price.toFixed(2)}</div>
                            </div>
                        </a>
                    `;
                });
            }

            function filterLibrary() {
                const query = document.getElementById('lib-search').value.toLowerCase();
                const genre = document.getElementById('lib-genre').value;
                const cond = document.getElementById('lib-cond').value;
                const maxPrice = parseFloat(document.getElementById('lib-price').value) || 9999;
                const type = document.getElementById('lib-type').value;

                const filtered = libraryItems.filter(item => {
                    const matchText = item.title.toLowerCase().includes(query) || item.isbn.includes(query);
                    const matchGenre = !genre || item.genre === genre;
                    const matchCond = !cond || item.condition === cond;
                    const matchPrice = item.price <= maxPrice;
                    const matchType = !type || item.type === type;
                    return matchText && matchGenre && matchCond && matchPrice && matchType;
                });
                renderLibrary(filtered);
            }

            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['Gen 2025', 'Lug 2025', 'Gen 2026', 'Mag 2026', 'Ott 2026'],
                    datasets: [{
                        label: 'Patrimonio Netto (€)',
                        data: [30, 50, 75, 110, 142.5],
                        borderColor: '#00d2ff',
                        backgroundColor: 'rgba(0, 210, 255, 0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: { responsive: true, plugins: { legend: { labels: { color: '#fff' } } }, scales: { x: { ticks: { color: '#888' }, grid: { color: '#333' } }, y: { ticks: { color: '#888' }, grid: { color: '#333' } } } }
            });

            const ctxPie = document.getElementById('pieChart').getContext('2d');
            new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: ['Guadagno Totale', 'Spese Totali', 'Magazzino Totale'],
                    datasets: [{
                        data: [10.0, 28.0, 14.5],
                        backgroundColor: ['#28a745', '#e50914', '#00d2ff']
                    }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#fff', boxWidth: 12 } } } }
            });

            renderLibrary(libraryItems);
        </script>
    </body>
    </html>
    """

# --- 5. METTI IN VENDITA ---
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
            .form-container { max-width: 600px; margin: auto; background: #1f1f1f; padding: 30px; border-radius: 8px; border: 1px solid #333; }
            input, select, textarea { width: 100%; padding: 10px; margin: 10px 0 20px 0; background: #333; border: none; color: #fff; border-radius: 4px; box-sizing: border-box; }
            button { background: #e50914; color: white; padding: 12px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>Metti in Vendita (Flusso Guidato IA)</h2>
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

                <button type="submit">Conferma e Pubblica Annuncio</button>
            </form>
            <p><a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/api/sell")
def post_sell(isbn: str = Form(...), price: float = Form(...)):
    return HTMLResponse("<html><body style='background:#141414;color:#fff;text-align:center;padding-top:50px;'><h2>Annuncio pubblicato con successo!</h2><a href='/' style='color:#00d2ff;'>Torna alla Home</a></body></html>")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
