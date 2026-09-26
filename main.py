import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# Layout comune con la barra di navigazione in alto
def render_layout(content: str, active_page: str = "home"):
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
            
            /* Barra di navigazione in alto */
            header {{ background: #1e293b; border-bottom: 1px solid #334155; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ font-size: 1.5rem; font-weight: bold; color: #38bdf8; text-decoration: none; letter-spacing: -0.5px; }}
            nav {{ display: flex; gap: 1.5rem; align-items: center; }}
            nav a {{ color: #94a3b8; text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }}
            nav a:hover, nav a.active {{ color: #38bdf8; }}
            .btn-login {{ background: #0369a1; color: #e0f2fe !important; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; }}
            .btn-login:hover {{ background: #0284c7; }}

            /* Contenuto principale */
            main {{ flex: 1; display: flex; justify-content: center; align-items: center; padding: 2rem; }}
            .card {{ background: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); text-align: center; max-width: 500px; width: 100%; border: 1px solid #334155; }}
            h1 {{ color: #f8fafc; margin-bottom: 0.75rem; font-size: 1.8rem; }}
            p {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.5; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo">LoopBooks</a>
            <nav>
                <a href="/" class="{"active" if active_page == "home" else ""}">Home</a>
                <a href="/aggiungi" class="{"active" if active_page == "aggiungi" else ""}">Aggiungi libro</a>
                <a href="/biblioteca" class="{"active" if active_page == "biblioteca" else ""}">La mia biblioteca</a>
                <a href="/login" class="btn-login">Log in</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    content = """
    <div class="card">
        <h1>Benvenuto su LoopBooks</h1>
        <p>Il marketplace circolare per i tuoi libri. Esplora i volumi disponibili o inizia ad aggiungere i tuoi titoli preferiti.</p>
    </div>
    """
    return render_layout(content, "home")

@app.get("/aggiungi", response_class=HTMLResponse)
async def aggiungi(request: Request):
    content = """
    <div class="card">
        <h1>Aggiungi Libro</h1>
        <p>Qui potrai inserire i dettagli del libro o cercarlo automaticamente tramite codice ISBN.</p>
    </div>
    """
    return render_layout(content, "aggiungi")

@app.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca(request: Request):
    content = """
    <div class="card">
        <h1>La mia biblioteca</h1>
        <p>Qui troverai l'elenco dei libri che hai messo in vendita o salvato nella tua collezione personale.</p>
    </div>
    """
    return render_layout(content, "biblioteca")

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    content = """
    <div class="card">
        <h1>Accedi a LoopBooks</h1>
        <p>Area riservata per il login degli utenti e la gestione del profilo.</p>
    </div>
    """
    return render_layout(content, "login")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
