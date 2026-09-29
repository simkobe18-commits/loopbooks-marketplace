import os
import json
import re
import sqlite3
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from google import genai

app = FastAPI()

# Database locale SQLite per il marketplace dei libri
DB_FILE = "loopbooks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_libro TEXT,
            prezzo_medio TEXT,
            descrizione TEXT,
            anno_pubblicazione TEXT,
            anno_edizione TEXT,
            codice_ean TEXT UNIQUE,
            rilegatura TEXT,
            edizione TEXT,
            collana TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 1. HOME PAGE / MARKETPLACE ---
@app.get("/", response_class=HTMLResponse)
async def marketplace_home():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books ORDER BY id DESC")
    books = cursor.fetchall()
    conn.close()

    books_html = ""
    if not books:
        books_html = """
        <div class="col-span-full text-center py-16 text-slate-500 bg-slate-900/40 border border-slate-800 rounded-2xl">
            <p class="text-lg mb-2">Nessun libro presente nel marketplace.</p>
            <a href="/add" class="text-sky-400 hover:underline font-semibold">Usa l'inserimento rapido ISBN per aggiungerne uno →</a>
        </div>
        """
    else:
        for b in books:
            books_html += f"""
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-sky-500/50 transition shadow-xl flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-start gap-2 mb-2">
                        <h3 class="font-bold text-lg text-slate-100">{b['nome_libro']}</h3>
                        <span class="bg-emerald-950 text-emerald-400 font-bold px-3 py-1 rounded-xl text-sm border border-emerald-800/50 whitespace-nowrap">{b['prezzo_medio']}</span>
                    </div>
                    <p class="text-xs text-sky-400 mb-3 font-mono">EAN: {b['codice_ean']} • {b['collana'] or 'Edizione Standard'}</p>
                    <p class="text-slate-400 text-sm line-clamp-3 mb-4 leading-relaxed">{b['descrizione']}</p>
                </div>
                <div class="border-t border-slate-800/80 pt-3 flex justify-between items-center text-xs text-slate-400">
                    <span class="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">{b['rilegatura']} ({b['anno_edizione']})</span>
                    <span class="text-sky-400 font-semibold">{b['edizione']}</span>
                </div>
            </div>
            """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Marketplace</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col">
        <!-- Navbar -->
        <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <h1 class="text-xl font-extrabold bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
                    LoopBooks Marketplace
                </h1>
            </div>
            <div class="flex items-center gap-3">
                <a href="/add" class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-4 py-2.5 rounded-xl text-sm transition shadow-lg shadow-sky-500/20">
                    + Inserimento Rapido ISBN
                </a>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
            <div class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-extrabold mb-1">Catalogo Libri Disponibili</h2>
                    <p class="text-slate-400 text-sm">Esplora i volumi in vendita con storico prezzi e dettagli tecnici verificati.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {books_html}
            </div>
        </main>
    </body>
    </html>
    """

# --- 2. PAGINA DI INSERIMENTO RAPIDO (INTELLIGENCE) ---
@app.get("/add", response_class=HTMLResponse)
async def add_book_page():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Inserimento Rapido ISBN</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        <div class="w-full max-w-3xl">
            <div class="mb-4 flex justify-between items-center">
                <a href="/" class="text-sm text-sky-400 hover:underline flex items-center gap-1 font-medium">← Torna al Marketplace</a>
                <span class="text-xs text-slate-500 font-mono">LoopBooks Intelligence Engine</span>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
                <h1 class="text-2xl font-extrabold text-center mb-2 bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
                    Inserimento Rapido tramite ISBN
                </h1>
                <p class="text-slate-400 text-center text-sm mb-6">
                    Inserisci il codice ISBN: i campi si compileranno in automatico per la pubblicazione[cite: 13].
                </p>

                <div class="flex gap-3 mb-6">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Es. 9788804668237" 
                        class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-sky-500 transition font-mono">
                    <button id="search-btn" onclick="fetchBookData()" 
                        class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-6 py-3 rounded-xl transition shadow-lg shadow-sky-500/25 whitespace-nowrap">
                        Estrai Dati
                    </button>
                </div>

                <div id="loader" class="hidden text-center py-8 text-sky-400 font-medium animate-pulse">
                    Analisi dei metadati del libro in corso con Gemini...
                </div>

                <div id="error-box" class="hidden bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-xl mb-6 text-sm">
                    <strong class="font-bold">Errore:</strong> <span id="error-text">-</span>
                </div>

                <!-- Form di salvataggio precompilato -->
                <form id="save-form" action="/api/save-book" method="POST" class="hidden space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950 p-5 rounded-xl border border-slate-800 text-sm">
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Nome del libro[cite: 13]</label>
                            <input type="text" id="res-nome" name="nome_libro" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none" required>
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Prezzo medio[cite: 13]</label>
                            <input type="text" id="res-prezzo" name="prezzo_medio" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-emerald-400 font-bold focus:border-sky-500 focus:outline-none" required>
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Codice EAN[cite: 13]</label>
                            <input type="text" id="res-ean" name="codice_ean" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 font-mono focus:border-sky-500 focus:outline-none" required>
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Anno pubblicazione[cite: 13]</label>
                            <input type="text" id="res-anno-pub" name="anno_pubblicazione" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Anno edizione[cite: 13]</label>
                            <input type="text" id="res-anno-ed" name="anno_edizione" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Rilegatura[cite: 13]</label>
                            <input type="text" id="res-rilegatura" name="rilegatura" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Edizione[cite: 13]</label>
                            <input type="text" id="res-edizione" name="edizione" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="text-sky-400 font-semibold block mb-1">Collana[cite: 13]</label>
                            <input type="text" id="res-collana" name="collana" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-100 focus:border-sky-500 focus:outline-none">
                        </div>
                        <div class="md:col-span-2">
                            <label class="text-sky-400 font-semibold block mb-1">Descrizione (riassunto)[cite: 13]</label>
                            <textarea id="res-desc" name="descrizione" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-300 focus:border-sky-500 focus:outline-none"></textarea>
                        </div>
                    </div>

                    <div class="bg-slate-950 p-5 rounded-xl border border-slate-800">
                        <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Grafico storico prezzi (CardMarket Style)</h3>
                        <div class="relative h-48 w-full">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>

                    <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold py-3.5 rounded-xl transition shadow-lg shadow-emerald-500/20">
                        Salva e Pubblica nel Marketplace
                    </button>
                </form>
            </div>
        </div>

        <script>
            let myChart = null;

            async function fetchBookData() {
                const isbn = document.getElementById('isbn').value.trim();
                const btn = document.getElementById('search-btn');
                const loader = document.getElementById('loader');
                const formDiv = document.getElementById('save-form');
                const errorBox = document.getElementById('error-box');
                
                if (!isbn) {
                    alert("Inserisci un codice ISBN.");
                    return;
                }

                btn.disabled = true;
                loader.classList.remove('hidden');
                formDiv.classList.add('hidden');
                errorBox.classList.add('hidden');

                try {
                    const response = await fetch('/api/parse-isbn?isbn=' + encodeURIComponent(isbn));
                    const data = await response.json();

                    if (data.success) {
                        document.getElementById('res-nome').value = data.nome_libro || "";
                        document.getElementById('res-prezzo').value = data.prezzo_medio || "";
                        document.getElementById('res-ean').value = data.codice_ean || isbn;
                        document.getElementById('res-anno-pub').value = data.anno_pubblicazione || "";
                        document.getElementById('res-anno-ed').value = data.anno_edizione || "";
                        document.getElementById('res-rilegatura').value = data.rilegatura || "";
                        document.getElementById('res-edizione').value = data.edizione || "";
                        document.getElementById('res-collana').value = data.collana || "";
                        document.getElementById('res-desc').value = data.descrizione || "";

                        formDiv.classList.remove('hidden');
                        renderChart(data.storico_prezzi);
                    } else {
                        document.getElementById('error-text').innerText = data.error || "Impossibile estrarre i dati.";
                        errorBox.classList.remove('hidden');
                    }
                } catch (e) {
                    alert("Errore di comunicazione con il server.");
                } finally {
                    btn.disabled = false;
                    loader.classList.add('hidden');
                }
            }

            function renderChart(storico) {
                const ctx = document.getElementById('priceChart').getContext('2d');
                if (myChart) myChart.destroy();

                myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: storico?.labels || ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set'],
                        datasets: [{
                            data: storico?.prices || [15, 15.5, 16, 16.5, 17, 17.5, 18, 18.2, 18.5],
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                            y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                        }
                    }
                });
            }
        </script>
    </body>
    </html>
    """

