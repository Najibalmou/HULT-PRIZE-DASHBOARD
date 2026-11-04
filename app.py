import requests
import instaloader
import streamlit as st

# ==========================================
# ⚙️ CONFIGURATION NOTION (Sécurisée)
# ==========================================
# Le token est maintenant caché et récupéré de manière sécurisée
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = "40e3b91d19d280e484f3da2ca4e2de1a"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ==========================================
# 🛡️ FONCTIONS NOTION
# ==========================================
def post_exists_in_notion(post_url):
    """Vérifie si le post IG existe déjà dans le dashboard pour éviter les doublons."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Lien IG / LinkedIn",
            "url": {"equals": post_url}
        }
    }
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return len(results) > 0
    return False

def add_post_to_notion(program_name, region, category, post_url, likes, caption_snippet):
    if post_exists_in_notion(post_url):
        return "doublon"
        
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Program Name": {"title": [{"text": {"content": program_name}}]},
            "Région": {"select": {"name": region}},
            "Catégorie": {"multi_select": [{"name": category}]},
            "Lien IG / LinkedIn": {"url": post_url},
            "Note Impact": {"select": {"name": "⭐⭐⭐⭐"}},
            "Faisabilité EMSI": {"select": {"name": "Moyen"}},
            "Statut": {"select": {"name": "À évaluer"}}
        },
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": "📌 Analyse Automatique"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Likes: {likes}\n\nLégende extraite:\n{caption_snippet}"}}]}
            }
        ]
    }
    res = requests.post(url, headers=NOTION_HEADERS, json=payload)
    return "ajouté" if res.status_code in [200, 201] else "erreur"

# ==========================================
# 🌐 INTERFACE WEB STREAMLIT
# ==========================================
st.set_page_config(page_title="Hult Prize Radar", page_icon="🎯")
st.title("🎯 Hult Prize Global Radar - Extracteur")

st.markdown("Ajoute les pseudonymes Instagram à surveiller (un par ligne) :")
comptes_input = st.text_area("Comptes Instagram", "hultprize\nhultprize.eg\nhultprize.emsicasa\nhultprizeunilag", height=150)

if st.button("🚀 Lancer l'analyse et synchroniser avec Notion"):
    L = instaloader.Instaloader(download_videos=False, download_video_thumbnails=False, save_metadata=False, download_comments=False)
    
    comptes_list = [c.strip() for c in comptes_input.split('\n') if c.strip()]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, username in enumerate(comptes_list):
        status_text.text(f"📡 Exploration de @{username}...")
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            posts = profile.get_posts()
            
            count = 0
            for post in posts:
                if count >= 3:
                    break
                
                post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                caption = (post.caption[:200] + "...") if post.caption else "Pas de texte"
                
                # Catégorisation basique
                category = "Marketing / Reel"
                if caption and any(k in caption.lower() for k in ["jury", "speaker"]): category = "Jury / Mentors"
                elif caption and any(k in caption.lower() for k in ["sponsor", "partner"]): category = "Sponsoring"
                
                # Injection Notion
                resultat = add_post_to_notion(f"Hult Prize @{username}", "Global", category, post_url, post.likes, caption)
                
                if resultat == "doublon":
                    st.warning(f"⏩ Déjà dans Notion (Doublon ignoré) : @{username}")
                elif resultat == "ajouté":
                    st.success(f"✅ Nouveau post ajouté : @{username}")
                else:
                    st.error(f"❌ Erreur API pour : @{username}")
                    
                count += 1
                
        except Exception as e:
            st.error(f"⚠️ Erreur avec @{username}: {e}")
            
        progress_bar.progress((i + 1) / len(comptes_list))
        
    status_text.text("🎉 Extraction terminée !")