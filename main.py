import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Marketplace</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); text-align: center; max-width: 400px; }
            h1 { color: #38bdf8; margin-bottom: 0.5rem; font-size: 2rem; letter-spacing: -0.5px; }
            p { color: #94a3b8; font-size: 0.95rem; }
            .badge { display: inline-block; background: #0369a1; color: #e0f2fe; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin-top: 1.2rem; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>LoopBooks</h1>
            <p>Il marketplace di libri è pronto per il deploy!</p>
            <div class="badge">Online su GitHub & Render</div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)