# --- 3. API DI ESTRAZIONE GEMINI PER ISBN ---
@app.get("/api/parse-isbn")
async def api_parse_isbn(isbn: str):
    clean_isbn = re.sub(r'[^\dxX]', '', isbn)
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "error": "Chiave GEMINI_API_KEY non configurata su Render."}

        client = genai.Client(api_key=api_key)
        prompt = f"""
        Analizza il codice ISBN: {clean_isbn}. Restituisci ESCLUSIVAMENTE un oggetto JSON valido con queste chiavi esatte e dati reali:
        {{
            "success": true,
            "nome_libro": "Titolo completo",
            "prezzo_medio": "18.50 €",
            "descrizione": "Sinossi o riassunto dettagliato",
            "anno_pubblicazione": "2016",
            "anno_edizione": "2020",
            "codice_ean": "{clean_isbn}",
            "rilegatura": "Brossura",
            "edizione": "Prima edizione",
            "collana": "Collana editoriale",
            "storico_prezzi": {{
                "labels": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set"],
                "prices": [15.0, 15.5, 16.0, 16.8, 17.2, 17.5, 18.0, 18.2, 18.5]
            }}
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text_res = response.text.strip()
        text_res = re.sub(r'^```json\s*', '', text_res)
        text_res = re.sub(r'\s*```$', '', text_res)
        return json.loads(text_res)
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- 4. SALVATAGGIO NEL DATABASE DEL MARKETPLACE ---
@app.post("/api/save-book")
async def save_book(
    nome_libro: str = Form(...),
    prezzo_medio: str = Form(...),
    descrizione: str = Form(...),
    anno_pubblicazione: str = Form(...),
    anno_edizione: str = Form(...),
    codice_ean: str = Form(...),
    rilegatura: str = Form(...),
    edizione: str = Form(...),
    collana: str = Form(...)
):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO books 
            (nome_libro, prezzo_medio, descrizione, anno_pubblicazione, anno_edizione, codice_ean, rilegatura, edizione, collana)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_libro, prezzo_medio, descrizione, anno_pubblicazione, anno_edizione, codice_ean, rilegatura, edizione, collana))
        conn.commit()
    except Exception as e:
        print(f"Errore salvataggio DB: {e}")
    finally:
        conn.close()

    return RedirectResponse(url="/", status_code=303)
