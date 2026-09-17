import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
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

def preprocess_image(image):
    """Migliora il contrasto e converte in scala di grigi per facilitare l'OCR."""
    gray_image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(gray_image)
    return enhancer.enhance(2.0)

def parse_ocr_data(image):
    """
    Estrae le righe numeriche dall'immagine ottimizzata.
    Ignora la colonna Agt%, la cella M12 e Ferriera/Produttore.
    """
    processed_img = preprocess_image(image)
    # --psm 6 indica a Tesseract che l'immagine è un blocco di testo/tabella uniforme
    text = pytesseract.image_to_string(processed_img, config='--psm 6')
    
    rows = []
    lines = text.split('\n')
    
    for line in lines:
        # Pulisce la riga tenendo solo numeri, punti e virgole
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Estrae tutte le sequenze numeriche trovate nella riga
        numbers = re.findall(r'\b\d+(?:[\.,]\d+)?\b', clean_line)
        numbers = [n.replace(',', '.') for n in numbers]
        
        # Se la riga contiene almeno 3 o 4 valori numerici, la consideriamo una riga di provino validabile
        if len(numbers) >= 3:
            rows.append([float(n) for n in numbers])
            
    return rows

def compare_datasets(data1, data2):
    """Confronta le righe estratte dalle due immagini e rileva le incongruenze."""
    discrepancies = []
    
    if not data1 or not data2:
        return ["⚠️ **Lettura incompleta:** Non è stato possibile estrarre tabelle numeriche da una o entrambe le immagini. Assicurati che le foto siano ben illuminate e a fuoco."]
    
    # Confronta riga per riga per i provini corrispondenti
    min_rows = min(len(data1), len(data2))
    
    for i in range(min_rows):
        r1 = data1[i]
        r2 = data2[i]
        
        # Identifica l'eventuale ID provino se presente come primo numero, altrimenti usa l'indice di riga
        provino_label = f"Riga {i+1}"
        
        # Prende i primi valori di confronto (es. Snervamento, Rottura, Allungamento)
        vals1 = r1[-3:] if len(r1) >= 3 else r1
        vals2 = r2[-3:] if len(r2) >= 3 else r2
        
        param_names = ["Snervamento (F_y / R_eH)", "Rottura (F_t / R_m)", "Allungamento (A_g / A)"]
        
        for idx in range(min(len(vals1), len(vals2))):
            v1 = vals1[idx]
            v2 = vals2[idx]
            
            # Soglia per scartare piccole imprecisioni di arrotondamento
            if abs(v1 - v2) > 0.5:
                discrepancies.append(f"🔴 **{provino_label} — {param_names[idx] if idx < 3 else 'Valore'}:** Foto 1 = `{v1}` vs Foto 2 = `{v2}`")
                
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
