import os
import sqlite3
import requests
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="LoopBooks")

# Configurazione Database SQLite locale
DB_FILE = "loopbooks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabella Utenti
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            saldo REAL DEFAULT 0.0
        )
    """)
    
    # Tabella Libri (Catalogo Globale)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ean_isbn TEXT UNIQUE,
            titolo TEXT,
            immagine_copertina_url TEXT,
            genere TEXT,
            editore TEXT,
            collana TEXT,
            anno_edizione INTEGER,
            descrizione TEXT
        )
    """)
    
    # Tabella Offerte di Vendita
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offerte_vendita (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER,
            venditore_id INTEGER,
            prezzo_richiesto REAL,
            commissione_piattaforma REAL,
            guadagno_netto REAL,
            condizioni TEXT,
            modalita_consegna TEXT,
            foto_reale_url TEXT,
            stato TEXT DEFAULT 'attiva',
            FOREIGN KEY(libro_id) REFERENCES libri(id),
            FOREIGN KEY(venditore_id) REFERENCES utenti(id)
        )
    """)
    
    # Tabella Materiali di Spedizione
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiali_spedizione (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descrizione TEXT,
            prezzo REAL,
            immagine_url TEXT
        )
    """)
    
    # Tabella Preferiti
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferiti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utente_id INTEGER,
            libro_id INTEGER,
            FOREIGN KEY(libro_id) REFERENCES libri(id)
        )
    """)
    
    # Tabella Transazioni (Acquisti)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offerta_id INTEGER,
            compratore_id INTEGER,
            prezzo_pagato REAL,
            data_transazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(offerta_id) REFERENCES offerte_vendita(id)
        )
    """)
    
    # Inseriamo un utente di test e materiali di spedizione predefiniti se vuoti
    cursor.execute("SELECT COUNT(*) FROM utenti")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO utenti (nome, email, saldo) VALUES ('Simone', 'simone@loopbooks.it', 50.0)")
        
    cursor.execute("SELECT COUNT(*) FROM materiali_spedizione")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO materiali_spedizione (nome, descrizione, prezzo, immagine_url) VALUES (?, ?, ?, ?)",
                       ("Busta Imbottita Protettiva", "Busta in carta Kraft con pluriball interno per spedizioni sicure.", 1.50, "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=400&auto=format&fit=crop"))
        cursor.execute("INSERT INTO materiali_spedizione (nome, descrizione, prezzo, immagine_url) VALUES (?, ?, ?, ?)",
                       ("Scatola Cartonata per Libri", "Scatola rigida anti-urto su misura per volumi di ogni formato.", 2.80, "https://images.unsplash.com/photo-1607344645866-009c320c5ab8?q=80&w=400&auto=format&fit=crop"))
        cursor.execute("INSERT INTO materiali_spedizione (nome, descrizione, prezzo, immagine_url) VALUES (?, ?, ?, ?)",
                       ("Rotolo Pluriball 5mt", "Protezione extra per libri di pregio e collezioni.", 4.00, "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=400&auto=format&fit=crop"))

    conn.commit()
    conn.close()

init_db()

