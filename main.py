import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database esteso di volumi in stile Netflix
BOOKS_DATABASE = [
    {
        "id": "9788806200085",
        "titolo": "Il Nome della Rosa",
        "autore": "Umberto Eco",
        "prezzo": "14.00 €",
        "valutazione": "4.9 ★",
        "condizione": "Ottime condizioni",
        "editore": "Bompiani",
        "collana": "Tascabili",
        "codice_ean": "9788806200085",
        "anno_edizione": "2015",
        "anno_pubblicazione": "1980",
        "descrizione": "Un monastero isolato, un segreto custodito tra i codici miniati e un crimine che scuote l'ordine monastico.",
        "venditore": "Libreria Antiquaria Roma",
        "venditore_posizione": "Roma (RM)",
        "venditore_valutazione": "4.9 ★ (1.2k recensioni)",
        "sezione": "tendenza",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg"
    },
    {
        "id": "9788804668237",
        "titolo": "Le otto montagne",
        "autore": "Paolo Cognetti",
        "prezzo": "18.50 €",
        "valutazione": "4.8 ★",
        "condizione": "Come nuovo",
        "editore": "Einaudi",
        "collana": "SuperET",
        "codice_ean": "9788804668237",
        "anno_edizione": "2018",
        "anno_pubblicazione": "2016",
        "descrizione": "Un romanzo profondo e intenso che racconta la storia di un'amicizia fraterna tra due ragazzi cresciuti in montagna.",
        "venditore": "LoopBooks Official",
        "venditore_posizione": "Milano (MI)",
        "venditore_valutazione": "4.8 ★ (850 recensioni)",
        "sezione": "migliori-venditori",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg"
    },
    {
        "id": "9788806231362",
        "titolo": "Omero, Iliade",
        "autore": "Alessandro Baricco",
        "prezzo": "16.50 €",
        "valutazione": "4.7 ★",
        "condizione": "Buone condizioni",
        "editore": "Feltrinelli",
        "collana": "I Narratori",
        "codice_ean": "9788806231362",
        "anno_edizione": "2020",
        "anno_pubblicazione": "2004",
        "descrizione": "La rilettura appassionante del più grande poema epico di tutti i tempi, focalizzata sul destino e la guerra.",
        "venditore": "Antica Stamperia",
        "venditore_posizione": "Firenze (FI)",
        "venditore_valutazione": "4.6 ★ (410 recensioni)",
        "sezione": "libri-per-te",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806231362-L.jpg"
    },
    {
        "id": "9788866325087",
        "titolo": "L'amica geniale",
        "autore": "Elena Ferrante",
        "prezzo": "15.00 €",
        "valutazione": "5.0 ★",
        "condizione": "Perfetto",
        "editore": "Edizioni E/O",
        "collana": "Dal Mondo",
        "codice_ean": "9788866325087",
        "anno_edizione": "2016",
        "anno_pubblicazione": "2011",
        "descrizione": "La storia di un'amicizia complessa e duratura sullo sfondo di una Napoli popolare e in evoluzione.",
        "venditore": "BookBaron Milano",
        "venditore_posizione": "Milano (MI)",
        "venditore_valutazione": "5.0 ★ (3.4k recensioni)",
        "sezione": "migliori-venditori",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788866325087-L.jpg"
    },
    {
        "id": "9788804707035",
        "titolo": "Codice Atlantico (Raro)",
        "autore": "Leonardo da Vinci",
        "prezzo": "120.00 €",
        "valutazione": "5.0 ★",
        "condizione": "Rarità da collezione",
        "editore": "Giunti Editore",
        "collana": "Edizioni Pregiate",
        "codice_ean": "9788804707035",
        "anno_edizione": "2001",
        "anno_pubblicazione": "1490",
        "descrizione": "Raccolta di disegni e scritti di Leonardo da Vinci, edizione facsimile di inestimabile valore storico.",
        "venditore": "Rari & Co.",
        "venditore_posizione": "Venezia (VE)",
        "venditore_valutazione": "4.9 ★ (95 recensioni)",
        "sezione": "libri-rari",
        "copertina": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"
    }
]

