import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database esteso di volumi con i rispettivi generi
BOOKS_DATABASE = [
    {
        "id": "9788806200085",
        "titolo": "Il Nome della Rosa",
        "autore": "Umberto Eco",
        "genere": "mistero",
        "genere_label": "Mistero & Noir",
        "prezzo": "14.00 Sesterzi",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg",
        "descrizione": "Un monastero isolato, un segreto custodito tra i codici miniati e un crimine che scuote l'ordine monastico."
    },
    {
        "id": "9788804668237",
        "titolo": "Le otto montagne",
        "autore": "Paolo Cognetti",
        "genere": "narrativa",
        "genere_label": "Narrativa",
        "prezzo": "18.50 Sesterzi",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg",
        "descrizione": "Un romanzo profondo e intenso che racconta la storia di un'amicizia fraterna tra due ragazzi cresciuti in montagna."
    },
    {
        "id": "9788806231362",
        "titolo": "Omero, Iliade",
        "autore": "Alessandro Baricco",
        "genere": "storia",
        "genere_label": "Filosofia & Storia",
        "prezzo": "16.50 Sesterzi",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806231362-L.jpg",
        "descrizione": "La rilettura appassionante del più grande poema epico di tutti i tempi, focalizzata sul destino e la guerra."
    },
    {
        "id": "9788866325087",
        "titolo": "L'amica geniale",
        "autore": "Elena Ferrante",
        "genere": "narrativa",
        "genere_label": "Narrativa",
        "prezzo": "15.00 Sesterzi",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788866325087-L.jpg",
        "descrizione": "La storia di un'amicizia complessa e duratura sullo sfondo di una Napoli popolare e in evoluzione."
    }
]

def get_navbar(active_page="home"):
    home_class = 'bg-[#7a1c1c] text-[#f3ead8] border-[#d4af37]' if active_page == 'home' else 'bg-[#1e1a16] text-slate-300 border-[#d4af37]/30 hover:border-[#d4af37]'
    biblio_class = 'bg-[#7a1c1c] text-[#f3ead8] border-[#d4af37]' if active_page == 'biblioteca' else 'bg-[#1e1a16] text-slate-300 border-[#d4af37]/30 hover:border-[#d4af37]'
    vendita_class = 'bg-[#7a1c1c] text-[#f3ead8] border-[#d4af37]' if active_page == 'metti-in-vendita' else 'bg-[#1e1a16] text-slate-300 border-[#d4af37]/30 hover:border-[#d4af37]'
    
    return f"""
    <header class="w-full bg-[#14110e] border-b-2 border-[#d4af37]/40 py-6 px-8 shadow-2xl flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="text-center md:text-left">
            <span class="text-xs uppercase tracking-[0.3em] text-[#d4af37] font-serif block mb-1">Bibliotheca Imperiale</span>
            <h1 class="text-2xl md:text-3xl font-serif font-black tracking-widest text-[#f3ead8]">ROMA BIBLIOTHECA</h1>
        </div>
        <nav class="flex flex-wrap justify-center gap-3 font-serif text-xs uppercase tracking-wider">
            <a href="/" class="{home_class} px-5 py-2.5 rounded border transition shadow">Portico Principale</a>
            <a href="/biblioteca" class="{biblio_class} px-5 py-2.5 rounded border transition shadow">La Mia Raccolta</a>
            <a href="/metti-in-vendita" class="{vendita_class} px-5 py-2.5 rounded border transition shadow">Bottega Scriba</a>
        </nav>
    </header>
    """

