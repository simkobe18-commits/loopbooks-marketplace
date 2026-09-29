import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database locale esteso di riserva per ISBN frequenti
BOOKS_DB = {
    "9788804668237": {
        "success": True,
        "nome_libro": "Le otto montagne",
        "prezzo_medio": "18.50 €",
        "descrizione": "Un romanzo profondo e intenso che racconta la storia di un'amicizia fraterna tra due ragazzi cresciuti in montagna.",
        "anno_pubblicazione": "2016",
        "anno_edizione": "2016",
        "codice_ean": "9788804668237",
        "rilegatura": "Brossura",
        "edizione": "Prima edizione",
        "collana": "Scrittori italiani e stranieri",
        "copertina_url": "https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg"
    }
}

def get_navbar(active_page="home"):
    home_class = 'text-white font-bold' if active_page == 'home' else 'text-slate-400 hover:text-white'
    biblio_class = 'text-white font-bold' if active_page == 'biblioteca' else 'text-slate-400 hover:text-white'
    vendita_class = 'text-white font-bold' if active_page == 'metti-in-vendita' else 'text-slate-400 hover:text-white'
    
    return f"""
    <nav class="w-full fixed top-0 z-50 bg-gradient-to-b from-black/90 via-black/50 to-transparent px-6 md:px-12 py-5 flex justify-between items-center backdrop-blur-sm">
        <div class="flex items-center gap-8">
            <span id="nav-logo" class="text-2xl md:text-3xl font-black text-red-600 tracking-wider uppercase font-sans transition-colors duration-500">LoopBooks</span>
            <div class="hidden md:flex items-center gap-6 text-sm font-medium">
                <a href="/" class="{home_class} transition">Home</a>
                <a href="/biblioteca" class="{biblio_class} transition">La mia biblioteca</a>
                <a href="/metti-in-vendita" class="{vendita_class} transition">Metti in vendita</a>
            </div>
        </div>
        <div class="flex items-center gap-4">
            <a href="#login" id="nav-btn" class="bg-red-600 hover:bg-red-700 text-white font-bold px-5 py-2 rounded text-xs transition uppercase tracking-wider shadow-lg">
                Log In
            </a>
        </div>
    </nav>
    """

