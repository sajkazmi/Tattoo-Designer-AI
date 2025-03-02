from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
import requests
import uuid
import os

app = FastAPI()

API_KEY = "SG_c4cc748f6bc39daf"
API_URL = "https://api.segmind.com/v1/flux-schnell"
OUTPUT_DIR = "generated_tattoos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sajeel's Tattoo Designer AI</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Arial', sans-serif;
                background-color: #111;
                color: #fff;
                padding: 20px;
                overflow-x: hidden;
                min-height: 200vh; /* Longer page for scroll effect */
            }
            h1, h2 {
                text-align: center;
                margin-bottom: 20px;
                animation: fadeIn 1.5s ease-in-out;
            }
            form {
                background: #222;
                padding: 30px;
                border-radius: 10px;
                max-width: 600px;
                margin: 20px auto;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.8);
                animation: slideIn 1s ease-in-out;
            }
            label, select, input, button {
                display: block;
                width: 100%;
                margin-bottom: 20px;
            }
            input, select, button {
                padding: 10px;
                font-size: 1rem;
                border: none;
                border-radius: 5px;
            }
            button {
                background-color: #e91e63;
                color: white;
                cursor: pointer;
                transition: background-color 0.3s ease-in-out, transform 0.2s;
            }
            button:hover {
                background-color: #ff4081;
                transform: scale(1.05);
            }
            img {
                max-width: 100%;
                display: block;
                margin: 20px auto;
                border-radius: 10px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.8);
                animation: fadeIn 2s ease-in-out;
            }
            .loading {
                text-align: center;
                font-size: 1.2rem;
                color: #ff4081;
                display: none;
                margin-top: 20px;
                animation: pulse 1.5s infinite;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
    </head>
    <body>
    <header>
        <h1>Welcome to Sajeel's Tattoo Designer AI</h1>
        <p style="text-align: center; margin-bottom: 50px;">Create custom tattoo designs using AI — Let your imagination ink your skin!</p>
        <div id="particle-background"></div>

        <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
        <script>
            particlesJS("particle-background", {
                particles: {
                    number: { value: 100 },
                    size: { value: 3 },
                    move: { speed: 1 }
                }
            });
        </script>

        <style>
            #particle-background {
                position: fixed;
                width: 100%;
                height: 100%;
                z-index: -1;
            }
        </style>

        
        <form action="/generate" method="post">
            <label for="prompt">Tattoo Idea:<pre>(Press CTRL+M for Preset Prompts)</pre></label>
            <input type="text" id="prompt" name="prompt" placeholder="Enter your tattoo concept..." required>
            
            <label for="style">Choose your favorite style:</label>
            <select id="style" name="style">
                <option value="minimalist">Minimalist</option>
                <option value="realism">Realism</option>
                <option value="tribal">Tribal</option>
                <option value="geometric">Geometric</option>
                <option value="watercolor">Watercolor</option>
            </select>
            
            <button type="submit">Generate Tattoo</button>
        </form>

        <div class="loading" id="loading">🤖 Cooking up your badass tattoo design... Please hold tight!</div>

        <h2>Your Generated Tattoo:</h2>
        <img id="tattooImage" src="" alt="Your tattoo will appear here" style="display: none;">
        <!-- Add this to your existing HTML, keeping the design unchanged -->

        <!-- Pop-up with preset prompts (hidden by default) -->
        <div class="popup" id="presetPopup">
            <p onclick="selectPrompt('A roaring lion with tribal patterns')">A roaring lion with tribal patterns</p>
            <p onclick="selectPrompt('A delicate floral design with a hidden eye')">A delicate floral design with a hidden eye</p>
            <p onclick="selectPrompt('A futuristic cybernetic dragon')">A futuristic cybernetic dragon</p>
        </div>

        <!-- Add this JS at the end of your body tag -->
        <script>
            const popup = document.getElementById('presetPopup');
            const promptInput = document.getElementById('prompt');

            // Toggle popup with Ctrl + M
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'm') {
                    e.preventDefault();
                    popup.style.right = popup.style.right === "20px" ? "-300px" : "20px";
                }
            });

            // Select a prompt and set it in the input field
            function selectPrompt(prompt) {
                promptInput.value = prompt;
                popup.style.right = "-300px";
            }

            // Close popup if clicked outside
            document.addEventListener('click', (e) => {
                if (!popup.contains(e.target)) {
                    popup.style.right = "-300px";
                }
            });
        </script>

        <!-- Add this to your existing CSS -->
        <style>
            /* Pop-up box (hidden by default) */
            .popup {
                position: fixed;
                top: 40%;
                right: -300px; /* Hidden off-screen */
                background: rgba(34, 34, 34, 0.95);
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
                z-index: 100;
                width: 250px;
                transition: right 0.4s ease-in-out;
            }

            .popup p {
                margin-bottom: 1rem;
                padding: 12px;
                background: #4ca1af;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                color: white;
                text-align: center;
                transition: background 0.3s ease;
            }

            .popup p:hover {
                background: #3a7f8f;
                transform: scale(1.05);
            }
        </style>

        <script>
            const form = document.querySelector('form');
            const loading = document.getElementById('loading');
            const img = document.getElementById('tattooImage');

            form.onsubmit = async (e) => {
                e.preventDefault();
                loading.style.display = 'block';
                img.style.display = 'none';
                const formData = new FormData(form);
                const startTime = Date.now();

                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                const endTime = Date.now();
                const timeTaken = ((endTime - startTime) / 1000).toFixed(2);
                
                if (response.ok) {
                    const { image_url } = await response.json();
                    img.src = image_url;
                    img.style.display = 'block';
                    loading.innerText = `✅ Tattoo ready in ${timeTaken} seconds!`; 
                    setTimeout(() => loading.style.display = 'none', 3000);
                } else {
                    loading.innerText = '❌ Oops! Something went wrong. Please try again.';
                    setTimeout(() => loading.style.display = 'none', 3000);
                }
            };
        </script>
        
    </body>
    </html>
    """

@app.post("/generate")
async def generate_tattoo(prompt: str = Form(...), style: str = Form(...)):
    payload = {
        "prompt": f"{style} tattoo of {prompt}",
        "steps": 50,
        "width": 512,
        "height": 512
    }

    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        image_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.png")
        with open(image_path, "wb") as file:
            file.write(response.content)
        return {"image_url": f"/generated_tattoos/{os.path.basename(image_path)}"}
    else:
        return {"error": "Failed to generate tattoo."}

@app.get("/generated_tattoos/{filename}", response_class=FileResponse)
async def get_image(filename: str):
    return FileResponse(os.path.join(OUTPUT_DIR, filename))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
