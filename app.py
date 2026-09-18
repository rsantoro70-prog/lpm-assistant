import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Riscontro Visivo Trazione")
st.write("Carica le due foto JPEG (registro cartaceo e stampato Excel) per il confronto diretto.")

# Caricamento delle foto JPEG
uploaded_files = st.file_uploader(
    "Carica esattamente 2 file JPEG", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 2:
    # Mostra le foto affiancate per il riscontro visivo immediato
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_files[0], caption=f"Documento 1: {uploaded_files[0].name}", use_container_width=True)
    with col2:
        st.image(uploaded_files[1], caption=f"Documento 2: {uploaded_files[1].name}", use_container_width=True)

    st.markdown("---")
    st.subheader("📝 Tabella di Controllo Rapido dei Provini")
    st.write("Inserisci i valori letti dalle foto per verificare la corrispondenza (Regola: ignora Agt%, cella M12 e Ferriera).")

    # Tabella interattiva precompilata per inserire i dati osservati nelle foto
    df_input = pd.DataFrame([
        {"Provino": 10379, "Doc1_Fy": 0.0, "Doc2_Fy": 0.0, "Doc1_Ft": 0.0, "Doc2_Ft": 0.0, "Doc1_Ag": 0.0, "Doc2_Ag": 0.0},
        {"Provino": 10380, "Doc1_Fy": 0.0, "Doc2_Fy": 0.0, "Doc1_Ft": 0.0, "Doc2_Ft": 0.0, "Doc1_Ag": 0.0, "Doc2_Ag": 0.0},
        {"Provino": 10381, "Doc1_Fy": 0.0, "Doc2_Fy": 0.0, "Doc1_Ft": 0.0, "Doc2_Ft": 0.0, "Doc1_Ag": 0.0, "Doc2_Ag": 0.0},
    ])

    edited_table = st.data_editor(df_input, num_rows="dynamic", key="jpeg_verification_grid")

    st.markdown("---")
    st.subheader("📋 Esito Verifica Incongruenze")

    discrepancies = []

    # Controllo matematico istantaneo sui dati inseriti dall'utente guardando le foto
    for idx, row in edited_table.iterrows():
        prov = int(row["Provino"]) if pd.notna(row["Provino"]) else f"Riga {idx+1}"
        
        # Snervamento (Fy / ReH)
        if row["Doc1_Fy"] != row["Doc2_Fy"] and (row["Doc1_Fy"] > 0 or row["Doc2_Fy"] > 0):
            discrepancies.append(f"🔴 **Provino {prov} — Snervamento (F_y / R_eH):** Doc 1 = `{row['Doc1_Fy']}` vs Doc 2 = `{row['Doc2_Fy']}`")
            
        # Rottura (Ft / Rm)
        if row["Doc1_Ft"] != row["Doc2_Ft"] and (row["Doc1_Ft"] > 0 or row["Doc2_Ft"] > 0):
            discrepancies.append(f"🔴 **Provino {prov} — Rottura (F_t / R_m):** Doc 1 = `{row['Doc1_Ft']}` vs Doc 2 = `{row['Doc2_Ft']}`")
            
        # Allungamento (Ag / A)
        if row["Doc1_Ag"] != row["Doc2_Ag"] and (row["Doc1_Ag"] > 0 or row["Doc2_Ag"] > 0):
            discrepancies.append(f"🔴 **Provino {prov} — Allungamento (A_g / A):** Doc 1 = `{row['Doc1_Ag']}%` vs Doc 2 = `{row['Doc2_Ag']}%`")

    if discrepancies:
        for err in discrepancies:
            st.error(err)
    else:
        st.success("✅ Tutti i dati inseriti corrispondono perfettamente. Nessuna incongruenza.")

else:
    st.info("📂 Carica esattamente 2 file JPEG (es. il registro cartaceo e lo stampato) per avviare la sessione di riscontro visivo.")
