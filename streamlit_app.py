import streamlit as st

st.set_page_config(page_title="YouTube Keyword Research", layout="wide")

st.title("🎬 YouTube Keyword Research Tool")
st.write("Recherche des vidéos YouTube et extrait les commentaires pour analyse IA")

col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("🔍 Mot-clé:", placeholder="guerre en Irak")

with col2:
    max_videos = st.slider("📊 Vidéos:", 1, 20, 5)

if st.button("🚀 Lancer la recherche"):
    st.success(f"✅ Recherche lancée pour: **{keyword}**")
    st.info(f"Nombre de vidéos: {max_videos}")
    st.write("Pour l'utilisation complète, installez le script localement!")
