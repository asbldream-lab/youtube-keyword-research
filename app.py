import streamlit as st

st.set_page_config(page_title="YouTube Keyword Research", layout="wide")

st.title("🎬 YouTube Keyword Research Tool")
st.write("Recherche des vidéos YouTube et extrait les commentaires")

keyword = st.text_input("🔍 Mot-clé:", placeholder="guerre en Irak")
max_videos = st.slider("📊 Vidéos:", 1, 20, 5)

if st.button("🚀 Chercher"):
    st.success(f"✅ Recherche: {keyword}")
    st.info("Pour utiliser le script complet, installez localement!")
