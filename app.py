import streamlit as st
import pandas as pd

st.title("🧪 LPM Assistant - Controllo Prove Trazione")
st.write("Carica il file Excel per iniziare la verifica automatica.")

uploaded_file = st.file_uploader("Scegli il file Excel", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("File Excel caricato con successo!")
    st.dataframe(df)