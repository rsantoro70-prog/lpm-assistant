import streamlit as st
from PIL import Image

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Verifica Prove Trazione")
st.write("Carica le foto/scansioni (JPG) per incrociare i dati tra registro e stampati.")

uploaded_files = st.file_uploader(
    "Carica una o più immagini JPG dei verbali/stampati Excel", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        # Corretto use_column_width con use_container_width
        st.image(image, caption=f"Immagine caricata: {uploaded_file.name}", use_container_width=True)
        
        st.info("Piattaforma pronta per la scansione OCR e il confronto dei dati.")