def get_navbar(active_page="home"):
    return f"""
    <header class="w-full bg-[#141414] border-b border-neutral-800 py-4 px-8 sticky top-0 z-50 flex justify-between items-center shadow-xl">
        <div class="flex items-center gap-8">
            <a href="/" class="text-red-600 font-black text-2xl tracking-tighter uppercase font-sans">LOOPBOOKS</a>
            <nav class="hidden md:flex items-center gap-6 text-sm font-medium">
                <a href="/" class="{'text-white font-bold' : active_page == 'home'} text-neutral-300 hover:text-white transition">HOME</a>
                <a href="/biblioteca" class="{'text-white font-bold' : active_page == 'biblioteca'} text-neutral-300 hover:text-white transition">LA MIA BIBLIOTECA</a>
                <a href="/metti-in-vendita" class="{'text-white font-bold' : active_page == 'metti-in-vendita'} text-neutral-300 hover:text-white transition">METTI IN VENDITA</a>
            </nav>
        </div>
        <div>
            <a href="/metti-in-vendita" class="bg-red-600 hover:bg-red-700 text-white font-bold px-4 py-2 rounded text-sm transition shadow-lg">
                LOG IN
            </a>
        </div>
    </header>
    """

# --- 1. HOME PAGE STILE NETFLIX ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    
    # Funzione per generare le card stile Netflix
    def render_row(sezione_key):
        filtered = [b for b in BOOKS_DATABASE if b["sezione"] == sezione_key or sezione_key == "tutti"]
        html = ""
        for b in filtered:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[200px] md:min-w-[220px] bg-neutral-900 rounded-md overflow-hidden shadow-lg hover:scale-105 transition duration-300 flex-shrink-0 group border border-neutral-800">
                <div class="h-64 bg-black overflow-hidden relative">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:opacity-90 transition">
                    <span class="absolute bottom-2 right-2 bg-black/80 text-amber-400 text-xs px-2 py-0.5 rounded font-bold">{b['valutazione']}</span>
                </div>
                <div class="p-3 space-y-1">
                    <h4 class="font-bold text-sm text-white truncate">{b['titolo']}</h4>
                    <p class="text-xs text-neutral-400">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-2">
                        <span class="text-emerald-400 font-bold text-sm">{b['prezzo']}</span>
                        <span class="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded">{b['condizione']}</span>
                    </div>
                </div>
            </a>
            """
        return html

    tendenza_html = render_row("tendenza")
    venditori_html = render_row("migliori-venditori")
    per_te_html = render_row("libri-per-te")
    rari_html = render_row("libri-rari")

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Streaming di Cultura</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #141414; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
            .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        
        <!-- HERO / BANNER PRINCIPALE -->
        <div class="relative w-full h-[500px] bg-cover bg-center flex items-end p-8 md:p-16" style="background-image: linear-gradient(to top, #141414, rgba(20,20,20,0.4)), url('https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg');">
            <div class="max-w-2xl space-y-4">
                <span class="bg-red-600 text-white text-xs font-bold px-3 py-1 uppercase tracking-widest rounded">In Primo Piano</span>
                <h1 class="text-4xl md:text-6xl font-black tracking-tight">CREA LA TUA BIBLIOTECA</h1>
                <p class="text-neutral-300 text-sm md:text-base leading-relaxed">
                    Esplora migliaia di volumi rari, bestseller e perle letterarie. Gestisci la tua collezione e scambia volumi in tutta sicurezza.
                </p>
                <div class="flex gap-4 pt-2">
                    <a href="/metti-in-vendita" class="bg-white hover:bg-neutral-200 text-black font-bold px-8 py-3 rounded flex items-center gap-2 transition shadow-lg">
                        ▶ Metti in Vendita
                    </a>
                </div>
            </div>
        </div>

        <main class="px-6 md:px-12 space-y-10 mt-6">
            
            <!-- FILTRI DI RICERCA RAPIDA -->
            <div class="flex items-center gap-3 overflow-x-auto hide-scroll py-2">
                <span class="text-xs font-bold uppercase tracking-widest text-neutral-400 mr-2">Filtri:</span>
                <a href="#tendenza" class="bg-neutral-800 hover:bg-neutral-700 text-xs px-4 py-2 rounded-full border border-neutral-700 whitespace-nowrap transition">🔥 Di Tendenza</a>
                <a href="#migliori" class="bg-neutral-800 hover:bg-neutral-700 text-xs px-4 py-2 rounded-full border border-neutral-700 whitespace-nowrap transition">⭐ Migliori Venditori</a>
                <a href="#per-te" class="bg-neutral-800 hover:bg-neutral-700 text-xs px-4 py-2 rounded-full border border-neutral-700 whitespace-nowrap transition">🎯 Consigliati per Te</a>
                <a href="#rari" class="bg-neutral-800 hover:bg-neutral-700 text-xs px-4 py-2 rounded-full border border-neutral-700 whitespace-nowrap transition">💎 Libri Rari</a>
            </div>

            <!-- SEZIONE 1: LIBRI DI TENDENZA -->
            <section id="tendenza" class="space-y-4">
                <h3 class="text-xl font-bold tracking-wide">Libri di Tendenza</h3>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {tendenza_html}
                </div>
            </section>

            <!-- SEZIONE 2: MIGLIORI VENDITORI -->
            <section id="migliori" class="space-y-4">
                <h3 class="text-xl font-bold tracking-wide">Migliori Venditori</h3>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {venditori_html}
                </div>
            </section>

            <!-- SEZIONE 3: LIBRI PER TE -->
            <section id="per-te" class="space-y-4">
                <h3 class="text-xl font-bold tracking-wide">Libri per Te</h3>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {per_te_html}
                </div>
            </section>

            <!-- SEZIONE 4: LIBRI RARI -->
            <section id="rari" class="space-y-4">
                <h3 class="text-xl font-bold tracking-wide">Libri Rari & Collezioni</h3>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {rari_html}
                </div>
            </section>

        </main>
    </body>
    </html>
    """

