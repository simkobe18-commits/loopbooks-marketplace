import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Database esteso con generi, venditori e oggettistica
BOOKS_DATABASE = [
    {
        "id": "9788806200085",
        "titolo": "Il Nome della Rosa",
        "autore": "Umberto Eco",
        "prezzo": 14.00,
        "valutazione_num": 4.9,
        "valutazione": "4.9 ★",
        "condizione": "Ottime condizioni",
        "editore": "Bompiani",
        "collana": "Tascabili",
        "codice_ean": "9788806200085",
        "anno_edizione": "2015",
        "anno_pubblicazione": "1980",
        "descrizione": "Un monastero isolato, un segreto custodito tra i codici miniati e un crimine che scuote l'ordine monastico.",
        "venditore": "Libreria Antiquaria Roma",
        "venditore_id": "roma-antiquaria",
        "venditore_posizione": "Roma (RM)",
        "venditore_valutazione": "4.9 ★ (1.2k recensioni)",
        "sezione": "tendenza",
        "genere": "Gialli, Thriller e Noir",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg"
    },
    {
        "id": "9788804668237",
        "titolo": "Le otto montagne",
        "autore": "Paolo Cognetti",
        "prezzo": 18.50,
        "valutazione_num": 4.8,
        "valutazione": "4.8 ★",
        "condizione": "Come nuovo",
        "editore": "Einaudi",
        "collana": "SuperET",
        "codice_ean": "9788804668237",
        "anno_edizione": "2018",
        "anno_pubblicazione": "2016",
        "descrizione": "Un romanzo profondo e intenso che racconta la storia di un'amicizia fraterna tra due ragazzi cresciuti in montagna.",
        "venditore": "LoopBooks Official",
        "venditore_id": "loopbooks-official",
        "venditore_posizione": "Milano (MI)",
        "venditore_valutazione": "4.8 ★ (850 recensioni)",
        "sezione": "migliori-venditori",
        "genere": "Romanzi contemporanei",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg"
    },
    {
        "id": "9788806231362",
        "titolo": "Omero, Iliade",
        "autore": "Alessandro Baricco",
        "prezzo": 16.50,
        "valutazione_num": 4.7,
        "valutazione": "4.7 ★",
        "condizione": "Buone condizioni",
        "editore": "Feltrinelli",
        "collana": "I Narratori",
        "codice_ean": "9788806231362",
        "anno_edizione": "2020",
        "anno_pubblicazione": "2004",
        "descrizione": "La rilettura appassionante del più grande poema epico di tutti i tempi, focalizzata sul destino e la guerra.",
        "venditore": "Antica Stamperia",
        "venditore_id": "antica-stamperia",
        "venditore_posizione": "Firenze (FI)",
        "venditore_valutazione": "4.6 ★ (410 recensioni)",
        "sezione": "libri-per-te",
        "genere": "Classici della letteratura",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788806231362-L.jpg"
    },
    {
        "id": "9788866325087",
        "titolo": "L'amica geniale",
        "autore": "Elena Ferrante",
        "prezzo": 15.00,
        "valutazione_num": 5.0,
        "valutazione": "5.0 ★",
        "condizione": "Perfetto",
        "editore": "Edizioni E/O",
        "collana": "Dal Mondo",
        "codice_ean": "9788866325087",
        "anno_edizione": "2016",
        "anno_pubblicazione": "2011",
        "descrizione": "La storia di un'amicizia complessa e duratura sullo sfondo di una Napoli popolare e in evoluzione.",
        "venditore": "BookBaron Milano",
        "venditore_id": "bookbaron-milano",
        "venditore_posizione": "Milano (MI)",
        "venditore_valutazione": "5.0 ★ (3.4k recensioni)",
        "sezione": "migliori-venditori",
        "genere": "Romanzi contemporanei",
        "copertina": "https://covers.openlibrary.org/b/isbn/9788866325087-L.jpg"
    },
    {
        "id": "9788804707035",
        "titolo": "Codice Atlantico (Raro)",
        "autore": "Leonardo da Vinci",
        "prezzo": 120.00,
        "valutazione_num": 5.0,
        "valutazione": "5.0 ★",
        "condizione": "Rarità da collezione",
        "editore": "Giunti Editore",
        "collana": "Edizioni Pregiate",
        "codice_ean": "9788804707035",
        "anno_edizione": "2001",
        "anno_pubblicazione": "1490",
        "descrizione": "Raccolta di disegni e scritti di Leonardo da Vinci, edizione facsimile di inestimabile valore storico.",
        "venditore": "Rari & Co.",
        "venditore_id": "rari-co",
        "venditore_posizione": "Venezia (VE)",
        "venditore_valutazione": "4.9 ★ (95 recensioni)",
        "sezione": "libri-rari",
        "genere": "Arte, Musica e Cinema",
        "copertina": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"
    }
]