# Funzione per recuperare o scaricare i dati del libro tramite API Google Books usando l'ISBN
def fetch_or_create_book_by_isbn(isbn: str):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    isbn_clean = isbn.strip().replace("-", "")
    cursor.execute("SELECT * FROM libri WHERE ean_isbn = ?", (isbn_clean,))
    book = cursor.fetchone()
    
    if book:
        conn.close()
        return dict(book)
    
    # Fallback su Google Books API
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"
        res = requests.get(url).json()
        if "items" in res:
            volume_info = res["items"][0]["volumeInfo"]
            titolo = volume_info.get("title", "Titolo non disponibile")
            editore = volume_info.get("editore", volume_info.get("publisher", "Editore Sconosciuto"))
            descrizione = volume_info.get("description", "Nessuna descrizione disponibile.")
            anno = int(volume_info.get("publishedDate", "2020")[:4])
            categories = volume_info.get("categories", ["Narrativa"])
            genere = categories[0] if categories else "Narrativa"
            
            images = volume_info.get("imageLinks", {})
            img_url = images.get("thumbnail", images.get("smallThumbnail", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=400&auto=format&fit=crop"))
            # Sostituisci http con https per evitare problemi di sicurezza
            img_url = img_url.replace("http://", "https://")
            
            cursor.execute("""
                INSERT INTO libri (ean_isbn, titolo, immagine_copertina_url, genere, editore, collana, anno_edizione, descrizione)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (isbn_clean, titolo, img_url, genere, editore, "Collana Standard", anno, descrizione))
            conn.commit()
            
            cursor.execute("SELECT * FROM libri WHERE ean_isbn = ?", (isbn_clean,))
            book = cursor.fetchone()
            conn.close()
            return dict(book)
    except Exception as e:
        print(f"Errore API Google Books: {e}")
        
    conn.close()
    return None

# HTML Frontend Integrato con Design Cinematografico / Dark Mode Responsive
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LoopBooks - Marketplace Globale Libri</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #0a0c10;
            --bg-card: #141822;
            --accent: #e50914;
            --accent-hover: #b20710;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #222836;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg-base); color: var(--text-main); overflow-x: hidden; }

        /* HEADER */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 5%;
            background: rgba(10, 12, 16, 0.92);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--border);
        }
        .logo { font-size: 1.6rem; font-weight: 700; color: #fff; text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .logo span { color: var(--accent); }
        nav { display: flex; gap: 30px; }
        nav a { color: var(--text-muted); text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s; }
        nav a:hover, nav a.active { color: #fff; }
        .user-badge { background: var(--bg-card); border: 1px solid var(--border); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; }

        /* HERO CINEMATOGRAFICA */
        .hero {
            position: relative;
            min-height: 65vh;
            background: linear-gradient(to bottom, rgba(10,12,16,0.2), var(--bg-base)), 
                        url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=1600&auto=format&fit=crop') no-repeat center center/cover;
            display: flex;
            align-items: center;
            padding: 50px 5%;
        }
        .hero-inner { max-width: 650px; }
        .hero h1 { font-size: 3rem; font-weight: 700; line-height: 1.1; margin-bottom: 20px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }
        .hero p { font-size: 1.15rem; color: #d1d5db; margin-bottom: 30px; line-height: 1.5; }

        /* BARRA RICERCA & FILTRI */
        .search-filter-bar {
            padding: 25px 5%;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: space-between;
        }
        .search-form { display: flex; gap: 10px; flex: 1; min-width: 280px; }
        .search-form input {
            flex: 1; padding: 12px 18px; background: var(--bg-base); border: 1px solid var(--border);
            border-radius: 8px; color: #fff; font-size: 0.95rem; outline: none;
        }
        .btn-primary {
            background: var(--accent); color: #fff; border: none; padding: 12px 24px; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: background 0.2s;
        }
        .btn-primary:hover { background: var(--accent-hover); }

        .filters-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .filters-group select {
            padding: 12px 15px; background: var(--bg-base); border: 1px solid var(--border);
            border-radius: 8px; color: #fff; cursor: pointer; outline: none;
        }

        /* SEZIONI E GRIGLIE */
        .container { padding: 40px 5%; }
        .section-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; }
        
        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }
        .book-card {
            background: var(--bg-card); border-radius: 12px; overflow: hidden;
            border: 1px solid var(--border); transition: transform 0.3s, box-shadow 0.3s;
            display: flex; flex-direction: column; text-decoration: none; color: inherit;
        }
        .book-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 30px rgba(229, 9, 20, 0.2);
            border-color: var(--accent);
        }
        .book-img { height: 260px; background-size: cover; background-position: center; background-color: #1f2430; }
        .book-details { padding: 15px; display: flex; flex-direction: column; gap: 6px; flex: 1; }
        .book-title { font-size: 1rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .book-genre { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .book-price-tag { font-size: 0.95rem; font-weight: 700; color: var(--accent); margin-top: auto; }

        /* MATERIALI SPEDIZIONE */
        .materials-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }
        .material-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px;
            display: flex; flex-direction: column; gap: 12px;
        }
        .material-img { height: 140px; background-size: cover; background-position: center; border-radius: 8px; }

        /* FORM VENDITA / CALCOLATORE */
        .form-container {
            max-width: 600px; margin: 40px auto; background: var(--bg-card); padding: 35px;
            border-radius: 16px; border: 1px solid var(--border);
        }
        .form-group { margin-bottom: 20px; display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-size: 0.9rem; font-weight: 600; color: var(--text-muted); }
        .form-group input, .form-group select, .form-group textarea {
            padding: 12px 15px; background: var(--bg-base); border: 1px solid var(--border);
            border-radius: 8px; color: #fff; font-size: 0.95rem; outline: none;
        }
        .net-calc-box {
            background: rgba(229, 9, 20, 0.1); border: 1px dashed var(--accent); padding: 15px;
            border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
        }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            nav { display: none; }
            .hero h1 { font-size: 2.2rem; }
            .search-filter-bar { flex-direction: column; align-items: stretch; }
            .books-grid { grid-template-columns: repeat(2, 1fr); gap: 15px; }
        }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo">📖 Loop<span>books</span></a>
        <nav>
            <a href="/" class="active">Home</a>
            <a href="/vendi">Metti in Vendita</a>
            <a href="/biblioteca">La mia biblioteca</a>
            <a href="/materiali">Materiali Spedizione</a>
        </nav>
        <div class="user-badge">👤 Simone (50.00 €)</div>
    </header>

    {% if view == 'home' %}
    <section class="hero">
        <div class="hero-inner">
            <h1>Il mercato globale dei tuoi libri.</h1>
            <p>Cerca per ISBN o titolo, confronta i prezzi dell'usato in tempo reale e vendi i tuoi volumi trattenendo solo il 5% di commissione.</p>
            <form action="/" method="get" class="search-form" style="max-width: 450px;">
                <input type="text" name="q" placeholder="Cerca titolo o ISBN..." value="{{ search_query or '' }}">
                <button type="submit" class="btn-primary">Cerca</button>
            </form>
        </div>
    </section>

    <div class="search-filter-bar">
        <form action="/" method="get" style="display: flex; gap: 15px; width: 100%; flex-wrap: wrap;">
            <div class="search-form">
                <input type="text" name="q" placeholder="Inserisci ISBN o Titoloesatto..." value="{{ search_query or '' }}">
            </div>
            <div class="filters-group">
                <select name="genere" onchange="this.form.submit()">
                    <option value="">Tutti i Generi</option>
                    <option value="Narrativa" {% if genere == 'Narrativa' %}selected{% endif %}>Narrativa</option>
                    <option value="Thriller" {% if genere == 'Thriller' %}selected{% endif %}>Thriller & Gialli</option>
                    <option value="Scienza" {% if genere == 'Scienza' %}selected{% endif %}>Scienza & Tech</option>
                </select>
                <button type="submit" class="btn-primary">Filtra</button>
            </div>
        </form>
    </div>

    <div class="container">
        <div class="section-title">📚 Libri in Evidenza & Tendenza</div>
        <div class="books-grid">
            {% for libro in libri %}
            <a href="/libro/{{ libro.id }}" class="book-card">
                <div class="book-img" style="background-image: url('{{ libro.immagine_copertina_url }}');"></div>
                <div class="book-details">
                    <div class="book-genre">{{ libro.genere or 'Libro' }}</div>
                    <div class="book-title">{{ libro.titolo }}</div>
                    <div class="book-price-tag">Da € 5.00</div>
                </div>
            </a>
            {% endfor %}
        </div>

        <div class="section-title">📦 Materiali di Spedizione Consigliati</div>
        <div class="materials-grid">
            {% for mat in materiali %}
            <div class="material-card">
                <div class="material-img" style="background-image: url('{{ mat.immagine_url }}');"></div>
                <div style="font-weight: 600; font-size: 1.1rem;">{{ mat.nome }}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">{{ mat.descrizione }}</div>
                <div style="font-weight: 700; color: var(--accent); margin-top: auto;">€ {{ "%.2f"|format(mat.prezzo) }}</div>
                <button class="btn-primary" onclick="alert('Articolo aggiunto al carrello!')">Acquista Materiale</button>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    {% if view == 'vendi' %}
    <div class="container">
        <div class="form-container">
            <h2 style="margin-bottom: 20px;">Metti in Vendita un Libro</h2>
            <form action="/vendi" method="post">
                <div class="form-group">
                    <label>Codice ISBN (EAN)</label>
                    <input type="text" name="isbn" required placeholder="Es. 9788806246105">
                </div>
                <div class="form-group">
                    <label>Prezzo di Vendita (€)</label>
                    <input type="number" step="0.05" id="prezzo_input" name="prezzo" required placeholder="Es. 15.00" oninput="calcolaGuadagno()">
                </div>
                
                <div class="net-calc-box">
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Commissione Piattaforma (5%): <span id="commissione_val">0.00</span> €</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin-top: 4px;">Il tuo guadagno netto:</div>
                    </div>
                    <div style="font-size: 1.4rem; font-weight: 750; color: #22c55e;" id="netto_val">0.00 €</div>
                </div>

                <div class="form-group">
                    <label>Condizioni del libro</label>
                    <select name="condizioni">
                        <option value="Nuovo">Nuovo (Mai letto)</option>
                        <option value="Ottime">Ottime condizioni</option>
                        <option value="Buone">Buone condizioni</option>
                        <option value="Accettabile">Accettabile (Segni d'usura)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Modalità di Consegna</label>
                    <select name="consegna">
                        <option value="Spedizione tracciata">Spedizione tracciata</option>
                        <option value="Consegna a mano">Consegna a mano</option>
                        <option value="Entrambe">Entrambe</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>URL Foto Reale del Libro Usato</label>
                    <input type="text" name="foto_reale" placeholder="Incolla link immagine reale (es. Imgur o simile)">
                </div>
                <button type="submit" class="btn-primary" style="width: 100%; margin-top: 10px;">Conferma e Pubblica Offerta</button>
            </form>
        </div>
    </div>
    <script>
        function calcolaGuadagno() {
            let prezzo = parseFloat(document.getElementById('prezzo_input').value) || 0;
            let commissione = prezzo * 0.05;
            let netto = prezzo - commissione;
            document.getElementById('commissione_val').innerText = commissione.toFixed(2);
            document.getElementById('netto_val').innerText = netto.toFixed(2) + ' €';
        }
    </script>
    {% endif %}

    {% if view == 'dettaglio' %}
    <div class="container" style="max-width: 1000px;">
        <div style="display: flex; gap: 30px; flex-wrap: wrap; background: var(--bg-card); padding: 30px; border-radius: 16px; border: 1px solid var(--border);">
            <div style="width: 220px; height: 320px; background-size: cover; background-position: center; border-radius: 8px; background-image: url('{{ libro.immagine_copertina_url }}'); flex-shrink: 0;"></div>
            <div style="flex: 1; display: flex; flexDirection: column; gap: 12px;">
                <h1 style="font-size: 2rem;">{{ libro.titolo }}</h1>
                <p style="color: var(--text-muted); font-size: 0.95rem;">Editore: {{ libro.editore }} | Anno: {{ libro.anno_edizione }} | ISBN: {{ libro.ean_isbn }}</p>
                <p style="line-height: 1.6; font-size: 0.95rem; color: #d1d5db;">{{ libro.descrizione }}</p>
            </div>
        </div>

        <!-- Sezione Grafico Prezzi -->
        <div style="background: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid var(--border); margin-top: 30px;">
            <h3 style="margin-bottom: 15px;">Andamento Storico dei Prezzi</h3>
            <canvas id="priceChart" height="90"></canvas>
        </div>

        <!-- Lista Venditori -->
        <div style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px;">Venditori Disponibili per questo Libro</h3>
            {% if offerte %}
                <div style="display: flex; flexDirection: column; gap: 12px;">
                    {% for off in offerte %}
                    <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <div style="font-weight: 600; font-size: 1.05rem;">Condizioni: {{ off.condizioni }}</div>
                            <div style="font-size: 0.85rem; color: var(--text-muted);">Consegna: {{ off.modalita_consegna }} | Venditore ID: #{{ off.venditore_id }}</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div style="font-size: 1.4rem; font-weight: 700; color: var(--accent);">€ {{ "%.2f"|format(off.prezzo_richiesto) }}</div>
                            <button class="btn-primary" onclick="alert('Acquisto completato con successo!')">Acquista Ora</button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <p style="color: var(--text-muted);">Nessun venditore attivo per questo titolo. Sii il primo a metterlo in vendita!</p>
            {% endif %}
        </div>
    </div>
    <script>
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Ago', 'Set', 'Ott'],
                datasets: [{
                    label: 'Prezzo Medio Usato (€)',
                    data: [14, 13.5, 13, 12.5, 12, 11.5, 11, 10.5, 9.8],
                    borderColor: '#e50914',
                    backgroundColor: 'rgba(229, 9, 20, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    </script>
    {% endif %}

    {% if view == 'biblioteca' %}
    <div class="container">
        <h2 style="margin-bottom: 25px;">La Mia Biblioteca & Statistiche</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 40px;">
            <div style="background: var(--bg-card); padding: 25px; border-radius: 12px; border: 1px solid var(--border);">
                <div style="color: var(--text-muted); font-size: 0.9rem;">Spesa Totale</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-top: 5px;">€ 45.00</div>
            </div>
            <div style="background: var(--bg-card); padding: 25px; border-radius: 12px; border: 1px solid var(--border);">
                <div style="color: var(--text-muted); font-size: 0.9rem;">Guadagno Totale Netto</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #22c55e; margin-top: 5px;">€ 85.50</div>
            </div>
            <div style="background: var(--bg-card); padding: 25px; border-radius: 12px; border: 1px solid var(--border);">
                <div style="color: var(--text-muted); font-size: 0.9rem;">Libri Comprati / Venduti</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-top: 5px;">3 / 5</div>
            </div>
        </div>

        <div class="section-title">I tuoi libri in vendita</div>
        <div class="books-grid">
            {% for off in mie_offerte %}
            <div class="book-card">
                <div class="book-img" style="background-image: url('{{ off.immagine_copertina_url }}');"></div>
                <div class="book-details">
                    <div class="book-title">{{ off.titolo }}</div>
                    <div class="book-price-tag">Prezzo: € {{ "%.2f"|format(off.prezzo_richiesto) }} (Netto: € {{ "%.2f"|format(off.guadagno_netto) }})</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    {% if view == 'materiali' %}
    <div class="container">
        <h2 style="margin-bottom: 25px;">Materiali per Spedizioni Sicure</h2>
        <div class="materials-grid">
            {% for mat in materiali %}
            <div class="material-card">
                <div class="material-img" style="background-image: url('{{ mat.immagine_url }}');"></div>
                <div style="font-weight: 600; font-size: 1.1rem;">{{ mat.nome }}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">{{ mat.descrizione }}</div>
                <div style="font-weight: 700; color: var(--accent); margin-top: auto;">€ {{ "%.2f"|format(mat.prezzo) }}</div>
                <button class="btn-primary" onclick="alert('Acquistato con successo!')">Acquista Ora</button>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(q: str = None, genere: str = None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM libri WHERE 1=1"
    params = []
    
    if q:
        # Se l'utente cerca un ISBN (es. numeri), proviamo prima a cercarlo o scaricarlo
        if q.strip().isdigit() and len(q.strip()) >= 10:
            fetch_or_create_book_by_isbn(q.strip())
        query += " AND (titolo LIKE ? OR ean_isbn = ?)"
        params.extend([f"%{q}%", q.strip()])
        
    if genere:
        query += " AND genere = ?"
        params.append(genere)
        
    cursor.execute(query, params)
    libri = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM materiali_spedizione")
    materiali = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Renderizziamo inline tramite HTML template
    html = HTML_TEMPLATE.replace("{% if view == 'home' %}", "")
    # Semplificazione per passare variabili via string replace o logica template pulita
    return HTMLResponse(content=render_html("home", {"libri": libri, "materiali": materiali, "search_query": q, "genere": genere}))

@app.get("/vendi", response_class=HTMLResponse)
def vendi_get():
    return HTMLResponse(content=render_html("vendi", {}))

@app.post("/vendi")
def vendi_post(isbn: str = Form(...), prezzo: float = Form(...), condizioni: str = Form(...), consegna: str = Form(...), foto_reale: str = Form(None)):
    # Assicuriamoci che il libro esista nel catalogo globale tramite ISBN
    book = fetch_or_create_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Libro non trovato tramite ISBN inserito.")
    
    commissione = prezzo * 0.05
    guadagno_netto = prezzo - commissione
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO offerte_vendita (libro_id, venditore_id, prezzo_richiesto, commissione_piattaforma, guadagno_netto, condizioni, modalita_consegna, foto_reale_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (book["id"], 1, prezzo, commissione, guadagno_netto, condizioni, consegna, foto_reale or book["immagine_copertina_url"]))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/biblioteca", status_code=303)

@app.get("/libro/{libro_id}", response_class=HTMLResponse)
def dettaglio_libro(libro_id: int):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM libri WHERE id = ?", (libro_id,))
    libro = cursor.fetchone()
    
    cursor.execute("SELECT * FROM offerte_vendita WHERE libro_id = ? AND stato = 'attiva'", (libro_id,))
    offerte = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not libro:
        raise HTTPException(status_code=404, detail="Libro non trovato")
        
    return HTMLResponse(content=render_html("dettaglio", {"libro": dict(libro), "offerte": offerte}))

@app.get("/biblioteca", response_class=HTMLResponse)
def biblioteca():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.*, l.titolo, l.immagine_copertina_url 
        FROM offerte_vendita o 
        JOIN libri l ON o.libro_id = l.id 
        WHERE o.venditore_id = 1
    """)
    mie_offerte = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return HTMLResponse(content=render_html("biblioteca", {"mie_offerte": mie_offerte}))

@app.get("/materiali", response_class=HTMLResponse)
def materiali():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materiali_spedizione")
    mats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return HTMLResponse(content=render_html("materiali", {"materiali": mats}))


def render_html(current_view: str, context: dict):
    # Funzione di supporto per iniettare i contesti nel template HTML monolitico
    html = HTML_TEMPLATE
    html = html.replace("{% if view == '" + current_view + "' %}", "").replace("{% endif %}", "")
    
    # Rimuoviamo blocchi condizionali non attivi
    views = ["home", "vendi", "dettaglio", "biblioteca", "materiali"]
    for v in views:
        if v != current_view:
            start_tag = "{% if view == '" + v + "' %}"
            end_tag = "{% endif %}"
            # Rimuove il blocco tra i tag se presente
            while start_tag in html:
                start_idx = html.find(start_tag)
                end_idx = html.find(end_tag, start_idx) + len(end_tag)
                html = html[:start_idx] + html[end_idx:]
                
    # Sostituzioni variabili semplici
    html = html.replace("{{ view }}", current_view)
    html = html.replace("{{ search_query or '' }}", context.get("search_query", ""))
    html = html.replace("{% if genere == 'Narrativa' %}selected{% endif %}", "selected" if context.get("genere") == "Narrativa" else "")
    html = html.replace("{% if genere == 'Thriller' %}selected{% endif %}", "selected" if context.get("genere") == "Thriller" else "")
    html = html.replace("{% if genere == 'Scienza' %}selected{% endif %}", "selected" if context.get("genere") == "Scienza" else "")

    # Inserimento dinamico delle liste tramite sostituzione stringa o generazione HTML lato Python
    if current_view == "home":
        libri_html = ""
        for libro in context.get("libri", []):
            libri_html += f"""
            <a href="/libro/{libro['id']}" class="book-card">
                <div class="book-img" style="background-image: url('{libro['immagine_copertina_url']}');"></div>
                <div class="book-details">
                    <div class="book-genre">{libro.get('genere') or 'Libro'}</div>
                    <div class="book-title">{libro['titolo']}</div>
                    <div class="book-price-tag">Da € 5.00</div>
                </div>
            </a>
            """
        # Sostituisce il blocco for dei libri
        start_for = "{% for libro in libri %}"
        end_for = "{% endfor %}"
        if start_for in html:
            s_idx = html.find(start_for)
            e_idx = html.find(end_for) + len(end_for)
            html = html[:s_idx] + libri_html + html[e_idx:]

        mat_html = ""
        for mat in context.get("materiali", []):
            mat_html += f"""
            <div class="material-card">
                <div class="material-img" style="background-image: url('{mat['immagine_url']}');"></div>
                <div style="font-weight: 600; font-size: 1.1rem;">{mat['nome']}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">{mat['descrizione']}</div>
                <div style="font-weight: 700; color: var(--accent); margin-top: auto;">€ {mat['prezzo']:.2f}</div>
                <button class="btn-primary" onclick="alert('Articolo aggiunto al carrello!')">Acquista Materiale</button>
            </div>
            """
        start_mat = "{% for mat in materiali %}"
        end_mat = "{% endfor %}"
        if start_mat in html:
            # Sostituisce la prima occorrenza (home)
            s_idx = html.find(start_mat)
            e_idx = html.find(end_mat, s_idx) + len(end_mat)
            html = html[:s_idx] + mat_html + html[e_idx:]

    if current_view == "dettaglio":
        libro = context.get("libro", {})
        html = html.replace("{{ libro.titolo }}", libro.get("titolo", ""))
        html = html.replace("{{ libro.editore }}", libro.get("editore", ""))
        html = html.replace("{{ libro.anno_edizione }}", str(libro.get("anno_edizione", "")))
        html = html.replace("{{ libro.ean_isbn }}", libro.get("ean_isbn", ""))
        html = html.replace("{{ libro.descrizione }}", libro.get("descrizione", ""))
        html = html.replace("{{ libro.immagine_copertina_url }}", libro.get("immagine_copertina_url", ""))
        
        off_html = ""
        for off in context.get("offerte", []):
            off_html += f"""
            <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <div style="font-weight: 600; font-size: 1.05rem;">Condizioni: {off['condizioni']}</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Consegna: {off['modalita_consegna']} | Venditore ID: #{off['venditore_id']}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--accent);">€ {off['prezzo_richiesto']:.2f}</div>
                    <button class="btn-primary" onclick="alert('Acquisto completato con successo!')">Acquista Ora</button>
                </div>
            </div>
            """
        start_off = "{% for off in offerte %}"
        end_off = "{% endfor %}"
        if start_off in html:
            s_idx = html.find(start_off)
            e_idx = html.find(end_off) + len(end_off)
            html = html[:s_idx] + off_html + html[e_idx:]

    if current_view == "biblioteca":
        mie_html = ""
        for off in context.get("mie_offerte", []):
            mie_html += f"""
            <div class="book-card">
                <div class="book-img" style="background-image: url('{off['immagine_copertina_url']}');"></div>
                <div class="book-details">
                    <div class="book-title">{off['titolo']}</div>
                    <div class="book-price-tag">Prezzo: € {off['prezzo_richiesto']:.2f} (Netto: € {off['guadagno_netto']:.2f})</div>
                </div>
            </div>
            """
        start_mie = "{% for off in mie_offerte %}"
        end_mie = "{% endfor %}"
        if start_mie in html:
            s_idx = html.find(start_mie)
            e_idx = html.find(end_mie) + len(end_mie)
            html = html[:s_idx] + mie_html + html[e_idx:]

    if current_view == "materiali":
        mat_html2 = ""
        for mat in context.get("materiali", []):
            mat_html2 += f"""
            <div class="material-card">
                <div class="material-img" style="background-image: url('{mat['immagine_url']}');"></div>
                <div style="font-weight: 600; font-size: 1.1rem;">{mat['nome']}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">{mat['descrizione']}</div>
                <div style="font-weight: 700; color: var(--accent); margin-top: auto;">€ {mat['prezzo']:.2f}</div>
                <button class="btn-primary" onclick="alert('Acquistato con successo!')">Acquista Ora</button>
            </div>
            """
        start_mat2 = "{% for mat in materiali %}"
        end_mat2 = "{% endfor %}"
        if start_mat2 in html:
            # Trova la seconda occorrenza per la pagina materiali
            s_idx = html.rfind(start_mat2)
            e_idx = html.rfind(end_mat2) + len(end_mat2)
            html = html[:s_idx] + mat_html2 + html[e_idx:]

    return html

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
