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
        "prezzo_medio": "18.50 Sesterzi",
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
    home_class = 'text-[#d4af37] font-bold border-b-2 border-[#d4af37]' if active_page == 'home' else 'text-slate-300 hover:text-[#d4af37]'
    biblio_class = 'text-[#d4af37] font-bold border-b-2 border-[#d4af37]' if active_page == 'biblioteca' else 'text-slate-300 hover:text-[#d4af37]'
    vendita_class = 'text-[#d4af37] font-bold border-b-2 border-[#d4af37]' if active_page == 'metti-in-vendita' else 'text-slate-300 hover:text-[#d4af37]'
    
    return f"""
    <nav class="w-full fixed top-0 z-50 bg-[#12100e]/95 border-b border-[#d4af37]/30 px-6 md:px-12 py-4 flex justify-between items-center backdrop-blur-md shadow-2xl">
        <div class="flex items-center gap-8">
            <span class="text-2xl md:text-3xl font-serif tracking-widest text-[#d4af37] uppercase font-bold drop-shadow">BIBLIOTECA IMPERIALE</span>
            <div class="hidden md:flex items-center gap-8 text-sm font-serif tracking-wider">
                <a href="/" class="{home_class} transition pb-1">Portico Principale</a>
                <a href="/biblioteca" class="{biblio_class} transition pb-1">La Mia Biblioteca</a>
                <a href="/metti-in-vendita" class="{vendita_class} transition pb-1">Bottega dei Libri</a>
            </div>
        </div>
        <div class="flex items-center gap-4">
            <a href="#login" class="bg-[#7a1c1c] hover:bg-[#992424] text-[#d4af37] border border-[#d4af37]/50 font-serif font-bold px-5 py-2 rounded text-xs transition uppercase tracking-widest shadow-lg">
                Accesso Patrizi
            </a>
        </div>
    </nav>
    """

