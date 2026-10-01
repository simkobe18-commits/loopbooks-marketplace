import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database esteso di volumi con estetica Jarvis / Netflix
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
    home_class = 'text-cyan-400 font-bold border-b border-cyan-400' if active_page == 'home' else 'text-neutral-400 hover:text-cyan-300 transition'
    biblio_class = 'text-cyan-400 font-bold border-b border-cyan-400' if active_page == 'biblioteca' else 'text-neutral-400 hover:text-cyan-300 transition'
    vendita_class = 'text-cyan-400 font-bold border-b border-cyan-400' if active_page == 'metti-in-vendita' else 'text-neutral-400 hover:text-cyan-300 transition'
    
    return f"""
    <header class="w-full bg-[#050b14]/90 backdrop-blur-md border-b border-cyan-500/30 py-4 px-8 sticky top-0 z-50 flex justify-between items-center shadow-[0_0_20px_rgba(6,182,212,0.15)]">
        <div class="flex items-center gap-10">
            <a href="/" class="text-cyan-400 font-black text-xl tracking-[0.2em] uppercase font-mono flex items-center gap-2">
                <span class="inline-block w-2.5 h-2.5 bg-cyan-400 rounded-full animate-ping"></span>
                LOOPBOOKS // HUD
            </a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest uppercase">
                <a href="/" class="{home_class} pb-1">HOME</a>
                <a href="/biblioteca" class="{biblio_class} pb-1">LA MIA BIBLIOTECA</a>
                <a href="/metti-in-vendita" class="{vendita_class} pb-1">METTI IN VENDITA</a>
            </nav>
        </div>
        <div>
            <a href="/metti-in-vendita" class="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 font-mono text-xs px-4 py-2 rounded transition shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                LOG IN
            </a>
        </div>
    </header>
    """

