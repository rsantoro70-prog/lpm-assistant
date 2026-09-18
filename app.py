import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Automazione Multi-Foto JPEG")
st.write("Carica tutti i file JPEG necessari (registri e stampati) per il confronto automatico incrociato.")

uploaded_files = st.file_uploader(
    "Carica i file JPEG dei verbali e stampati", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

def extract_numbers_from_image(image):
    """Converte la foto in bianco e nero ed estrae tutte le sequenze numeriche valide."""
    gray = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
    
    text = pytesseract.image_to_string(enhanced, config='--psm 6')
    
    rows_data = []
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        numbers = re.findall(r'\b\d+(?:[\.,]\d+)?\b', clean_line)
        numbers = [float(n.replace(',', '.')) for n in numbers]
        
        if len(numbers) >= 3:
            rows_data.append(numbers)
            
    return rows_data

def compare_multiple_datasets(datasets):
    """Confronta a catena o sul primo dataset di riferimento tutti i file caricati."""
    discrepancies = []
    param_names = ["Snervamento (F_y / R_eH)", "Rottura (F_t / R_m)", "Allungamento (A_g / A)"]
    
    # Prende il primo file come riferimento principale e lo confronta con i successivi
    base_data = datasets[0]
    
    for file_idx in range(1, len(datasets)):
        comp_data = datasets[file_idx]
        min_rows = min(len(base_data), len(comp_data))
        
        for i in range(min_rows):
            r1 = base_data[i]
            r2 = comp_data[i]
            
            vals1 = r1[-3:]
            vals2 = r2[-3:]
            
            for idx in range(3):
                v1 = vals1[idx]
                v2 = vals2[idx]
                
                if abs(v1 - v2) > 0.5:
                    discrepancies.append(f"🔴 **File 1 vs File {file_idx+1} (Riga {i+1}) — {param_names[idx]}:** `{v1}` vs `{v2}`")
                    
    return discrepancies

if uploaded_files:
    # Mostra tutte le anteprime delle immagini caricate
    cols = st.columns(len(uploaded_files))
    extracted_datasets = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)
            numbers = extract_numbers_from_image(image)
            extracted_datasets.append(numbers)

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze Multi-File")

    # Richiede almeno 2 o più file per il confronto (gestisce 4 o più file perfettamente)
    if len(extracted_datasets) >= 2:
        discrepancies = compare_multiple_datasets(extracted_datasets)
        
        if discrepancies:
            for err in discrepancies:
                st.error(err)
        else:
            st.success("✅ Tutti i dati letti tra i file caricati corrispondono perfettamente. Nessuna incongruenza.")
    else:
        st.info("Carica almeno 2 o più file JPEG per avviare il confronto automatico.")
