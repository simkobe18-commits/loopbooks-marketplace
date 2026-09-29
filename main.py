import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database locale di riserva per ISBN frequenti[cite: 14]
BOOKS_DB = {
    "9788804668237": {
        "success": True,
        "nome_libro": "Le otto montagne",
        "prezzo_medio": "18.50 €",
        "descrizione": "Un romanzo profondo e intenso che racconta la storia di un'amicizia fraterna tra due ragazzi cresciuti in montagna, esplorando il legame con le radici, i padri e le scelte di vita.",
        "anno_pubblicazione": "2016",
        "anno_edizione": "2016",
        "codice_ean": "9788804668237",
        "rilegatura": "Brossura",
        "edizione": "Prima edizione",
        "collana": "Scrittori italiani e stranieri"
    }
}

def get_navbar(active_page="home"):
    home_class = 'text-sky-400 font-bold' if active_page == 'home' else 'text-slate-300 hover:text-sky-400'
    biblio_class = 'text-sky-400 font-bold' if active_page == 'biblioteca' else 'text-slate-300 hover:text-sky-400'
    vendita_class = 'text-sky-400 font-bold' if active_page == 'metti-in-vendita' else 'text-slate-300 hover:text-sky-400'
    
    return f"""
    <nav class="w-full max-w-6xl bg-slate-900/90 backdrop-blur border border-slate-800 rounded-2xl mb-8 px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4 shadow-xl sticky top-4 z-50">
        <div class="font-extrabold text-xl bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
            LoopBooks
        </div>
        <div class="flex items-center gap-6 text-sm font-medium">
            <a href="/" class="{home_class}">HOME</a>
            <a href="/biblioteca" class="{biblio_class}">LA MIA BIBLIOTECA</a>
            <a href="/metti-in-vendita" class="{vendita_class}">METTI IN VENDITA</a>
        </div>
        <div>
            <a href="#login" class="bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 font-semibold px-4 py-2 rounded-xl text-xs transition">
                LOG IN
            </a>
        </div>
    </nav>
    """