OGGETTISTICA_DATABASE = [
    {
        "id": "obj-01",
        "nome": "Valigetta Olografica in Pelle Nera",
        "prezzo": "45.00 €",
        "descrizione": "Custodia rigida rinforzata con interno in velluto e chiusura biometrica.",
        "immagine": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": "obj-02",
        "nome": "Sigillo in Ceralacca Personalizzato",
        "prezzo": "28.00 €",
        "descrizione": "Kit completo con manico in ottone massiccio e ceralacca color oro antico.",
        "immagine": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": "obj-03",
        "nome": "Guanti Bianchi Antistatici",
        "prezzo": "12.00 €",
        "descrizione": "Cotone organico certificato per la manipolazione di tomi antichi.",
        "immagine": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80"
    }
]

GENERI_STRUTTURA = {
    "Narrativa e Letteratura": [
        "Romanzi contemporanei",
        "Narrativa storica",
        "Gialli, Thriller e Noir",
        "Fantasy e Fantascienza (Sci-Fi)",
        "Horror",
        "Narrativa rosa / Romance",
        "Classici della letteratura"
    ],
    "Saggistica e Cultura": [
        "Storia e Biografie",
        "Filosofia e Religione",
        "Scienze, Tecnologia e Natura",
        "Sociologia, Politica e Attualità",
        "Arte, Musica e Cinema"
    ],
    "Crescita Personale e Lifestyle": [
        "Self-help e Motivazione",
        "Business, Economia e Finanza Personale",
        "Benessere, Salute e Psicologia",
        "Cucina, Enogastronomia e Vini",
        "Viaggi e Guide turistiche"
    ],
    "Passioni, Hobby e Creatività": [
        "Fumetti, Manga e Graphic Novel",
        "Libri illustrati e Design",
        "Sport e Giochi",
        "Esoterismo e Astrologia"
    ],
    "Bambini e Ragazzi (Young Adult)": [
        "Narrativa ragazzi",
        "Fiabe e Fiabe illustrate",
        "Young Adult"
    ]
}

