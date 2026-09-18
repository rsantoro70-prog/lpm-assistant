
import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione")
st.write("Verifica rapida e puntuale delle incongruenze tra registro cartaceo e stampato Excel.")

# 1. Caricamento immagini di riferimento
uploaded_files = st.file_uploader(
    "Carica i file JPG di riscontro", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"File {idx+1}: {uploaded_file.name}", use_container_width=True)

st.markdown("---")
st.subheader("📊 Inserimento e Riscontro Dati")
st.write("Inserisci i valori letti dai due documenti per verificare la corrispondenza (Regola: ignora Agt%, cella M12 e Ferriera).")

# Creazione di una tabella interattiva precompilata per l'inserimento rapido
default_data = pd.DataFrame([
    {"Provino": 10379, "Reg_Fy (ReH)": 0.0, "Stmp_Fy (ReH)": 0.0, "Reg_Ft (Rm)": 0.0, "Stmp_Ft (Rm)": 0.0, "Reg_Ag (A)": 0.0, "Stmp_Ag (A)": 0.0},
    {"Provino": 10380, "Reg_Fy (ReH)": 0.0, "Stmp_Fy (ReH)": 0.0, "Reg_Ft (Rm)": 0.0, "Stmp_Ft (Rm)": 0.0, "Reg_Ag (A)": 0.0, "Stmp_Ag (A)": 0.0},
    {"Provino": 10381, "Reg_Fy (ReH)": 0.0, "Stmp_Fy (ReH)": 0.0, "Reg_Ft (Rm)": 0.0, "Stmp_Ft (Rm)": 0.0, "Reg_Ag (A)": 0.0, "Stmp_Ag (A)": 0.0},
])

# Tabella editabile direttamente da mobile/desktop
edited_df = st.data_editor(default_data, num_rows="dynamic", key="comparison_table")

st.markdown("---")
st.subheader("📋 Esito Verifica Incongruenze")

discrepancies = []

# Analisi riga per riga dei dati inseriti nella tabella
for index, row in edited_df.iterrows():
    prov = int(row["Provino"]) if pd.notna(row["Provino"]) else f"N.{index+1}"
    
    # Controllo Snervamento (Fy <-> ReH)
    if row["Reg_Fy (ReH)"] != row["Stmp_Fy (ReH)"] and (row["Reg_Fy (ReH)"] > 0 or row["Stmp_Fy (ReH)"] > 0):
        discrepancies.append(f"🔴 **Provino {prov} — Snervamento (F_y / R_eH):** Registro = `{row['Reg_Fy (ReH)']}` vs Stampato = `{row['Stmp_Fy (ReH)']}`")
        
    # Controllo Rottura (Ft <-> Rm)
    if row["Reg_Ft (Rm)"] != row["Stmp_Ft (Rm)"] and (row["Reg_Ft (Rm)"] > 0 or row["Stmp_Ft (Rm)"] > 0):
        discrepancies.append(f"🔴 **Provino {prov} — Rottura (F_t / R_m):** Registro = `{row['Reg_Ft (Rm)']}` vs Stampato = `{row['Stmp_Ft (Rm)']}`")
        
    # Controllo Allungamento (Ag <-> A)
    if row["Reg_Ag (A)"] != row["Stmp_Ag (A)"] and (row["Reg_Ag (A)"] > 0 or row["Stmp_Ag (A)"] > 0):
        discrepancies.append(f"🔴 **Provino {prov} — Allungamento (A_g / A):** Registro = `{row['Reg_Ag (A)']}%` vs Stampato = `{row['Stmp_Ag (A)']}%`")

if discrepancies:
    for err in discrepancies:
        st.error(err)
else:
    st.success("✅ Tutti i dati inseriti corrispondono perfettamente. Nessuna incongruenza riscontrata.")
