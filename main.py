import os
import json
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from google import genai
from google.genai import types

app = FastAPI()

# Inizializza il client Gemini (legge automaticamente la variabile d'ambiente GEMINI_API_KEY)
client = genai.Client()

books_db = []
users_db = {}

def render_layout(content: str, active_page: str = "home", user: str = None):
    home_cls = "active" if active_page == "home" else ""
    aggiungi_cls = "active" if active_page == "aggiungi" else ""
    biblioteca_cls = "active" if active_page == "biblioteca" else ""
    
    if user:
        nav_right = f'<span style="color: #38bdf8; margin-left: 1rem; font-size: 0.9rem;">👤 {user}</span><a href="/logout" style="color: #f87171; margin-left: 1rem; text-decoration: none;">Esci</a>'
    else:
        nav_right = '<a href="/login" class="btn-login">Log in</a>'

    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Marketplace</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; }}
            header {{ background: #1e293b; border-bottom: 1px solid #334155; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ font-size: 1.5rem; font-weight: bold; color: #38bdf8; text-decoration: none; letter-spacing: -0.5px; }}
            nav {{ display: flex; gap: 1.5rem; align-items: center; }}
            nav a {{ color: #94a3b8; text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }}
            nav a:hover, nav a.active {{ color: #38bdf8; }}
            .btn-login {{ background: #0369a1; color: #e0f2fe !important; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; }}
            .btn-login:hover {{ background: #0284c7; }}
            main {{ flex: 1; padding: 2rem; display: flex; justify-content: center; align-items: center; }}
            .container {{ max-width: 800px; width: 100%; }}
            .card {{ background: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); border: 1px solid #334155; margin-bottom: 1.5rem; }}
            h1 {{ color: #f8fafc; margin-bottom: 0.75rem; font-size: 1.8rem; }}
            p {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }}
            form {{ display: flex; flex-direction: column; gap: 1rem; text-align: left; }}
            .form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
            .form-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
            label {{ font-size: 0.9rem; color: #94a3b8; }}
            input, select, textarea {{ padding: 0.75rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #f8fafc; font-size: 1rem; width: 100%; }}
            input:focus, select:focus, textarea:focus {{ outline: none; border-color: #38bdf8; }}
            button {{ background: #38bdf8; color: #0f172a; border: none; padding: 0.75rem; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
            button:hover {{ background: #7dd3fc; }}
            .book-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-top: 1.5rem; text-align: left; }}
            .book-card {{ background: #0f172a; border: 1px solid #334155; padding: 1.25rem; border-radius: 8px; display: flex; flex-direction: column; justify-content: space-between; }}
            .book-title {{ font-weight: bold; color: #f8fafc; font-size: 1.1rem; margin-bottom: 0.3rem; }}
            .book-author {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.8rem; }}
            .book-price {{ color: #38bdf8; font-weight: bold; margin-bottom: 1rem; }}
            .btn-buy {{ background: #0369a1; color: white; padding: 0.5rem; text-align: center; border-radius: 4px; text-decoration: none; font-size: 0.9rem; }}
            .btn-buy:hover {{ background: #0284c7; }}
            .auth-link {{ margin-top: 1rem; text-align: center; font-size: 0.9rem; color: #94a3b8; }}
            .auth-link a {{ color: #38bdf8; text-decoration: none; }}
            .auth-link a:hover {{ text-decoration: underline; }}
            .alert-error {{ background: rgba(248, 113, 113, 0.1); border: 1px solid #f87171; color: #f87171; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem; text-align: center; }}
        </style>
        <script>
            async function fetchGoogleBooks() {{
                const isbnInput = document.getElementById('isbn');
                const isbn = isbnInput.value.trim();
                if (isbn.length < 10) {{
                    alert("Inserisci un codice ISBN valido (almeno 10 caratteri).");
                    return;
                }}
                
                // Feedback visivo immediato di ricerca in corso
                const searchBtn = document.getElementById('search-btn');
                const originalText = searchBtn.innerText;
                searchBtn.innerText = "Cerco...";
                searchBtn.disabled = true;

                try {{
                    const response = await fetch('/api/search-isbn?isbn=' + encodeURIComponent(isbn));
                    const data = await response.json();
                    
                    if (data.success) {{
                        if (data.title) document.getElementById('title').value = data.title;
                        if (data.author) document.getElementById('author').value = data.author;
                        if (data.editore) document.getElementById('editore').value = data.editore;
                        if (data.anno_pubblicazione) document.getElementById('anno_pubblicazione').value = data.anno_pubblicazione;
                        if (data.descrizione) document.getElementById('descrizione').value = data.descrizione;
                        if (data.image) document.getElementById('image').value = data.image;
                        if (data.ean) document.getElementById('ean').value = data.ean;
                    }} else {{
                        alert("Libro non trovato tramite questo ISBN.");
                    }}
                }} catch (e) {{
                    console.error("Errore di rete durante il recupero ISBN", e);
                    alert("Errore di connessione durante la ricerca.");
                }} finally {{
                    searchBtn.innerText = originalText;
                    searchBtn.disabled = false;
                }}
            }}

            function calcolaGuadagno() {{
                const prezzo = parseFloat(document.getElementById('price').value) || 0;
                const trattenuta = prezzo * 0.05;
                document.getElementById('trattenuta_val').value = trattenuta.toFixed(2) + " €";
                
                const guadagno = prezzo - trattenuta;
                document.getElementById('guadagno_tot').value = guadagno.toFixed(2) + " €";
            }}
        </script>
    </head>
    <body>
        <header>
            <a href="/" class="logo">LoopBooks</a>
            <nav>
                <a href="/" class="{home_cls}">Home</a>
                <a href="/aggiungi" class="{aggiungi_cls}">Aggiungi libro</a>
                <a href="/biblioteca" class="{biblioteca_cls}">La mia biblioteca</a>
                {nav_right}
            </nav>
        </header>
        <main>
            <div class="container">{content}</div>
        </main>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.cookies.get("session_user")
    books_html = ""
    for book in books_db:
        img_url = book.get('image', '')
        img_tag = f'<img src="{img_url}" style="width:100%; height:160px; object-fit:cover; border-radius:4px; margin-bottom:0.5rem;" alt="Copertina">' if img_url else ''
        books_html += f"""
        <div class="book-card">
            <div>
                {img_tag}
                <div class="book-title">{book['title']}</div>
                <div class="book-author">di {book['author']} ({book['editore']})</div>
                <div class="book-price">{book['price']} €</div>
            </div>
            <a href="/compra/{book['id']}" class="btn-buy">Acquista libro</a>
        </div>
        """
    
    content = f"""
    <div class="card" style="text-align: center;">
        <h1>Marketplace LoopBooks</h1>
        <p>Esplora i libri disponibili o metti in vendita i tuoi volumi.</p>
    </div>
    <h2 style="font-size: 1.4rem; margin-bottom: 1rem;">Libri in evidenza</h2>
    <div class="book-grid">
        {books_html if books_html else "<p>Nessun libro disponibile al momento.</p>"}
    </div>
    """
    return render_layout(content, "home", user)

@app.get("/api/search-isbn")
async def search_isbn(isbn: str):
    try:
        prompt = f"""
        Cerca sul web tutte le informazioni relative al codice ISBN: {isbn}.
        Voglio che restituisci ESCLUSIVAMENTE un oggetto JSON valido (senza blocchi di codice markdown come ```json, solo il testo JSON puro) con le seguenti chiavi esatte:
        - "success": true (oppure false se non trovi assolutamente nulla)
        - "title": "Titolo del libro in italiano o nella lingua originale"
        - "author": "Nome dell'autore o degli autori"
        - "editore": "Casa editrice"
        - "anno_pubblicazione": "Anno di pubblicazione (solo l'anno in formato numerico o stringa es. 2001)"
        - "descrizione": "Una breve sinossi o descrizione del libro"
        - "image": "URL di un'immagine di copertina ufficiale del libro trovata online, oppure stringa vuota se non disponibile"
        - "ean": "{isbn}"
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            ),
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
            raw_text = raw_text.rstrip("`").strip()
            
        data = json.loads(raw_text)
        return JSONResponse(data)
        
    except Exception as e:
        print("Errore durante la ricerca ISBN con Gemini:", e)
        return JSONResponse({"success": False})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    err_html = f'<div class="alert-error">{error}</div>' if error else ''
    content = f"""
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h1>Accedi</h1>
        <p>Usa la tua email per accedere alla tua area personale.</p>
        {err_html}
        <form action="/login" method="post">
            <div class="form-group"><label>Email</label><input type="email" name="email" required placeholder="nome@esempio.it"></div>
            <div class="form-group"><label>Password</label><input type="password" name="password" required placeholder="••••••••"></div>
            <button type="submit">Entra</button>
        </form>
        <div class="auth-link">Non hai ancora un account? <a href="/registra">Registrati ora</a></div>
    </div>
    """
    return render_layout(content, "login")

@app.post("/login")
async def login_action(email: str = Form(...), password: str = Form(...)):
    if email not in users_db or users_db[email] != password:
        return RedirectResponse(url="/login?error=Email+o+password+errati", status_code=303)
    response = RedirectResponse(url="/biblioteca", status_code=303)
    response.set_cookie(key="session_user", value=email)
    return response

@app.get("/registra", response_class=HTMLResponse)
async def registra_page(request: Request, error: str = None):
    err_html = f'<div class="alert-error">{error}</div>' if error else ''
    content = f"""
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h1>Crea un account</h1>
        <p>Registrati per iniziare a pubblicare e vendere i tuoi libri.</p>
        {err_html}
        <form action="/registra" method="post">
            <div class="form-group"><label>Email</label><input type="email" name="email" required placeholder="nome@esempio.it"></div>
            <div class="form-group"><label>Password</label><input type="password" name="password" required placeholder="••••••••"></div>
            <button type="submit">Registrati</button>
        </form>
        <div class="auth-link">Hai già un account? <a href="/login">Accedi</a></div>
    </div>
    """
    return render_layout(content, "login")

@app.post("/registra")
async def registra_action(email: str = Form(...), password: str = Form(...)):
    if email in users_db:
        return RedirectResponse(url="/registra?error=Email+già+registrata", status_code=303)
    users_db[email] = password
    response = RedirectResponse(url="/biblioteca", status_code=303)
    response.set_cookie(key="session_user", value=email)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_user")
    return response

@app.get("/aggiungi", response_class=HTMLResponse)
async def aggiungi_page(request: Request):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    content = """
    <div class="card" style="max-width: 700px; margin: 0 auto;">
        <h1>Aggiungi un nuovo libro</h1>
        <p>Inserisci l'ISBN e premi invio o clicca su "Cerca" per autocompilare i dati tramite IA.</p>
        <form action="/aggiungi" method="post">
            <div class="form-row">
                <div class="form-group">
                    <label>ISBN / Codice EAN (Autocompilazione)</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="isbn" name="isbn" placeholder="Es. 9788845292613" onkeydown="if(event.key === 'Enter') { event.preventDefault(); fetchGoogleBooks(); }" style="flex: 1;">
                        <button type="button" id="search-btn" onclick="fetchGoogleBooks()" style="padding: 0.75rem 1rem; background: #0369a1; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Cerca</button>
                    </div>
                </div>
                <div class="form-group">
                    <label>Codice EAN confermato</label>
                    <input type="text" id="ean" name="ean" placeholder="Codice EAN">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Nome libro (Titolo)</label>
                    <input type="text" id="title" name="title" required placeholder="Titolo del libro">
                </div>
                <div class="form-group">
                    <label>Autore</label>
                    <input type="text" id="author" name="author" required placeholder="Autore">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Editore</label>
                    <input type="text" id="editore" name="editore" placeholder="Casa editrice">
                </div>
                <div class="form-group">
                    <label>Collana</label>
                    <input type="text" name="collana" placeholder="Nome collana">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Anno edizione</label>
                    <input type="text" name="anno_edizione" placeholder="Es. 2021">
                </div>
                <div class="form-group">
                    <label>Anno pubblicazione</label>
                    <input type="text" id="anno_pubblicazione" name="anno_pubblicazione" placeholder="Es. 1980">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Tipologia</label>
                    <select id="tipologia" name="tipologia">
                        <option value="Narrativa">Narrativa</option>
                        <option value="Saggistica">Saggistica</option>
                        <option value="Universitario / Scolastico">Universitario / Scolastico</option>
                        <option value="Giallo / Thriller">Giallo / Thriller</option>
                        <option value="Fantascienza / Fantasy">Fantascienza / Fantasy</option>
                        <option value="Altro">Altro</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Condizioni</label>
                    <select name="condizioni">
                        <option value="Nuovo">Nuovo</option>
                        <option value="Ottime">Ottime condizioni</option>
                        <option value="Buone">Buone condizioni</option>
                        <option value="Discreto">Discreto</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>URL Immagine libro</label>
                <input type="text" id="image" name="image" placeholder="https://...">
            </div>

            <div class="form-group">
                <label>Descrizione</label>
                <textarea id="descrizione" name="descrizione" rows="3" placeholder="Descrizione..."></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Metodo di consegna</label>
                    <select name="consegna">
                        <option value="A domicilio (Casa)">A domicilio (Casa)</option>
                        <option value="Punto di ritiro">Punto di ritiro</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Spese a carico di:</label>
                    <select name="spese_a_carico">
                        <option value="Venditore">Venditore</option>
                        <option value="Fornitore">Fornitore</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Prezzo di vendita (€)</label>
                    <input type="number" step="0.01" id="price" name="price" required placeholder="15.00" oninput="calcolaGuadagno()">
                </div>
                <div class="form-group">
                    <label>Trattenute 5% dell'app</label>
                    <input type="text" id="trattenuta_val" readonly value="0.00 €" style="background: #111827; color: #94a3b8;">
                </div>
            </div>

            <div class="form-group">
                <label><b>GUADAGNO TOTALE STIMATO</b></label>
                <input type="text" id="guadagno_tot" readonly value="0.00 €" style="background: #111827; color: #38bdf8; font-weight: bold; font-size: 1.1rem;">
            </div>

            <button type="submit" style="margin-top: 1rem;">Pubblica annuncio</button>
        </form>
    </div>
    """
    return render_layout(content, "aggiungi", user)

@app.post("/aggiungi")
async def aggiungi_action(
    request: Request, 
    title: str = Form(...), 
    author: str = Form(...), 
    editore: str = Form(...),
    price: float = Form(...),
    image: str = Form(None),
    ean: str = Form(None),
    consegna: str = Form(...)
):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    new_id = len(books_db) + 1
    books_db.append({
        "id": new_id, 
        "title": title, 
        "author": author, 
        "editore": editore,
        "price": f"{price:.2f}", 
        "image": image,
        "ean": ean,
        "consegna": consegna,
        "seller": user
    })
    return RedirectResponse(url="/biblioteca", status_code=303)

@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page(request: Request):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    user_books = [b for b in books_db if b['seller'] == user]
    books_html = ""
    for book in user_books:
        books_html += f"""
        <div class="book-card">
            <div>
                <div class="book-title">{book['title']}</div>
                <div class="book-author">di {book['author']} ({book['editore']})</div>
                <div class="book-price">{book['price']} €</div>
            </div>
            <span style="font-size: 0.8rem; color: #10b981; margin-top: 0.5rem;">In vendita</span>
        </div>
        """

    content = f"""
    <div class="card">
        <h1>La mia biblioteca</h1>
        <p>Benvenuto nell'area riservata di <strong>{user}</strong>. Qui puoi gestire i libri che hai pubblicato.</p>
        <a href="/aggiungi" style="display: inline-block; background: #38bdf8; color: #0f172a; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-weight: bold;">+ Aggiungi nuovo libro</a>
    </div>
    <h2 style="font-size: 1.4rem; margin-bottom: 1rem;">I tuoi annunci attivi</h2>
    <div class="book-grid">
        {books_html if books_html else "<p>Non hai ancora inserito nessun libro nella tua biblioteca.</p>"}
    </div>
    """
    return render_layout(content, "biblioteca", user)

@app.get("/compra/{book_id}", response_class=HTMLResponse)
async def compra_page(request: Request, book_id: int):
    user = request.cookies.get("session_user")
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        return RedirectResponse(url="/", status_code=303)
        
    content = f"""
    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
        <h1>Conferma acquisto</h1>
        <p>Stai per acquistare <strong>{book['title']}</strong> di {book['author']}.</p>
        <div style="font-size: 1.5rem; color: #38bdf8; margin: 1.5rem 0; font-weight: bold;">{book['price']} €</div>
        <p style="font-size: 0.85rem; color: #94a3b8;">Consegna: {book.get('consegna', 'A domicilio')}</p>
        <p style="font-size: 0.85rem; color: #94a3b8;">Venduto da: {book['seller']}</p>
        <a href="/grazie" style="display: block; background: #10b981; color: white; padding: 0.75rem; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 1rem;">Conferma e paga</a>
    </div>
    """
    return render_layout(content, "home", user)

@app.get("/grazie", response_class=HTMLResponse)
async def grazie_page(request: Request):
    user = request.cookies.get("session_user")
    content = """
    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
        <h1 style="color: #10b981;">Acquisto completato!</h1>
        <p>Grazie per aver acquistato su LoopBooks. Il venditore è stato avvisato della transazione.</p>
        <a href="/" style="display: inline-block; background: #38bdf8; color: #0f172a; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 1rem;">Torna alla Home</a>
    </div>
    """
    return render_layout(content, "home", user)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