# --- 2. PAGINA DETTAGLIO LIBRO ---
@app.get("/libro/{libro_id}", response_class=HTMLResponse)
async def libro_detail_page(libro_id: str):
    navbar = get_navbar('home')
    
    # Trova il libro o usa il primo come default
    libro = next((b for b in BOOKS_DATABASE if b["id"] == libro_id), BOOKS_DATABASE[0])
    
    # Libri simili (tutti tranne quello corrente)
    simili_html = ""
    for b in [x for x in BOOKS_DATABASE if x["id"] != libro_id]:
        simili_html += f"""
        <a href="/libro/{b['id']}" class="min-w-[200px] bg-neutral-900 rounded-md overflow-hidden shadow hover:scale-105 transition flex-shrink-0 border border-neutral-800">
            <div class="h-48 bg-black overflow-hidden">
                <img src="{b['copertina']}" class="w-full h-full object-cover">
            </div>
            <div class="p-3">
                <h4 class="font-bold text-sm text-white truncate">{b['titolo']}</h4>
                <p class="text-xs text-neutral-400">{b['prezzo']}</p>
            </div>
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{libro['titolo']} - LoopBooks</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #141414; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        
        <main class="max-w-6xl mx-auto px-6 py-10 space-y-12">
            
            <!-- DETTAGLIO PRINCIPALE -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bg-neutral-900/60 p-8 rounded-xl border border-neutral-800 shadow-2xl">
                <div class="flex flex-col items-center">
                    <img src="{libro['copertina']}" class="w-64 h-80 object-cover rounded shadow-2xl border border-neutral-700 mb-4">
                    <span class="text-xs text-emerald-400 font-bold uppercase tracking-widest">{libro['valutazione']} Media Recensioni</span>
                </div>
                
                <div class="md:col-span-2 space-y-4">
                    <h1 class="text-3xl md:text-4xl font-black">{libro['titolo']}</h1>
                    <p class="text-lg text-neutral-400 font-medium">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']} <span class="text-xs font-normal text-neutral-400">({libro['condizione']})</span></div>
                    
                    <p class="text-neutral-300 text-sm leading-relaxed italic">{libro['descrizione']}</p>
                    
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-neutral-800 text-xs">
                        <div><span class="text-neutral-500 block">Editore</span> <strong class="text-white">{libro['editore']}</strong></div>
                        <div><span class="text-neutral-500 block">Collana</span> <strong class="text-white">{libro['collana']}</strong></div>
                        <div><span class="text-neutral-500 block">Codice EAN</span> <strong class="text-white">{libro['codice_ean']}</strong></div>
                        <div><span class="text-neutral-500 block">Anno Edizione</span> <strong class="text-white">{libro['anno_edizione']}</strong></div>
                        <div><span class="text-neutral-500 block">Anno Pubblicazione</span> <strong class="text-white">{libro['anno_pubblicazione']}</strong></div>
                        <div><span class="text-neutral-500 block">Condizioni</span> <strong class="text-white">{libro['condizione']}</strong></div>
                    </div>
                </div>
            </div>

            <!-- GRAFICO ANDAMENTO PREZZI E VENDITE -->
            <div class="bg-neutral-900/60 p-6 rounded-xl border border-neutral-800 space-y-4">
                <h3 class="text-xl font-bold">Andamento Prezzi e Vendite (Ultimi 6 Mesi)</h3>
                <div class="h-72 w-full">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <!-- TUTTI I VENDITORI DI QUESTO LIBRO -->
            <div class="space-y-4">
                <h3 class="text-xl font-bold">Tutti i Venditori per questo Libro</h3>
                <div class="bg-neutral-900 rounded-xl border border-neutral-800 overflow-hidden divide-y divide-neutral-800">
                    <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-neutral-800/50 transition">
                        <div>
                            <h4 class="font-bold text-white text-base">{libro['venditore']}</h4>
                            <p class="text-xs text-neutral-400">📍 {libro['venditore_posizione']} | Valutazione: {libro['venditore_valutazione']}</p>
                        </div>
                        <div class="flex items-center gap-6">
                            <div class="text-right">
                                <span class="text-xs text-neutral-500 block">{libro['condizione']}</span>
                                <strong class="text-emerald-400 text-lg">{libro['prezzo']}</strong>
                            </div>
                            <button class="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-4 py-2 rounded transition">Acquista</button>
                        </div>
                    </div>
                    <!-- Secondo venditore simulato -->
                    <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-neutral-800/50 transition">
                        <div>
                            <h4 class="font-bold text-white text-base">Biblioteca Centrale Express</h4>
                            <p class="text-xs text-neutral-400">📍 Bologna (BO) | Valutazione: 4.7 ★ (620 recensioni)</p>
                        </div>
                        <div class="flex items-center gap-6">
                            <div class="text-right">
                                <span class="text-xs text-neutral-500 block">Ottime condizioni</span>
                                <strong class="text-emerald-400 text-lg">19.00 €</strong>
                            </div>
                            <button class="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-4 py-2 rounded transition">Acquista</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ALTRI LIBRI SIMILI -->
            <div class="space-y-4">
                <h3 class="text-xl font-bold">Altri Libri Simili</h3>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {simili_html}
                </div>
            </div>

        </main>

        <script>
            const ctx = document.getElementById('priceChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: ['Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre'],
                    datasets: [{{
                        label: 'Prezzo Medio (€)',
                        data: [18.0, 17.5, 16.0, 15.5, 15.0, 14.0],
                        borderColor: '#e50914',
                        backgroundColor: 'rgba(229, 9, 20, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}, {{
                        label: 'Copie Vendute',
                        data: [5, 8, 12, 10, 15, 22],
                        borderColor: '#34d399',
                        tension: 0.3,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ beginAtZero: false, grid: {{ color: '#262626' }} }},
                        y1: {{ position: 'right', grid: {{ display: false }} }},
                        x: {{ grid: {{ color: '#262626' }} }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

# --- 3. LA MIA BIBLIOTECA ---
@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page():
    navbar = get_navbar('biblioteca')
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>La Mia Biblioteca - LoopBooks</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #141414; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="bg-neutral-900 border border-neutral-800 rounded-xl p-8 space-y-6">
                <h2 class="text-2xl font-black">La Tua Raccolta Personale</h2>
                <p class="text-neutral-400 text-sm">I volumi registrati nella tua domus o salvati nei preferiti.</p>
                <div class="border border-neutral-800 rounded-lg p-12 text-center text-neutral-500 text-sm">
                    Nessun manoscritto registrato. Visita <a href="/metti-in-vendita" class="text-red-500 underline font-bold">Metti in Vendita</a> per aggiungere libri.
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- 4. METTI IN VENDITA ---
@app.get("/metti-in-vendita", response_class=HTMLResponse)
async def metti_in_vendita_page():
    navbar = get_navbar('metti-in-vendita')
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Metti in Vendita - LoopBooks</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #141414; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-3xl mx-auto px-6 py-12">
            <div class="bg-neutral-900 border border-neutral-800 rounded-xl p-8 space-y-6 shadow-2xl">
                <div class="text-center space-y-2">
                    <h2 class="text-3xl font-black">Registra un Nuovo Tomo</h2>
                    <p class="text-neutral-400 text-xs">Inserisci il codice ISBN per estrarre automaticamente metadati e stime di mercato.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Codice ISBN..." 
                        class="flex-1 bg-black border border-neutral-700 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-red-600">
                    <button onclick="alert('Tomo registrato con successo nei registri di LoopBooks!')" 
                        class="bg-red-600 hover:bg-red-700 text-white font-bold px-6 py-3 rounded text-xs uppercase tracking-wider transition">
                        Pubblica
                    </button>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
