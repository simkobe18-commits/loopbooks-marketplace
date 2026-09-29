import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Inizializzazione del client con la libreria ufficiale google-genai
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KY_3CAtTnmc-F5tPCANTkYuIJWvXPuXFrAyraEXqIuWQ")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoopBooks - Analisi ISBN & Trend Prezzi</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center p-4 md:p-8">
        <div class="w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
            <h1 class="text-2xl md:text-3xl font-extrabold text-center mb-2 bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
                LoopBooks Intelligence
            </h1>
            <p class="text-slate-400 text-center text-sm mb-6">
                Inserisci il codice ISBN per estrarre la scheda tecnica completa e il grafico storico dei prezzi.
            </p>

            <div class="flex gap-3 mb-6">
                <input type="text" id="isbn" placeholder="Es. 9788804668237" 
                    class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-sky-500 transition">
                <button id="search-btn" onclick="searchBook()" 
                    class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-6 py-3 rounded-xl transition shadow-lg shadow-sky-500/20">
                    Cerca
                </button>
            </div>

            <div id="loader" class="hidden text-center py-8 text-sky-400 font-medium animate-pulse">
                Analisi del libro e generazione trend di mercato in corso...
            </div>

            <div id="result" class="hidden space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950 p-5 rounded-xl border border-slate-800 text-sm">
                    <div><span class="text-sky-400 font-semibold">Nome del libro:</span> <span id="res-nome">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Prezzo medio:</span> <span id="res-prezzo" class="text-emerald-400 font-bold">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Codice EAN:</span> <span id="res-ean">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Anno pubblicazione:</span> <span id="res-anno-pub">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Anno edizione:</span> <span id="res-anno-ed">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Rilegatura:</span> <span id="res-rilegatura">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Edizione:</span> <span id="res-edizione">-</span></div>
                    <div><span class="text-sky-400 font-semibold">Collana:</span> <span id="res-collana">-</span></div>
                    <div class="md:col-span-2"><span class="text-sky-400 font-semibold">Descrizione (riassunto):</span> <p id="res-desc" class="text-slate-300 mt-1 leading-relaxed">-</p></div>
                </div>

                <div class="bg-slate-950 p-5 rounded-xl border border-slate-800">
                    <h3 class="text-sm font-semibold text-slate-400 mb-3 flex items-center justify-between">
                        <span>Grafico delle vendite e prezzo medio nel tempo</span>
                        <span class="text-xs text-sky-400 bg-sky-950 px-2 py-1 rounded border border-sky-800">Trend CardMarket Style</span>
                    </h3>
                    <div class="relative h-64 w-full">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let myChart = null;

            async function searchBook() {
                const isbn = document.getElementById('isbn').value.trim();
                const btn = document.getElementById('search-btn');
                const loader = document.getElementById('loader');
                const resultDiv = document.getElementById('result');
                
                if (!isbn) {
                    alert("Inserisci un codice ISBN valido.");
                    return;
                }

                btn.disabled = true;
                loader.classList.remove('hidden');
                resultDiv.classList.add('hidden');

                try {
                    const response = await fetch('/api/search?isbn=' + encodeURIComponent(isbn));
                    const data = await response.json();

                    if (data.success) {
                        document.getElementById('res-nome').innerText = data.nome_libro || "-";
                        document.getElementById('res-prezzo').innerText = data.prezzo_medio || "-";
                        document.getElementById('res-ean').innerText = data.codice_ean || "-";
                        document.getElementById('res-anno-pub').innerText = data.anno_pubblicazione || "-";
                        document.getElementById('res-anno-ed').innerText = data.anno_edizione || "-";
                        document.getElementById('res-rilegatura').innerText = data.rilegatura || "-";
                        document.getElementById('res-edizione').innerText = data.edizione || "-";
                        document.getElementById('res-collana').innerText = data.collana || "-";
                        document.getElementById('res-desc').innerText = data.descrizione || "-";

                        resultDiv.classList.remove('hidden');
                        renderChart(data.storico_prezzi);
                    } else {
                        alert("Libro non trovato o codice ISBN non valido.");
                    }
                } catch (e) {
                    alert("Errore di connessione al server.");
                } finally {
                    btn.disabled = false;
                    loader.classList.add('hidden');
                }
            }

            function renderChart(storico) {
                const ctx = document.getElementById('priceChart').getContext('2d');
                if (myChart) myChart.destroy();

                const labels = storico?.labels || ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set'];
                const prices = storico?.prices || [15.0, 15.5, 16.0, 15.8, 16.5, 17.0, 16.8, 17.5, 18.0];

                myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Prezzo Medio (€)',
                            data: prices,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3,
                            pointBackgroundColor: '#38bdf8'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                            y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                        }
                    }
                });
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/search")
async def api_search(isbn: str):
    try:
        prompt = f"""
        Analizza il codice ISBN: {isbn} e restituisci un oggetto JSON puro (senza blocchi markdown o backticks) con esattamente queste chiavi:
        {{
            "success": true,
            "nome_libro": "Titolo completo",
            "prezzo_medio": "Prezzo stimato di mercato in formato es. 16.50 €",
            "descrizione": "Breve sinossi o riassunto del libro",
            "anno_pubblicazione": "Anno della prima pubblicazione",
            "anno_edizione": "Anno di questa specifica edizione",
            "codice_ean": "Codice EAN corrispondente all'ISBN",
            "rilegatura": "Es. Cartonato o Brossura",
            "edizione": "Numero o tipo di edizione",
            "collana": "Nome della collana editoriale (se presente, altrimenti -)",
            "storico_prezzi": {{
                "labels": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set"],
                "prices": [14.0, 14.5, 15.0, 14.8, 15.5, 16.0, 15.8, 16.2, 16.5]
            }}
        }}
        Se non trovi il libro o l'ISBN è errato, restituisci: {{"success": false}}
        """
        
        # Chiamata pulita tramite l'SDK ufficiale genai
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        text_res = response.text.strip()
        text_res = re.sub(r'^```json\s*', '', text_res)
        text_res = re.sub(r'\s*```$', '', text_res)
        
        return json.loads(text_res)
        
    except Exception as e:
        print(f"Errore SDK Gemini: {e}")
        return {"success": False}
