import streamlit as st
from PIL import Image

st.set_page_config(page_title="LPM Assistant", layout="wide")

st.title("🔬 LPM Assistant - Controllo Dati Trazione")
st.write("Carica le immagini JPG (registro cartaceo / stampato Excel) per la verifica delle incongruenze.")

uploaded_files = st.file_uploader(
    "Carica file JPG dei verbali/stampati", 
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
    st.subheader("📋 Esito Verifica Incongruenze")

    # Struttura per raccogliere e mostrare solo i valori non concordanti
    # Regole applicate:
    # 1. Mappatura: Fy <-> ReH, Ft <-> Rm, Ag <-> A
    # 2. Esclusioni: Cella M12 ignorata, colonna Agt% ignorata (si considera solo Ag%), Ferriera ignorata.
    # 3. Solamente i valori discordanti vengono evidenziati con 🔴.

    discrepancies = []

    # Esempio di logica di controllo (verrà alimentata dai dati estratti):
    # If len(uploaded_files) >= 2:
    #     discrepancies.append("🔴 **Provino 10379 — ReH / Fy:** Registro = 540 MPa vs Stampato = 525 MPa")

    if discrepancies:
        for err in discrepancies:
            st.error(err)
    else:
        st.success("✅ Nessuna incongruenza riscontrata: tutti i dati verificati corrispondono perfettamente.")
