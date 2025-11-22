import streamlit as st
import requests
import base64
import json
from PIL import Image
import io

# --- SID-INSTÄLLNINGAR ---
st.set_page_config(page_title="Stryktips-AI", page_icon="⚽")
st.title("⚽ Stryktips-AI")
st.write("Ladda upp din kupongbild så analyserar AI:n bästa raden.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Inställningar")
    api_key = st.text_input("Din Gemini API-nyckel", type="password")
    st.caption("Hämta gratis på: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
    st.divider()
    budget = st.selectbox("Budget", ["64 kr (64 rader)", "128 kr (128 rader)", "256 kr (256 rader)"])

# --- FUNKTIONER ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def call_gemini_api(api_key, image, prompt):
    # Vi pratar direkt med Google via deras webb-adress istället för bibliotek
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Gör om bilden till text (base64) så vi kan skicka den
    img_b64 = image_to_base64(image)
    
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                }
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

# --- HUVUDPROGRAM ---
uploaded_file = st.file_uploader("Ladda upp bild på kupongen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Din kupong", use_container_width=True)

    if st.button("🚀 Kör Analys"):
        if not api_key:
            st.error("Du måste ange en API-nyckel i menyn till vänster först!")
            st.stop()
            
        with st.spinner("AI:n analyserar odds och streck..."):
            try:
                prompt = f"""
                Du är en expert på Stryktipset. Analysera denna bild.
                BUDGET: {budget}
                
                UPPGIFT:
                1. Läs av matcher, svenska folket % och odds.
                2. Hitta SPELVÄRDE (Där % är lägre än vinstchansen enligt oddsen).
                3. Hitta FÄLLOR (Överstreckade favoriter).
                
                Svara med Markdown:
                ## 📊 Snabbanalys
                (Kort sammanfattning)

                ## 💎 Bästa Spikarna
                * Match X: Lag (Motivering)

                ## 💣 Skrällvarningar
                * Match Y: (Vilken favorit ska vi gardera?)

                ## 📝 Systemförslag ({budget})
                Gör en tydlig tabell med Match 1-13 och tecken (1, X, 2).
                """
                
                result = call_gemini_api(api_key, image, prompt)
                
                st.markdown("---")
                st.markdown(result)
                st.success("Analys klar!")

            except Exception as e:
                st.error(f"Ett fel uppstod: {e}")
