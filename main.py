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
        "nome": "Valigetta Olografica in Pelle Nera per Consegne Rari",
        "prezzo": "45.00 €",
        "descrizione": "Custodia rigida rinforzata con interno in velluto e chiusura biometrica per trasporto manoscritti preziosi.",
        "immagine": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": "obj-02",
        "nome": "Sigillo in Ceralacca Personalizzato Roma Bibliotheca",
        "prezzo": "28.00 €",
        "descrizione": "Kit completo con manico in ottone massiccio e ceralacca color oro antico per certificare la consegna.",
        "immagine": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": "obj-03",
        "nome": "Guanti Bianchi Antistatici per Archivi Storici",
        "prezzo": "12.00 €",
        "descrizione": "Cotone organico certificato per la manipolazione sicura di tomi antichi e volumi da collezione.",
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

def get_navbar(active_page="home"):
    return f"""
    <header class="w-full bg-[#050b14]/95 backdrop-blur-md border-b border-[#e5c158]/40 py-3 px-8 sticky top-0 z-50 flex justify-between items-center shadow-[0_0_20px_rgba(229,193,88,0.15)]">
        <div class="flex items-center gap-10">
            <a href="/" class="text-[#e5c158] font-black text-lg tracking-[0.2em] uppercase font-mono flex items-center gap-2">
                <span class="inline-block w-2.5 h-2.5 bg-[#e5c158] rounded-full animate-ping"></span>
                LOOPBOOKS
            </a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest uppercase">
                <a href="/" class="{'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'home' else 'text-neutral-400 hover:text-[#e5c158]'} pb-1 transition">HOME</a>
                <a href="/biblioteca" class="{'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'biblioteca' else 'text-neutral-400 hover:text-[#e5c158]'} pb-1 transition">LA MIA BIBLIOTECA</a>
                <a href="/metti-in-vendita" class="{'text-[#e5c158] font-bold border-b border-[#e5c158]' if active_page == 'metti-in-vendita' else 'text-neutral-400 hover:text-[#e5c158]'} pb-1 transition">METTI IN VENDITA</a>
            </nav>
        </div>
        <div>
            <a href="/metti-in-vendita" class="bg-[#e5c158]/10 hover:bg-[#e5c158]/20 text-[#e5c158] border border-[#e5c158]/60 font-mono text-xs px-4 py-2 rounded transition shadow-[0_0_10px_rgba(229,193,88,0.2)]">
                LOG IN
            </a>
        </div>
    </header>
    """

