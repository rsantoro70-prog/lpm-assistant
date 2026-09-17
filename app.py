import streamlit as st
from PIL import Image

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione")
st.write("Carica le immagini JPG (registro cartaceo / stampato Excel) per la verifica.")

uploaded_files = st.file_uploader(
    "Carica file JPG", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, use_container_width=True)

    st.subheader("📋 Esito Verifica Incongruenze")
    st.info("Immagini caricate correttamente e pronte per il confronto.")
