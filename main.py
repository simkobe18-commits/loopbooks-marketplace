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

# Database profili venditori dettagliati
fake_sellers_db = [
    SellerProfile(
        seller_id=101,
        name="Libreria Del Borgo",
        location="Milano",
        photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        verified=True,
        books_sold=142,
        total_rating=4.8,
        comments=["Spedizione velocissima e imballaggio perfetto!", "Libro in condizioni persino migliori del descritto."],
        catalog=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"),
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=9.50, book_image="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80")
        ]
    )
]

fake_books_db = [
    Book(
        id=1, title="Il monastero dei segreti", author="Anonimo", genre="Gialli/Thriller/Noir", price=14.50, condition="Ottime", isbn="9788804712345", 
        description="Un monastero isolato tra le nebbie, un antico manoscritto e un delitto inspiegabile.", 
        image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=13.50, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"),
            SellerOffer(seller_id=102, seller_name="BookLovers Store", location="Bologna", rating=4.5, condition="Buone", price=11.00, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")
        ]
    ),
    Book(
        id=2, title="Python per Intelligenza Artificiale", author="Mario Rossi", genre="Scienze/Tecnologia/Natura", price=28.00, condition="Nuovo", isbn="9788803987654", 
        description="Guida avanzata allo sviluppo di modelli intelligenti con FastAPI e Python.", 
        image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=103, seller_name="TechBooks Italia", location="Roma", rating=4.9, condition="Nuovo", price=28.00, book_image="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80")
        ]
    ),
    Book(
        id=3, title="I Promessi Sposi", author="Alessandro Manzoni", genre="Classici", price=10.00, condition="Buone", isbn="9788801234567", 
        description="Il capolavoro della letteratura italiana.", 
        image_url="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
        sellers=[
            SellerOffer(seller_id=101, seller_name="Libreria Del Borgo", location="Milano", rating=4.8, condition="Ottime", price=9.50, book_image="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80")
        ]
    )
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
            .profile-icon { width: 36px; height: 36px; background: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; cursor: pointer; }
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
            <h2 class="section-title">Catalogo Principale (Tutti i Libri)</h2>
            <div class="carousel-container" id="trending-carousel"></div>
        </div>

        <script>
            async function loadHome() {
                const res = await fetch('/api/books');
                const books = await res.json();
                const container = document.getElementById('trending-carousel');
                container.innerHTML = '';
                books.forEach(b => {
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

@app.get("/api/books", response_model=List[Book])
def get_books():
    return fake_books_db

# --- PAGINA INFO LIBRO ---
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

            <h3 style="color:#fff; margin-bottom: 15px;">Tutti i venditori per questo libro</h3>
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

# --- PAGINA DEL VENDITORE COMPLETA ---
@app.get("/seller/{seller_id}", response_class=HTMLResponse)
def seller_profile(seller_id: int):
    seller = next((s for s in fake_sellers_db if s.seller_id == seller_id), None)
    if not seller:
        # Profilo di default simulato se non trovato esplicitamente
        seller = SellerProfile(
            seller_id=seller_id,
            name=f"Venditore Ufficiale #{seller_id}",
            location="Roma, Italia",
            photo_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=80",
            verified=True,
            books_sold=89,
            total_rating=4.9,
            comments=["Ottimo venditore, consigliato a tutti!", "Puntuale e preciso."],
            catalog=[
                SellerOffer(seller_id=seller_id, seller_name=f"Venditore #{seller_id}", location="Roma", rating=4.9, condition="Nuovo", price=16.00, book_image="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80")
            ]
        )

    comments_html = "".join([f"<p style='background:#2a2a2a; padding:10px; border-radius:4px; margin:8px 0;'>💬 {c}</p>" for c in seller.comments])
    catalog_html = ""
    for item in seller.catalog:
        catalog_html += f"""
        <div style="background:#1f1f1f; border-radius:8px; overflow:hidden; display:flex; flex-direction:column; justify-content:space-between;">
            <img src="{item.book_image}" style="width:100%; height:200px; object-fit:cover;">
            <div style="padding:15px;">
                <h4 style="margin:0 0 5px 0;">Offerta Condizione: {item.condition}</h4>
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
            <!-- Header Profilo -->
            <div class="profile-header">
                <img src="{seller.photo_url}" class="profile-avatar">
                <div>
                    <h1 style="margin:0 0 5px 0;">{seller.name} <span style="font-size:1rem; color:#00d2ff;">{'✓ Verificato' if seller.verified else ''}</span></h1>
                    <p style="margin:0 0 10px 0; color:#aaa;">📍 {seller.location} | Libri venduti: <b>{seller.books_sold}</b> | Valutazione complessiva: ⭐ <b>{seller.total_rating}/5.0</b></p>
                </div>
            </div>

            <!-- Strumenti di ricerca interna -->
            <div class="search-tools">
                <input type="text" placeholder="Cerca libro per nome o ISBN...">
                <select>
                    <option value="">Tutti i generi</option>
                    <option value="gialli">Gialli / Thriller</option>
                    <option value="narrativa">Narrativa</option>
                </select>
                <select>
                    <option value="">Prezzo (qualsiasi)</option>
                    <option value="10">Fino a 10 €</option>
                    <option value="20">Fino a 20 €</option>
                </select>
                <select>
                    <option value="">Condizioni</option>
                    <option value="nuovo">Nuovo</option>
                    <option value="ottime">Ottime</option>
                </select>
            </div>

            <!-- Catalogo del Venditore -->
            <h2 style="color:#fff; margin-bottom:20px;">Catalogo del Venditore</h2>
            <div class="catalog-grid">
                {catalog_html}
            </div>

            <!-- Sezione Commenti e Recensioni -->
            <div style="margin-top: 50px; background:#1f1f1f; padding:25px; border-radius:8px;">
                <h3 style="margin-top:0;">Commenti e Recensioni</h3>
                <div>{comments_html}</div>
                <h4 style="margin-top:20px;">Scrivi il tuo commento</h4>
                <textarea placeholder="Condividi la tua esperienza con questo venditore..." style="width:100%; height:80px; background:#333; border:none; color:#fff; padding:10px; border-radius:4px; box-sizing:border-box;"></textarea>
                <button onclick="alert('Commento pubblicato con successo!')" style="background:#e50914; color:#fff; border:none; padding:10px 20px; margin-top:10px; border-radius:4px; font-weight:bold; cursor:pointer;">Invia commento</button>
            </div>
        </div>
    </body>
    </html>
    """

# --- ALTRE ROUTINE (Vendita e Biblioteca) ---
@app.get("/sell", response_class=HTMLResponse)
def sell_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head><meta charset="UTF-8"><title>Metti in Vendita - Loopbooks</title></head>
    <body style="background:#141414;color:#fff;font-family:sans-serif;padding:40px;">
        <div style="max-width:600px;margin:auto;background:#1f1f1f;padding:30px;border-radius:8px;">
            <h2>Metti in Vendita</h2>
            <form action="/api/sell" method="POST">
                <label>Codice ISBN:</label><br><input type="text" name="isbn" style="width:100%;padding:10px;margin:10px 0;background:#333;border:none;color:#fff;" required><br>
                <label>Prezzo (€):</label><br><input type="number" step="0.01" name="price" style="width:100%;padding:10px;margin:10px 0;background:#333;border:none;color:#fff;" required><br>
                <button type="submit" style="background:#e50914;color:#fff;padding:10px 20px;border:none;width:100%;font-weight:bold;cursor:pointer;">Pubblica</button>
            </form>
            <p><a href="/" style="color:#aaa;">← Home</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/api/sell")
def post_sell(isbn: str = Form(...), price: float = Form(...)):
    return HTMLResponse("<html><body style='background:#141414;color:#fff;text-align:center;padding-top:50px;'><h2>Inserito con successo!</h2><a href='/' style='color:#00d2ff;'>Home</a></body></html>")

@app.get("/library", response_class=HTMLResponse)
def library_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head><meta charset="UTF-8"><title>La Mia Biblioteca</title></head>
    <body style="background:#141414;color:#fff;font-family:sans-serif;padding:40px;">
        <div style="max-width:800px;margin:auto;background:#1f1f1f;padding:30px;border-radius:8px;">
            <h2>La Mia Biblioteca (Dashboard)</h2>
            <p>Magazzino libri: <b>2</b> | Guadagno netto: <b>€ 42.50</b></p>
            <p><a href="/" style="color:#aaa;">← Home</a></p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