# --- HOME PAGE (CON FILTRI, GENERI E OGGETTISTICA) ---
@app.get("/", response_class=HTMLResponse)
async def home_page(q: str = "", ordine: str = "nessuno", genere: str = "tutti"):
    navbar = get_navbar('home')
    
    # Filtraggio e ordinamento libri
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

    def render_cards(lista):
        if not lista:
            return '<p class="text-xs text-neutral-500 font-mono italic">Nessun tomo corrisponde ai parametri HUD.</p>'
        html = ""
        for b in lista:
            html += f"""
            <a href="/libro/{b['id']}" class="min-w-[200px] md:min-w-[210px] bg-[#0b1320] rounded border border-[#e5c158]/30 overflow-hidden shadow-lg hover:border-[#e5c158] hover:scale-105 transition duration-300 flex-shrink-0 group relative">
                <div class="h-60 bg-black overflow-hidden relative">
                    <img src="{b['copertina']}" class="w-full h-full object-cover group-hover:opacity-90 transition">
                    <span class="absolute top-2 right-2 bg-black/85 text-[#e5c158] font-mono text-[10px] px-2 py-0.5 rounded border border-[#e5c158]/40">{b['valutazione']}</span>
                </div>
                <div class="p-3 space-y-1 font-mono">
                    <h4 class="font-bold text-xs text-[#f3e5ab] truncate">{b['titolo']}</h4>
                    <p class="text-[11px] text-[#e5c158]/70 truncate">{b['autore']}</p>
                    <div class="flex justify-between items-center pt-2">
                        <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
                        <span class="text-[9px] bg-[#1a170c] text-[#e5c158] px-1.5 py-0.5 rounded border border-[#e5c158]/30 truncate max-w-[90px]">{b['condizione']}</span>
                    </div>
                </div>
            </a>
            """
        return html

    tendenza_html = render_cards([b for b in libri_filtrati if b["sezione"] == "tendenza"] or libri_filtrati)
    venditori_html = render_cards([b for b in libri_filtrati if b["sezione"] == "migliori-venditori"] or libri_filtrati)
    per_te_html = render_cards([b for b in libri_filtrati if b["sezione"] == "libri-per-te"] or libri_filtrati)
    rari_html = render_cards(sorted(libri_filtrati, key=lambda x: x['prezzo'], reverse=True))

    oggettistica_html = ""
    for obj in OGGETTISTICA_DATABASE:
        oggettistica_html += f"""
        <div class="min-w-[220px] bg-[#0b1320] rounded border border-[#e5c158]/30 overflow-hidden shadow-lg p-4 flex-shrink-0 space-y-3 font-mono">
            <div class="h-40 bg-black rounded overflow-hidden">
                <img src="{obj['immagine']}" class="w-full h-full object-cover">
            </div>
            <h4 class="font-bold text-xs text-[#f3e5ab] truncate">{obj['nome']}</h4>
            <p class="text-[11px] text-neutral-400 line-clamp-2">{obj['descrizione']}</p>
            <div class="flex justify-between items-center pt-2">
                <span class="text-emerald-400 font-bold text-xs">{obj['prezzo']}</span>
                <button onclick="alert('Oggetto aggiunto al kit di consegna olografico!')" class="bg-[#e5c158]/20 hover:bg-[#e5c158]/30 text-[#e5c158] text-[10px] px-3 py-1.5 rounded border border-[#e5c158]/60 transition">Ordina</button>
            </div>
        </div>
        """

    # Generazione HTML select generi
    generi_options = '<option value="tutti">Tutti i Generi HUD</option>'
    for macro, sottos in GENERI_STRUTTURA.items():
        generi_options += f'<optgroup label="{macro}">'
        for sotto in sottos:
            sel = "selected" if genere == sotto else ""
            generi_options += f'<option value="{sotto}" {sel}>{sotto}</option>'
        generi_options += '</optgroup>'

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Roma Bibliotheca HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
            .hide-scroll::-webkit-scrollbar {{ display: none; }}
            .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
        </style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        
        <!-- ROMA BIBLIOTHECA TOP BADGE -->
        <div class="w-full bg-[#080d16] border-b border-[#e5c158]/30 py-2 text-center">
            <span class="text-[#e5c158] font-mono text-xs tracking-[0.3em] uppercase">ROMA BIBLIOTHECA // SECURE ARCHIVE PROTOCOL</span>
        </div>

        <!-- HERO / BANNER PRINCIPALE -->
        <div class="relative w-full h-[450px] bg-cover bg-center flex items-end p-8 md:p-14 border-b border-[#e5c158]/30" style="background-image: linear-gradient(to top, #030712, rgba(3,7,18,0.4)), url('https://covers.openlibrary.org/b/isbn/9788806200085-L.jpg');">
            <div class="max-w-2xl space-y-4">
                <span class="bg-[#e5c158]/20 text-[#e5c158] border border-[#e5c158]/60 text-[10px] font-mono font-bold px-3 py-1 uppercase tracking-widest rounded shadow-[0_0_10px_rgba(229,193,88,0.3)]">SISTEMA ATTIVO // ARCHIVIO CENTRALE</span>
                <h1 class="text-4xl md:text-5xl font-black tracking-tight text-[#f3e5ab] font-sans">CREA LA TUA BIBLIOTECA</h1>
                <p class="text-[#f3e5ab]/80 text-xs md:text-sm leading-relaxed font-mono">
                    Interfaccia di scansione e gestione volumi rari, bestseller e inventari digitali. Sincronizzazione protetta attiva.
                </p>
                <div class="flex gap-4 pt-2">
                    <a href="/metti-in-vendita" class="bg-[#e5c158] hover:bg-[#d4b045] text-black font-mono font-bold px-8 py-3 rounded flex items-center gap-2 transition shadow-[0_0_20px_rgba(229,193,88,0.4)] text-xs uppercase tracking-widest">
                        ▶ Metti in Vendita
                    </a>
                </div>
            </div>
        </div>

        <main class="px-6 md:px-12 space-y-12 mt-8">
            
            <!-- BARRA FILTRI E RICERCA AVANZATA -->
            <form method="GET" action="/" class="bg-[#0b1320] p-6 rounded border border-[#e5c158]/40 shadow-[0_0_20px_rgba(229,193,88,0.1)] grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
                <div>
                    <label class="block text-[11px] text-[#e5c158] mb-1 uppercase tracking-wider">Cerca libro per nome o autore</label>
                    <input type="text" name="q" value="{q}" placeholder="Es. Il Nome della Rosa..." class="w-full bg-black border border-[#e5c158]/40 rounded px-3 py-2 text-xs text-[#f3e5ab] focus:outline-none focus:border-[#e5c158]">
                </div>
                <div>
                    <label class="block text-[11px] text-[#e5c158] mb-1 uppercase tracking-wider">Filtra per Genere HUD</label>
                    <select name="genere" class="w-full bg-black border border-[#e5c158]/40 rounded px-3 py-2 text-xs text-[#f3e5ab] focus:outline-none focus:border-[#e5c158]">
                        {generi_options}
                    </select>
                </div>
                <div class="flex items-end gap-2">
                    <div class="flex-1">
                        <label class="block text-[11px] text-[#e5c158] mb-1 uppercase tracking-wider">Ordina per</label>
                        <select name="ordine" class="w-full bg-black border border-[#e5c158]/40 rounded px-3 py-2 text-xs text-[#f3e5ab] focus:outline-none focus:border-[#e5c158]">
                            <option value="nessuno" {"selected" if ordine=="nessuno" else ""}>Predefinito</option>
                            <option value="prezzo_asc" {"selected" if ordine=="prezzo_asc" else ""}>Prezzo: Crescente</option>
                            <option value="prezzo_desc" {"selected" if ordine=="prezzo_desc" else ""}>Prezzo: Decrescente</option>
                            <option value="valutazione" {"selected" if ordine=="valutazione" else ""}>Miglior Valutazione</option>
                            <option value="rari" {"selected" if ordine=="rari" else ""}>Più Costosi (Rari)</option>
                        </select>
                    </div>
                    <button type="submit" class="bg-[#e5c158] hover:bg-[#d4b045] text-black font-bold px-4 py-2 rounded text-xs uppercase transition h-[34px]">Filtra</button>
                </div>
            </form>

            <!-- SEZIONE 1: LIBRI DI TENDENZA -->
            <section class="space-y-4">
                <div class="flex items-center gap-2 border-b border-[#e5c158]/30 pb-2">
                    <span class="w-2 h-2 bg-[#e5c158] rounded-full animate-pulse"></span>
                    <h3 class="text-sm font-mono font-bold tracking-widest text-[#f3e5ab] uppercase">Libri di Tendenza</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {tendenza_html}
                </div>
            </section>

            <!-- SEZIONE 2: MIGLIORI VENDITORI -->
            <section class="space-y-4">
                <div class="flex items-center gap-2 border-b border-[#e5c158]/30 pb-2">
                    <span class="w-2 h-2 bg-[#e5c158] rounded-full animate-pulse"></span>
                    <h3 class="text-sm font-mono font-bold tracking-widest text-[#f3e5ab] uppercase">Migliori Venditori (Con Collegamento Profilo)</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {venditori_html}
                </div>
            </section>

            <!-- SEZIONE 3: LIBRI PER TE -->
            <section class="space-y-4">
                <div class="flex items-center gap-2 border-b border-[#e5c158]/30 pb-2">
                    <span class="w-2 h-2 bg-[#e5c158] rounded-full animate-pulse"></span>
                    <h3 class="text-sm font-mono font-bold tracking-widest text-[#f3e5ab] uppercase">Libri per Te</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {per_te_html}
                </div>
            </section>

            <!-- SEZIONE 4: LIBRI RARI (PIÙ COSTOSI) -->
            <section class="space-y-4">
                <div class="flex items-center gap-2 border-b border-[#e5c158]/30 pb-2">
                    <span class="w-2 h-2 bg-[#e5c158] rounded-full animate-pulse"></span>
                    <h3 class="text-sm font-mono font-bold tracking-widest text-[#f3e5ab] uppercase">Libri Rari (Più Costosi)</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {rari_html}
                </div>
            </section>

            <!-- SEZIONE 5: OGGETTISTICA PER CONSEGNE -->
            <section class="space-y-4">
                <div class="flex items-center gap-2 border-b border-[#e5c158]/30 pb-2">
                    <span class="w-2 h-2 bg-[#e5c158] rounded-full animate-pulse"></span>
                    <h3 class="text-sm font-mono font-bold tracking-widest text-[#f3e5ab] uppercase">📦 Oggettistica per Consegne e Archiviazione</h3>
                </div>
                <div class="flex gap-4 overflow-x-auto hide-scroll pb-4">
                    {oggettistica_html}
                </div>
            </section>

        </main>
    </body>
    </html>
    """

# --- PAGINA PROFILO VENDITORE ---
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
        <a href="/libro/{b['id']}" class="bg-[#0b1320] rounded border border-[#e5c158]/30 overflow-hidden shadow hover:border-[#e5c158] transition p-4 flex gap-4 items-center">
            <img src="{b['copertina']}" class="w-16 h-20 object-cover rounded border border-[#e5c158]/20">
            <div class="font-mono space-y-1">
                <h4 class="font-bold text-sm text-[#f3e5ab]">{b['titolo']}</h4>
                <p class="text-xs text-[#e5c158]/70">{b['autore']}</p>
                <span class="text-emerald-400 font-bold text-xs">{b['prezzo']:.2f} €</span>
            </div>
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nome_venditore} - Profilo HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12 space-y-8">
            <div class="bg-[#0b1320] border border-[#e5c158]/40 rounded p-8 space-y-4 shadow-[0_0_30px_rgba(229,193,88,0.15)] font-mono">
                <span class="text-[10px] bg-[#e5c158]/20 text-[#e5c158] px-3 py-1 rounded border border-[#e5c158]/50 uppercase tracking-widest">PROFILO VENDITORE CERTIFICATO</span>
                <h1 class="text-3xl font-bold text-[#f3e5ab]">{nome_venditore}</h1>
                <p class="text-xs text-neutral-400">📍 Sede: {posizione} | Valutazione Globale: {valutazione_v}</p>
            </div>
            
            <div class="space-y-4">
                <h3 class="text-sm font-mono font-bold text-[#f3e5ab] uppercase tracking-wider">Cataloghi e Tomi in Vendita da questo Partner</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {catalogo_html if catalogo_html else '<p class="text-xs text-neutral-500 font-mono">Nessun tomo attualmente attivo.</p>'}
                </div>
            </div>
        </main>
    </body>
    </html>
    """

