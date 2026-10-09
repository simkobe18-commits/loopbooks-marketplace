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

fake_books_db = [
    Book(id=1, title="Il monastero dei segreti", author="Anonimo", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", description="Un monastero isolato...", image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"),
    Book(id=2, title="Python per Intelligenza Artificiale", author="Mario Rossi", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", description="Guida avanzata...", image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"),
    Book(id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", description="Il capolavoro italiano.", image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80"),
    Book(id=4, title="Il Potere dell'Abitudine", author="Charles Duhigg", genre="Crescita Personale", price=19.90, condition="Nuovo", isbn="9788803334445", description="Come cambiare abitudini.", image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80")
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
            :root { --bg-color: #141414; --card-bg: #1f1f1f; --text-color: #e5e5e5; --accent-color: #e50914; --blue-glow: #00d2ff; }
            body { margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-color); color: var(--text-color); }
            header { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(0,0,0,0.9); position: fixed; top: 0; width: 100%; box-sizing: border-box; z-index: 1000; }
            .logo-area { font-size: 1.5rem; font-weight: 700; color: #fff; text-decoration: none; }
            .nav-center { display: flex; gap: 30px; align-items: center; }
            .nav-center a { color: var(--text-color); text-decoration: none; font-weight: 600; font-size: 0.9rem; }
            .container { padding: 120px 50px 60px 50px; max-width: 1200px; margin: auto; text-align: center; }
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo-area">📖 Loopbooks</a>
            <div class="nav-center">
                <a href="/sell">METTI IN VENDITA</a>
                <a href="/library">LA MIA BIBLIOTECA</a>
            </div>
            <a href="/library" style="background:#e50914; color:#fff; padding:8px 16px; border-radius:4px; text-decoration:none; font-weight:600;">Dashboard</a>
        </header>
        <div class="container">
            <h1>Benvenuto su Loopbooks Marketplace</h1>
            <p style="color:#aaa;">Accedi a <a href="/library" style="color:#00d2ff; text-decoration:none; font-weight:bold;">La Mia Biblioteca</a> per visualizzare le tue metriche, KPI e la gestione del magazzino.</p>
        </div>
    </body>
    </html>
    """

# --- SEZIONE "LA MIA BIBLIOTECA" (DASHBOARD UTENTE) ---
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
            
            /* Metriche e KPI */
            .kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin-bottom: 30px; }
            .kpi-card { background: #1f1f1f; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; }
            .kpi-card h3 { margin: 0; color: #888; font-size: 0.75rem; text-transform: uppercase; }
            .kpi-card p { font-size: 1.2rem; font-weight: bold; margin: 8px 0 0 0; color: #00d2ff; }

            /* Grafici */
            .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 40px; }
            .chart-box { background: #1f1f1f; padding: 20px; border-radius: 8px; border: 1px solid #333; }
            
            /* Strumenti di Ricerca e Filtri */
            .filter-bar { background: #1f1f1f; padding: 20px; border-radius: 8px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px; border: 1px solid #333; }
            .filter-bar input, .filter-bar select { padding: 10px; background: #333; border: none; color: #fff; border-radius: 4px; font-family: inherit; }

            /* Elenco Libri */
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

            <!-- Riepilogo Metriche e KPI -->
            <div class="kpi-grid">
                <div class="kpi-card"><h3>Libri Venduti</h3><p>1</p></div>
                <div class="kpi-card"><h3>Guadagno Netto</h3><p>€ 10.00</p></div>
                <div class="kpi-card"><h3>Libri Comprati</h3><p>1</p></div>
                <div class="kpi-card"><h3>Totale Comprato</h3><p>€ 28.00</p></div>
                <div class="kpi-card"><h3>Magazzino (Libri)</h3><p>1</p></div>
                <div class="kpi-card"><h3>Valore Magazzino</h3><p>€ 14.50</p></div>
            </div>

            <!-- Grafici e Analitiche -->
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

            <!-- Gestione e Ricerca -->
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

            <!-- Elenco Libri in Biblioteca -->
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

            // Trend Portafoglio Temporale (Chart.js Line)
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

            // Grafico a Torta Ripartizione (Chart.js Doughnut)
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

@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int):
    book = next((b for b in fake_books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Libro non trovato")
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="it">
    <head><meta charset="UTF-8"><title>{book.title} - Info Libro</title></head>
    <body style="background:#141414;color:#fff;font-family:sans-serif;padding:50px;text-align:center;">
        <h1>{book.title}</h1>
        <p>Autore: <b>{book.author}</b> | Prezzo medio: € {book.price:.2f}</p>
        <p>{book.description}</p>
        <p><a href="/library" style="color:#00d2ff; text-decoration:none;">← Torna alla Biblioteca</a></p>
    </body>
    </html>
    """)

@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="it">
    <head><meta charset="UTF-8"><title>Metti in Vendita</title></head>
    <body style="background:#141414;color:#fff;font-family:sans-serif;padding:50px;text-align:center;">
        <h2>Flusso Metti in Vendita</h2>
        <p><a href="/library" style="color:#00d2ff; text-decoration:none;">← Torna alla Biblioteca</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
