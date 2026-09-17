import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione (OCR)")
st.write("Carica le immagini JPG (registro cartaceo / stampato Excel) per la verifica automatica.")

uploaded_files = st.file_uploader(
    "Carica i file JPG del verbale e dello stampato Excel", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

def parse_ocr_data(text):
    """
    Estrae i numeri di provino e i relativi valori (Fy/ReH, Ft/Rm, Ag/A) dal testo OCR.
    Ignora la colonna Agt%, la cella M12 e la voce Ferriera/Produttore.
    """
    data = {}
    lines = text.split('\n')
    
    for line in lines:
        # Cerca numeri di provino a 4 o 5 cifre (es. 10379)
        provino_match = re.search(r'\b(\d{4,6})\b', line)
        if provino_match:
            prov_id = provino_match.group(1)
            # Estrae tutti i valori decimali/interi presenti nella riga
            numbers = re.findall(r'\b\d+(?:[\.,]\d+)?\b', line)
            # Rimuove il numero del provino stesso dalla lista dei valori
            values = [n.replace(',', '.') for n in numbers if n != prov_id]
            
            if len(values) >= 3:
                # Mappatura standard delle 3 grandezze fondamentali
                data[prov_id] = {
                    "snervamento": float(values[0]),  # Fy / ReH
                    "rottura": float(values[1]),      # Ft / Rm
                    "allungamento": float(values[2])  # Ag / A
                }
    return data

def compare_data(dataset1, dataset2):
    """Confronta i dataset estratte dalle immagini e rileva le sole incongruenze."""
    discrepancies = []
    
    # Identifica i provini comuni
    common_keys = set(dataset1.keys()).intersection(set(dataset2.keys()))
    
    for prov in common_keys:
        d1 = dataset1[prov]
        d2 = dataset2[prov]
        
        if abs(d1["snervamento"] - d2["snervamento"]) > 0.5:
            discrepancies.append(f"🔴 **Provino {prov} — Snervamento (F_y / R_eH):** {d1['snervamento']} vs {d2['snervamento']}")
            
        if abs(d1["rottura"] - d2["rottura"]) > 0.5:
            discrepancies.append(f"🔴 **Provino {prov} — Rottura (F_t / R_m):** {d1['rottura']} vs {d2['rottura']}")
            
        if abs(d1["allungamento"] - d2["allungamento"]) > 0.1:
            discrepancies.append(f"🔴 **Provino {prov} — Allungamento (A_g / A):** {d1['allungamento']}% vs {d2['allungamento']}%")
            
    return discrepancies

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    extracted_datasets = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)
            text = pytesseract.image_to_string(image, lang='ita+eng')
            parsed_data = parse_ocr_data(text)
            extracted_datasets.append(parsed_data)

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze")

    if len(extracted_datasets) >= 2:
        # Confronto tra le prime due immagini caricate
        discrepancies = compare_data(extracted_datasets[0], extracted_datasets[1])
        
        if discrepancies:
            for err in discrepancies:
                st.error(err)
        else:
            st.success("✅ Tutti i dati letti nelle immagini corrispondono perfettamente.")
    else:
        st.info("Carica almeno 2 immagini JPG per eseguire il confronto automatico.")