# --- PAGINA DETTAGLIO LIBRO (Aggiornata con collegamento venditore) ---
@app.get("/libro/{libro_id}", response_class=HTMLResponse)
async def libro_detail_page(libro_id: str):
    navbar = get_navbar('home')
    libro = next((b for b in BOOKS_DATABASE if b["id"] == libro_id), BOOKS_DATABASE[0])
    
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{libro['titolo']} - HUD Analisi</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-5xl mx-auto px-6 py-12 space-y-8 font-mono">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 bg-[#0b1320] p-8 rounded border border-[#e5c158]/40 shadow-[0_0_30px_rgba(229,193,88,0.15)]">
                <div class="flex flex-col items-center justify-center">
                    <img src="{libro['copertina']}" class="w-60 h-80 object-cover rounded border border-[#e5c158]/40 shadow-2xl mb-4">
                    <span class="text-xs text-[#e5c158] font-bold uppercase tracking-widest bg-[#1a170c] px-3 py-1 rounded border border-[#e5c158]/40">{libro['valutazione']} Media</span>
                </div>
                <div class="md:col-span-2 space-y-4">
                    <span class="text-[10px] text-[#e5c158] tracking-widest uppercase">ID PROTOCOLLO // {libro['id']}</span>
                    <h1 class="text-3xl md:text-4xl font-black text-[#f3e5ab] font-sans">{libro['titolo']}</h1>
                    <p class="text-base text-[#e5c158]">di {libro['autore']}</p>
                    <div class="text-2xl font-bold text-emerald-400">{libro['prezzo']:.2f} € <span class="text-xs font-normal text-neutral-400">({libro['condizione']})</span></div>
                    <p class="text-[#f3e5ab]/80 text-xs leading-relaxed italic border-l-2 border-[#e5c158] pl-3">{libro['descrizione']}</p>
                    
                    <div class="pt-4 border-t border-[#e5c158]/20 flex items-center justify-between text-xs">
                        <div>
                            <span class="text-neutral-500 block">Venditore Partner:</span>
                            <a href="/venditore/{libro['venditore_id']}" class="text-[#e5c158] font-bold underline hover:text-[#f3e5ab]">{libro['venditore']} ({libro['venditore_posizione']})</a>
                        </div>
                        <button onclick="alert('Richiesta d\\'acquisto registrata nei protocolli di LoopBooks!')" class="bg-[#e5c158] hover:bg-[#d4b045] text-black font-bold px-6 py-2.5 rounded transition uppercase tracking-wider">Acquista Ora</button>
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
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>La Mia Biblioteca - HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-4xl mx-auto px-6 py-12">
            <div class="bg-[#0b1320] border border-[#e5c158]/40 rounded p-8 space-y-6 shadow-[0_0_20px_rgba(229,193,88,0.1)] font-mono">
                <h2 class="text-xl font-bold text-[#f3e5ab] uppercase tracking-widest">La Tua Raccolta Personale</h2>
                <p class="text-neutral-400 text-xs">I volumi registrati nella tua domus o sincronizzati con il cloud di Jarvis.</p>
                <div class="border border-[#e5c158]/20 rounded p-12 text-center text-neutral-500 text-xs">
                    Nessun manoscritto registrato. Visita <a href="/metti-in-vendita" class="text-[#e5c158] underline font-bold">Metti in Vendita</a> per sincronizzare libri.
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
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Metti in Vendita - HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #030712; color: #e2e8f0; font-family: ui-monospace, monospace; }}</style>
    </head>
    <body class="min-h-screen pb-24">
        {navbar}
        <main class="max-w-3xl mx-auto px-6 py-12 font-mono">
            <div class="bg-[#0b1320] border border-[#e5c158]/40 rounded p-8 space-y-6 shadow-[0_0_30px_rgba(229,193,88,0.15)]">
                <div class="text-center space-y-2">
                    <h2 class="text-2xl font-bold text-[#f3e5ab] uppercase tracking-widest">Registra un Nuovo Tomo</h2>
                    <p class="text-neutral-400 text-xs">Inserisci il codice ISBN per attivare la scansione olografica e l'estrazione dati automatica.</p>
                </div>
                <div class="flex gap-3">
                    <input type="text" id="isbn" value="9788804668237" placeholder="Codice ISBN..." 
                        class="flex-1 bg-black border border-[#e5c158]/40 rounded px-4 py-3 text-[#f3e5ab] text-xs focus:outline-none focus:border-[#e5c158]">
                    <button onclick="alert('Tomo scansionato e registrato con successo nei registri di LoopBooks!')" 
                        class="bg-[#e5c158] hover:bg-[#d4b045] text-black font-bold px-6 py-3 rounded text-xs uppercase tracking-wider transition shadow-[0_0_15px_rgba(229,193,88,0.4)]">
                        Pubblica
                    </button>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
