import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
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

def preprocess_for_ocr(image):
    """Applica un filtro B/N ad alto contrasto per rimuovere ombre e grana della carta."""
    gray = ImageOps.grayscale(image)
    # Aumenta il contrasto per marcare i numeri neri sullo sfondo bianco
    enhanced = ImageEnhance.Contrast(gray).enhance(2.5)
    # Binarizzazione netta (soglia)
    threshold = 150
    binary = enhanced.point(lambda p: 255 if p > threshold else 0)
    return binary

def parse_ocr_data(image):
    """Estrae le sequenze di numeri rilevate nell'immagine."""
    processed_img = preprocess_for_ocr(image)
    
    # Prova prima con psm 6 (blocco di testo), se fallisce passa a psm 11 (testo sparso)
    text = pytesseract.image_to_string(processed_img, config='--psm 6')
    if not text.strip():
        text = pytesseract.image_to_string(processed_img, config='--psm 11')
    
    rows = []
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Trova tutti i numeri (interi e decimali) isolandoli da linee o simboli della tabella
        numbers = re.findall(r'\b\d+(?:[\.,]\d+)?\b', clean_line)
        numbers = [n.replace(',', '.') for n in numbers]
        
        # Considera la riga valida se contiene almeno 2 valori numerici utili
        if len(numbers) >= 2:
            try:
                float_vals = [float(n) for n in numbers]
                rows.append(float_vals)
            except ValueError:
                continue
            
    return rows

def compare_datasets(data1, data2):
    """Confronta i numeri estratti dalle due immagini e rileva le incongruenze."""
    discrepancies = []
    
    if not data1 or not data2:
        return ["⚠️ **Lettura incompleta:** L'OCR non è riuscito a leggere chiaramente i numeri. Prova a ritagliare l'immagine sulla sola tabella o ad aumentare la luminosità."]
    
    min_rows = min(len(data1), len(data2))
    param_names = ["Snervamento (F_y / R_eH)", "Rottura (F_t / R_m)", "Allungamento (A_g / A)"]
    
    for i in range(min_rows):
        r1 = data1[i]
        r2 = data2[i]
        
        provino_label = f"Riga/Provino {i+1}"
        
        # Confronta i valori numerici presenti nella riga
        min_vals = min(len(r1), len(r2))
        
        for idx in range(min_vals):
            v1 = r1[idx]
            v2 = r2[idx]
            
            # Scarta l'eventuale ID provino se i numeri sono identici (es. 10379 == 10379)
            if v1 == v2 and v1 > 1000:
                provino_label = f"Provino {int(v1)}"
                continue
                
            # Verifica difformità sui valori fisici
            if abs(v1 - v2) > 0.5:
                label_idx = min(idx, len(param_names) - 1)
                discrepancies.append(f"🔴 **{provino_label} — {param_names[label_idx]}:** Foto 1 = `{v1}` vs Foto 2 = `{v2}`")
                
    return discrepancies

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    extracted_datasets = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)
            data = parse_ocr_data(image)
            extracted_datasets.append(data)

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze")

    if len(extracted_datasets) >= 2:
        discrepancies = compare_datasets(extracted_datasets[0], extracted_datasets[1])
        
        if discrepancies:
            for err in discrepancies:
                if "⚠️" in err:
                    st.warning(err)
                else:
                    st.error(err)
        else:
            st.success("✅ Tutti i dati letti nelle immagini corrispondono perfettamente.")
    else:
        st.info("Carica almeno 2 immagini JPG per eseguire il confronto automatico.")
