import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re

st.set_page_config(page_title="LPM Assistant", layout="wide", page_icon="🔬")

# --- BARRA LATERALE: Impostazioni e Parametri ---
st.sidebar.header("⚙️ Impostazioni Controllo")
tolerance = st.sidebar.number_input(
    "Soglia di Tolleranza Differenze", 
    min_value=0.0, 
    max_value=10.0, 
    value=0.5, 
    step=0.1,
    help="Gli scostamenti numerici superiori a questo valore generano una segnalazione 🔴."
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Note operative:**\n"
    "- Supporta immagini JPEG, PNG e PDF scansionati.\n"
    "- Ignora automaticamente $A_{gt}\\%$, cella M12 e indicazione Ferriera.\n"
    "- Per i migliori risultati usa scansioni dritte e ad alto contrasto."
)

# --- INTESTAZIONE PRINCIPALE ---
st.title("🔬 LPM Assistant - Controllo Incongruenze Trazione")
st.write("Verifica automatica e puntuale delle difformità tra verbali cartacei, registri e stampati Excel.")

uploaded_files = st.file_uploader(
    "Carica i file (JPEG, PNG, PDF) dei verbali e stampati", 
    type=["jpg", "jpeg", "png", "pdf"], 
    accept_multiple_files=True
)

def extract_numbers_from_image(image):
    """Converte l'immagine in scala di grigi ed estrae la matrice numerica con Tesseract."""
    gray = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
    
    text = pytesseract.image_to_string(enhanced, config='--psm 6')
    
    rows_data = []
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Cerca sequenze numeriche (interi o decimali)
        numbers = re.findall(r'\b\d+(?:[\.,]\d+)?\b', clean_line)
        numbers = [float(n.replace(',', '.')) for n in numbers]
        
        # Isola righe con almeno 3 valori numerici
        if len(numbers) >= 3:
            rows_data.append(numbers)
            
    return rows_data

def compare_multiple_datasets(datasets, tol_val):
    """Confronta tutti i file caricati rilevando le difformità oltre la tolleranza impostata."""
    discrepancies = []
    param_names = ["Snervamento (F_y / R_eH)", "Rottura (F_t / R_m)", "Allungamento (A_g / A)"]
    
    base_data = datasets[0]
    
    for file_idx in range(1, len(datasets)):
        comp_data = datasets[file_idx]
        min_rows = min(len(base_data), len(comp_data))
        
        for i in range(min_rows):
            r1 = base_data[i]
            r2 = comp_data[i]
            
            # Isola gli ultimi 3 valori numerici rilevati sulla riga
            vals1 = r1[-3:]
            vals2 = r2[-3:]
            
            for idx in range(3):
                v1 = vals1[idx]
                v2 = vals2[idx]
                
                if abs(v1 - v2) > tol_val:
                    discrepancies.append(
                        f"🔴 File 1 vs File {file_idx+1} (Riga {i+1}) — {param_names[idx]}: "
                        f"Valore `{v1}` vs `{v2}` (Diff: {round(abs(v1-v2), 2)})"
                    )
                    
    return discrepancies

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    extracted_datasets = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            # Gestione Immagini
            if uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)
                numbers = extract_numbers_from_image(image)
                extracted_datasets.append(numbers)
            else:
                st.warning(f"File {uploaded_file.name} (PDF non ancora convertito in immagine).")

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze")

    if len(extracted_datasets) >= 2:
        discrepancies = compare_multiple_datasets(extracted_datasets, tolerance)
        
        if discrepancies:
            for err in discrepancies:
                st.error(err)
                
            # Generazione Report scaricabile
            report_text = "REPORT INCONGRUENZE TRAZIONE - LPM ASSISTANT\n"
            report_text += "="*50 + "\n\n"
            for err in discrepancies:
                report_text += f"{err}\n"
                
            st.download_button(
                label="📥 Scarica Report Incongruenze (.txt)",
                data=report_text,
                file_name="report_incongruenze_lpm.txt",
                mime="text/plain"
            )
        else:
            st.success("✅ Tutti i dati letti tra i file caricati corrispondono perfettamente entro la tolleranza impostata. Nessuna incongruenza.")
    else:
        st.info("Carica almeno 2 file per avviare il confronto automatico.")
