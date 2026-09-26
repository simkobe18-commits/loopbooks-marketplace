import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Database in memoria temporaneo
books_db = [
    {"id": 1, "title": "Il Nome della Rosa", "author": "Umberto Eco", "price": "15.00 €", "seller": "admin@loopbooks.it"},
    {"id": 2, "title": "1984", "author": "George Orwell", "price": "12.00 €", "seller": "admin@loopbooks.it"}
]

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
            label {{ font-size: 0.9rem; color: #94a3b8; }}
            input {{ padding: 0.75rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #f8fafc; font-size: 1rem; }}
            input:focus {{ outline: none; border-color: #38bdf8; }}
            button {{ background: #38bdf8; color: #0f172a; border: none; padding: 0.75rem; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
            button:hover {{ background: #7dd3fc; }}
            .book-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-top: 1.5rem; text-align: left; }}
            .book-card {{ background: #0f172a; border: 1px solid #334155; padding: 1.25rem; border-radius: 8px; display: flex; flex-direction: column; justify-content: space-between; }}
            .book-title {{ font-weight: bold; color: #f8fafc; font-size: 1.1rem; margin-bottom: 0.3rem; }}
            .book-author {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.8rem; }}
            .book-price {{ color: #38bdf8; font-weight: bold; margin-bottom: 1rem; }}
            .btn-buy {{ background: #0369a1; color: white; padding: 0.5rem; text-align: center; border-radius: 4px; text-decoration: none; font-size: 0.9rem; }}
            .btn-buy:hover {{ background: #0284c7; }}
        </style>
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
        books_html += f"""
        <div class="book-card">
            <div>
                <div class="book-title">{book['title']}</div>
                <div class="book-author">di {book['author']}</div>
                <div class="book-price">{book['price']}</div>
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

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    content = """
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h1>Accedi</h1>
        <p>Usa la tua email per accedere alla tua area personale.</p>
        <form action="/login" method="post">
            <label>Email</label>
            <input type="email" name="email" required placeholder="nome@esempio.it">
            <label>Password</label>
            <input type="password" name="password" required placeholder="••••••••">
            <button type="submit">Entra</button>
        </form>
    </div>
    """
    return render_layout(content, "login")

@app.post("/login")
async def login_action(email: str = Form(...), password: str = Form(...)):
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
    <div class="card" style="max-width: 500px; margin: 0 auto;">
        <h1>Aggiungi un nuovo libro</h1>
        <p>Inserisci i dettagli del libro che desideri mettere in vendita.</p>
        <form action="/aggiungi" method="post">
            <label>Titolo del libro</label>
            <input type="text" name="title" required placeholder="Es. Il Nome della Rosa">
            <label>Autore</label>
            <input type="text" name="author" required placeholder="Es. Umberto Eco">
            <label>Prezzo (€)</label>
            <input type="text" name="price" required placeholder="Es. 12.50 €">
            <button type="submit">Pubblica annuncio</button>
        </form>
    </div>
    """
    return render_layout(content, "aggiungi", user)

@app.post("/aggiungi")
async def aggiungi_action(request: Request, title: str = Form(...), author: str = Form(...), price: str = Form(...)):
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    new_id = len(books_db) + 1
    books_db.append({"id": new_id, "title": title, "author": author, "price": price, "seller": user})
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
                <div class="book-author">di {book['author']}</div>
                <div class="book-price">{book['price']}</div>
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
        <div style="font-size: 1.5rem; color: #38bdf8; margin: 1.5rem 0; font-weight: bold;">{book['price']}</div>
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
