import os
import json
import re
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Chiave API di Gemini
GEMINI_API_KEY = "AQ.Ab8RN6KY_3CAtTnmc-F5tPCANTkYuIJWvXPuXFrAyraEXqIuWQ"
client = genai.Client(api_key=GEMINI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cerca Libro con ISBN & Gemini</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 1rem; }
            .card { background: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); border: 1px solid #334155; width: 100%; max-width: 600px; }
            h1 { color: #f8fafc; margin-bottom: 0.5rem; font-size: 1.6rem; text-align: center; }
            p { color: #94a3b8; font-size: 0.95rem; text-align: center; margin-bottom: 1.5rem; }
            .input-group { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
            input { padding: 0.75rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #f8fafc; font-size: 1rem; flex: 1; }
            input:focus { outline: none; border-color: #38bdf8; }
            button { background: #38bdf8; color: #0f172a; border: none; padding: 0.75rem 1.25rem; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #7dd3fc; }
            #result { background: #0f172a; border: 1px solid #334155; padding: 1.5rem; border-radius: 8px; display: none; margin-top: 1rem; }
            .result-item { margin-bottom: 0.75rem; font-size: 0.95rem; }
            .result-label { color: #38bdf8; font-weight: bold; }
        </style>
        <script>
            async function searchBook() {
                const isbn = document.getElementById('isbn').value.trim();
                const btn = document.getElementById('search-btn');
                const resultDiv = document.getElementById('result');
                
                if (!isbn) {
                    alert("Inserisci un codice ISBN.");
                    return;
                }

                btn.innerText = "Gemini sta analizzando...";
                btn.disabled = true;
                resultDiv.style.display = 'none';

                try {
                    const response = await fetch('/api/search?isbn=' + encodeURIComponent(isbn));
                    const data = await response.json();

                    if (data.success) {
                        document.getElementById('res-title').innerText = data.title || "-";
                        document.getElementById('res-author').innerText = data.author || "-";
                        document.getElementById('res-publisher').innerText = data.editore || "-";
                        document.getElementById('res-year').innerText = data.anno_pubblicazione || "-";
                        document.getElementById('res-desc').innerText = data.descrizione || "-";
                        resultDiv.style.display = 'block';
                    } else {
                        alert("Libro non trovato o codice ISBN non valido.");
                    }
                } catch (e) {
                    alert("Errore di connessione.");
                } finally {
                    btn.innerText = "Cerca";
                    btn.disabled = false;
                }
            }
        </script>
    </head>
    <body>
        <div class="card">
            <h1>Cerca Libro con ISBN</h1>
            <p>Inserisci il codice ISBN per estrarre le informazioni tramite Gemini.</p>
            <div class="input-group">
                <input type="text" id="isbn" placeholder="Es. 9788869183157">
                <button id="search-btn" onclick="searchBook()">Cerca</button>
            </div>
            <div id="result">
                <div class="result-item"><span class="result-label">Titolo:</span> <span id="res-title"></span></div>
                <div class="result-item"><span class="result-label">Autore:</span> <span id="res-author"></span></div>
                <div class="result-item"><span class="result-label">Editore:</span> <span id="res-publisher"></span></div>
                <div class="result-item"><span class="result-label">Anno:</span> <span id="res-year"></span></div>
                <div class="result-item"><span class="result-label">Descrizione:</span> <span id="res-desc"></span></div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/search")
async def api_search(isbn: str):
    try:
        prompt = f"""
        Fornisci le informazioni bibliografiche per il codice ISBN: {isbn}.
        Rispondi ESCLUSIVAMENTE con un oggetto JSON valido (senza blocchi di codice markdown o backticks) con queste chiavi:
        {{
            "success": true,
            "title": "Titolo del libro",
            "author": "Autore",
            "editore": "Casa editrice",
            "anno_pubblicazione": "Anno",
            "descrizione": "Breve sinossi o descrizione"
        }}
        Se non trovi il libro, restituisci: {{"success": false}}
        """
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        text_res = response.text.strip()
        text_res = re.sub(r'^```json\s*', '', text_res)
        text_res = re.sub(r'\s*```$', '', text_res)
        return json.loads(text_res)
    except Exception as e:
        return {"success": False}
