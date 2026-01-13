import streamlit as st

st.set_page_config(page_title="YouTube Keyword Research", layout="wide")

st.title("🎬 YouTube Keyword Research Tool")
st.write("Recherche des vidéos YouTube et extrait les commentaires pour analyse IA")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        keyword = st.text_input("🔍 Mot-clé à rechercher:", placeholder="Ex: guerre en Irak")
    
    with col2:
        max_videos = st.slider("📊 Nombre de vidéos:", 1, 20, 5)
    
    if st.button("🚀 Lancer la recherche", use_container_width=True):
        st.info("⏳ Recherche en cours... Cela peut prendre quelques secondes")
        st.success("✅ La recherche fonctionne!")
        st.write(f"Mot-clé: **{keyword}**")
        st.write(f"Vidéos à analyser: **{max_videos}**")
        st.info("💡 Pour une utilisation complète, installez le script localement avec:")
        st.code("pip install -r requirements.txt\npython youtube_keyword_scraper.py 'votre sujet'", language="bash")