# --- 1. HOME PAGE STILE NETFLIX + JARVIS ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    
    def render_row(sezione_key):
        filtered = [b for b in BOOKS_DATABASE if b["sezione"] == sezione_key or sezione_key == "tutti"]
        html = ""
        for b in filtered:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[200px] md:min-w-[220px] bg-[#0b1320] rounded border border-cyan-500/20 overflow-hidden shadow-lg hover:border-cyan-400 hover:scale-105 transition duration-300 flex-shrink-0 group relative">
                <div class="h-64 bg-black overflow-hidden relative">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:opacity-90 transition">
                    <span class="absolute top-2 right-2 bg-black/80 text-cyan-400 font-mono text-[10px] px-2 py-0.5 rounded border border-cyan-500/30">{b['valutazione']}</span>
                </div>
                <div class="p-3 space-y-1 font-mono">
                    <h4 class="font-bold text-sm text-cyan-100 truncate">{b['titolo']}</h4>
                    <p class="text-[11px] text-cyan-400/70">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-2">
                        <span class="text-emerald-400 font-bold text-xs">{b['prezzo']}</span>
                        <span class="text-[9px] bg-cyan-950 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-800">{b['condizione']}</span>
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
        <title>LoopBooks - JARVIS Interface</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
            .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
            .jarvis-glow {{ box-shadow: 0 0 25px rgba(6, 182, 212, 0.15); }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        
        <!-- HERO / BANNER PRINCIPALE -->
        <div class="relative w-full h-[520px] bg-cover bg-center flex items-end p-8 md:p-16 border-b border-cyan-500/30" style="background-image: linear-gradient(to top, #030712, rgba(3,7,18,0.3)), url('https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg');">
            <div class="max-w-2xl space-y-4">
                <span class="bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 text-[10px] font-mono font-bold px-3 py-1 uppercase tracking-widest rounded shadow-[0_0_10px_rgba(6,182,212,0.3)]">SISTEMA ATTIVO // ARCHIVIO CENTRALE</span>
                <h1 class="text-4xl md:text-6xl font-black tracking-tight text-white font-sans">CREA LA TUA BIBLIOTECA</h1>
                <p class="text-cyan-100/80 text-sm md:text-base leading-relaxed font-mono">
                    Interfaccia di scansione e gestione volumi rari, bestseller e inventari digitali. Sincronizzazione protetta attiva.
                </p>
                <div class="flex gap-4 pt-2">
                    <a href="/metti-in-vendita" class="bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold px-8 py-3 rounded flex items-center gap-2 transition shadow-[0_0_20px_rgba(6,182,212,0.5)] text-xs uppercase tracking-widest">
                        ▶ Metti in Vendita
                    </a>
                </div>
            </div>
        </div>

        <main class="px-6 md:px-12 space-y-12 mt-8">
            
            <!-- FILTRI DI RICERCA RAPIDA -->
            <div class="flex items-center gap-3 overflow-x-auto hide-scroll py-2">
                <span class="text-xs font-mono font-bold uppercase tracking-widest text-cyan-400 mr-2">Filtri HUD:</span>
                <a href="#tendenza" class="bg-[#0b1320] hover:bg-cyan-950 text-cyan-300 text-xs px-4 py-2 rounded border border-cyan-500/30 whitespace-nowrap transition">🔥 Di Tendenza</a>
                <a href="#migliori" class="bg-[#0b1320] hover:bg-cyan-950 text-cyan-300 text-xs px-4 py-2 rounded border border-cyan-500/30 whitespace-nowrap transition">⭐ Migliori Venditori</a>
                <a href="#per-te" class="bg-[#0b1320] hover:bg-cyan-950 text-cyan-300 text-xs px-4 py-2 rounded border border-cyan-500/30 whitespace-nowrap transition">🎯 Consigliati per Te</a>
                <a href="#rari" class="bg-[#0b1320] hover:bg-cyan-950 text-cyan-300 text-xs px-4 py-2 rounded border border-cyan-500/30 whitespace-nowrap transition">💎 Libri Rari</a>
            </div>

            <!-- SEZIONE 1: LIBRI DI TENDENZA -->
            <section id="tendenza" class="space-y-4">
                <div class="flex items-center gap-2 border-b border-cyan-500/30 pb-2">
                    <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                    <h3 class="text-lg font-mono font-bold tracking-wide text-cyan-300 uppercase">Libri di Tendenza</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {tendenza_html}
                </div>
            </section>

            <!-- SEZIONE 2: MIGLIORI VENDITORI -->
            <section id="migliori" class="space-y-4">
                <div class="flex items-center gap-2 border-b border-cyan-500/30 pb-2">
                    <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                    <h3 class="text-lg font-mono font-bold tracking-wide text-cyan-300 uppercase">Migliori Venditori</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {venditori_html}
                </div>
            </section>

            <!-- SEZIONE 3: LIBRI PER TE -->
            <section id="per-te" class="space-y-4">
                <div class="flex items-center gap-2 border-b border-cyan-500/30 pb-2">
                    <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                    <h3 class="text-lg font-mono font-bold tracking-wide text-cyan-300 uppercase">Libri per Te</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {per_te_html}
                </div>
            </section>

            <!-- SEZIONE 4: LIBRI RARI -->
            <section id="rari" class="space-y-4">
                <div class="flex items-center gap-2 border-b border-cyan-500/30 pb-2">
                    <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                    <h3 class="text-lg font-mono font-bold tracking-wide text-cyan-300 uppercase">Libri Rari & Collezioni</h3>
                </div>
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
    
    libro = next((b for b in BOOKS_DATABASE if b["id"] == libro_id), BOOKS_DATABASE[0])
    
    simili_html = ""
    for b in [x for x in BOOKS_DATABASE if x["id"] != libro_id]:
        simili_html += f"""
        <a href="/libro/{b['id']}" class="min-w-[200px] bg-[#0b1320] rounded border border-cyan-500/20 overflow-hidden shadow hover:border-cyan-400 hover:scale-105 transition flex-shrink-0">
            <div class="h-48 bg-black overflow-hidden">
                <img src="{b['copertina']}" class="w-full h-full object-cover">
            </div>
            <div class="p-3 font-mono">
                <h4 class="font-bold text-xs text-cyan-200 truncate">{b['titolo']}</h4>
                <p class="text-[11px] text-emerald-400 mt-1">{b['prezzo']}</p>
            </div>
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{libro['titolo']} - HUD Analisi</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        
        <main class="max-w-6xl mx-auto px-6 py-10 space-y-12">
            
            <!-- SCHEDA DETTAGLIO HUD -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bg-[#0b1320] p-8 rounded border border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.1)]">
                <div class="flex flex-col items-center justify-center">
                    <img src="{libro['copertina']}" class="w-60 h-80 object-cover rounded border border-cyan-500/40 shadow-2xl mb-4">
                    <span class="text-xs text-cyan-300 font-mono font-bold uppercase tracking-widest bg-cyan-950 px-3 py-1 rounded border border-cyan-800">{libro['valutazione']} Media Recensioni</span>
                </div>
                
                <div class="md:col-span-2 space-y-4">
                    <span class="text-[10px] text-cyan-400 font-mono tracking-widest uppercase">ID PROTOCOLLO // {libro['id']}</span>
                    <h1 class="text-3xl md:text-4xl font-black text-white font-sans">{libro['titolo']}</h1>
                    <p class="text-base text-cyan-400">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']} <span class="text-xs font-normal text-cyan-300/70 font-mono">({libro['condizione']})</span></div>
                    
                    <p class="text-cyan-100/80 text-xs leading-relaxed italic border-l-2 border-cyan-400 pl-3">{libro['descrizione']}</p>
                    
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-cyan-500/20 text-xs">
                        <div><span class="text-cyan-500 block">Editore</span> <strong class="text-cyan-200">{libro['editore']}</strong></div>
                        <div><span class="text-cyan-500 block">Collana</span> <strong class="text-cyan-200">{libro['collana']}</strong></div>
                        <div><span class="text-cyan-500 block">Codice EAN</span> <strong class="text-cyan-200">{libro['codice_ean']}</strong></div>
                        <div><span class="text-cyan-500 block">Anno Edizione</span> <strong class="text-cyan-200">{libro['anno_edizione']}</strong></div>
                        <div><span class="text-cyan-500 block">Anno Pubblicazione</span> <strong class="text-cyan-200">{libro['anno_pubblicazione']}</strong></div>
                        <div><span class="text-cyan-500 block">Condizioni</span> <strong class="text-cyan-200">{libro['condizione']}</strong></div>
                    </div>
                </div>
            </div>

            <!-- GRAFICO HUD ANDAMENTO PREZZI -->
            <div class="bg-[#0b1320] p-6 rounded border border-cyan-500/30 space-y-4">
                <div class="flex items-center justify-between border-b border-cyan-500/20 pb-2">
                    <h3 class="text-sm font-bold text-cyan-300 uppercase tracking-wider">Telemetria Mercato & Vendite (Ultimi 6 Mesi)</h3>
                    <span class="text-[10px] text-emerald-400 font-mono animate-pulse">● LIVE STATUS</span>
                </div>
                <div class="h-72 w-full">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <!-- VENDITORI MULTIPLI -->
            <div class="space-y-4">
                <h3 class="text-sm font-bold text-cyan-300 uppercase tracking-wider">Venditori Autorizzati per questo Tomo</h3>
                <div class="bg-[#0b1320] rounded border border-cyan-500/30 overflow-hidden divide-y divide-cyan-500/20">
                    <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-cyan-950/30 transition">
                        <div>
                            <h4 class="font-bold text-cyan-100 text-sm">{libro['venditore']}</h4>
                            <p class="text-[11px] text-cyan-400/70">📍 {libro['venditore_posizione']} | Valutazione: {libro['venditore_valutazione']}</p>
                        </div>
                        <div class="flex items-center gap-6">
                            <div class="text-right">
                                <span class="text-[10px] text-cyan-500 block">{libro['condizione']}</span>
                                <strong class="text-emerald-400 text-base">{libro['prezzo']}</strong>
                            </div>
                            <button class="bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-mono font-bold px-4 py-2 rounded transition shadow-[0_0_10px_rgba(6,182,212,0.3)]">Acquista</button>
                        </div>
                    </div>
                    <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-cyan-950/30 transition">
                        <div>
                            <h4 class="font-bold text-cyan-100 text-sm">Biblioteca Centrale Express</h4>
                            <p class="text-[11px] text-cyan-400/70">📍 Bologna (BO) | Valutazione: 4.7 ★ (620 recensioni)</p>
                        </div>
                        <div class="flex items-center gap-6">
                            <div class="text-right">
                                <span class="text-[10px] text-cyan-500 block">Ottime condizioni</span>
                                <strong class="text-emerald-400 text-base">19.00 €</strong>
                            </div>
                            <button class="bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-mono font-bold px-4 py-2 rounded transition shadow-[0_0_10px_rgba(6,182,212,0.3)]">Acquista</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ALTRI LIBRI SIMILI -->
            <div class="space-y-4">
                <h3 class="text-sm font-bold text-cyan-300 uppercase tracking-wider">Altri Libri Simili</h3>
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
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
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
                        y: {{ beginAtZero: false, grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8' }} }},
                        y1: {{ position: 'right', grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
                        x: {{ grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8' }} }}
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
        <title>La Mia Biblioteca - HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="bg-[#0b1320] border border-cyan-500/30 rounded p-8 space-y-6 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                <h2 class="text-xl font-bold text-cyan-300 uppercase tracking-widest">La Tua Raccolta Personale</h2>
                <p class="text-cyan-400/70 text-xs">I volumi registrati nella tua domus o sincronizzati con il cloud di Jarvis.</p>
                <div class="border border-cyan-500/20 rounded p-12 text-center text-cyan-500/50 text-xs">
                    Nessun manoscritto registrato. Visita <a href="/metti-in-vendita" class="text-cyan-400 underline font-bold">Metti in Vendita</a> per sincronizzare libri.
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
        <title>Metti in Vendita - HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-3xl mx-auto px-6 py-12">
            <div class="bg-[#0b1320] border border-cyan-500/30 rounded p-8 space-y-6 shadow-[0_0_30px_rgba(6,182,212,0.15)]">
                <div class="text-center space-y-2">
                    <h2 class="text-2xl font-bold text-cyan-300 uppercase tracking-widest">Registra un Nuovo Tomo</h2>
                    <p class="text-cyan-400/70 text-xs">Inserisci il codice ISBN per attivare la scansione olografica e l'estrazione dati automatica.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Codice ISBN..." 
                        class="flex-1 bg-black border border-cyan-500/40 rounded px-4 py-3 text-cyan-200 text-xs focus:outline-none focus:border-cyan-400">
                    <button onclick="alert('Tomo scansionato e registrato con successo nei sistemi di LoopBooks!')" 
                        class="bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold px-6 py-3 rounded text-xs uppercase tracking-wider transition shadow-[0_0_15px_rgba(6,182,212,0.4)]">
                        Pubblica
                    </button>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