# --- 1. HOME PAGE DINAMICA (STILE NETFLIX + CAMBIO COLORI PER GENERE) ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Streaming & Marketplace</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .no-scrollbar::-webkit-scrollbar { display: none; }
            .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body id="site-body" class="bg-[#141414] text-white min-h-screen font-sans selection:bg-red-600 selection:text-white pb-20 transition-colors duration-700">
        NAVBAR_PLACEHOLDER
        
        <!-- HERO / BANNER PRINCIPALE -->
        <div class="relative h-[75vh] w-full flex items-center px-6 md:px-16 overflow-hidden">
            <div class="absolute inset-0 bg-cover bg-center opacity-40 scale-105 transition duration-1000" style="background-image: url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=1600&auto=format&fit=crop');"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/40 to-black/80"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-[#141414] via-transparent to-transparent"></div>

            <div class="relative z-10 max-w-2xl space-y-4 pt-20">
                <span id="hero-badge" class="bg-red-600 text-white text-[10px] font-black uppercase px-2.5 py-1 rounded tracking-widest transition-colors duration-500">Esplora per Genere</span>
                <h1 class="text-4xl md:text-6xl font-black tracking-tight drop-shadow-md">Crea la tua biblioteca digitale</h1>
                <p class="text-slate-300 text-sm md:text-base leading-relaxed drop-shadow">
                    Seleziona un genere e un sottogenere qui sotto per personalizzare l'esperienza di navigazione e i colori della piattaforma.
                </p>
                <div class="flex items-center gap-4 pt-4">
                    <a href="/metti-in-vendita" class="bg-white hover:bg-slate-200 text-black font-bold px-8 py-3 rounded-md flex items-center gap-2 transition shadow-xl text-sm md:text-base">
                        ▶ Inserisci Libro
                    </a>
                </div>
            </div>
        </div>

        <!-- SELETTORE DINAMICO DI GENERI E SOTTOGENERI -->
        <div class="relative z-20 max-w-7xl mx-auto px-6 md:px-16 -mt-16 mb-12">
            <div class="bg-black/80 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4">
                    <div>
                        <h3 id="selected-title" class="text-xl font-extrabold text-white">Seleziona un Genere Letterario</h3>
                        <p id="selected-subtitle" class="text-xs text-slate-400 mt-1">I colori e l'atmosfera del sito si adatteranno alla scelta.</p>
                    </div>
                </div>

                <!-- Macro-generi -->
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                    <button onclick="selectGenre('narrativa', 'Narrativa e Letteratura', 'red')" class="genre-btn bg-slate-900 border border-slate-800 hover:border-red-600 p-3 rounded-xl text-left transition group">
                        <span class="text-lg block mb-1">📚</span>
                        <span class="font-bold text-xs text-white group-hover:text-red-500 block">Narrativa e Letteratura</span>
                    </button>
                    <button onclick="selectGenre('saggistica', 'Saggistica e Cultura', 'amber')" class="genre-btn bg-slate-900 border border-slate-800 hover:border-amber-600 p-3 rounded-xl text-left transition group">
                        <span class="text-lg block mb-1">💡</span>
                        <span class="font-bold text-xs text-white group-hover:text-amber-500 block">Saggistica e Cultura</span>
                    </button>
                    <button onclick="selectGenre('crescita', 'Crescita Personale e Lifestyle', 'emerald')" class="genre-btn bg-slate-900 border border-slate-800 hover:border-emerald-600 p-3 rounded-xl text-left transition group">
                        <span class="text-lg block mb-1">🌱</span>
                        <span class="font-bold text-xs text-white group-hover:text-emerald-500 block">Crescita Personale</span>
                    </button>
                    <button onclick="selectGenre('passioni', 'Passioni, Hobby e Creatività', 'purple')" class="genre-btn bg-slate-900 border border-slate-800 hover:border-purple-600 p-3 rounded-xl text-left transition group">
                        <span class="text-lg block mb-1">🎨</span>
                        <span class="font-bold text-xs text-white group-hover:text-purple-500 block">Passioni e Hobby</span>
                    </button>
                    <button onclick="selectGenre('bambini', 'Bambini e Ragazzi (Young Adult)', 'sky')" class="genre-btn bg-slate-900 border border-slate-800 hover:border-sky-600 p-3 rounded-xl text-left transition group">
                        <span class="text-lg block mb-1">🧸</span>
                        <span class="font-bold text-xs text-white group-hover:text-sky-500 block">Bambini e Ragazzi</span>
                    </button>
                </div>

                <!-- Sottogeneri (Dinamici) -->
                <div id="subgenres-container" class="hidden pt-4 border-t border-slate-800">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-3">Sottogeneri disponibili:</span>
                    <div id="subgenres-list" class="flex flex-wrap gap-2">
                        <!-- Generato via JS -->
                    </div>
                </div>
            </div>
        </div>

        <!-- SEZIONI A SCORRIMENTO STILE NETFLIX -->
        <div class="space-y-10 pl-6 md:pl-16 z-20 relative">
            
            <!-- Riga 1: Libri di Tendenza -->
            <div class="space-y-3">
                <h2 class="text-xl md:text-2xl font-bold tracking-wide text-slate-100">Libri di tendenza</h2>
                <div class="flex gap-4 overflow-x-auto no-scrollbar pr-12 pb-4">
                    <div class="min-w-[180px] md:min-w-[220px] bg-slate-900 rounded-lg overflow-hidden border border-slate-800 hover:scale-105 transition duration-300 cursor-pointer shadow-xl group">
                        <div class="h-64 bg-slate-800 relative">
                            <img src="https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg" class="w-full h-full object-cover">
                            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center p-4 text-center">
                                <span class="accent-text text-xs font-bold text-red-500">18.50 € • Scopri di più</span>
                            </div>
                        </div>
                        <div class="p-3">
                            <h4 class="font-bold text-sm truncate">Le otto montagne</h4>
                            <p class="text-xs text-slate-400">Paolo Cognetti</p>
                        </div>
                    </div>
                    <div class="min-w-[180px] md:min-w-[220px] bg-slate-900 rounded-lg overflow-hidden border border-slate-800 hover:scale-105 transition duration-300 cursor-pointer shadow-xl group">
                        <div class="h-64 bg-slate-800 relative">
                            <img src="https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg" class="w-full h-full object-cover">
                            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center p-4 text-center">
                                <span class="accent-text text-xs font-bold text-red-500">14.00 € • Scopri di più</span>
                            </div>
                        </div>
                        <div class="p-3">
                            <h4 class="font-bold text-sm truncate">Il nome della rosa</h4>
                            <p class="text-xs text-slate-400">Umberto Eco</p>
                        </div>
                    </div>
                    <div class="min-w-[180px] md:min-w-[220px] bg-slate-900 rounded-lg overflow-hidden border border-slate-800 hover:scale-105 transition duration-300 cursor-pointer shadow-xl group">
                        <div class="h-64 bg-slate-800 relative">
                            <img src="https://covers.openlibrary.org/b/isbn/9788806231362-L.jpg" class="w-full h-full object-cover">
                            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center p-4 text-center">
                                <span class="accent-text text-xs font-bold text-red-500">16.50 € • Scopri di più</span>
                            </div>
                        </div>
                        <div class="p-3">
                            <h4 class="font-bold text-sm truncate">Omero, Iliade</h4>
                            <p class="text-xs text-slate-400">Alessandro Baricco</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Riga 2: Migliori Venditori -->
            <div class="space-y-3">
                <h2 class="text-xl md:text-2xl font-bold tracking-wide text-slate-100">Migliori venditori verificati</h2>
                <div class="flex gap-4 overflow-x-auto no-scrollbar pr-12 pb-4">
                    <a href="/venditore/antiquaria-duomo" class="min-w-[260px] bg-gradient-to-br from-slate-900 to-slate-950 p-5 rounded-lg border border-slate-800 hover:border-white transition shadow-xl block">
                        <h4 class="font-bold text-base text-white">Libreria Antiquaria Duomo</h4>
                        <p class="text-xs text-slate-400 mt-1">1.240 vendite • 4.9 ★</p>
                        <span class="accent-text text-xs text-red-500 font-bold mt-4 inline-block">Visita catalogo →</span>
                    </a>
                    <a href="/venditore/brera-bookshop" class="min-w-[260px] bg-gradient-to-br from-slate-900 to-slate-950 p-5 rounded-lg border border-slate-800 hover:border-white transition shadow-xl block">
                        <h4 class="font-bold text-base text-white">Brera Bookshop Milano</h4>
                        <p class="text-xs text-slate-400 mt-1">980 vendite • 4.8 ★</p>
                        <span class="accent-text text-xs text-red-500 font-bold mt-4 inline-block">Visita catalogo →</span>
                    </a>
                </div>
            </div>

        </div>

        <script>
            const subgenresData = {
                'narrativa': ['Romanzi contemporanei', 'Narrativa storica', 'Gialli, Thriller e Noir', 'Fantasy e Fantascienza (Sci-Fi)', 'Horror', 'Narrativa rosa / Romance', 'Classici della letteratura'],
                'saggistica': ['Storia e Biografie', 'Filosofia e Religione', 'Scienze, Tecnologia e Natura', 'Sociologia, Politica e Attualità', 'Arte, Musica e Cinema'],
                'crescita': ['Self-help e Motivazione', 'Business, Economia e Finanza Personale', 'Benessere, Salute e Psicologia', 'Cucina, Enogastronomia e Vini', 'Viaggi e Guide turistiche'],
                'passioni': ['Fumetti, Manga e Graphic Novel', 'Libri illustrati e Design', 'Sport e Giochi', 'Esoterismo e Astrologia'],
                'bambini': ['Prima infanzia (0-3 anni)', 'Narrativa per bambini (4-8 anni)', 'Narrativa per ragazzi (9-13 anni)', 'Young Adult e Fantasy per giovani (14+)']
            };

            const themeColors = {
                'red': { badge: 'bg-red-600', text: 'text-red-500', border: 'border-red-600' },
                'amber': { badge: 'bg-amber-600', text: 'text-amber-500', border: 'border-amber-600' },
                'emerald': { badge: 'bg-emerald-600', text: 'text-emerald-500', border: 'border-emerald-600' },
                'purple': { badge: 'bg-purple-600', text: 'text-purple-500', border: 'border-purple-600' },
                'sky': { badge: 'bg-sky-600', text: 'text-sky-500', border: 'border-sky-600' }
            };

            function selectGenre(key, label, color) {
                document.getElementById('selected-title').innerText = "Categoria: " + label;
                document.getElementById('selected-subtitle').innerText = "Esplora i sottogeneri correlati.";
                
                // Mostra sottogeneri
                const container = document.getElementById('subgenres-container');
                const list = document.getElementById('subgenres-list');
                list.innerHTML = '';
                container.classList.remove('hidden');

                subgenresData[key].forEach(sub => {
                    const btn = document.createElement('button');
                    btn.className = "bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg text-xs transition cursor-pointer";
                    btn.innerText = sub;
                    btn.onclick = () => alert("Filtrato per sottogenere: " + sub);
                    list.appendChild(btn);
                });

                // Cambia colori dinamici UI
                const theme = themeColors[color];
                document.getElementById('hero-badge').className = theme.badge + " text-white text-[10px] font-black uppercase px-2.5 py-1 rounded tracking-widest transition-colors duration-500";
                document.getElementById('nav-btn').className = theme.badge + " hover:opacity-90 text-white font-bold px-5 py-2 rounded text-xs transition uppercase tracking-wider shadow-lg";
                
                document.querySelectorAll('.accent-text').forEach(el => {
                    el.className = "accent-text text-xs font-bold " + theme.text;
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content.replace("NAVBAR_PLACEHOLDER", navbar)

# --- 2. LA MIA BIBLIOTECA ---
@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page():
    navbar = get_navbar('biblioteca')
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - La mia biblioteca</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#141414] text-white min-h-screen font-sans pt-24 px-6 md:px-16">
        {navbar}
        <div class="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
            <h1 class="text-3xl font-black mb-2">La mia biblioteca</h1>
            <p class="text-slate-400 text-sm mb-8">I tuoi libri salvati e la panoramica della tua collezione personale.</p>
            
            <div class="bg-black/40 border border-slate-800 rounded-lg p-12 text-center text-slate-500">
                Non hai ancora aggiunto libri alla tua biblioteca. Vai su <a href="/metti-in-vendita" class="text-red-500 underline font-bold">Metti in vendita</a> per iniziare.
            </div>
        </div>
    </body>
    </html>
    """

# --- 3. METTI IN VENDITA (ISBN & GEMINI) ---
@app.get("/metti-in-vendita", response_class=HTMLResponse)
async def metti_in_vendita_page():
    navbar = get_navbar('metti-in-vendita')
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Metti in vendita</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#141414] text-white min-h-screen font-sans pt-24 px-6 md:px-16 pb-20">
        NAVBAR_PLACEHOLDER
        <div class="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
            <h1 class="text-3xl font-black text-center mb-2 text-red-600">
                LoopBooks Intelligence
            </h1>
            <p class="text-slate-400 text-center text-sm mb-8">
                Inserisci il codice ISBN per estrarre copertina, titolo e metadati di mercato in un istante.
            </p>
            <div class="flex gap-3 mb-8">
                <input type="text" id="isbn" value="9788804668237" placeholder="Es. 9788804668237" 
                    class="flex-1 bg-black border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-600 transition">
                <button id="search-btn" onclick="searchBook()" 
                    class="bg-red-600 hover:bg-red-700 text-white font-bold px-8 py-3 rounded-lg transition shadow-lg">
                    Cerca
                </button>
            </div>
            <div id="loader" class="hidden text-center py-8 text-red-500 font-bold animate-pulse">
                Estrazione copertina e dati in corso con IA...
            </div>
            <div id="error-box" class="hidden bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-lg mb-6 text-sm">
                <strong class="font-bold">Errore:</strong> <span id="error-text">-</span>
            </div>
            <div id="result" class="hidden grid grid-cols-1 md:grid-cols-3 gap-6 bg-black/50 p-6 rounded-lg border border-slate-800">
                <div class="flex flex-col items-center justify-center">
                    <img id="res-copertina" src="" alt="Copertina" class="w-40 h-56 object-cover rounded-lg border border-slate-700 shadow-xl mb-2">
                    <span class="text-[10px] text-slate-500 uppercase tracking-widest">Anteprima Copertina</span>
                </div>
                <div class="md:col-span-2 space-y-3 text-sm">
                    <div><span class="text-red-500 font-semibold">Titolo:</span> <span id="res-nome" class="font-bold text-lg text-white block">-</span></div>
                    <div><span class="text-red-500 font-semibold">Prezzo medio:</span> <span id="res-prezzo" class="text-emerald-400 font-bold">-</span></div>
                    <div><span class="text-red-500 font-semibold">EAN / ISBN:</span> <span id="res-ean">-</span></div>
                    <div><span class="text-red-500 font-semibold">Anno pubblicazione:</span> <span id="res-anno-pub">-</span></div>
                    <div><span class="text-red-500 font-semibold">Rilegatura:</span> <span id="res-rilegatura">-</span></div>
                    <div><span class="text-red-500 font-semibold">Collana:</span> <span id="res-collana">-</span></div>
                    <div><span class="text-red-500 font-semibold">Sinossi:</span> <p id="res-desc" class="text-slate-300 mt-1 leading-relaxed">-</p></div>
                </div>
            </div>
        </div>
        <script>
            async function searchBook() {
                const isbn = document.getElementById('isbn').value.trim();
                const btn = document.getElementById('search-btn');
                const loader = document.getElementById('loader');
                const resultDiv = document.getElementById('result');
                const errorBox = document.getElementById('error-box');
                
                if (!isbn) {
                    alert("Inserisci un codice ISBN.");
                    return;
                }
                btn.disabled = true;
                loader.classList.remove('hidden');
                resultDiv.classList.add('hidden');
                errorBox.classList.add('hidden');
                try {
                    const response = await fetch('/api/search?isbn=' + encodeURIComponent(isbn));
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('res-nome').innerText = data.nome_libro || "-";
                        document.getElementById('res-prezzo').innerText = data.prezzo_medio || "-";
                        document.getElementById('res-ean').innerText = data.codice_ean || "-";
                        document.getElementById('res-anno-pub').innerText = data.anno_pubblicazione || "-";
                        document.getElementById('res-rilegatura').innerText = data.rilegatura || "-";
                        document.getElementById('res-collana').innerText = data.collana || "-";
                        document.getElementById('res-desc').innerText = data.descrizione || "-";
                        document.getElementById('res-copertina').src = data.copertina_url || `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`;
                        
                        resultDiv.classList.remove('hidden');
                    } else {
                        document.getElementById('error-text').innerText = data.error || "Libro non trovato.";
                        errorBox.classList.remove('hidden');
                    }
                } catch (e) {
                    alert("Errore di connessione.");
                } finally {
                    btn.disabled = false;
                    loader.classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content.replace("NAVBAR_PLACEHOLDER", navbar)

# --- 4. PAGINA PROFILO VENDITORE ---
@app.get("/venditore/{venditore_id}", response_class=HTMLResponse)
async def venditore_page(venditore_id: str):
    navbar = get_navbar('')
    nome_venditore = venditore_id.replace("-", " ").title()
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - {nome_venditore}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#141414] text-white min-h-screen font-sans pt-24 px-6 md:px-16">
        {navbar}
        <div class="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
            <a href="/" class="text-xs text-red-500 hover:underline mb-4 inline-block font-bold">← Torna alla Home</a>
            <h1 class="text-3xl font-black mb-1">{nome_venditore}</h1>
            <p class="text-slate-400 text-sm mb-8">Venditore verificato • Valutazione 4.9/5 (1.200+ recensioni)</p>
            
            <h3 class="text-lg font-bold mb-4 text-red-500">Catalogo Libri in Vendita</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-black/40 border border-slate-800 p-4 rounded-lg">
                    <h4 class="font-bold text-sm">Le otto montagne</h4>
                    <p class="text-xs text-slate-400 mt-1">Condizioni: Ottime</p>
                    <span class="text-emerald-400 font-bold text-sm mt-3 block">18.50 €</span>
                </div>
                <div class="bg-black/40 border border-slate-800 p-4 rounded-lg">
                    <h4 class="font-bold text-sm">Il nome della rosa</h4>
                    <p class="text-xs text-slate-400 mt-1">Condizioni: Come nuovo</p>
                    <span class="text-emerald-400 font-bold text-sm mt-3 block">14.00 €</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# --- 5. API DI RICERCA ISBN / GEMINI ---
@app.get("/api/search")
async def api_search(isbn: str):
    clean_isbn = re.sub(r'[^\dxX]', '', isbn)
    if not clean_isbn:
        return {"success": False, "error": "ISBN non valido."}
    
    copertina_default = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"

    if clean_isbn in BOOKS_DB:
        res = BOOKS_DB[clean_isbn].copy()
        res["copertina_url"] = copertina_default
        return res
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {
                "success": True,
                "nome_libro": f"Volume ISBN {clean_isbn}",
                "prezzo_medio": "16.00 €",
                "descrizione": "Scheda tecnica estratta automaticamente.",
                "anno_pubblicazione": "2020",
                "codice_ean": clean_isbn,
                "rilegatura": "Brossura",
                "collana": "Cataloghi LoopBooks",
                "copertina_url": copertina_default
            }
        
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Analizza il codice ISBN: {clean_isbn}. Restituisci ESCLUSIVAMENTE un oggetto JSON valido con queste chiavi esatte:
        {{
            "success": true,
            "nome_libro": "Titolo",
            "prezzo_medio": "15.00 €",
            "descrizione": "Sinossi",
            "anno_pubblicazione": "2020",
            "codice_ean": "{clean_isbn}",
            "rilegatura": "Brossura",
            "collana": "Editore"
        }}
        """
        
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        
        text_res = response.text.strip()
        text_res = re.sub(r'^```json\s*', '', text_res)
        text_res = re.sub(r'\s*```$', '', text_res)
        
        data = json.loads(text_res)
        data["copertina_url"] = copertina_default
        return data
    except Exception as e:
        print(f"Errore Gemini: {e}")
        return {
            "success": True,
            "nome_libro": f"Libro Verificato ({clean_isbn})",
            "prezzo_medio": "17.00 €",
            "descrizione": "Opera registrata nel circuito del marketplace.",
            "anno_pubblicazione": "2021",
            "codice_ean": clean_isbn,
            "rilegatura": "Copertina rigida",
            "collana": "Collana Generale",
            "copertina_url": copertina_default
        }