# --- 1. HOME PAGE ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Marketplace</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        {navbar}
        
        <div class="w-full max-w-6xl space-y-10">
            <!-- Banner Principale: Crea la tua biblioteca -->
            <div class="relative bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-8 overflow-hidden">
                <div class="space-y-4 max-w-xl">
                    <span class="bg-sky-500/10 text-sky-400 border border-sky-500/30 text-xs font-bold px-3 py-1 rounded-full">LoopBooks Marketplace</span>
                    <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight">CREA LA TUA BIBLIOTECA</h1>
                    <p class="text-slate-400 text-sm md:text-base leading-relaxed">
                        Gestisci la tua collezione, analizza i trend di mercato in tempo reale e metti in vendita i tuoi libri in pochi secondi grazie all'intelligenza artificiale.
                    </p>
                    <div class="pt-2">
                        <a href="/metti-in-vendita" class="inline-block bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-6 py-3.5 rounded-xl transition shadow-lg shadow-sky-500/25">
                            Inserisci i tuoi libri ora →
                        </a>
                    </div>
                </div>
                <div class="w-full md:w-80 h-48 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-center p-6 text-center text-slate-500 text-sm italic shadow-inner">
                    [ Immagine Vetrina / Libreria Digitale ]
                </div>
            </div>

            <!-- Pannello Filtri Avanzati (Genere & Prezzo Regolabile) -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4">
                    <h3 class="font-bold text-lg text-sky-400">Filtri di Ricerca Avanzati</h3>
                    <div class="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800">
                        <span class="text-xs font-medium text-slate-400">Prezzo massimo:</span>
                        <input type="range" id="priceRange" min="5" max="300" value="300" oninput="updatePrice(this.value)" class="accent-sky-500 cursor-pointer">
                        <span id="priceValue" class="text-emerald-400 font-bold text-sm w-16 text-right">300 €</span>
                    </div>
                </div>

                <div class="space-y-4 text-xs md:text-sm">
                    <!-- 📚 Narrativa e Letteratura -->
                    <div>
                        <span class="font-bold text-slate-200 block mb-2">📚 Narrativa e Letteratura</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="filterCategory('all')" class="bg-sky-500/20 text-sky-400 border border-sky-500/40 px-3 py-1.5 rounded-lg transition">Tutti</button>
                            <button onclick="filterCategory('contemporanei')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Romanzi contemporanei</button>
                            <button onclick="filterCategory('storica')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Narrativa storica</button>
                            <button onclick="filterCategory('gialli')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Gialli, Thriller e Noir</button>
                            <button onclick="filterCategory('fantasy')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Fantasy e Fantascienza</button>
                            <button onclick="filterCategory('horror')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Horror</button>
                            <button onclick="filterCategory('romance')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Narrativa rosa / Romance</button>
                            <button onclick="filterCategory('classici')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Classici della letteratura</button>
                        </div>
                    </div>

                    <!-- 💡 Saggistica e Cultura -->
                    <div>
                        <span class="font-bold text-slate-200 block mb-2">💡 Saggistica e Cultura</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="filterCategory('storia')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Storia e Biografie</button>
                            <button onclick="filterCategory('filosofia')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Filosofia e Religione</button>
                            <button onclick="filterCategory('scienza')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Scienze, Tecnologia e Natura</button>
                            <button onclick="filterCategory('sociologia')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Sociologia, Politica e Attualità</button>
                            <button onclick="filterCategory('arte')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Arte, Musica e Cinema</button>
                        </div>
                    </div>

                    <!-- 🌱 Crescita Personale e Lifestyle -->
                    <div>
                        <span class="font-bold text-slate-200 block mb-2">🌱 Crescita Personale e Lifestyle</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="filterCategory('selfhelp')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Self-help e Motivazione</button>
                            <button onclick="filterCategory('business')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Business e Finanza Personale</button>
                            <button onclick="filterCategory('benessere')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Benessere, Salute e Psicologia</button>
                            <button onclick="filterCategory('cucina')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Cucina, Enogastronomia e Vini</button>
                            <button onclick="filterCategory('viaggi')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Viaggi e Guide turistiche</button>
                        </div>
                    </div>

                    <!-- 🎨 Passioni, Hobby e Creatività -->
                    <div>
                        <span class="font-bold text-slate-200 block mb-2">🎨 Passioni, Hobby e Creatività</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="filterCategory('fumetti')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Fumetti, Manga e Graphic Novel</button>
                            <button onclick="filterCategory('design')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Libri illustrati e Design</button>
                            <button onclick="filterCategory('sport')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Sport e Giochi</button>
                            <button onclick="filterCategory('esoterismo')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Esoterismo e Astrologia</button>
                        </div>
                    </div>

                    <!-- 🧸 Bambini e Ragazzi (Young Adult) -->
                    <div>
                        <span class="font-bold text-slate-200 block mb-2">🧸 Bambini e Ragazzi (Young Adult)</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="filterCategory('infanzia')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Prima infanzia (0-3 anni)</button>
                            <button onclick="filterCategory('bambini')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Narrativa per bambini (4-8 anni)</button>
                            <button onclick="filterCategory('ragazzi')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Narrativa per ragazzi (9-13 anni)</button>
                            <button onclick="filterCategory('youngadult')" class="bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-3 py-1.5 rounded-lg transition">Young Adult e Fantasy (14+)</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sezione: Libri di tendenza -->
            <section class="space-y-4">
                <h2 class="text-xl font-bold border-l-4 border-sky-500 pl-3">Libri di tendenza</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-sky-500/50 transition" data-price="18.50">
                        <div>
                            <div class="h-32 bg-slate-950 rounded-lg mb-3 flex items-center justify-center text-xs text-slate-600">Copertina</div>
                            <h3 class="font-bold text-sm">Le otto montagne</h3>
                            <p class="text-xs text-slate-400 mt-1">Paolo Cognetti</p>
                        </div>
                        <div class="mt-4 flex items-center justify-between">
                            <span class="text-emerald-400 font-bold text-sm">18.50 €</span>
                            <a href="/metti-in-vendita" class="text-xs bg-sky-500/10 text-sky-400 px-2.5 py-1 rounded border border-sky-500/20">Dettagli</a>
                        </div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-sky-500/50 transition" data-price="14.00">
                        <div>
                            <div class="h-32 bg-slate-950 rounded-lg mb-3 flex items-center justify-center text-xs text-slate-600">Copertina</div>
                            <h3 class="font-bold text-sm">Il nome della rosa</h3>
                            <p class="text-xs text-slate-400 mt-1">Umberto Eco</p>
                        </div>
                        <div class="mt-4 flex items-center justify-between">
                            <span class="text-emerald-400 font-bold text-sm">14.00 €</span>
                            <a href="/metti-in-vendita" class="text-xs bg-sky-500/10 text-sky-400 px-2.5 py-1 rounded border border-sky-500/20">Dettagli</a>
                        </div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-sky-500/50 transition" data-price="16.50">
                        <div>
                            <div class="h-32 bg-slate-950 rounded-lg mb-3 flex items-center justify-center text-xs text-slate-600">Copertina</div>
                            <h3 class="font-bold text-sm">Omero, Iliade</h3>
                            <p class="text-xs text-slate-400 mt-1">Alessandro Baricco</p>
                        </div>
                        <div class="mt-4 flex items-center justify-between">
                            <span class="text-emerald-400 font-bold text-sm">16.50 €</span>
                            <a href="/metti-in-vendita" class="text-xs bg-sky-500/10 text-sky-400 px-2.5 py-1 rounded border border-sky-500/20">Dettagli</a>
                        </div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-sky-500/50 transition" data-price="15.00">
                        <div>
                            <div class="h-32 bg-slate-950 rounded-lg mb-3 flex items-center justify-center text-xs text-slate-600">Copertina</div>
                            <h3 class="font-bold text-sm">L'amica geniale</h3>
                            <p class="text-xs text-slate-400 mt-1">Elena Ferrante</p>
                        </div>
                        <div class="mt-4 flex items-center justify-between">
                            <span class="text-emerald-400 font-bold text-sm">15.00 €</span>
                            <a href="/metti-in-vendita" class="text-xs bg-sky-500/10 text-sky-400 px-2.5 py-1 rounded border border-sky-500/20">Dettagli</a>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Sezione: Migliori venditori -->
            <section class="space-y-4">
                <h2 class="text-xl font-bold border-l-4 border-indigo-500 pl-3">Migliori venditori</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between">
                        <div>
                            <h4 class="font-bold text-slate-200">Libreria Antiquaria Duomo</h4>
                            <p class="text-xs text-slate-400 mt-0.5">1.240 vendite • 4.9 ★</p>
                        </div>
                        <a href="/venditore/antiquaria-duomo" class="bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold px-3 py-2 rounded-lg transition">Visita profilo →</a>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between">
                        <div>
                            <h4 class="font-bold text-slate-200">Brera Bookshop Milano</h4>
                            <p class="text-xs text-slate-400 mt-0.5">980 vendite • 4.8 ★</p>
                        </div>
                        <a href="/venditore/brera-bookshop" class="bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold px-3 py-2 rounded-lg transition">Visita profilo →</a>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between">
                        <div>
                            <h4 class="font-bold text-slate-200">Porteno Books & Rare</h4>
                            <p class="text-xs text-slate-400 mt-0.5">650 vendite • 5.0 ★</p>
                        </div>
                        <a href="/venditore/porteno-books" class="bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold px-3 py-2 rounded-lg transition">Visita profilo →</a>
                    </div>
                </div>
            </section>

            <!-- Sezione: Libri per te -->
            <section class="space-y-4">
                <h2 class="text-xl font-bold border-l-4 border-sky-400 pl-3">Libri per te</h2>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="12.00">
                        <h3 class="font-bold text-sm">Così parlò Bellavista</h3>
                        <p class="text-xs text-slate-400 mt-1">Luciano De Crescenzo</p>
                        <span class="text-emerald-400 font-bold text-xs mt-3 block">12.00 €</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="11.50">
                        <h3 class="font-bold text-sm">Fontamara</h3>
                        <p class="text-xs text-slate-400 mt-1">Ignazio Silone</p>
                        <span class="text-emerald-400 font-bold text-xs mt-3 block">11.50 €</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="13.00">
                        <h3 class="font-bold text-sm">Se questo è un uomo</h3>
                        <p class="text-xs text-slate-400 mt-1">Primo Levi</p>
                        <span class="text-emerald-400 font-bold text-xs mt-3 block">13.00 €</span>
                    </div>
                </div>
            </section>

            <!-- Sezione: Libri rari -->
            <section class="space-y-4">
                <h2 class="text-xl font-bold border-l-4 border-amber-500 pl-3">Libri rari</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center" data-price="145.00">
                        <div>
                            <span class="text-[10px] bg-amber-950 text-amber-400 border border-amber-800 px-2 py-0.5 rounded font-mono">Edizione Limitata 1952</span>
                            <h3 class="font-bold text-sm mt-2">I Promessi Sposi (Prima Ed. Illustrata)</h3>
                        </div>
                        <span class="text-emerald-400 font-bold">145.00 €</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center" data-price="290.00">
                        <div>
                            <span class="text-[10px] bg-amber-950 text-amber-400 border border-amber-800 px-2 py-0.5 rounded font-mono">Collezione Rara</span>
                            <h3 class="font-bold text-sm mt-2">Divina Commedia (Commento del '300)</h3>
                        </div>
                        <span class="text-emerald-400 font-bold">290.00 €</span>
                    </div>
                </div>
            </section>

            <!-- Sezione: Oggettistica per consegne -->
            <section class="space-y-4 pb-12">
                <h2 class="text-xl font-bold border-l-4 border-emerald-500 pl-3">Oggettistica per consegne</h2>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="8.50">
                        <h3 class="font-bold text-sm">Scatole protettive rigide per libri (Pack da 5)</h3>
                        <p class="text-xs text-slate-400 mt-1">Cartone rinforzato anti-urto</p>
                        <span class="text-sky-400 font-bold text-xs mt-3 block">8.50 €</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="6.00">
                        <h3 class="font-bold text-sm">Buste imbottite in carta ecologica</h3>
                        <p class="text-xs text-slate-400 mt-1">Formato Standard (Pack da 10)</p>
                        <span class="text-sky-400 font-bold text-xs mt-3 block">6.00 €</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl" data-price="4.50">
                        <h3 class="font-bold text-sm">Nastro adesivo personalizzato LoopBooks</h3>
                        <p class="text-xs text-slate-400 mt-1">Alta tenuta di sicurezza</p>
                        <span class="text-sky-400 font-bold text-xs mt-3 block">4.50 €</span>
                    </div>
                </div>
            </section>
        </div>

        <script>
            function updatePrice(val) {
                document.getElementById('priceValue').innerText = val + " €";
                const maxPrice = parseFloat(val);
                
                const items = document.querySelectorAll('[data-price]');
                items.forEach(item => {
                    const price = parseFloat(item.getAttribute('data-price'));
                    if (price <= maxPrice) {
                        item.style.display = "";
                    } else {
                        item.style.display = "none";
                    }
                });
            }

            function filterCategory(category) {
                console.log("Filtro categoria selezionato: ", category);
            }
        </script>
    </body>
    </html>
    """

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
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        {navbar}
        <div class="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
            <h1 class="text-2xl font-extrabold mb-2 text-slate-100">La mia biblioteca</h1>
            <p class="text-slate-400 text-sm mb-6">I tuoi libri salvati e la panoramica della tua collezione personale.</p>
            
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-8 text-center text-slate-500">
                Non hai ancora aggiunto libri alla tua biblioteca personale. Vai su <a href="/metti-in-vendita" class="text-sky-400 underline">Metti in vendita</a> per iniziare.
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
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        NAVBAR_PLACEHOLDER
        <div class="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
            <h1 class="text-2xl md:text-3xl font-extrabold text-center mb-2 bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
                LoopBooks Intelligence[cite: 14]
            </h1>
            <p class="text-slate-400 text-center text-sm mb-6">
                Inserisci il codice ISBN per estrarre la scheda tecnica completa e il grafico storico dei prezzi[cite: 14].
            </p>
            <div class="flex gap-3 mb-6">
                <input type="text" id="isbn" value="9788804668237" placeholder="Es. 9788804668237" 
                    class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-sky-500 transition">
                <button id="search-btn" onclick="searchBook()" 
                    class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-6 py-3 rounded-xl transition shadow-lg shadow-sky-500/25">
                    Cerca
                </button>
            </div>
            <div id="loader" class="hidden text-center py-8 text-sky-400 font-medium animate-pulse">
                Estrazione dati del libro in corso con Gemini[cite: 14]...
            </div>
            <div id="error-box" class="hidden bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-xl mb-6 text-sm">
                <strong class="font-bold">Errore di sistema:</strong> <span id="error-text">-</span>
            </div>
            <div id="result" class="hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950 p-5 rounded-xl border border-slate-800 text-sm">
                    <div><span class="text-sky-400 font-semibold">Nome del libro:</span> <span id="res-nome">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Prezzo medio:</span> <span id="res-prezzo" class="text-emerald-400 font-bold">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Codice EAN:</span> <span id="res-ean">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Anno pubblicazione:</span> <span id="res-anno-pub">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Anno edizione:</span> <span id="res-anno-ed">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Rilegatura:</span> <span id="res-rilegatura">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Edizione:</span> <span id="res-edizione">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Collana:</span> <span id="res-collana">-</span></div>
                    <div class="md:col-span-2"><span class="text-sky-400 font-semibold">Descrizione (riassunto):</span> <p id="res-desc" class="text-slate-300 mt-1 leading-relaxed">-</p></div>
                </div>
                <div class="bg-slate-950 p-5 rounded-xl border border-slate-800">
                    <h3 class="text-sm font-semibold text-slate-400 mb-3 flex items-center justify-between">
                        <span>Grafico delle vendite e prezzo medio nel tempo[cite: 14]</span>
                        <span class="text-xs text-sky-400 bg-sky-950 px-2 py-1 rounded border border-sky-800">Trend CardMarket Style</span>
                    </h3>
                    <div class="relative h-64 w-full">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        <script>
            let myChart = null;
            async function searchBook() {
                const isbn = document.getElementById('isbn').value.trim();
                const btn = document.getElementById('search-btn');
                const loader = document.getElementById('loader');
                const resultDiv = document.getElementById('result');
                const errorBox = document.getElementById('error-box');
                
                if (!isbn) {
                    alert("Inserisci un codice ISBN valido.");
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
                        document.getElementById('res-anno-ed').innerText = data.anno_edizione || "-";
                        document.getElementById('res-rilegatura').innerText = data.rilegatura || "-";
                        document.getElementById('res-edizione').innerText = data.edizione || "-";
                        document.getElementById('res-collana').innerText = data.collana || "-";
                        document.getElementById('res-desc').innerText = data.descrizione || "-";
                        resultDiv.classList.remove('hidden');
                        renderChart(data.storico_prezzi);
                    } else {
                        document.getElementById('error-text').innerText = data.error || "Libro non trovato o codice ISBN non valido.";
                        errorBox.classList.remove('hidden');
                    }
                } catch (e) {
                    alert("Errore di connessione al server.");
                } finally {
                    btn.disabled = false;
                    loader.classList.add('hidden');
                }
            }
            function renderChart(storico) {
                const ctx = document.getElementById('priceChart').getContext('2d');
                if (myChart) myChart.destroy();
                const labels = storico?.labels || ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set'];
                const prices = storico?.prices || [14.0, 14.5, 15.0, 14.8, 15.5, 16.0, 15.8, 16.2, 16.5];
                myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Prezzo Medio (€)',
                            data: prices,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3,
                            pointBackgroundColor: '#38bdf8'
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
        <title>LoopBooks - Profilo Venditore</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        {navbar}
        <div class="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
            <a href="/" class="text-xs text-sky-400 hover:underline mb-4 inline-block">← Torna alla Home</a>
            <h1 class="text-3xl font-extrabold text-slate-100 mb-2">{nome_venditore}</h1>
            <p class="text-slate-400 text-sm mb-6">Venditore verificato • Valutazione 4.9/5 (1.200+ recensioni positive)</p>
            
            <h3 class="text-lg font-bold mb-4 text-sky-400">Catalogo Libri in Vendita</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                    <h4 class="font-bold text-sm">Le otto montagne</h4>
                    <p class="text-xs text-slate-400">Condizioni: Ottime</p>
                    <span class="text-emerald-400 font-bold text-sm mt-2 block">18.50 €</span>
                </div>
                <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                    <h4 class="font-bold text-sm">Il nome della rosa</h4>
                    <p class="text-xs text-slate-400">Condizioni: Come nuovo</p>
                    <span class="text-emerald-400 font-bold text-sm mt-2 block">14.00 €</span>
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
    
    if clean_isbn in BOOKS_DB:
        res = BOOKS_DB[clean_isbn].copy()
        res["storico_prezzi"] = {
            "labels": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set"],
            "prices": [16.0, 16.5, 17.0, 16.8, 17.2, 17.8, 18.0, 18.2, 18.5]
        }
        return res
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "error": "Chiave GEMINI_API_KEY non configurata su Render."}
        
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Analizza il codice ISBN: {clean_isbn}. Restituisci ESCLUSIVAMENTE un oggetto JSON valido con queste chiavi e informazioni accurate:
        {{
            "success": true,
            "nome_libro": "Titolo completo del libro",
            "prezzo_medio": "Prezzo medio stimato in formato euro (es. 15.00 €)",
            "descrizione": "Un dettagliato riassunto o sinossi del libro",
            "anno_pubblicazione": "Anno di prima pubblicazione",
            "anno_edizione": "Anno di questa specifica edizione",
            "codice_ean": "{clean_isbn}",
            "rilegatura": "Tipo di rilegatura (es. Brossura, Copertina rigida)",
            "edizione": "Numero o tipo di edizione (es. Prima edizione)",
            "collana": "Nome della collana editoriale o editore",
            "storico_prezzi": {{
                "labels": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set"],
                "prices": [14.0, 14.5, 15.0, 14.8, 15.5, 16.0, 15.8, 16.2, 16.5]
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
        print(f"Errore durante l'interrogazione di Gemini: {e}")
        return {"success": False, "error": "Impossibile recuperare i dati per questo ISBN tramite l'intelligenza artificiale."}
