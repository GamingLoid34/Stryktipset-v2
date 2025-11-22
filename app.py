import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SID-INSTÄLLNINGAR ---
st.set_page_config(page_title="Stryktips-AI", page_icon="⚽")

st.title("⚽ Stryktips-AI")
st.write("Ladda upp din kupongbild så analyserar AI:n bästa raden.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Inställningar")
    # Hämta nyckeln från användaren
    api_key = st.text_input("Din Gemini API-nyckel", type="password")
    st.caption("Hämta gratis på: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    budget = st.selectbox("Budget", ["64 kr (64 rader)", "128 kr (128 rader)", "256 kr (256 rader)"])

# --- HUVUDPROGRAMMET ---
uploaded_file = st.file_uploader("Ladda upp bild på kupongen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Visa bilden
    image = Image.open(uploaded_file)
    st.image(image, caption="Din kupong", use_container_width=True)

    if st.button("🚀 Kör Analys"):
        if not api_key:
            st.error("Du måste ange en API-nyckel i menyn till vänster först!")
            st.stop()
            
        with st.spinner("AI:n analyserar odds och streck..."):
            try:
                genai.configure(api_key=api_key)
                
                # Vi använder en "try-catch" loop för att hitta rätt modell
                # Detta löser problemet med "404 Not Found" om en modell bytt namn
                models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                active_model = None
                
                for m in models_to_try:
                    try:
                        test_model = genai.GenerativeModel(m)
                        active_model = test_model
                        break # Vi hittade en som funkar!
                    except:
                        continue # Testa nästa
                
                if not active_model:
                     # Nödlösning
                    active_model = genai.GenerativeModel('gemini-1.5-flash-latest')

                # Prompten
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
                
                response = active_model.generate_content([prompt, image])
                st.markdown("---")
                st.markdown(response.text)
                st.success("Analys klar!")

            except Exception as e:
                st.error(f"Ett fel uppstod: {e}")
                st.info("Tips: Kolla att din API-nyckel är giltig.")
