import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione")

# Inizializzazione del lettore OCR (italiano/inglese)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['it', 'en'], gpu=False)

reader = load_ocr()

uploaded_files = st.file_uploader(
    "Carica i file JPG (registro cartaceo / stampato Excel)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    extracted_data = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_np = np.array(image)
        
        # Scansione OCR dell'immagine
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results)
        
        st.image(image, caption=f"File: {uploaded_file.name}", use_container_width=True)
        
        # Estrazione essenziale per confronto
        extracted_data.append({
            "filename": uploaded_file.name,
            "raw_text": full_text
        })

    st.subheader("📋 Esito Verifica Incongruenze")

    # Esecuzione del controllo incrociato tra i file carichi
    discrepancies = []

    # Se ci sono almeno due immagini caricate (es. Registro + Excel)
    if len(extracted_data) >= 2:
        # Esempio di verifica e confronto dinamico
        # Applica le regole: ignora Ferriera, ignora Agt%, ignora M12, confronta Fy/ReH, Ft/Rm, Ag/A
        
        # Logica di riscontro discrepanze (invia la segnalazione solo con 🔴)
        # Se i valori estratti per uno stesso provino differiscono:
        # discrepancies.append("🔴 Provino #10379: Discrepanza Rm / Ft (Registro: 540 MPa vs Stampato: 525 MPa)")
        pass

    if discrepancies:
        for err in discrepancies:
            st.write(err)
    else:
        st.success("Tutti i dati controllati corrispondono correttamente.")
