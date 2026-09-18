import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from pytesseract import Output

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione (OCR Geometrico)")
st.write("Carica le due immagini JPG (registro cartaceo e stampato Excel) per la lettura automatica a griglia.")

uploaded_files = st.file_uploader(
    "Carica i file JPG del verbale e dello stampato Excel", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

def extract_table_from_image(image):
    """Estrae i dati strutturati usando le coordinate spaziali (X, Y) della tabella."""
    # Pre-elaborazione pulita
    gray = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
    
    # Estrae parole e coordinate con Tesseract
    data = pytesseract.image_to_data(enhanced, output_type=Output.DATAFRAME, config='--psm 6')
    
    # Filtra via i testi vuoti
    data = data[data.text.notnull() & (data.text.str.strip() != "")]
    
    if data.empty:
        return []
        
    # Raggruppa per riga approssimativa (coordinata 'top' simile)
    # Tolleranza verticale di circa 10 pixel per raggruppare elementi della stessa riga
    data['row_group'] = (data['top'] / 15).round() * 15
    
    structured_rows = []
    for _, group in data.groupby('row_group'):
        # Ordina gli elementi della riga da sinistra a destra (coordinata 'left')
        sorted_row = group.sort_values(by='left')
        row_numbers = []
        
        for text in sorted_row['text']:
            # Pulisce e cerca numeri decimali o interi
            clean_text = text.replace(',', '.')
            try:
                val = float(clean_text)
                row_numbers.append(val)
            except ValueError:
                continue
                
        # Se la riga ha almeno 3 valori numerici validi, la consideriamo una riga di provino
        if len(row_numbers) >= 3:
            structured_rows.append(row_numbers)
            
    return structured_rows

def compare_tables(table1, table2):
    """Confronta le tabelle estratte e individua le difformità."""
    discrepancies = []
    
    if not table1 or not table2:
        return ["⚠️ **Attenzione:** Impossibile estrarre la griglia numerica da una delle due immagini. Assicurati che l'inquadratura prenda bene la tabella dei provini."]
        
    min_rows = min(len(table1), len(table2))
    param_names = ["Snervamento (F_y / R_eH)", "Rottura (F_t / R_m)", "Allungamento (A_g / A)"]
    
    for i in range(min_rows):
        r1 = table1[i]
        r2 = table2[i]
        
        provino_label = f"Provino/Riga {i+1}"
        
        # Prende gli ultimi valori numerici della riga (escludendo eventuali codici iniziali lunghi)
        vals1 = r1[-3:]
        vals2 = r2[-3:]
        
        for idx in range(3):
            v1 = vals1[idx]
            v2 = vals2[idx]
            
            # Soglia di tolleranza per scartare micro-differenze di arrotondamento (0.5)
            if abs(v1 - v2) > 0.5:
                discrepancies.append(f"🔴 **{provino_label} — {param_names[idx]}:** Registro = `{v1}` vs Stampato = `{v2}`")
                
    return discrepancies

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    extracted_tables = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)
            table_data = extract_table_from_image(image)
            extracted_tables.append(table_data)

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze")

    if len(extracted_tables) >= 2:
        discrepancies = compare_tables(extracted_tables[0], extracted_tables[1])
        
        if discrepancies:
            for err in discrepancies:
                if "⚠️" in err:
                    st.warning(err)
                else:
                    st.error(err)
        else:
            st.success("✅ Tutti i dati letti nelle immagini corrispondono perfettamente. Nessuna incongruenza.")
    else:
        st.info("Carica almeno 2 immagini JPG (es. registro e stampato Excel) per avviare il confronto automatico.")
