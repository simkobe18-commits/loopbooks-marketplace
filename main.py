import os
import json
import re
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
    
    if user:
        nav_right = f'<span style="color: #38bdf8; margin-left: 1rem; font-size: 0.9rem;">👤 {user}</span><a href="/logout" style="color: #f87171; text-decoration: none; margin-left: 1rem; font-size: 0.9rem;">Esci</a>'
    else:
        nav_right = '<a href="/login" class="btn-login">Log in</a>'

    return f"""<!DOCTYPE html>
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

        window.addEventListener('DOMContentLoaded', () => {{
            const isbnInput = document.getElementById('isbn');
            if (isbnInput) {{
                isbnInput.addEventListener('keydown', function(event) {{
                    if (event.key === 'Enter') {{
                        event.preventDefault();
                        fetchGoogleBooks();
                    }}
                }});
            }}
        }});
    </script>
</head>
<body>
    <header>
        <a href="/" class="logo">LoopBooks</a>
        <nav>
            <a href="/" class="{home_cls}">Home</a>
            <a href="/aggiungi" class="{aggiungi_cls}">Metti in vendita</a>
            {nav_right}
        </nav>
    </header>
    <main>
        <div class="container">
            {content}
        </div>
    </main>
</body>
</html>"""

@app.get("/api/search-isbn")
async def search_isbn(isbn: str):
    try:
        prompt = f"""
        Trova i dati completi per il codice ISBN: {isbn}.
        Restituisci ESCLUSIVAMENTE un oggetto JSON con queste chiavi esatte e nessun altro testo attorno:
        {{
            "success": true,
            "title": "Titolo del libro",
            "author": "Autore o autori",
            "editore": "Casa editrice",
            "anno_pubblicazione": "Anno (es. 2021)",
            "descrizione": "Breve sinossi del libro",
            "image": "",
            "ean": "{isbn}"
        }}
        Se non trovi il libro, restituisci: {{"success": false}}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            ),
        )

        data = json.loads(response.text.strip())
        return data

    except Exception as e:
        print(f"Errore ricerca ISBN: {e}")
        return {"success": False}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.cookies.get("session_user")
    
    books_html = ""
    if not books_db:
        books_html = "<p style='color: #64748b; text-align: center; grid-column: 1/-1;'>Nessun libro in vendita al momento. Sii il primo ad aggiungerne uno!</p>"
    else:
        for book in books_db:
            books_html += f"""
            <div class="book-card">
                <div>
                    <div class="book-title">{book.get('title')}</div>
                    <div class="book-author">di {book.get('author')} ({book.get('editore', 'N/D')})</div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.5rem;">Condizioni: {book.get('condizioni')}</div>
                </div>
                <div>
                    <div class="book-price">€ {book.get('prezzo')}</div>
                    <a href="#" class="btn-buy" onclick="alert('Contatta il venditore per procedere.'); return false;">Acquista</a>
                </div>
            </div>
            """

    content = f"""
    <div class="card" style="text-align: center;">
        <h1>Marketplace di Libri Usati</h1>
        <p>Acquista e vendi libri in modo semplice e veloce tra lettori.</p>
        <div class="book-grid">
            {books_html}
        </div>
    </div>
    """
    return render_layout(content, active_page="home", user=user)

@app.get("/aggiungi", response_class=HTMLResponse)
async def aggiungi_form(request: Request):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    content = """
    <div class="card">
        <h1>Aggiungi un nuovo libro</h1>
        <p>Inserisci l'ISBN e premi invio o clicca su "Cerca" per autocompilare i dati tramite IA.</p>
        <form action="/aggiungi" method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label for="isbn">ISBN / Codice EAN (Autocompilazione)</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="isbn" name="isbn" placeholder="Es. 9788869183157" style="flex: 1;">
                        <button type="button" id="search-btn" onclick="fetchGoogleBooks()" style="padding: 0.75rem 1rem;">Cerca...</button>
                    </div>
                </div>
                <div class="form-group">
                    <label for="ean">Codice EAN confermato</label>
                    <input type="text" id="ean" name="ean" placeholder="Codice EAN" readonly>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="title">Nome libro (Titolo)</label>
                    <input type="text" id="title" name="title" required placeholder="Titolo del libro">
                </div>
                <div class="form-group">
                    <label for="author">Autore</label>
                    <input type="text" id="author" name="author" required placeholder="Autore">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="editore">Editore</label>
                    <input type="text" id="editore" name="editore" placeholder="Casa editrice">
                </div>
                <div class="form-group">
                    <label for="collana">Collana</label>
                    <input type="text" id="collana" name="collana" placeholder="Nome collana">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="anno_edizione">Anno edizione</label>
                    <input type="text" id="anno_edizione" name="anno_edizione" placeholder="Es. 2021">
                </div>
                <div class="form-group">
                    <label for="anno_pubblicazione">Anno pubblicazione</label>
                    <input type="text" id="anno_pubblicazione" name="anno_pubblicazione" placeholder="Es. 1980">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="tipologia">Tipologia</label>
                    <select id="tipologia" name="tipologia">
                        <option value="Narrativa">Narrativa</option>
                        <option value="Saggistica">Saggistica</option>
                        <option value="Universitario">Universitario</option>
                        <option value="Fumetti / Manga">Fumetti / Manga</option>
                        <option value="Altro">Altro</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="condizioni">Condizioni</label>
                    <select id="condizioni" name="condizioni">
                        <option value="Nuovo">Nuovo</option>
                        <option value="Ottime">Ottime</option>
                        <option value="Buone">Buone</option>
                        <option value="Discrete">Discrete</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label for="image">URL Immagine libro</label>
                <input type="url" id="image" name="image" placeholder="https://...">
            </div>
            <div class="form-group">
                <label for="descrizione">Descrizione</label>
                <textarea id="descrizione" name="descrizione" rows="3" placeholder="Descrizione..."></textarea>
            </div>
            <div class="form-group">
                <label for="prezzo">Prezzo (€)</label>
                <input type="number" step="0.01" id="prezzo" name="prezzo" required placeholder="15.00">
            </div>
            <button type="submit">Pubblica Annuncio</button>
        </form>
    </div>
    """
    return render_layout(content, active_page="aggiungi", user=user)

@app.post("/aggiungi")
async def aggiungi_post(
    request: Request,
    isbn: str = Form(""),
    ean: str = Form(""),
    title: str = Form(...),
    author: str = Form(...),
    editore: str = Form(""),
    collana: str = Form(""),
    anno_edizione: str = Form(""),
    anno_pubblicazione: str = Form(""),
    tipologia: str = Form(""),
    condizioni: str = Form(""),
    image: str = Form(""),
    descrizione: str = Form(""),
    prezzo: float = Form(...)
):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    book = {
        "isbn": isbn,
        "ean": ean,
        "title": title,
        "author": author,
        "editore": editore,
        "collana": collana,
        "anno_edizione": anno_edizione,
        "anno_pubblicazione": anno_pubblicazione,
        "tipologia": tipologia,
        "condizioni": condizioni,
        "image": image,
        "descrizione": descrizione,
        "prezzo": prezzo,
        "seller": user
    }
    books_db.append(book)
    return RedirectResponse(url="/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_get(error: str = None):
    err_html = f'<div class="alert-error">{error}</div>' if error else ''
    content = f"""
    <div class="card" style="max-width: 400px; margin: 0 auto; text-align: center;">
        <h1>Accedi</h1>
        <p>Entra nel tuo account LoopBooks</p>
        {err_html}
        <form action="/login" method="POST">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required placeholder="tu@email.com">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" style="margin-top: 0.5rem;">Accedi</button>
        </form>
        <div class="auth-link">
            Non hai un account? <a href="/register">Registrati</a>
        </div>
    </div>
    """
    return render_layout(content, active_page="login")

@app.post("/login")
async def login_post(email: str = Form(...), password: str = Form(...)):
    if email in users_db and users_db[email] == password:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_user", value=email)
        return response
    return RedirectResponse(url="/login?error=Credenziali+non+valide", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_get(error: str = None):
    err_html = f'<div class="alert-error">{error}</div>' if error else ''
    content = f"""
    <div class="card" style="max-width: 400px; margin: 0 auto; text-align: center;">
        <h1>Registrati</h1>
        <p>Crea un nuovo account su LoopBooks</p>
        {err_html}
        <form action="/register" method="POST">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required placeholder="tu@email.com">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" style="margin-top: 0.5rem;">Registrati</button>
        </form>
        <div class="auth-link">
            Hai già un account? <a href="/login">Accedi</a>
        </div>
    </div>
    """
    return render_layout(content, active_page="register")

@app.post("/register")
async def register_post(email: str = Form(...), password: str = Form(...)):
    if email in users_db:
        return RedirectResponse(url="/register?error=Utente+gia+esistente", status_code=303)
    users_db[email] = password
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_user", value=email)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_user")
    return response
