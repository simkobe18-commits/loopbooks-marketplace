import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Database esteso di volumi con estetica HUD / Roma Bibliotheca
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
        "descrizione": "Un monastero, un segreto, un crimine. Scopri il mistero custodito tra i codici miniati.",
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
        "titolo": "Codice Atlantico",
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
    home_class = 'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'home' else 'text-neutral-400 hover:text-[#f3e5ab] transition'
    biblio_class = 'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'biblioteca' else 'text-neutral-400 hover:text-[#f3e5ab] transition'
    vendita_class = 'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'metti-in-vendita' else 'text-neutral-400 hover:text-[#f3e5ab] transition'
    
    return f"""
    <header class="w-full bg-[#070b14]/90 backdrop-blur-md border-b border-[#e5c158]/30 py-3 px-8 sticky top-0 z-50 flex justify-between items-center shadow-[0_0_25px_rgba(229,193,88,0.15)] font-mono">
        <div class="flex items-center gap-10">
            <a href="/" class="text-[#e5c158] font-black text-lg tracking-[0.25em] uppercase flex items-center gap-2">
                <span class="inline-block w-2 h-2 bg-[#e5c158] rounded-full animate-ping"></span>
                📖 Loopbooks
            </a>
            <nav class="hidden md:flex items-center gap-8 text-xs tracking-widest uppercase">
                <a href="/" class="{home_class} pb-1">Home</a>
                <a href="/biblioteca" class="{biblio_class} pb-1">Le tue liste</a>
                <a href="/metti-in-vendita" class="{vendita_class} pb-1">Vendi</a>
            </nav>
        </div>
        <div>
            <a href="/metti-in-vendita" class="bg-[#e5c158]/10 hover:bg-[#e5c158]/20 text-[#e5c158] border border-[#e5c158]/50 text-xs px-4 py-1.5 rounded transition shadow-[0_0_10px_rgba(229,193,88,0.2)]">
                Accedi HUD
            </a>
        </div>
    </header>
    """

# --- 1. HOME PAGE STILE ROMA BIBLIOTHECA HUD ---
@app.get("/", response_class=HTMLResponse)
async def home_page():
    navbar = get_navbar('home')
    
    def render_row(sezione_key):
        filtered = [b for b in BOOKS_DATABASE if b["sezione"] == sezione_key or sezione_key == "tutti"]
        html = ""
        for b in filtered:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[150px] md:min-w-[170px] bg-[#0b1322] rounded border border-[#e5c158]/30 overflow-hidden shadow-lg hover:border-[#e5c158] hover:scale-105 transition duration-300 flex-shrink-0 group relative">
                <div class="h-44 bg-black overflow-hidden relative">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:opacity-90 transition">
                    <span class="absolute top-1 right-1 bg-black/80 text-[#e5c158] font-mono text-[9px] px-1.5 py-0.5 rounded border border-[#e5c158]/30">{b['valutazione']}</span>
                </div>
                <div class="p-2 space-y-1 font-mono">
                    <h4 class="font-bold text-xs text-[#f3e5ab] truncate">{b['titolo']}</h4>
                    <p class="text-[10px] text-neutral-400 truncate">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-1">
                        <span class="text-emerald-400 font-bold text-[11px]">{b['prezzo']}</span>
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
        <title>Roma Bibliotheca - HUD Interface</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #03060c; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
            .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
            .hud-border {{ border: 1px solid rgba(229, 193, 88, 0.35); box-shadow: 0 0 25px rgba(229, 193, 88, 0.1); }}
            .hud-circle {{ border: 2px dashed rgba(229, 193, 88, 0.5); border-radius: 50%; animation: spin 20s linear infinite; }}
            @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body class="min-h-screen pb-24 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#0d1526] via-[#040812] to-[#020408]">
        
        <!-- ROMA BIBLIOTHECA TOP BADGE -->
        <div class="w-full flex justify-center py-2 bg-[#050810] border-b border-[#e5c158]/20">
            <div class="px-6 py-1 bg-[#0b1322] border border-[#e5c158]/50 rounded-b-lg shadow-[0_0_15px_rgba(229,193,88,0.2)] text-[#e5c158] font-mono text-xs font-bold tracking-[0.3em] uppercase">
                Roma Bibliotheca
            </div>
        </div>

        {navbar}

        <main class="max-w-7xl mx-auto px-6 py-8 space-y-8">
            
            <!-- HERO / OLOGRAFICA CENTRALE (ISIRPIS 1:1 CON L'IMMAGINE) -->
            <div class="relative w-full hud-border bg-[#070e1b]/80 backdrop-blur-md rounded-xl p-6 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                
                <!-- Cornice Tech Sinistra (Descrizione) -->
                <div class="lg:col-span-5 space-y-4">
                    <div class="inline-block px-3 py-1 bg-[#e5c158]/10 border border-[#e5c158]/40 text-[#e5c158] text-[10px] uppercase tracking-widest rounded">
                        Protocollo Scansione Attivo
                    </div>
                    <h1 class="text-2xl md:text-3xl font-black text-white tracking-wide font-sans">
                        Un monastero, un segreto, un crimine. Scopri il mistero...
                    </h1>
                    <p class="text-neutral-300 text-xs leading-relaxed font-mono">
                        Analisi codici miniati e volumi antichi in corso. Sincronizzato con l'archivio centrale di Roma.
                    </p>
                    <div class="flex items-center gap-3 pt-2">
                        <span class="w-2 h-2 bg-emerald-400 rounded-full animate-ping"></span>
                        <span class="text-[11px] text-emerald-400 font-mono">Stato: Disponibile per Scambio</span>
                    </div>
                </div>

                <!-- Copertina Centrale in Evidenza -->
                <div class="lg:col-span-4 flex justify-center items-center relative">
                    <div class="absolute w-56 h-56 hud-circle pointer-events-none"></div>
                    <div class="relative z-10 bg-[#0b1322] p-2 rounded-lg hud-border shadow-[0_0_30px_rgba(229,193,88,0.3)] transform hover:scale-105 transition duration-300">
                        <img src="https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg" class="w-36 h-48 md:w-44 md:h-60 object-cover rounded">
                        <div class="absolute -bottom-3 -right-3 bg-[#e5c158] text-black text-[10px] font-bold px-2 py-0.5 rounded shadow">
                            HUD-01
                        </div>
                    </div>
                </div>

                <!-- Radar Olografico Destra -->
                <div class="lg:col-span-3 flex flex-col items-center justify-center relative">
                    <div class="w-40 h-40 hud-circle flex items-center justify-center relative">
                        <div class="w-28 h-28 border border-[#e5c158]/30 rounded-full flex items-center justify-center">
                            <div class="w-16 h-16 bg-[#e5c158]/10 rounded-full flex items-center justify-center animate-pulse">
                                <span class="text-[#e5c158] text-xl">📖</span>
                            </div>
                        </div>
                    </div>
                    <span class="text-[10px] text-[#e5c158] mt-3 tracking-widest uppercase">Target Scanner 360°</span>
                </div>

            </div>

            <!-- CAROSELLI STILE NETFLIX CON INTERFACCIA HUD -->
            <div class="space-y-8">
                
                <!-- Sezione 1 -->
                <section class="space-y-3">
                    <div class="flex items-center gap-2 border-b border-[#e5c158]/20 pb-2">
                        <span class="w-2 h-2 bg-[#e5c158] rounded-full"></span>
                        <h3 class="text-sm font-mono font-bold tracking-wider text-[#e5c158] uppercase">Libri di Tendenza</h3>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {tendenza_html}
                    </div>
                </section>

                <!-- Sezione 2 -->
                <section class="space-y-3">
                    <div class="flex items-center gap-2 border-b border-[#e5c158]/20 pb-2">
                        <span class="w-2 h-2 bg-[#e5c158] rounded-full"></span>
                        <h3 class="text-sm font-mono font-bold tracking-wider text-[#e5c158] uppercase">Migliori Venditori</h3>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {venditori_html}
                    </div>
                </section>

                <!-- Sezione 3 -->
                <section class="space-y-3">
                    <div class="flex items-center gap-2 border-b border-[#e5c158]/20 pb-2">
                        <span class="w-2 h-2 bg-[#e5c158] rounded-full"></span>
                        <h3 class="text-sm font-mono font-bold tracking-wider text-[#e5c158] uppercase">Consigliati per Te</h3>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {per_te_html}
                    </div>
                </section>

                <!-- Sezione 4 -->
                <section class="space-y-3">
                    <div class="flex items-center gap-2 border-b border-[#e5c158]/20 pb-2">
                        <span class="w-2 h-2 bg-[#e5c158] rounded-full"></span>
                        <h3 class="text-sm font-mono font-bold tracking-wider text-[#e5c158] uppercase">Libri Rari & Collezioni</h3>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {rari_html}
                    </div>
                </section>

            </div>

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
        <a href="/libro/{b['id']}" class="min-w-[160px] bg-[#0b1322] rounded border border-[#e5c158]/30 overflow-hidden shadow hover:border-[#e5c158] hover:scale-105 transition flex-shrink-0">
            <div class="h-40 bg-black overflow-hidden">
                <img src="{b['copertina']}" class="w-full h-full object-cover">
            </div>
            <div class="p-2 font-mono">
                <h4 class="font-bold text-xs text-[#f3e5ab] truncate">{b['titolo']}</h4>
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
        <title>{libro['titolo']} - Roma Bibliotheca HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #03060c; color: #e2e8f0; font-family: ui-monospace, monospace; }}
            .hud-border {{ border: 1px solid rgba(229, 193, 88, 0.35); box-shadow: 0 0 25px rgba(229, 193, 88, 0.1); }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        
        <div class="w-full flex justify-center py-2 bg-[#050810] border-b border-[#e5c158]/20">
            <div class="px-6 py-1 bg-[#0b1322] border border-[#e5c158]/50 rounded-b-lg text-[#e5c158] font-mono text-xs font-bold tracking-[0.3em] uppercase">
                Roma Bibliotheca // Analisi Tomo
            </div>
        </div>

        {navbar}
        
        <main class="max-w-6xl mx-auto px-6 py-10 space-y-10">
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bg-[#0b1322] p-8 rounded hud-border">
                <div class="flex flex-col items-center justify-center">
                    <img src="{libro['copertina']}" class="w-60 h-80 object-cover rounded border border-[#e5c158]/40 shadow-2xl mb-4">
                    <span class="text-xs text-[#e5c158] font-mono font-bold uppercase tracking-widest bg-[#e5c158]/10 px-3 py-1 rounded border border-[#e5c158]/30">{libro['valutazione']} Media</span>
                </div>
                
                <div class="md:col-span-2 space-y-4 font-mono">
                    <span class="text-[10px] text-[#e5c158] tracking-widest uppercase">ID PROTOCOLLO // {libro['id']}</span>
                    <h1 class="text-3xl font-black text-white font-sans">{libro['titolo']}</h1>
                    <p class="text-base text-[#e5c158]">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']} <span class="text-xs font-normal text-neutral-400">({libro['condizione']})</span></div>
                    
                    <p class="text-neutral-300 text-xs leading-relaxed italic border-l-2 border-[#e5c158] pl-3">{libro['descrizione']}</p>
                    
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-[#e5c158]/20 text-xs">
                        <div><span class="text-neutral-500 block">Editore</span> <strong class="text-neutral-200">{libro['editore']}</strong></div>
                        <div><span class="text-neutral-500 block">Collana</span> <strong class="text-neutral-200">{libro['collana']}</strong></div>
                        <div><span class="text-neutral-500 block">Codice EAN</span> <strong class="text-neutral-200">{libro['codice_ean']}</strong></div>
                        <div><span class="text-neutral-500 block">Anno Edizione</span> <strong class="text-neutral-200">{libro['anno_edizione']}</strong></div>
                        <div><span class="text-neutral-500 block">Anno Pubblicazione</span> <strong class="text-neutral-200">{libro['anno_pubblicazione']}</strong></div>
                        <div><span class="text-neutral-500 block">Condizioni</span> <strong class="text-neutral-200">{libro['condizione']}</strong></div>
                    </div>
                </div>
            </div>

            <div class="bg-[#0b1322] p-6 rounded hud-border space-y-4">
                <div class="flex items-center justify-between border-b border-[#e5c158]/20 pb-2">
                    <h3 class="text-sm font-bold text-[#e5c158] uppercase tracking-wider font-mono">Telemetria Mercato & Storico Vendite</h3>
                    <span class="text-[10px] text-emerald-400 font-mono animate-pulse">● LIVE STATUS</span>
                </div>
                <div class="h-72 w-full">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <div class="space-y-4">
                <h3 class="text-sm font-bold text-[#e5c158] uppercase tracking-wider font-mono">Venditori Autorizzati per questo Tomo</h3>
                <div class="bg-[#0b1322] rounded hud-border overflow-hidden divide-y divide-[#e5c158]/20 font-mono">
                    <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-[#131e35] transition">
                        <div>
                            <h4 class="font-bold text-neutral-100 text-sm">{libro['venditore']}</h4>
                            <p class="text-[11px] text-neutral-400">📍 {libro['venditore_posizione']} | Valutazione: {libro['venditore_valutazione']}</p>
                        </div>
                        <div class="flex items-center gap-6">
                            <div class="text-right">
                                <span class="text-[10px] text-neutral-500 block">{libro['condizione']}</span>
                                <strong class="text-emerald-400 text-base">{libro['prezzo']}</strong>
                            </div>
                            <button class="bg-[#e5c158] hover:bg-[#d4b046] text-black text-xs font-mono font-bold px-4 py-2 rounded transition shadow">Acquista</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="space-y-4">
                <h3 class="text-sm font-bold text-[#e5c158] uppercase tracking-wider font-mono">Altri Libri Simili</h3>
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
                        borderColor: '#e5c158',
                        backgroundColor: 'rgba(229, 193, 88, 0.1)',
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
                        y: {{ beginAtZero: false, grid: {{ color: '#1a263f' }}, ticks: {{ color: '#94a3b8' }} }},
                        y1: {{ position: 'right', grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
                        x: {{ grid: {{ color: '#1a263f' }}, ticks: {{ color: '#94a3b8' }} }}
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
        <title>Le tue liste - Roma Bibliotheca HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #03060c; color: #e2e8f0; font-family: ui-monospace, monospace; }} .hud-border {{ border: 1px solid rgba(229, 193, 88, 0.35); box-shadow: 0 0 25px rgba(229, 193, 88, 0.1); }}</style>
    </head>
    <body class="min-h-screen pb-24">
        <div class="w-full flex justify-center py-2 bg-[#050810] border-b border-[#e5c158]/20">
            <div class="px-6 py-1 bg-[#0b1322] border border-[#e5c158]/50 rounded-b-lg text-[#e5c158] font-mono text-xs font-bold tracking-[0.3em] uppercase">
                Roma Bibliotheca // Le tue liste
            </div>
        </div>
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="bg-[#0b1322] hud-border rounded p-8 space-y-6 font-mono">
                <h2 class="text-xl font-bold text-[#e5c158] uppercase tracking-widest">La Tua Raccolta Personale</h2>
                <p class="text-neutral-400 text-xs">I volumi registrati nella tua domus o sincronizzati con l'archivio.</p>
                <div class="border border-[#e5c158]/20 rounded p-12 text-center text-neutral-500 text-xs">
                    Nessun manoscritto registrato. Visita <a href="/metti-in-vendita" class="text-[#e5c158] underline font-bold">Vendi</a> per aggiungere libri.
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
        <title>Vendi - Roma Bibliotheca HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #03060c; color: #e2e8f0; font-family: ui-monospace, monospace; }} .hud-border {{ border: 1px solid rgba(229, 193, 88, 0.35); box-shadow: 0 0 25px rgba(229, 193, 88, 0.1); }}</style>
    </head>
    <body class="min-h-screen pb-24">
        <div class="w-full flex justify-center py-2 bg-[#050810] border-b border-[#e5c158]/20">
            <div class="px-6 py-1 bg-[#0b1322] border border-[#e5c158]/50 rounded-b-lg text-[#e5c158] font-mono text-xs font-bold tracking-[0.3em] uppercase">
                Roma Bibliotheca // Terminale Vendita
            </div>
        </div>
        {navbar}
        <main class="max-w-3xl mx-auto px-6 py-12">
            <div class="bg-[#0b1322] hud-border rounded p-8 space-y-6 font-mono">
                <div class="text-center space-y-2">
                    <h2 class="text-2xl font-bold text-[#e5c158] uppercase tracking-widest">Registra un Nuovo Tomo</h2>
                    <p class="text-neutral-400 text-xs">Inserisci il codice ISBN per attivare la scansione olografica e l'estrazione metadati.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Codice ISBN..." 
                        class="flex-1 bg-black border border-[#e5c158]/40 rounded px-4 py-3 text-[#f3e5ab] text-xs focus:outline-none focus:border-[#e5c158]">
                    <button onclick="alert('Tomo scansionato e registrato nei registri di Roma Bibliotheca!')" 
                        class="bg-[#e5c158] hover:bg-[#d4b046] text-black font-mono font-bold px-6 py-3 rounded text-xs uppercase tracking-wider transition shadow">
                        Pubblica
                    </button>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
