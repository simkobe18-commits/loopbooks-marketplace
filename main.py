import os
import json
from fastapi import FastAPI, Form
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

BIBLIOTECA_UTENTE = {
    "profilo": {
        "nome": "Aaru Curatore",
        "ruolo": "Master Collector",
        "id_venditore": "aaru-milano",
        "sede": "Milano (MI)",
        "valutazione": "5.0 ★ (420 recensioni)"
    },
    "metriche": {
        "libri_venduti_num": 14,
        "guadagno_totale_netto": 840.50,
        "libri_comprati_num": 22,
        "totale_comprato": 1320.00,
        "magazzino_num": 8,
        "valore_magazzino": 745.00
    },
    "elenco": [
        {"id": "lib-u1", "titolo": "Il Nome della Rosa", "autore": "Umberto Eco", "prezzo": 14.00, "valutazione": 4.9, "stato": "magazzino", "genere": "Gialli, Thriller e Noir", "condizione": "Ottime condizioni", "copertina": "https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg"},
        {"id": "lib-u2", "titolo": "Le otto montagne", "autore": "Paolo Cognetti", "prezzo": 18.50, "valutazione": 4.8, "stato": "comprato", "genere": "Romanzi contemporanei", "condizione": "Come nuovo", "copertina": "https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg"},
        {"id": "lib-u3", "titolo": "L'amica geniale", "autore": "Elena Ferrante", "prezzo": 15.00, "valutazione": 5.0, "stato": "venduto", "genere": "Romanzi contemporanei", "condizione": "Perfetto", "copertina": "https://covers.openlibrary.org/b/isbn/9788866325087-L.jpg"},
        {"id": "lib-u4", "titolo": "Codice Atlantico (Raro)", "autore": "Leonardo da Vinci", "prezzo": 120.00, "valutazione": 5.0, "stato": "preferiti", "genere": "Arte, Musica e Cinema", "condizione": "Rarità", "copertina": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"},
        {"id": "lib-u5", "titolo": "Omero, Iliade", "autore": "Alessandro Baricco", "prezzo": 16.50, "valutazione": 4.7, "stato": "magazzino", "genere": "Classici della letteratura", "copertina": "https://covers.openlibrary.org/b/isbn/9788806231362-L.jpg"}
    ]
}

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
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            body {{
                background-color: #030712;
                color: #e5e7eb;
                font-family: 'Plus Jakarta Sans', sans-serif;
                overflow-x: hidden;
            }}
            h1, h2, h3, h4, .font-hud {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                letter-spacing: -0.02em;
            }}
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
            <a href="/" class="text-[#00f0ff] font-extrabold text-sm md:text-base tracking-[0.15em] uppercase font-hud flex items-center gap-2">
                <span class="inline-block w-2.5 h-2.5 bg-[#00f0ff] rounded-full animate-pulse shadow-[0_0_10px_#00f0ff]"></span>
                LOOPBOOKS // BENTO HUD
            </a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-semibold tracking-wider uppercase">
                <a href="/" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'home' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">COMPRA (HOME)</a>
                <a href="/metti-in-vendita" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'metti-in-vendita' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">VENDI</a>
                <a href="/biblioteca" class="{'text-[#00f0ff] font-bold border-b-2 border-[#00f0ff]' if active_page == 'biblioteca' else 'text-neutral-400 hover:text-[#00f0ff]'} pb-1 transition">LA MIA BIBLIOTECA</a>
            </nav>
        </div>
        <div class="flex items-center gap-4">
            <a href="/biblioteca" class="hidden lg:inline-block text-[11px] font-medium text-cyan-400 bg-cyan-950/40 px-3.5 py-1 rounded-lg border border-cyan-500/30 hover:border-cyan-400 transition">👤 {BIBLIOTECA_UTENTE['profilo']['nome']}</a>
            <a href="/metti-in-vendita" class="bg-cyan-950/60 hover:bg-cyan-900/80 text-[#00f0ff] border border-[#00f0ff]/50 font-semibold text-xs px-4 py-2 rounded-lg transition shadow-[0_0_12px_rgba(0,240,255,0.2)]">
                [ SCANNER ]
            </a>
        </div>
    </header>
    """

# --- HOME PAGE (COMPRA) ---
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
    elif ordine == "alfabetico":
        libri_filtrati.sort(key=lambda x: x['titolo'])

    def render_cards_horizontal(lista):
        if not lista:
            return '<p class="text-xs text-neutral-500 font-medium italic">Nessun tomo trovato.</p>'
        html = ""
        for b in lista:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[190px] md:min-w-[210px] bg-black/40 border border-cyan-500/20 rounded-xl p-3 hover:border-cyan-400 hover:scale-[1.02] transition duration-300 flex-shrink-0 group relative space-y-2">
                <div class="h-44 bg-black rounded-lg overflow-hidden relative border border-cyan-500/10">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                    <span class="absolute top-2 right-2 bg-black/80 backdrop-blur text-[#00f0ff] font-semibold text-[10px] px-2 py-0.5 rounded border border-cyan-500/40">{b['valutazione']}</span>
                </div>
                <div class="space-y-1">
                    <h4 class="font-bold text-xs text-cyan-100 truncate group-hover:text-[#00f0ff] transition">{b['titolo']}</h4>
                    <p class="text-[11px] text-cyan-400/70 truncate">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-1 border-t border-cyan-950">
                        <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
                        <span class="text-[9px] font-medium bg-cyan-950/80 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/20 truncate max-w-[85px]">{b['condizione']}</span>
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
        <div class="min-w-[210px] bg-black/40 border border-cyan-500/20 rounded-xl p-3 flex-shrink-0 space-y-2">
            <div class="h-32 bg-black rounded-lg overflow-hidden border border-cyan-500/10">
                <img src="{obj['immagine']}" class="w-full h-full object-cover">
            </div>
            <h4 class="font-bold text-xs text-cyan-100 truncate">{obj['nome']}</h4>
            <p class="text-[10px] text-neutral-400 line-clamp-2">{obj['descrizione']}</p>
            <div class="flex justify-between items-center pt-1 border-t border-cyan-950">
                <span class="text-emerald-400 font-bold text-xs">{obj['prezzo']}</span>
                <button onclick="alert('[SUCCESS] Oggetto aggiunto al kit olografico!')" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] font-semibold text-[10px] px-2.5 py-1 rounded border border-cyan-500/40 transition">ORDINA</button>
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
    {get_base_head("LoopBooks - Compra & Bento Grid HUD")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bento-card bento-glow-blue rounded-2xl p-6 flex flex-col justify-between space-y-4">
                    <div class="space-y-1">
                        <span class="text-[10px] font-semibold text-[#00f0ff] uppercase tracking-widest bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/35">NODO COMPRA</span>
                        <h2 class="text-xl md:text-2xl font-bold text-white font-hud pt-2">Esplora Cataloghi</h2>
                        <p class="text-xs text-neutral-400 font-medium">Ricerca avanzata tomi e volumi garantiti.</p>
                    </div>
                    <div class="pt-4 border-t border-cyan-950 flex justify-between items-center text-xs">
                        <span class="text-neutral-400 font-medium">Tomi Disponibili:</span>
                        <span class="text-[#00f0ff] font-bold">{len(BOOKS_DATABASE)} Volumi Attivi</span>
                    </div>
                </div>
                <div class="md:col-span-2 bento-card bento-glow-orange rounded-2xl p-6">
                    <form method="GET" action="/" class="grid grid-cols-1 sm:grid-cols-3 gap-3 h-full items-center">
                        <div class="space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase tracking-wider">Cerca Titolo / Autore</label>
                            <input type="text" name="q" value="{q}" placeholder="Cerca nel database..." class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase tracking-wider">Genere</label>
                            <select name="genere" class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                {generi_options}
                            </select>
                        </div>
                        <div class="space-y-1 flex flex-col justify-end">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase tracking-wider">Ordinamento</label>
                            <div class="flex gap-2">
                                <select name="ordine" class="flex-1 bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                    <option value="nessuno" {"selected" if ordine=="nessuno" else ""}>Standard</option>
                                    <option value="prezzo_asc" {"selected" if ordine=="prezzo_asc" else ""}>Prezzo Min</option>
                                    <option value="prezzo_desc" {"selected" if ordine=="prezzo_desc" else ""}>Prezzo Max</option>
                                    <option value="valutazione" {"selected" if ordine=="valutazione" else ""}>Top Voti</option>
                                    <option value="alfabetico" {"selected" if ordine=="alfabetico" else ""}>Alfabetico</option>
                                </select>
                                <button type="submit" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] border border-cyan-500/50 font-bold px-4 py-2 rounded-xl text-xs uppercase transition shadow-[0_0_10px_rgba(0,240,255,0.2)]">Vai</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div class="bento-card rounded-2xl p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-[#00f0ff] rounded-full animate-ping"></span>
                        <h3 class="text-xs md:text-sm font-hud font-bold tracking-wider text-cyan-100 uppercase">Libri di Tendenza</h3>
                    </div>
                    <span class="text-[10px] font-semibold text-cyan-400">LIVE FEED</span>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                    {tendenza_html}
                </div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bento-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 bg-emerald-400 rounded-full"></span>
                            <h3 class="text-xs md:text-sm font-hud font-bold tracking-wider text-cyan-100 uppercase">Migliori Venditori</h3>
                        </div>
                        <span class="text-[10px] font-semibold text-emerald-400">VERIFIED</span>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {venditori_html}
                    </div>
                </div>
                <div class="bento-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 bg-amber-400 rounded-full"></span>
                            <h3 class="text-xs md:text-sm font-hud font-bold tracking-wider text-cyan-100 uppercase">Rarità & Collezioni</h3>
                        </div>
                        <span class="text-[10px] font-semibold text-amber-400">PREMIUM</span>
                    </div>
                    <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                        {rari_html}
                    </div>
                </div>
            </div>
            <div class="bento-card rounded-2xl p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-cyan-950 pb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-purple-400 rounded-full"></span>
                        <h3 class="text-xs md:text-sm font-hud font-bold tracking-wider text-cyan-100 uppercase">📦 Oggettistica per Consegne e Archiviazione</h3>
                    </div>
                    <span class="text-[10px] font-semibold text-purple-400">LOGISTICS KIT</span>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-2">
                    {oggettistica_html}
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- SEZIONE LA MIA BIBLIOTECA ---
@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page(filtro_stato: str = "tutti", q_biblio: str = "", ordine_biblio: str = "nessuno", genere_biblio: str = "tutti"):
    navbar = get_navbar('biblioteca')
    met = BIBLIOTECA_UTENTE["metriche"]
    prof = BIBLIOTECA_UTENTE["profilo"]
    
    elenco = BIBLIOTECA_UTENTE["elenco"].copy()
    if q_biblio:
        elenco = [b for b in elenco if q_biblio.lower() in b['titolo'].lower() or q_biblio.lower() in b['autore'].lower()]
    if filtro_stato != "tutti":
        elenco = [b for b in elenco if b['stato'] == filtro_stato]
    if genere_biblio != "tutti":
        elenco = [b for b in elenco if b['genere'] == genere_biblio]

    if ordine_biblio == "prezzo_asc":
        elenco.sort(key=lambda x: x['prezzo'])
    elif ordine_biblio == "prezzo_desc":
        elenco.sort(key=lambda x: x['prezzo'], reverse=True)
    elif ordine_biblio == "valutazione":
        elenco.sort(key=lambda x: float(x.get('valutazione', 0)), reverse=True)
    elif ordine_biblio == "alfabetico":
        elenco.sort(key=lambda x: x['titolo'])

    elenco_html = ""
    for b in elenco:
        badge_stato = ""
        if b['stato'] == 'comprato': badge_stato = '<span class="bg-blue-950 text-blue-400 border border-blue-500/40 text-[9px] font-semibold px-2 py-0.5 rounded">COMPRATO</span>'
        elif b['stato'] == 'venduto': badge_stato = '<span class="bg-emerald-950 text-emerald-400 border border-emerald-500/40 text-[9px] font-semibold px-2 py-0.5 rounded">VENDUTO</span>'
        elif b['stato'] == 'magazzino': badge_stato = '<span class="bg-amber-950 text-amber-400 border border-amber-500/40 text-[9px] font-semibold px-2 py-0.5 rounded">MAGAZZINO</span>'
        elif b['stato'] == 'preferiti': badge_stato = '<span class="bg-purple-950 text-purple-400 border border-purple-500/40 text-[9px] font-semibold px-2 py-0.5 rounded">PREFERITO</span>'

        elenco_html += f"""
        <div class="bento-card rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-cyan-400 transition">
            <div class="flex items-center gap-4">
                <img src="{b['copertina']}" class="w-16 h-20 object-cover rounded-lg border border-cyan-500/30">
                <div class="space-y-1">
                    <div class="flex items-center gap-2">
                        <h4 class="font-bold text-sm text-cyan-100">{b['titolo']}</h4>
                        {badge_stato}
                    </div>
                    <p class="text-xs text-cyan-400/70 font-medium">di {b['autore']} • <span class="text-neutral-400">{b['condizione']}</span></p>
                    <p class="text-[11px] font-medium text-amber-300">Valutazione: {b['valutazione']} ★</p>
                </div>
            </div>
            <div class="flex sm:flex-col items-end justify-between w-full sm:w-auto">
                <span class="text-emerald-400 font-bold text-sm">{b['prezzo']:.2f} €</span>
                <a href="/libro/{b['id']}" class="text-[10px] font-semibold text-[#00f0ff] hover:underline mt-1">[ Visualizza Tomo ]</a>
            </div>
        </div>
        """

    generi_options_b = '<option value="tutti">-- TUTTI I GENERI --</option>'
    for macro, sottos in GENERI_STRUTTURA.items():
        generi_options_b += f'<optgroup label="{macro}">'
        for sotto in sottos:
            sel = "selected" if genere_biblio == sotto else ""
            generi_options_b += f'<option value="{sotto}" {sel}>{sotto}</option>'
        generi_options_b += '</optgroup>'

    return f"""
    {get_base_head("La Tua Biblioteca - Bento HUD")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bento-card bento-glow-blue p-6 rounded-2xl flex flex-col justify-between space-y-4">
                    <div class="space-y-1">
                        <span class="text-[10px] font-semibold text-[#00f0ff] uppercase tracking-widest bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/30">IL MIO PROFILO VENDITORE</span>
                        <h2 class="text-xl font-bold text-cyan-100 font-hud pt-2">{prof['nome']}</h2>
                        <p class="text-xs text-neutral-400 font-medium">📍 Sede: {prof['sede']} | Rating: {prof['valutazione']}</p>
                    </div>
                    <div class="pt-4 border-t border-cyan-950 flex justify-between items-center text-xs font-semibold">
                        <span class="text-neutral-400 font-medium">ID Preview Nodo:</span>
                        <a href="/venditore/{prof['id_venditore']}" class="text-[#00f0ff] underline font-bold hover:text-cyan-300">Apri Profilo Pubblico →</a>
                    </div>
                </div>
                <div class="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-4">
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Libri Venduti</span>
                        <div class="text-2xl font-bold text-cyan-100 font-hud pt-2">{met['libri_venduti_num']}</div>
                        <span class="text-[9px] font-semibold text-emerald-400 mt-1">Negoziati con successo</span>
                    </div>
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Guadagno Netto</span>
                        <div class="text-2xl font-bold text-emerald-400 font-hud pt-2">{met['guadagno_totale_netto']:.2f} €</div>
                        <span class="text-[9px] font-semibold text-emerald-400/80 mt-1">Totale incassato</span>
                    </div>
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Libri Comprati</span>
                        <div class="text-2xl font-bold text-cyan-100 font-hud pt-2">{met['libri_comprati_num']}</div>
                        <span class="text-[9px] font-semibold text-blue-400 mt-1">Acquisizioni totali</span>
                    </div>
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Totale Comprato</span>
                        <div class="text-2xl font-bold text-cyan-200 font-hud pt-2">{met['totale_comprato']:.2f} €</div>
                        <span class="text-[9px] font-semibold text-neutral-400 mt-1">Investimento spesa</span>
                    </div>
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Magazzino Libri</span>
                        <div class="text-2xl font-bold text-amber-300 font-hud pt-2">{met['magazzino_num']}</div>
                        <span class="text-[9px] font-semibold text-amber-400 mt-1">Volumi in stock</span>
                    </div>
                    <div class="bento-card p-4 rounded-xl flex flex-col justify-between">
                        <span class="text-[10px] font-semibold text-neutral-400 uppercase">Valore Magazzino</span>
                        <div class="text-2xl font-bold text-amber-400 font-hud pt-2">{met['valore_magazzino']:.2f} €</div>
                        <span class="text-[9px] font-semibold text-amber-400/80 mt-1">Stima inventario</span>
                    </div>
                </div>
            </div>
            <div class="bento-card rounded-2xl p-6 space-y-4">
                <form method="GET" action="/biblioteca" class="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
                    <div class="space-y-1">
                        <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Ricerca in Biblioteca</label>
                        <input type="text" name="q_biblio" value="{q_biblio}" placeholder="Cerca titolo/autore..." class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                    </div>
                    <div class="space-y-1">
                        <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Filtro Stato</label>
                        <select name="filtro_stato" class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                            <option value="tutti" {"selected" if filtro_stato=="tutti" else ""}>Tutti gli elementi</option>
                            <option value="comprato" {"selected" if filtro_stato=="comprato" else ""}>Comprati</option>
                            <option value="venduto" {"selected" if filtro_stato=="venduto" else ""}>Venduti</option>
                            <option value="magazzino" {"selected" if filtro_stato=="magazzino" else ""}>Magazzino</option>
                            <option value="preferiti" {"selected" if filtro_stato=="preferiti" else ""}>Preferiti</option>
                        </select>
                    </div>
                    <div class="space-y-1">
                        <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Filtro Genere</label>
                        <select name="genere_biblio" class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                            {generi_options_b}
                        </select>
                    </div>
                    <div class="space-y-1 flex gap-2">
                        <div class="flex-1 space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Ordina per</label>
                            <select name="ordine_biblio" class="w-full bg-black/70 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                <option value="nessuno" {"selected" if ordine_biblio=="nessuno" else ""}>Standard</option>
                                <option value="prezzo_asc" {"selected" if ordine_biblio=="prezzo_asc" else ""}>Prezzo Min</option>
                                <option value="prezzo_desc" {"selected" if ordine_biblio=="prezzo_desc" else ""}>Prezzo Max</option>
                                <option value="valutazione" {"selected" if ordine_biblio=="valutazione" else ""}>Valutazione ★</option>
                                <option value="alfabetico" {"selected" if ordine_biblio=="alfabetico" else ""}>Alfabetico</option>
                            </select>
                        </div>
                        <button type="submit" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] border border-cyan-500/50 font-bold px-4 py-2 rounded-xl text-xs uppercase transition h-[34px] self-end">Filtra</button>
                    </div>
                </form>
            </div>
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-xs font-hud font-bold text-cyan-100 uppercase tracking-wider">Elenco Completo Archiviato ({len(elenco)})</h3>
                    <span class="text-[10px] font-medium text-neutral-400">Qualità Immagini HD Attiva</span>
                </div>
                <div class="grid grid-cols-1 gap-4">
                    {elenco_html if elenco_html else '<p class="text-xs text-neutral-500 p-8 text-center font-medium">Nessun tomo corrisponde ai filtri selezionati.</p>'}
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
    nome_venditore = libri_venditore[0]["venditore"] if libri_venditore else BIBLIOTECA_UTENTE["profilo"]["nome"]
    posizione = libri_venditore[0]["venditore_posizione"] if libri_venditore else BIBLIOTECA_UTENTE["profilo"]["sede"]
    valutazione_v = libri_venditore[0]["venditore_valutazione"] if libri_venditore else BIBLIOTECA_UTENTE["profilo"]["valutazione"]

    catalogo_html = ""
    for b in libri_venditore:
        catalogo_html += f"""
        <a href="/libro/{b['id']}" class="bento-card rounded-xl p-4 flex gap-4 items-center hover:border-cyan-400 transition group">
            <img src="{b['copertina']}" class="w-16 h-20 object-cover rounded-lg border border-cyan-500/20">
            <div class="space-y-1">
                <h4 class="font-bold text-sm text-cyan-100 group-hover:text-[#00f0ff]">{b['titolo']}</h4>
                <p class="text-xs text-cyan-400/70 font-medium">{b['autore']}</p>
                <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
            </div>
        </a>
        """

    return f"""
    {get_base_head(f"{nome_venditore} - Profilo Bento")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-4xl mx-auto px-4 py-12 space-y-8">
            <div class="bento-card bento-glow-blue p-8 space-y-4 rounded-2xl">
                <span class="text-[10px] font-semibold bg-cyan-950 text-[#00f0ff] px-3 py-1 rounded border border-cyan-500/40 uppercase tracking-widest">PROFILO VENDITORE VERIFIED</span>
                <h1 class="text-3xl font-bold text-cyan-100 font-hud">{nome_venditore}</h1>
                <p class="text-xs text-cyan-400/80 font-medium">📍 Sede Nodo: {posizione} | Valutazione Integrale: {valutazione_v}</p>
            </div>
            <div class="space-y-4">
                <h3 class="text-sm font-hud font-bold text-cyan-200 uppercase tracking-wider">Cataloghi Attivi associati</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {catalogo_html if catalogo_html else '<p class="text-xs text-neutral-500 font-medium">Nessun tomo attivo al momento.</p>'}
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
        <main class="max-w-4xl mx-auto px-4 py-12">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bento-card bento-glow-orange p-8 rounded-2xl">
                <div class="flex flex-col items-center justify-center">
                    <img src="{libro['copertina']}" class="w-56 h-72 object-cover rounded-xl border border-cyan-500/40 shadow-xl mb-4">
                    <span class="text-xs font-bold text-[#00f0ff] uppercase tracking-widest bg-cyan-950 px-3 py-1 rounded border border-cyan-500/40">{libro['valutazione']} Media Indice</span>
                </div>
                <div class="md:col-span-2 space-y-4">
                    <span class="text-[10px] font-semibold text-cyan-400 tracking-widest uppercase">ID PROTOCOLLO ARCHIVIO // {libro['id']}</span>
                    <h1 class="text-3xl font-extrabold text-cyan-100 font-hud">{libro['titolo']}</h1>
                    <p class="text-sm text-cyan-300 font-medium">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']:.2f} € <span class="text-xs font-normal text-neutral-400">({libro['condizione']})</span></div>
                    <p class="text-cyan-200/80 text-xs leading-relaxed font-medium italic border-l-2 border-[#00f0ff] pl-3">{libro['descrizione']}</p>
                    <div class="pt-4 border-t border-cyan-950 flex items-center justify-between text-xs">
                        <div>
                            <span class="text-neutral-500 font-medium block">Nodo Partner Autorizzato:</span>
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

# --- METTI IN VENDITA (SCANNER + FORM COMPILAZIONE) ---
@app.get("/metti-in-vendita", response_class=HTMLResponse)
async def metti_in_vendita_page():
    navbar = get_navbar('metti-in-vendita')
    
    generi_options_v = ''
    for macro, sottos in GENERI_STRUTTURA.items():
        generi_options_v += f'<optgroup label="{macro}">'
        for sotto in sottos:
            generi_options_v += f'<option value="{sotto}">{sotto}</option>'
        generi_options_v += '</optgroup>'

    return f"""
    {get_base_head("Metti in Vendita - Bento HUD")}
    <body class="min-h-screen pb-20">
        {navbar}
        <main class="max-w-4xl mx-auto px-4 py-12 space-y-6">
            <div class="bento-card bento-glow-orange p-8 space-y-6 rounded-2xl">
                <div class="space-y-2">
                    <span class="text-[10px] font-semibold text-[#00f0ff] uppercase tracking-widest bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/35">MODULO DI ACCERTAMENTO</span>
                    <h2 class="text-2xl font-hud font-bold text-cyan-100 uppercase tracking-wider">Scanner Quantico ISBN & Pubblicazione</h2>
                    <p class="text-cyan-300/70 text-xs font-medium">Inserisci l'ISBN per interrogare gli archivi online oppure compila i dati del volume da inserire nel market.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn-input" value="9788804668237" placeholder="Inserisci ISBN (es. 9788804668237)..." 
                        class="flex-1 bg-black/80 border border-cyan-500/40 rounded-xl px-4 py-3 text-cyan-100 text-xs focus:outline-none focus:border-[#00f0ff]">
                    <button type="button" onclick="fetchBookData()" 
                        class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] border border-cyan-500/50 font-bold px-6 py-3 rounded-xl text-xs uppercase tracking-wider transition shadow-[0_0_15px_rgba(0,240,255,0.3)]">
                        🔍 Scansiona ISBN
                    </button>
                </div>
            </div>

            <form action="/pubblica-tomo" method="POST" class="bento-card p-8 space-y-6 rounded-2xl">
                <h3 class="text-sm font-hud font-bold text-cyan-200 uppercase tracking-wider border-b border-cyan-950 pb-3">Dettagli Tomo & Condizioni di Vendita</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <div class="space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Titolo Tomo</label>
                            <input type="text" id="titolo" name="titolo" required placeholder="Titolo del libro" 
                                class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Autore</label>
                            <input type="text" id="autore" name="autore" required placeholder="Autore" 
                                class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="space-y-1">
                                <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Prezzo (€)</label>
                                <input type="number" step="0.01" name="prezzo" required value="15.00" 
                                    class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-emerald-400 font-bold focus:outline-none focus:border-[#00f0ff]">
                            </div>
                            <div class="space-y-1">
                                <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Condizione</label>
                                <select name="condizione" class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                    <option value="Perfetto">Perfetto</option>
                                    <option value="Come nuovo" selected>Come nuovo</option>
                                    <option value="Ottime condizioni">Ottime condizioni</option>
                                    <option value="Buone condizioni">Buone condizioni</option>
                                    <option value="Rarità da collezione">Rarità da collezione</option>
                                </select>
                            </div>
                        </div>
                        <div class="space-y-1">
                            <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Genere Olografico</label>
                            <select name="genere" class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                {generi_options_v}
                            </select>
                        </div>
                    </div>
                    <div class="space-y-4 flex flex-col justify-between">
                        <div class="space-y-3">
                            <div class="space-y-1">
                                <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">URL Immagine Copertina</label>
                                <input type="text" id="copertina" name="copertina" required value="https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg" 
                                    class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]" oninput="updatePreview(this.value)">
                            </div>
                            <div class="space-y-1">
                                <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Modalità Consegna & Spedizione</label>
                                <select name="consegna" class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">
                                    <option value="Spedizione Corriere Tracciato (4.90 €)">Spedizione Corriere Tracciato (4.90 €)</option>
                                    <option value="Ritiro a mano in Sede a Milano (Gratuito)">Ritiro a mano in Sede a Milano (Gratuito)</option>
                                    <option value="Consegna Express Assicurata (9.90 €)">Consegna Express Assicurata (9.90 €)</option>
                                </select>
                            </div>
                            <div class="space-y-1">
                                <label class="block text-[10px] font-semibold text-[#00f0ff] uppercase">Descrizione / Note</label>
                                <textarea id="descrizione" name="descrizione" rows="3" class="w-full bg-black/80 border border-cyan-500/30 rounded-xl px-3 py-2 text-xs text-cyan-100 focus:outline-none focus:border-[#00f0ff]">Tomo verificato nei registri di LoopBooks.</textarea>
                            </div>
                        </div>
                        <div class="flex items-center gap-4 pt-4 border-t border-cyan-950">
                            <div class="w-16 h-20 bg-black rounded-lg overflow-hidden border border-cyan-500/30 flex-shrink-0">
                                <img id="preview-img" src="https://covers.openlibrary.org/b/isbn/9788804668237-L.jpg" class="w-full h-full object-cover">
                            </div>
                            <button type="submit" class="flex-1 bg-[#00f0ff] hover:bg-cyan-400 text-black font-bold py-3 px-6 rounded-xl text-xs uppercase tracking-wider transition shadow-[0_0_20px_rgba(0,240,255,0.4)]">
                                Pubblica Tomo nel Market
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </main>

        <script>
            function updatePreview(url) {{
                document.getElementById('preview-img').src = url;
            }}

            async function fetchBookData() {{
                const isbn = document.getElementById('isbn-input').value.trim();
                if(!isbn) {{
                    alert('Inserisci un codice ISBN valido.');
                    return;
                }}
                
                let found = false;
                
                // Tentativo 1: OpenLibrary API (molto affidabile per metadati e copertine)
                try {{
                    const response = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${{isbn}}&format=json&jscmd=data`);
                    const data = await response.json();
                    const key = `ISBN:${{isbn}}`;
                    if (data[key]) {{
                        const book = data[key];
                        document.getElementById('titolo').value = book.title || '';
                        document.getElementById('autore').value = book.authors ? book.authors.map(a => a.name).join(', ') : '';
                        let coverUrl = book.cover && book.cover.large ? book.cover.large : `https://covers.openlibrary.org/b/isbn/${{isbn}}-L.jpg`;
                        document.getElementById('copertina').value = coverUrl;
                        document.getElementById('preview-img').src = coverUrl;
                        document.getElementById('descrizione').value = `Tomo catalogato via OpenLibrary (ISBN: ${{isbn}}).`;
                        found = true;
                        alert('[SCAN OK] Metadati acquisiti tramite OpenLibrary!');
                    }}
                }} catch(e) {{
                    console.log('OpenLibrary fallito, provo Google Books...');
                }}

                // Tentativo 2: Google Books API se il primo non ha dato esito
                if (!found) {{
                    try {{
                        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${{isbn}}`);
                        const data = await response.json();
                        if(data.items && data.items.length > 0) {{
                            const book = data.items[0].volumeInfo;
                            document.getElementById('titolo').value = book.title || '';
                            document.getElementById('autore').value = book.authors ? book.authors.join(', ') : '';
                            if(book.description) {{
                                document.getElementById('descrizione').value = book.description.substring(0, 200) + '...';
                            }}
                            if(book.imageLinks && book.imageLinks.thumbnail) {{
                                let imgUrl = book.imageLinks.thumbnail.replace('http:', 'https:').replace('&zoom=1', '&zoom=0');
                                document.getElementById('copertina').value = imgUrl;
                                document.getElementById('preview-img').src = imgUrl;
                            }} else {{
                                let fallbackUrl = `https://covers.openlibrary.org/b/isbn/${{isbn}}-L.jpg`;
                                document.getElementById('copertina').value = fallbackUrl;
                                document.getElementById('preview-img').src = fallbackUrl;
                            }}
                            found = true;
                            alert('[SCAN OK] Metadati acquisiti tramite Google Books!');
                        }}
                    }} catch(e) {{
                        console.error(e);
                    }}
                }}

                // Fallback finale se nessun servizio risponde via API
                if (!found) {{
                    alert('[AVVISO] Connessione API non riuscita. Configurazione copertina e dati standard basati su ISBN.');
                    let fallbackUrl = `https://covers.openlibrary.org/b/isbn/${{isbn}}-L.jpg`;
                    document.getElementById('copertina').value = fallbackUrl;
                    document.getElementById('preview-img').src = fallbackUrl;
                    document.getElementById('titolo').value = "Volume ISBN " + isbn;
                    document.getElementById('autore').value = "Autore da specificare";
                }}
            }}
        </script>
    </body>
    </html>
    """

# --- AZIONE PUBBLICAZIONE TOMO ---
@app.post("/pubblica-tomo", response_class=HTMLResponse)
async def pubblica_tomo(
    titolo: str = Form(...),
    autore: str = Form(...),
    prezzo: float = Form(...),
    condizione: str = Form(...),
    genere: str = Form(...),
    copertina: str = Form(...),
    consegna: str = Form(...),
    descrizione: str = Form(...)
):
    new_id = f"lib-user-{len(BOOKS_DATABASE) + 1}"
    new_book = {
        "id": new_id,
        "titolo": titolo,
        "autore": autore,
        "prezzo": prezzo,
        "valutazione_num": 5.0,
        "valutazione": "5.0 ★",
        "condizione": condizione,
        "editore": "LoopBooks Publisher",
        "collana": "Edizioni Indipendenti",
        "codice_ean": "9788800000000",
        "anno_edizione": "2026",
        "anno_pubblicazione": "2026",
        "descrizione": f"{descrizione} [Consegna: {consegna}]",
        "venditore": BIBLIOTECA_UTENTE["profilo"]["nome"],
        "venditore_id": BIBLIOTECA_UTENTE["profilo"]["id_venditore"],
        "venditore_posizione": BIBLIOTECA_UTENTE["profilo"]["sede"],
        "venditore_valutazione": BIBLIOTECA_UTENTE["profilo"]["valutazione"],
        "sezione": "tendenza",
        "genere": genere,
        "copertina": copertina
    }
    
    BOOKS_DATABASE.insert(0, new_book)
    BIBLIOTECA_UTENTE["elenco"].insert(0, {
        "id": new_id,
        "titolo": titolo,
        "autore": autore,
        "prezzo": prezzo,
        "valutazione": 5.0,
        "stato": "magazzino",
        "genere": genere,
        "condizione": condizione,
        "copertina": copertina
    })
    BIBLIOTECA_UTENTE["metriche"]["magazzino_num"] += 1
    BIBLIOTECA_UTENTE["metriche"]["valore_magazzino"] += prezzo

    return f"""
    {get_base_head("Pubblicazione Avvenuta - Bento HUD")}
    <body class="min-h-screen pb-20 flex items-center justify-center">
        <div class="bento-card bento-glow-blue p-8 rounded-2xl max-w-lg text-center space-y-6">
            <span class="text-emerald-400 font-bold text-xs uppercase bg-emerald-950 px-3 py-1 rounded border border-emerald-500/40">PROTOCOLLO COMPLETATO</span>
            <h2 class="text-2xl font-bold text-cyan-100 font-hud">Tomo Pubblicato con Successo!</h2>
            <p class="text-xs text-cyan-300/80">Il libro <strong>{titolo}</strong> è ora attivo nel market globale e registrato nella tua biblioteca personale in magazzino.</p>
            <div class="flex justify-center gap-4 pt-4">
                <a href="/" class="bg-cyan-950 hover:bg-cyan-900 text-[#00f0ff] border border-cyan-500/50 font-bold px-5 py-2.5 rounded-xl text-xs uppercase transition">Vai al Market</a>
                <a href="/biblioteca" class="bg-[#00f0ff] hover:bg-cyan-400 text-black font-bold px-5 py-2.5 rounded-xl text-xs uppercase transition shadow-[0_0_15px_rgba(0,240,255,0.4)]">Apri Biblioteca</a>
            </div>
        </div>
    </body>
    </html>
    """
