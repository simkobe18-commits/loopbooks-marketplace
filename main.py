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
        seller_id=101, name="Libreria Del Borgo", location="Milano",
        photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        verified=True, books_sold=142, total_rating=4.8,
        comments=["Spedizione velocissima!", "Condizioni perfette."],
        catalog=[SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]
    )
]

fake_books_db = [
    Book(id=1, title="Il monastero dei segreti", author="Anonimo", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", description="Un monastero isolato...", image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80", sellers=[SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")]),
    Book(id=2, title="Python per Intelligenza Artificiale", author="Mario Rossi", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", description="Guida avanzata...", image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"),
    Book(id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", description="Il capolavoro italiano.", image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80")
]

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
            :root { --bg-color: #141414; --card-bg: #1f1f1f; --text-color: #e5e5e5; --accent-color: #e50914; --accent-hover: #b20710; --blue-glow: #00d2ff; }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-color); color: var(--text-color); }
            header { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0)); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }
            .logo-area { display: flex; align-items: center; gap: 10px; font-size: 1.5rem; font-weight: 700; color: #fff; text-decoration: none; }
            .nav-center { display: flex; gap: 30px; align-items: center; }
            .nav-center a { color: var(--text-color); text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: color 0.3s; }
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
                        <option value="Gialli/Thriller/Noir">Gialli/Thriller/Noir</option>
                        <option value="Scienze/Tecnologia/Natura">Scienze/Tecnologia/Natura</option>
                        <option value="Classici">Classici</option>
                        <option value="Crescita Personale">Crescita Personale</option>
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

            <h2 class="section-title">Grandi classici</h2>
            <div class="carousel-container" id="classics-carousel"></div>

            <div class="merch-section">
                <div>
                    <h3>📦 Oggettistica per Consegne e Packaging</h3>
                    <p style="color: #aaa; margin: 5px 0 0 0; font-size: 0.9rem;">Scopri scatole protettive e buste imbottite.</p>
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

# --- LA MIA BIBLIOTECA (DASHBOARD UTENTE COMPLETA) ---
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
            header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
            
            /* KPI Metrics Grid */
            .kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin-bottom: 30px; }
            .kpi-card { background: #1f1f1f; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; }
            .kpi-card h3 { margin: 0; color: #888; font-size: 0.75rem; text-transform: uppercase; }
            .kpi-card p { font-size: 1.2rem; font-weight: bold; margin: 8px 0 0 0; color: #00d2ff; }

            /* Charts Section */
            .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 40px; }
            .chart-box { background: #1f1f1f; padding: 20px; border-radius: 8px; border: 1px solid #333; }
            
            /* Search and Filters */
            .filter-bar { background: #1f1f1f; padding: 20px; border-radius: 8px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px; border: 1px solid #333; }
            .filter-bar input, .filter-bar select { padding: 10px; background: #333; border: none; color: #fff; border-radius: 4px; }

            /* Catalog Grid */
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
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <a href="/" style="color:#fff; text-decoration:none; font-weight:700; font-size:1.5rem;">📖 Loopbooks - Dashboard Utente</a>
                <a href="/" style="color: #aaa; text-decoration: none;">← Torna alla Home</a>
            </header>

            <!-- Riepilogo Metriche e KPI -->
            <div class="kpi-grid">
                <div class="kpi-card"><h3>Libri Venduti</h3><p id="kpi-venduti">1</p></div>
                <div class="kpi-card"><h3>Guadagno Netto</h3><p id="kpi-guadagno">€ 10.00</p></div>
                <div class="kpi-card"><h3>Libri Comprati</h3><p id="kpi-comprati">1</p></div>
                <div class="kpi-card"><h3>Totale Comprato</h3><p id="kpi-speso">€ 28.00</p></div>
                <div class="kpi-card"><h3>Magazzino (Libri)</h3><p id="kpi-magazzino">1</p></div>
                <div class="kpi-card"><h3>Valore Magazzino</h3><p id="kpi-valore">€ 14.50</p></div>
            </div>

            <!-- Grafici e Analitiche -->
            <div class="charts-grid">
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Trend Portafoglio Temporale (Soldi / Mesi)</h3>
                    <canvas id="trendChart" height="110"></canvas>
                </div>
                <div class="chart-box">
                    <h3 style="margin-top:0; font-size:1rem;">Ripartizione Finanziaria</h3>
                    <canvas id="pieChart" height="135"></canvas>
                </div>
            </div>

            <!-- Gestione e Ricerca Interna -->
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
                    <option value="">Condizioni</option>
                    <option value="Nuovo">Nuovo</option>
                    <option value="Ottime">Ottime</option>
                    <option value="Buone">Buone</option>
                </select>
                <select id="lib-price" onchange="filterLibrary()">
                    <option value="">Prezzo</option>
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

            <!-- Elenco Libri in Biblioteca -->
            <h2 style="color:#fff; margin-bottom:20px;">I tuoi libri (<span id="lib-count">4</span>)</h2>
            <div class="library-grid" id="library-grid">
                <!-- Popolato via JS -->
            </div>
        </div>

        <script>
            const libraryData = [
                {id: 1, title: "Il monastero dei segreti", image: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80", condition: "Ottime", price: 14.50, type: "In Magazzino", genre: "Gialli/Thriller/Noir", isbn: "9788804712345"},
                {id: 2, title: "Python per IA", image: "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80", condition: "Nuovo", price: 28.00, type: "Comprati", genre: "Scienze/Tecnologia/Natura", isbn: "9788803987654"},
                {id: 3, title: "I Promessi Sposi", image: "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80", condition: "Buone", price: 10.00, type: "Venduti", genre: "Classici", isbn: "9788801234567"},
                {id: 4, title: "Il Potere dell'Abitudine", image: "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80", condition: "Nuovo", price: 19.90, type: "Preferiti", genre: "Crescita Personale", isbn: "9788803334445"}
            ];

            function renderLibrary(items) {
                const grid = document.getElementById('library-grid');
                document.getElementById('lib-count').innerText = items.length;
                grid.innerHTML = '';
                if(items.length === 0) {
                    grid.innerHTML = '<p style="color:#888;">Nessun libro trovato con i filtri selezionati.</p>';
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

                const filtered = libraryData.filter(item => {
                    const matchText = item.title.toLowerCase().includes(query) || item.isbn.includes(query);
                    const matchGenre = !genre || item.genre === genre;
                    const matchCond = !cond || item.condition === cond;
                    const matchPrice = item.price <= maxPrice;
                    const matchType = !type || item.type === type;
                    return matchText && matchGenre && matchCond && matchPrice && matchType;
                });
                renderLibrary(filtered);
            }

            // Inizializzazione Grafici Chart.js
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
                    datasets: [{
                        label: 'Capitale / Valore (€)',
                        data: [40, 55, 70, 95, 120, 142.5],
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

            renderLibrary(libraryData);
        </script>
    </body>
    </html>
    """

# --- FLUSSO METTI IN VENDITA ---
@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head><meta charset="UTF-8"><title>Metti in Vendita - Loopbooks</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Plus Jakarta Sans', sans-serif; background: #141414; color: #fff; padding: 40px; }</style>
    </head>
    <body>
        <div style="max-width:600px; margin:auto; background:#1f1f1f; padding:30px; border-radius:8px;">
            <h2>Metti in Vendita (Flusso IA)</h2>
            <form action="/api/sell" method="POST">
                <label>Codice ISBN:</label><br><input type="text" name="isbn" style="width:100%; padding:10px; margin:10px 0; background:#333; border:none; color:#fff;" required><br>
                <label>Prezzo (€):</label><br><input type="number" step="0.01" name="price" style="width:100%; padding:10px; margin:10px 0; background:#333; border:none; color:#fff;" required><br>
                <button type="submit" style="background:#e50914; color:#fff; padding:12px; border:none; width:100%; font-weight:bold; cursor:pointer;">Conferma</button>
            </form>
            <p><a href="/" style="color:#aaa; text-decoration:none;">← Torna alla Home</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/api/sell")
def post_sell(isbn: str = Form(...), price: float = Form(...)):
    return HTMLResponse("<html><body style='background:#141414;color:#fff;text-align:center;padding-top:50px;'><h2>Annuncio pubblicato con successo!</h2><a href='/' style='color:#00d2ff;'>Torna alla Home</a></body></html>")

@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int):
    return HTMLResponse(f"<html><body style='background:#141414;color:#fff;text-align:center;padding-top:50px;'><h2>Scheda Info Libro #{book_id}</h2><a href='/' style='color:#00d2ff;'>← Torna alla Home</a></body></html>")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