def get_base_head(title="LoopBooks Bento HUD"):
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;600;800;900&display=swap');
            
            body {{
                background-color: #030712;
                color: #e5e7eb;
                font-family: 'Share Tech Mono', monospace;
                overflow-x: hidden;
            }}
            h1, h2, h3, h4, .font-hud {{
                font-family: 'Orbitron', sans-serif;
            }}
            /* Effetti di luce sfumati / Bento glow card */
            .bento-card {{
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(3, 7, 18, 0.95) 100%);
                border: 1px solid rgba(0, 240, 255, 0.15);
                box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(0, 240, 255, 0.03);
                position: relative;
                backdrop-filter: blur(12px);
                transition: all 0.3s ease;
            }}
            .bento-card:hover {{
                border-color: rgba(0, 240, 255, 0.4);
                box-shadow: 0 15px 35px -10px rgba(0, 240, 255, 0.15), inset 0 0 25px rgba(0, 240, 255, 0.08);
            }}
            /* Glow arancio/ambra ispirato all'angolo destro dell'immagine di riferimento */
            .bento-glow-orange {{
                position: relative;
            }}
            .bento-glow-orange::after {{
                content: '';
                position: absolute;
                bottom: 0; right: 0;
                width: 180px; height: 180px;
                background: radial-gradient(circle, rgba(249, 115, 22, 0.18) 0%, rgba(0,0,0,0) 70%);
                pointer-events: none;
                z-index: 0;
            }}
            .bento-glow-blue {{
                position: relative;
            }}
            .bento-glow-blue::after {{
                content: '';
                position: absolute;
                top: 0; right: 0;
                width: 200px; height: 200px;
                background: radial-gradient(circle, rgba(0, 240, 255, 0.12) 0%, rgba(0,0,0,0) 70%);
                pointer-events: none;
                z-index: 0;
            }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
            .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
        </style>
    </head>
    """

def get_navbar(active_page="home"):
    return f"""
    <header class="w-full bg-[#030712]/90 backdrop-blur-md border-b border-cyan-500/20 py-3 px-8 sticky top-0 z-50 flex justify-between items-center shadow-[0_4px_25px_rgba(0,0,0,0.8)]">
        <div class="flex items-center gap-10">
            <a href="/" class="text-[#00f0ff] font-black text-sm md:text-base tracking-[0.2em] uppercase font-hud flex items-center gap-2">
                <span class="inline-block w-2.5 h-2.5 bg-[#00f0ff] rounded-full animate-pulse shadow-[0_0_10px_#00f0ff]"></span>
                LOOPBOOKS // BENTO HUD
            </a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest uppercase">
                <a href="/" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'home' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">HOME</a>
                <a href="/biblioteca" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'biblioteca' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">LA MIA BIBLIOTECA</a>
                <a href="/metti-in-vendita" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'metti-in-vendita' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">METTI IN VENDITA</a>
            </nav>
        </div>
        <div class="flex items-center gap-4">
            <span class="hidden lg:inline-block text-[10px] text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded border border-cyan-500/30">ROMA // SECURE MESH</span>
            <a href="/metti-in-vendita" class="bg-cyan-950/60 hover:bg-cyan-900/80 text-[#00f0ff] border border-[#00f0ff]/50 font-mono text-xs px-4 py-2 rounded transition shadow-[0_0_12px_rgba(0,240,255,0.2)]">
                [ SCANNER ]
            </a>
        </div>
    </header>
    """

# --- HOME PAGE BENTO GRID ---
@app.get("/", response_class=HTMLResponse)
async def home_page(q: str = "", ordine: str = "nessuno", genere: str = "tutti"):
    navbar = get_navbar('home')
    
    libri_filtrati = BOOKS_DATABASE.copy()
    if q:
        libri_filtrati = [b for b in libri_filtrati if q.lower() in b['titolo'].lower() or q.lower() in b['autore'].lower()]
    if genere != "tutti":
        libri_filtrati = [b for b in libri_filtrati if b['genere'] == genere]
        
    if ordine == "prezzo_asc":
        libri_filtrati.sort(key=lambda x: x['prezzo'])
    elif ordine == "prezzo_desc":
        libri_filtrati.sort(key=lambda x: x['prezzo'], reverse=True)
    elif ordine == "valutazione":
        libri_filtrati.sort(key=lambda x: x['valutazione_num'], reverse=True)
    elif ordine == "rari":
        libri_filtrati.sort(key=lambda x: x['prezzo'], reverse=True)

    def render_cards_horizontal(lista):
        if not lista:
            return '<p class="text-xs text-neutral-500 font-mono italic">Nessun tomo trovato.</p>'
        html = ""
        for b in lista:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[190px] md:min-w-[210px] bg-black/40 border border-cyan-500/20 rounded-xl p-3 hover:border-cyan-400 hover:scale-[1.02] transition duration-300 flex-shrink-0 group relative space-y-2">
                <div class="h-44 bg-black rounded-lg overflow-hidden relative border border-cyan-500/10">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                    <span class="absolute top-2 right-2 bg-black/80 backdrop-blur text-[#00f0ff] font-mono text-[10px] px-2 py-0.5 rounded border border-cyan-500/40">{b['valutazione']}</span>
                </div>
                <div class="space-y-1 font-mono">
                    <h4 class="font-bold text-xs text-cyan-100 truncate group-hover:text-[#00f0ff] transition">{b['titolo']}</h4>
                    <p class="text-[11px] text-cyan-400/70 truncate">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-1 border-t border-cyan-950">
                        <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
                        <span class="text-[9px] bg-cyan-950/80 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/20 truncate max-w-[85px]">{b['condizione']}</span>
                    </div>
                </div>
            </a>
            """
        return html

    tendenza_html = render_cards_horizontal([b for b in libri_filtrati if b["sezione"] == "tendenza"] or libri_filtrati)
    venditori_html = render_cards_horizontal([b for b in libri_filtrati if b["sezione"] == "migliori-venditori"] or libri_filtrati)
    rari_html = render_cards_horizontal(sorted(libri_filtrati, key=lambda x: x['prezzo'], reverse=True))

    oggettistica_html = ""
    for obj in OGGETTISTICA_DATABASE:
        oggettistica_html += f"""
        <div class="min-w-[210px] bg-black/40 border border-cyan-500/20 rounded-xl p-3 flex-shrink-0 space-y-2 font-mono">
            <div class="h-32 bg-black rounded-lg overflow-hidden border border-cyan-500/10">
                <img src="{obj['immagine']}" class="w-full h-full object-cover">
            </div>
            <h4 class="font-bold text-xs text-cyan-100 truncate">{obj['nome']}</h4>
            <p class="text-[10px] text-neutral-400 line-clamp-2">{obj['descrizione']}</p>
            <div class="flex justify-between items-center pt-1 border-t border-cyan-950">
                <span class="text-emerald-400 font-bold text-xs">{obj['prezzo']}</span>
                <button onclick="alert('[SUCCESS] Oggetto aggiunto al kit olografico!')" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] text-[10px] px-2.5 py-1 rounded border border-cyan-500/40 transition">ORDINA</button>
            </div>
        </div>
        """

    generi_options = '<option value="tutti">-- TUTTI I GENERI OLOGRAFICI --</option>'
    for macro, sottos in GENERI_STRUTTURA.items():
        generi_options += f'<optgroup label="{macro}">'
        for sotto in sottos:
            sel = "selected" if genere == sotto else ""
            generi_options += f'<option value="{sotto}" {sel}>{sotto}</option>'
        generi_options += '</optgroup>'

    return f"""
    {get_base_head("LoopBooks - Bento Grid HUD")}
    <body class="min-h-screen pb-20">
        {navbar}

        <main class="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-6">
            
            <!-- BENTO GRID TOP ROW: Benvenuto, Ricerca rapida e Stato Sistema -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                <!-- Box 1: Saluto & Sistema (Colonna 1) -->
                <div class="bento-card bento-glow-blue rounded-2xl p-6 flex flex-col justify-between space-y-4">
                    <div class="space-y-1">
                        <span class="text-[10px] text-[#00f0ff] uppercase tracking-widest bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/30">NODO ROMA 01</span>
                        <h2 class="text-xl md:text-2xl font-bold text-white font-hud pt-2">Bentornato, Curatore</h2>
                        <p class="text-xs text-neutral-400">Sistema di archiviazione e scansione olografica attivo.</p>
                    </div>
                    <div class="pt-4 border-t border-cyan-950 flex justify-between items-center text-xs font-mono">
                        <span class="text-neutral-400">Sync Cloud:</span>
                        <span class="text-emerald-400 font-bold">99.8% Ottimale</span>
                    </div>
                </div>

                <!-- Box 2: Ricerca e Filtri Bento (Colonna 2 e 3) -->
                <div class="md:col-span-2 bento-card bento-glow-orange rounded-2xl p-6 font-mono">
                    <form method="GET" action="/" class="grid grid-cols-1 sm:grid-cols-3 gap-3 h-full items-center">
                        <div class="space-y-1">
                            <label class="block text-[10px] text-[#00f0ff] uppercase tracking-wider">Cerca Titolo / Autore</label>
                            <input type="text" name="q" value="{q}" placeholder="Cerca nel database..." class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-[10px] text-[#00f0ff] uppercase tracking-wider">Genere</label>
                            <select name="genere" class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                {generi_options}
                            </select>
                        </div>
                        <div class="space-y-1 flex flex-col justify-end">
                            <label class="block text-[10px] text-[#00f0ff] uppercase tracking-wider">Ordinamento</label>
                            <div class="flex gap-2">
                                <select name="ordine" class="flex-1 bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                    <option value="nessuno" {"selected" if ordine=="nessuno" else ""}>Standard</option>
                                    <option value="prezzo_asc" {"selected" if ordine=="prezzo_asc" else ""}>Prezzo Min</option>
                                    <option value="prezzo_desc" {"selected" if ordine=="prezzo_desc" else ""}>Prezzo Max</option>
                                    <option value="valutazione" {"selected" if ordine=="valutazione" else ""}>Top Voti</option>
                                </select>
                                <button type="submit" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] border border-cyan-500/50 font-bold px-4 py-2 rounded-xl text-xs uppercase transition shadow-[0_0_10px_rgba(0,240,255,0.2)]">Vai</button>
                            </div>
                        </div>
                    </form>
                </div>

            </div>

            <!-- BENTO GRID SECTION: Libri di Tendenza -->
            <div class="bento-card rounded-2xl p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-[#00f0ff] rounded-full animate-ping"></span>
                        <h3 class="text-xs md:text-sm font-hud font-bold tracking-widest text-cyan-100 uppercase">Libri di Tendenza</h3>
                    </div>
                    <span class="text-[10px] text-cyan-400 font-mono">LIVE FEED</span>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                    {tendenza_html}
                </div>
            </div>

            <!-- BENTO GRID TWO COLUMNS: Migliori Venditori & Libri Rari -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                <!-- Migliori Venditori -->
                <div class="bento-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 bg-emerald-400 rounded-full"></span>
                            <h3 class="text-xs md:text-sm font-hud font-bold tracking-widest text-cyan-100 uppercase">Migliori Venditori</h3>
                        </div>
                        <span class="text-[10px] text-emerald-400 font-mono">VERIFIED</span>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {venditori_html}
                    </div>
                </div>

                <!-- Libri Rari -->
                <div class="bento-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 bg-amber-400 rounded-full"></span>
                            <h3 class="text-xs md:text-sm font-hud font-bold tracking-widest text-cyan-100 uppercase">Rarità & Collezioni</h3>
                        </div>
                        <span class="text-[10px] text-amber-400 font-mono">PREMIUM</span>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {rari_html}
                    </div>
                </div>

            </div>

            <!-- BENTO GRID SECTION: Oggettistica per Consegne -->
            <div class="bento-card rounded-2xl p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-purple-400 rounded-full"></span>
                        <h3 class="text-xs md:text-sm font-hud font-bold tracking-widest text-cyan-100 uppercase">📦 Oggettistica per Consegne e Archiviazione</h3>
                    </div>
                    <span class="text-[10px] text-purple-400 font-mono">LOGISTICS KIT</span>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                    {oggettistica_html}
                </div>
            </div>

        </main>
    </body>
    </html>
    """

# --- PAGINA VENDITORE ---
@app.get("/venditore/{venditore_id}", response_class=HTMLResponse)
async def venditore_page(venditore_id: str):
    navbar = get_navbar('home')
    libri_venditore = [b for b in BOOKS_DATABASE if b["venditore_id"] == venditore_id]
    nome_venditore = libri_venditore[0]["venditore"] if libri_venditore else "Venditore Autorizzato"
    posizione = libri_venditore[0]["venditore_posizione"] if libri_venditore else "Italia"
    valutazione_v = libri_venditore[0]["venditore_valutazione"] if libri_venditore else "5.0 ★"

    catalogo_html = ""
    for b in libri_venditore:
        catalogo_html += f"""
        <a href="/libro/{b['id']}" class="bento-card rounded-xl p-4 flex gap-4 items-center hover:border-cyan-400 transition group">
            <img src="{b['copertina']}" class="w-16 h-20 object-cover rounded-lg border border-cyan-500/20">
            <div class="font-mono space-y-1">
                <h4 class="font-bold text-sm text-cyan-100 group-hover:text-[#00f0ff]">{b['titolo']}</h4>
                <p class="text-xs text-cyan-400/70">{b['autore']}</p>
                <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
            </div>
        </a>
        """

    return f"""
    {get_base_head(f"{nome_venditore} - Profilo Bento")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-4xl mx-auto px-4 py-12 space-y-8 font-mono">
            <div class="bento-card bento-glow-blue p-8 space-y-4 rounded-2xl">
                <span class="text-[10px] bg-cyan-950 text-[#00f0ff] px-3 py-1 rounded border border-cyan-500/40 uppercase tracking-widest">PROFILO VENDITORE VERIFIED</span>
                <h1 class="text-3xl font-bold text-cyan-100 font-hud">{nome_venditore}</h1>
                <p class="text-xs text-cyan-400/80">📍 Sede Nodo: {posizione} | Valutazione Integrale: {valutazione_v}</p>
            </div>
            
            <div class="space-y-4">
                <h3 class="text-sm font-hud font-bold text-cyan-200 uppercase tracking-wider">Cataloghi Attivi associati</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {catalogo_html if catalogo_html else '<p class="text-xs text-neutral-500 font-mono">Nessun tomo attivo al momento.</p>'}
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- DETTAGLIO LIBRO ---
@app.get("/libro/{libro_id}", response_class=HTMLResponse)
async def libro_detail_page(libro_id: str):
    navbar = get_navbar('home')
    libro = next((b for b in BOOKS_DATABASE if b["id"] == libro_id), BOOKS_DATABASE[0])
    
    return f"""
    {get_base_head(f"{libro['titolo']} - Analisi Bento")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-4xl mx-auto px-4 py-12 font-mono">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bento-card bento-glow-orange p-8 rounded-2xl">
                <div class="flex flex-col items-center justify-center">
                    <img src="{libro['copertina']}" class="w-56 h-72 object-cover rounded-xl border border-cyan-500/40 shadow-xl mb-4">
                    <span class="text-xs text-[#00f0ff] font-bold uppercase tracking-widest bg-cyan-950 px-3 py-1 rounded border border-cyan-500/40">{libro['valutazione']} Media Indice</span>
                </div>
                <div class="md:col-span-2 space-y-4">
                    <span class="text-[10px] text-cyan-400 tracking-widest uppercase">ID PROTOCOLLO ARCHIVIO // {libro['id']}</span>
                    <h1 class="text-3xl font-black text-cyan-100 font-hud">{libro['titolo']}</h1>
                    <p class="text-sm text-cyan-300">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']:.2f} € <span class="text-xs font-normal text-neutral-400">({libro['condizione']})</span></div>
                    <p class="text-cyan-200/80 text-xs leading-relaxed italic border-l-2 border-[#00f0ff] pl-3">{libro['descrizione']}</p>
                    
                    <div class="pt-4 border-t border-cyan-950 flex items-center justify-between text-xs">
                        <div>
                            <span class="text-neutral-500 block">Nodo Partner Autorizzato:</span>
                            <a href="/venditore/{libro['venditore_id']}" class="text-[#00f0ff] font-bold underline hover:text-cyan-300">{libro['venditore']} ({libro['venditore_posizione']})</a>
                        </div>
                        <button onclick="alert('[TRANSACTION COMPLETE] Richiesta registrata nei server centrali!')" class="bg-[#00f0ff] hover:bg-cyan-400 text-black font-bold px-6 py-2.5 rounded-xl transition uppercase tracking-wider shadow-[0_0_15px_rgba(0,240,255,0.4)]">Acquista Ora</button>
                    </div>
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- LA MIA BIBLIOTECA ---
@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page():
    navbar = get_navbar('biblioteca')
    return f"""
    {get_base_head("La Mia Biblioteca - Bento HUD")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-4xl mx-auto px-4 py-12">
            <div class="bento-card bento-glow-blue p-8 space-y-6 rounded-2xl font-mono">
                <h2 class="text-xl font-hud font-bold text-cyan-100 uppercase tracking-widest">La Tua Raccolta Personale</h2>
                <p class="text-cyan-300/70 text-xs">Inventario olografico sincronizzato con il cloud personale della Domus.</p>
                <div class="border border-cyan-500/20 rounded-xl p-12 text-center text-neutral-500 text-xs">
                    Nessun manoscritto registrato nel cloud. Visita <a href="/metti-in-vendita" class="text-[#00f0ff] underline font-bold">Metti in Vendita</a> per scansionare libri.
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- METTI IN VENDITA ---
@app.get("/metti-in-vendita", response_class=HTMLResponse)
async def metti_in_vendita_page():
    navbar = get_navbar('metti-in-vendita')
    return f"""
    {get_base_head("Metti in Vendita - Bento HUD")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-3xl mx-auto px-4 py-12 font-mono">
            <div class="bento-card bento-glow-orange p-8 space-y-6 rounded-2xl">
                <div class="text-center space-y-2">
                    <h2 class="text-2xl font-hud font-bold text-cyan-100 uppercase tracking-widest">Scanner Quantico Tomo</h2>
                    <p class="text-cyan-300/70 text-xs">Inserisci il codice ISBN per avviare il parsing automatico dei metadati olografici.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Codice ISBN..." 
                        class="flex-1 bg-black/80 border border-cyan-500/40 rounded-xl px-4 py-3 text-cyan-100 text-xs focus:outline-none focus:border-[#00f0ff]">
                    <button onclick="alert('[SCAN OK] Tomo scansionato e registrato nei registri globali di LoopBooks!')" 
                        class="bg-[#00f0ff] hover:bg-cyan-400 text-black font-bold px-6 py-3 rounded-xl text-xs uppercase tracking-wider transition shadow-[0_0_20px_rgba(0,240,255,0.5)]">
                        Pubblica
                    </button>
                </div>
            </div>
        </main>
    </body>
    </html>    """