# --- 1. HOME PAGE CON FILTRI PER GENERE ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    
    books_html = ""
    for b in BOOKS_DATABASE:
        books_html += f"""
        <div class="pergamena p-4 rounded-xl hover:border-[#d4af37] transition cursor-pointer group shadow-lg flex flex-col justify-between book-item" data-genere="{b['genere']}">
            <div>
                <div class="h-60 bg-black rounded mb-4 overflow-hidden border border-[#d4af37]/30">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <span class="text-[10px] uppercase tracking-widest text-[#d4af37] font-serif">{b['genere_label']}</span>
                <h4 class="font-bold text-base text-[#f3ead8] mt-1 group-hover:text-[#d4af37] transition">{b['titolo']}</h4>
                <p class="text-xs text-slate-400 italic mb-2">{b['autore']}</p>
                <p class="text-xs text-slate-300 line-clamp-2">{b['descrizione']}</p>
            </div>
            <div class="mt-4 pt-3 border-t border-[#d4af37]/20 flex justify-between items-center">
                <span class="text-xs font-bold text-emerald-400">{b['prezzo']}</span>
                <span class="text-xs text-[#d4af37] underline font-serif">Esamina →</span>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Roma Bibliotheca - Portico Principale</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0f0d0b; color: #e2d9c5; font-family: 'Georgia', serif; }}
            .pergamena {{ background: linear-gradient(135deg, #1b1713 0%, #14110e 100%); border: 1px solid rgba(212, 175, 55, 0.3); }}
            .filter-btn.active {{ background-color: #7a1c1c; color: #d4af37; border-color: #d4af37; }}
        </style>
    </head>
    <body class="min-h-screen pb-20 selection:bg-[#7a1c1c] selection:text-[#d4af37]">
        {navbar}
        
        <main class="max-w-6xl mx-auto px-6 py-12 space-y-12">
            
            <div class="pergamena rounded-2xl p-8 md:p-12 shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center gap-8 border-2 border-[#d4af37]/40">
                <div class="absolute -right-16 -bottom-16 text-9xl opacity-5 select-none font-serif text-[#d4af37]">XII</div>
                <div class="w-48 h-64 flex-shrink-0 bg-black rounded shadow-2xl border border-[#d4af37]/30 overflow-hidden">
                    <img src="https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg" class="w-full h-full object-cover">
                </div>
                <div class="space-y-4 flex-1 text-center md:text-left">
                    <span class="bg-[#7a1c1c] text-[#d4af37] border border-[#d4af37]/40 text-[10px] font-serif font-bold uppercase px-3 py-1 rounded tracking-widest">Tomo Consigliato dal Senato</span>
                    <h2 class="text-3xl font-serif font-black text-[#f3ead8]">Il Nome della Rosa</h2>
                    <p class="text-slate-300 text-sm italic leading-relaxed">
                        "Un monastero isolato, un segreto custodito tra i codici miniati e un crimine che scuote l'ordine monastico. Esamina i volumi attraverso i registri della bottega."
                    </p>
                    <div class="pt-2 flex flex-wrap justify-center md:justify-start gap-4">
                        <a href="/metti-in-vendita" class="bg-[#d4af37] hover:bg-[#e6c250] text-[#0f0d0b] font-serif font-bold px-6 py-3 rounded text-xs uppercase tracking-widest transition shadow-lg">
                            ✦ Esamina Nuovo Tomo
                        </a>
                    </div>
                </div>
            </div>

            <div class="space-y-6">
                <div class="border-b border-[#d4af37]/20 pb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <h3 class="text-xl font-serif font-bold text-[#d4af37]">Scaffali della Sapienza (Filtri)</h3>
                    
                    <div class="flex flex-wrap gap-2 text-xs font-serif">
                        <button onclick="filterBooks('tutti')" id="btn-tutti" class="filter-btn active px-4 py-2 rounded border border-[#d4af37]/40 bg-[#1e1a16] text-[#f3ead8] transition">Tutti i Tomi</button>
                        <button onclick="filterBooks('mistero')" id="btn-mistero" class="filter-btn px-4 py-2 rounded border border-[#d4af37]/30 bg-[#1e1a16] text-slate-300 transition">Mistero & Noir</button>
                        <button onclick="filterBooks('narrativa')" id="btn-narrativa" class="filter-btn px-4 py-2 rounded border border-[#d4af37]/30 bg-[#1e1a16] text-slate-300 transition">Narrativa</button>
                        <button onclick="filterBooks('storia')" id="btn-storia" class="filter-btn px-4 py-2 rounded border border-[#d4af37]/30 bg-[#1e1a16] text-slate-300 transition">Storia & Epica</button>
                    </div>
                </div>

                <div id="books-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {books_html}
                </div>
            </div>

        </main>

        <script>
            function filterBooks(genere) {
                document.querySelectorAll('.filter-btn').forEach(function(btn) {
                    btn.classList.remove('active');
                    btn.style.backgroundColor = '#1e1a16';
                    btn.style.color = '#cbd5e1';
                });
                var activeBtn = document.getElementById('btn-'.concat(genere));
                if (activeBtn) {
                    activeBtn.classList.add('active');
                    activeBtn.style.backgroundColor = '#7a1c1c';
                    activeBtn.style.color = '#d4af37';
                }

                var items = document.querySelectorAll('.book-item');
                items.forEach(function(item) {
                    var itemGenere = item.getAttribute('data-genere');
                    if (genere === 'tutti' || itemGenere === genere) {
                        item.style.display = 'flex';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content

# --- 2. LA MIA RACCOLTA ---
@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page():
    navbar = get_navbar('biblioteca')
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>La Mia Raccolta - Roma Bibliotheca</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0f0d0b; color: #e2d9c5; font-family: 'Georgia', serif; }}
            .pergamena {{ background: linear-gradient(135deg, #1b1713 0%, #14110e 100%); border: 1px solid rgba(212, 175, 55, 0.3); }}
        </style>
    </head>
    <body class="min-h-screen pb-20 selection:bg-[#7a1c1c] selection:text-[#d4af37]">
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="pergamena rounded-2xl p-8 shadow-2xl border-2 border-[#d4af37]/40 space-y-6">
                <div class="border-b border-[#d4af37]/20 pb-4">
                    <h2 class="text-2xl font-serif font-black text-[#d4af37]">La Raccolta Privata</h2>
                    <p class="text-slate-400 text-xs italic mt-1">I rotoli e i codici custoditi nella tua domus.</p>
                </div>
                <div class="bg-[#0f0d0b] border border-[#d4af37]/20 rounded-xl p-12 text-center text-slate-500 italic font-serif">
                    Nessun manoscritto registrato nella tua raccolta. Visita la <a href="/metti-in-vendita" class="text-[#d4af37] underline font-bold">Bottega Scriba</a> per aggiungere volumi.
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- 3. BOTTEGA SCRIBA (ISBN & GEMINI) ---
@app.get("/metti-in-vendita", response_class=HTMLResponse)
async def metti_in_vendita_page():
    navbar = get_navbar('metti-in-vendita')
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bottega Scriba - Roma Bibliotheca</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #0f0d0b; color: #e2d9c5; font-family: 'Georgia', serif; }
            .pergamena { background: linear-gradient(135deg, #1b1713 0%, #14110e 100%); border: 1px solid rgba(212, 175, 55, 0.3); }
        </style>
    </head>
    <body class="min-h-screen pb-20 selection:bg-[#7a1c1c] selection:text-[#d4af37]">
        NAVBAR_PLACEHOLDER
        
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="pergamena rounded-2xl p-8 md:p-12 shadow-2xl border-2 border-[#d4af37]/40 space-y-8">
                
                <div class="text-center space-y-2">
                    <span class="text-xs uppercase tracking-widest text-[#d4af37] font-serif">Archivio Centrale</span>
                    <h2 class="text-3xl font-serif font-black text-[#f3ead8]">Bottega dello Scriba</h2>
                    <p class="text-slate-400 text-xs italic max-w-lg mx-auto">
                        Immetti il codice ISBN del tomo per interrogare gli archivi imperiali ed estrarre la perizia di stima e la copertina originale.
                    </p>
                </div>

                <div class="flex flex-col sm:flex-row gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Es. 9788804668237" 
                        class="flex-1 bg-[#0f0d0b] border border-[#d4af37]/40 rounded-lg px-4 py-3 text-[#f3ead8] focus:outline-none focus:border-[#d4af37] transition font-serif text-sm">
                    <button id="search-btn" onclick="searchBook()" 
                        class="bg-[#7a1c1c] hover:bg-[#992424] text-[#d4af37] border border-[#d4af37]/50 font-serif font-bold px-8 py-3 rounded-lg transition shadow-lg text-xs uppercase tracking-widest">
                        Interroga Archivi
                    </button>
                </div>

                <div id="loader" class="hidden text-center py-8 text-[#d4af37] font-serif italic animate-pulse text-sm">
                    Consultazione dei registri del Senato in corso...
                </div>

                <div id="error-box" class="hidden bg-red-950/40 border border-red-800 text-red-200 p-4 rounded-lg text-xs font-serif">
                    <strong class="font-bold">Nota dello Scriba:</strong> <span id="error-text">-</span>
                </div>

                <div id="result" class="hidden grid grid-cols-1 md:grid-cols-3 gap-8 bg-[#0f0d0b] p-6 rounded-xl border border-[#d4af37]/30">
                    <div class="flex flex-col items-center justify-center">
                        <img id="res-copertina" src="" alt="Copertina" class="w-44 h-60 object-cover rounded border border-[#d4af37]/40 shadow-2xl mb-3">
                        <span class="text-[9px] text-slate-400 uppercase tracking-widest italic font-serif">Tomo Verificato</span>
                    </div>
                    <div class="md:col-span-2 space-y-3 text-xs font-serif">
                        <div><span class="text-[#d4af37] font-semibold">Titolo dell'Opera:</span> <span id="res-nome" class="font-bold text-base text-white block mt-0.5">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Stima di Mercato:</span> <span id="res-prezzo" class="text-emerald-400 font-bold text-sm">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Codice EAN:</span> <span id="res-ean" class="text-slate-300">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Anno di Stampa:</span> <span id="res-anno-pub" class="text-slate-300">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Rilegatura:</span> <span id="res-rilegatura" class="text-slate-300">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Collana:</span> <span id="res-collana" class="text-slate-300">-</span></div>
                        <div><span class="text-[#d4af37] font-semibold">Sinossi:</span> <p id="res-desc" class="text-slate-300 mt-1 leading-relaxed italic">-</p></div>
                    </div>
                </div>

            </div>
        </main>

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
                        document.getElementById('res-copertina').src = data.copertina_url || 'https://covers.openlibrary.org/b/isbn/' + isbn + '-L.jpg';
                        
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

# --- 4. API DI RICERCA ISBN ---
@app.get("/api/search")
async def api_search(isbn: str):
    clean_isbn = re.sub(r'[^\dxX]', '', isbn)
    if not clean_isbn:
        return {"success": False, "error": "ISBN non valido."}
    
    copertina_default = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {
                "success": True,
                "nome_libro": f"Tomo Imperiale {clean_isbn}",
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
            "prezzo_medio": "15.00 Sesterzi",
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
