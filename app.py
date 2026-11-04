import requests
import streamlit as st

# ==========================================
# ⚙️ CONFIGURATION NOTION & API
# ==========================================
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
DATABASE_ID = "40e3b91d19d280e484f3da2ca4e2de1a"

# Hôte de l'API choisie (à adapter selon celle que tu sélectionnes sur RapidAPI)
RAPIDAPI_HOST = "instagram-scraper-api2.p.rapidapi.com" 

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def post_exists_in_notion(post_url):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"filter": {"property": "Lien IG / LinkedIn", "url": {"equals": post_url}}}
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    if response.status_code == 200:
        return len(response.json().get("results", [])) > 0
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

def fetch_instagram_posts(username):
    """Récupère les posts via RapidAPI au lieu d'Instaloader"""
    url = f"https://{RAPIDAPI_HOST}/v1.2/posts"
    querystring = {"username_or_id_or_url": username}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        # La structure du JSON dépend de l'API exacte choisie sur RapidAPI.
        # Ce format correspond à la majorité des scrapers standards.
        return response.json().get("data", {}).get("items", [])[:3] 
    else:
        raise Exception(f"Erreur API ({response.status_code})")

# ==========================================
# 🌐 INTERFACE WEB STREAMLIT
# ==========================================
st.set_page_config(page_title="Hult Prize Radar", page_icon="🎯")
st.title("🎯 Hult Prize Global Radar - Extracteur")

st.markdown("Ajoute les pseudonymes Instagram à surveiller (un par ligne) :")
comptes_input = st.text_area("Comptes Instagram", "hultprize\nhultprize.eg\nhultprize.emsicasa\nhultprizeunilag", height=150)

if st.button("🚀 Lancer l'analyse et synchroniser avec Notion"):
    comptes_list = [c.strip() for c in comptes_input.split('\n') if c.strip()]
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, username in enumerate(comptes_list):
        status_text.text(f"📡 Exploration de @{username} via RapidAPI...")
        try:
            posts = fetch_instagram_posts(username)
            
            for post in posts:
                # Variables à adapter selon les clés exactes renvoyées par ton API
                shortcode = post.get("code") or post.get("shortcode")
                post_url = f"https://www.instagram.com/p/{shortcode}/"
                likes = post.get("like_count", 0)
                
                caption_text = post.get("caption", {}).get("text", "") if isinstance(post.get("caption"), dict) else str(post.get("caption", ""))
                caption_snippet = (caption_text[:200] + "...") if caption_text else "Pas de texte"
                
                category = "Marketing / Reel"
                if any(k in caption_text.lower() for k in ["jury", "speaker"]): category = "Jury / Mentors"
                elif any(k in caption_text.lower() for k in ["sponsor", "partner"]): category = "Sponsoring"
                
                resultat = add_post_to_notion(f"Hult Prize @{username}", "Global", category, post_url, likes, caption_snippet)
                
                if resultat == "doublon":
                    st.warning(f"⏩ Déjà dans Notion (Doublon ignoré) : @{username}")
                elif resultat == "ajouté":
                    st.success(f"✅ Nouveau post ajouté : @{username}")
                else:
                    st.error(f"❌ Erreur d'injection Notion pour : @{username}")
                    
        except Exception as e:
            st.error(f"⚠️ Échec de la récupération pour @{username}: {e}")
            
        progress_bar.progress((i + 1) / len(comptes_list))
        
    status_text.text("🎉 Extraction globale terminée !")