# --- 1. HOME PAGE STILE ANTICA ROMA ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Biblioteca Imperiale di Roma</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .no-scrollbar::-webkit-scrollbar { display: none; }
            .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
            body { background-color: #12100e; color: #e2d9c5; font-family: 'Georgia', serif; }
        </style>
    </head>
    <body class="min-h-screen selection:bg-[#7a1c1c] selection:text-[#d4af37] pb-20">
        NAVBAR_PLACEHOLDER
        
        <!-- HERO / BANNER IMPERIALE -->
        <div class="relative h-[75vh] w-full flex items-center px-6 md:px-16 overflow-hidden border-b border-[#d4af37]/20">
            <div class="absolute inset-0 bg-cover bg-center opacity-25 scale-105 transition duration-1000" style="background-image: url('https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?q=80&w=1600&auto=format&fit=crop');"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-[#12100e] via-[#12100e]/50 to-black/80"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-[#12100e] via-transparent to-transparent"></div>

            <div class="relative z-10 max-w-2xl space-y-4 pt-20">
                <span class="bg-[#7a1c1c] text-[#d4af37] border border-[#d4af37]/40 text-[10px] font-serif font-black uppercase px-3 py-1 rounded tracking-widest">Collezione Augustea</span>
                <h1 class="text-4xl md:text-6xl font-serif font-black tracking-wide text-[#f3ead8] drop-shadow-lg">IL TEMPO DEI LIBRI SACRI</h1>
                <p class="text-slate-300 text-sm md:text-base leading-relaxed font-serif italic">
                    "Custodisci il sapere del mondo antico e moderno. Esplora i generi letterari, consulta i rotoli preziosi e metti a disposizione i tuoi volumi nell'Urbe."
                </p>
                <div class="flex items-center gap-4 pt-4">
                    <a href="/metti-in-vendita" class="bg-[#d4af37] hover:bg-[#e6c250] text-[#12100e] font-serif font-bold px-8 py-3 rounded-md flex items-center gap-2 transition shadow-xl text-sm md:text-base uppercase tracking-wider">
                        ✦ Offri un Volume
                    </a>
                </div>
            </div>
        </div>

        <!-- SELETTORE DEI GENERI E SOTTOGENERI -->
        <div class="relative z-20 max-w-7xl mx-auto px-6 md:px-16 -mt-16 mb-12">
            <div class="bg-[#1a1714] border-2 border-[#d4af37]/40 rounded-xl p-6 shadow-2xl space-y-6">
                <div class="border-b border-[#d4af37]/20 pb-4">
                    <h3 id="selected-title" class="text-xl font-serif font-bold text-[#d4af37]">Catalogo delle Arti e delle Lettere</h3>
                    <p id="selected-subtitle" class="text-xs text-slate-400 font-serif italic mt-1">Scegli un genere letterario per esplorare le sezioni.</p>
                </div>

                <!-- Macro-generi -->
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                    <button onclick="selectGenre('narrativa', 'Narrativa e Letteratura')" class="bg-[#12100e] border border-[#d4af37]/30 hover:border-[#d4af37] p-3 rounded-lg text-left transition group">
                        <span class="text-lg block mb-1">📜</span>
                        <span class="font-serif font-bold text-xs text-[#f3ead8] group-hover:text-[#d4af37] block">Narrativa & Lettere</span>
                    </button>
                    <button onclick="selectGenre('saggistica', 'Saggistica e Cultura')" class="bg-[#12100e] border border-[#d4af37]/30 hover:border-[#d4af37] p-3 rounded-lg text-left transition group">
                        <span class="text-lg block mb-1">🏛</span>
                        <span class="font-serif font-bold text-xs text-[#f3ead8] group-hover:text-[#d4af37] block">Saggistica & Cultura</span>
                    </button>
                    <button onclick="selectGenre('crescita', 'Crescita Personale e Lifestyle')" class="bg-[#12100e] border border-[#d4af37]/30 hover:border-[#d4af37] p-3 rounded-lg text-left transition group">
                        <span class="text-lg block mb-1">🌿</span>
                        <span class="font-serif font-bold text-xs text-[#f3ead8] group-hover:text-[#d4af37] block">Crescita & Spirito</span>
                    </button>
                    <button onclick="selectGenre('passioni', 'Passioni, Hobby e Creatività')" class="bg-[#12100e] border border-[#d4af37]/30 hover:border-[#d4af37] p-3 rounded-lg text-left transition group">
                        <span class="text-lg block mb-1">🏺</span>
                        <span class="font-serif font-bold text-xs text-[#f3ead8] group-hover:text-[#d4af37] block">Arti & Passioni</span>
                    </button>
                    <button onclick="selectGenre('bambini', 'Bambini e Ragazzi (Young Adult)')" class="bg-[#12100e] border border-[#d4af37]/30 hover:border-[#d4af37] p-3 rounded-lg text-left transition group">
                        <span class="text-lg block mb-1">🛡️</span>
                        <span class="font-serif font-bold text-xs text-[#f3ead8] group-hover:text-[#d4af37] block">Giovani & Eroi</span>
                    </button>
                </div>

                <!-- Sottogeneri -->
                <div id="subgenres-container" class="hidden pt-4 border-t border-[#d4af37]/20">
                    <span class="text-xs font-serif font-bold text-[#d4af37] uppercase tracking-widest block mb-3">Sottogeneri della sezione:</span>
                    <div id="subgenres-list" class="flex flex-wrap gap-2"></div>
                </div>
            </div>
        </div>

        <!-- SEZIONI IN EVIDENZA -->
        <div class="space-y-10 pl-6 md:pl-16 z-20 relative font-serif">
            
            <div class="space-y-3">
                <h2 class="text-xl md:text-2xl font-bold tracking-wide text-[#d4af37] border-l-4 border-[#7a1c1c] pl-3">Volumi più letti nell'Impero</h2>
                <div class="flex gap-4 overflow-x-auto no-scrollbar pr-12 pb-4">
                    <div class="min-w-[180px] md:min-w-[220px] bg-[#1a1714] rounded-lg overflow-hidden border border-[#d4af37]/30 hover:border-[#d4af37] transition duration-300 cursor-pointer shadow-2xl group">
                        <div class="h-64 bg-black relative">
                            <img src="https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg" class="w-full h-full object-cover opacity-90">
                            <div class="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition flex items-center justify-center p-4 text-center">
                                <span class="text-xs font-bold text-[#d4af37]">18.50 Sesterzi • Esamina</span>
                            </div>
                        </div>
                        <div class="p-3">
                            <h4 class="font-bold text-sm truncate text-[#f3ead8]">Le otto montagne</h4>
                            <p class="text-xs text-slate-400 italic">Paolo Cognetti</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="space-y-3">
                <h2 class="text-xl md:text-2xl font-bold tracking-wide text-[#d4af37] border-l-4 border-[#7a1c1c] pl-3">Magistrati e Mercanti Verificati</h2>
                <div class="flex gap-4 overflow-x-auto no-scrollbar pr-12 pb-4">
                    <a href="/venditore/antiquaria-duomo" class="min-w-[260px] bg-gradient-to-br from-[#1a1714] to-[#12100e] p-5 rounded-lg border border-[#d4af37]/30 hover:border-[#d4af37] transition shadow-xl block">
                        <h4 class="font-bold text-base text-[#f3ead8]">Officina Libraria Senatoria</h4>
                        <p class="text-xs text-slate-400 mt-1 italic">1.240 scambi • 4.9 ★</p>
                        <span class="text-xs text-[#d4af37] font-bold mt-4 inline-block">Visita bottega →</span>
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

            function selectGenre(key, label) {
                document.getElementById('selected-title').innerText = "Sezione: " + label;
                document.getElementById('selected-subtitle').innerText = "Seleziona un sottogenere per consultare i rotoli.";
                
                const container = document.getElementById('subgenres-container');
                const list = document.getElementById('subgenres-list');
                list.innerHTML = '';
                container.classList.remove('hidden');

                subgenresData[key].forEach(sub => {
                    const btn = document.createElement('button');
                    btn.className = "bg-[#12100e] hover:bg-[#26211c] text-[#d4af37] border border-[#d4af37]/30 px-3 py-1.5 rounded text-xs font-serif transition cursor-pointer";
                    btn.innerText = sub;
                    btn.onclick = () => alert("Hai scelto la categoria: " + sub);
                    list.appendChild(btn);
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
        <title>La Mia Biblioteca Privata</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #12100e; color: #e2d9c5; font-family: 'Georgia', serif; }}</style>
    </head>
    <body class="min-h-screen pt-28 px-6 md:px-16">
        {navbar}
        <div class="max-w-4xl mx-auto bg-[#1a1714] border-2 border-[#d4af37]/30 rounded-xl p-8 shadow-2xl">
            <h1 class="text-3xl font-serif font-black mb-2 text-[#d4af37]">La Tua Collezione Privata</h1>
            <p class="text-slate-400 text-sm mb-8 italic">I tuoi manoscritti e rotoli custoditi nel caveau della domus.</p>
            
            <div class="bg-[#12100e] border border-[#d4af37]/20 rounded-lg p-12 text-center text-slate-500 italic">
                Nessun volume registrato nella tua biblioteca. Recati alla <a href="/metti-in-vendita" class="text-[#d4af37] underline font-bold">Bottega dei Libri</a> per aggiungerne uno.
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
        <title>Bottega dei Libri e Stime</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body { background-color: #12100e; color: #e2d9c5; font-family: 'Georgia', serif; }</style>
    </head>
    <body class="min-h-screen pt-28 px-6 md:px-16 pb-20">
        NAVBAR_PLACEHOLDER
        <div class="max-w-4xl mx-auto bg-[#1a1714] border-2 border-[#d4af37]/30 rounded-xl p-8 shadow-2xl">
            <h1 class="text-3xl font-serif font-black text-center mb-2 text-[#d4af37]">
                Archivio e Valutazione Volumi
            </h1>
            <p class="text-slate-400 text-center text-sm mb-8 italic">
                Immetti il codice ISBN del tomo per estrarre la copertina e le stime di mercato imperiali.
            </p>
            <div class="flex gap-3 mb-8">
                <input type="text" id="isbn" value="9788804668237" placeholder="Es. 9788804668237" 
                    class="flex-1 bg-[#12100e] border border-[#d4af37]/40 rounded-lg px-4 py-3 text-[#f3ead8] focus:outline-none focus:border-[#d4af37] transition font-serif">
                <button id="search-btn" onclick="searchBook()" 
                    class="bg-[#7a1c1c] hover:bg-[#992424] text-[#d4af37] border border-[#d4af37]/50 font-serif font-bold px-8 py-3 rounded-lg transition shadow-lg uppercase tracking-wider">
                    Esamina Tomo
                </button>
            </div>
            <div id="loader" class="hidden text-center py-8 text-[#d4af37] font-serif italic animate-pulse">
                Consultazione degli archivi di Roma in corso...
            </div>
            <div id="error-box" class="hidden bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-lg mb-6 text-sm">
                <strong class="font-bold">Nota dell'Amanuense:</strong> <span id="error-text">-</span>
            </div>
            <div id="result" class="hidden grid grid-cols-1 md:grid-cols-3 gap-6 bg-[#12100e] p-6 rounded-lg border border-[#d4af37]/30">
                <div class="flex flex-col items-center justify-center">
                    <img id="res-copertina" src="" alt="Copertina" class="w-40 h-56 object-cover rounded border border-[#d4af37]/40 shadow-xl mb-2">
                    <span class="text-[10px] text-slate-400 uppercase tracking-widest italic">Immagine del Volume</span>
                </div>
                <div class="md:col-span-2 space-y-3 text-sm">
                    <div><span class="text-[#d4af37] font-semibold">Titolo:</span> <span id="res-nome" class="font-bold text-lg text-white block font-serif">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Prezzo stimato:</span> <span id="res-prezzo" class="text-emerald-400 font-bold">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Codice EAN:</span> <span id="res-ean">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Anno di stampa:</span> <span id="res-anno-pub">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Rilegatura:</span> <span id="res-rilegatura">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Collana:</span> <span id="res-collana">-</span></div>
                    <div><span class="text-[#d4af37] font-semibold">Sinossi:</span> <p id="res-desc" class="text-slate-300 mt-1 leading-relaxed italic">-</p></div>
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
                    alert("Inserisci un codice valido.");
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
                        document.getElementById('error-text').innerText = data.error || "Tomo non rinvenuto negli scaffali.";
                        errorBox.classList.remove('hidden');
                    }
                } catch (e) {
                    alert("Errore di connessione con la bottega.");
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
        <title>Bottega di {nome_venditore}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #12100e; color: #e2d9c5; font-family: 'Georgia', serif; }}</style>
    </head>
    <body class="min-h-screen pt-28 px-6 md:px-16">
        {navbar}
        <div class="max-w-4xl mx-auto bg-[#1a1714] border-2 border-[#d4af37]/30 rounded-xl p-8 shadow-2xl">
            <a href="/" class="text-xs text-[#d4af37] hover:underline mb-4 inline-block font-bold">← Torna al Portico Principale</a>
            <h1 class="text-3xl font-serif font-black mb-1 text-[#f3ead8]">{nome_venditore}</h1>
            <p class="text-slate-400 text-sm mb-8 italic">Magistrato Mercante • Approvato dal Senato (4.9/5)</p>
            
            <h3 class="text-lg font-serif font-bold mb-4 text-[#d4af37]">Volumi disponibili nella bottega</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-[#12100e] border border-[#d4af37]/30 p-4 rounded-lg">
                    <h4 class="font-bold text-sm text-[#f3ead8]">Le otto montagne</h4>
                    <p class="text-xs text-slate-400 mt-1 italic">Condizioni: Ottime (Conservato intatto)</p>
                    <span class="text-emerald-400 font-bold text-sm mt-3 block">18.50 Sesterzi</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# --- 5. API DI RICERCA ISBN ---
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
                "nome_libro": f"Volume Imperiale {clean_isbn}",
                "prezzo_medio": "16.00 Sesterzi",
                "descrizione": "Manoscritto catalogato negli archivi imperiali.",
                "anno_pubblicazione": "2020",
                "codice_ean": clean_isbn,
                "rilegatura": "Pelle di vitello",
                "collana": "Archivio di Roma",
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
            "nome_libro": f"Tomo Classico ({clean_isbn})",
            "prezzo_medio": "17.00 Sesterzi",
            "descrizione": "Opera registrata nel circuito dei mercanti.",
            "anno_pubblicazione": "2021",
            "codice_ean": clean_isbn,
            "rilegatura": "Rilegatura Senatoria",
            "collana": "Collana Imperiale",
            "copertina_url": copertina_default
        }
