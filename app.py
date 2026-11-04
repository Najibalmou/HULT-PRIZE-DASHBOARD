from pathlib import Path

import requests
import streamlit as st
from PIL import Image

# ==========================================
# ⚙️ CONFIGURATION NOTION & API
# ==========================================
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"].strip()
DATABASE_ID = "40e3b91d19d280e484f3da2ca4e2de1a"

# ---- À COPIER depuis RapidAPI > Endpoints > Python (Requests) ----
RAPIDAPI_HOST = "instagram-scraper-stable-api.p.rapidapi.com"
ENDPOINT_PATH = "/get_ig_user_posts.php"   # chemin exact de l'endpoint
HTTP_METHOD = "POST"                       # "GET" ou "POST" selon le snippet
USERNAME_PARAM = "username_or_url"         # nom exact du paramètre username
EXTRA_PARAMS = {"amount": "3"}             # paramètres additionnels éventuels
# -------------------------------------------------------------------

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


def extract_posts_list(data):
    """Trouve la liste de posts quelle que soit la structure du JSON."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("posts", "items", "data", "edges", "results"):
            val = data.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                found = extract_posts_list(val)
                if found:
                    return found
    return []


def parse_post(raw):
    """Normalise un post : (shortcode, likes, caption)."""
    post = raw.get("node", raw) if isinstance(raw, dict) else {}
    shortcode = post.get("code") or post.get("shortcode")

    likes = post.get("like_count")
    if likes is None:
        likes = (post.get("edge_media_preview_like") or post.get("edge_liked_by") or {}).get("count", 0)

    caption = post.get("caption")
    if isinstance(caption, dict):
        caption_text = caption.get("text", "")
    elif caption:
        caption_text = str(caption)
    else:
        edges = (post.get("edge_media_to_caption") or {}).get("edges", [])
        caption_text = edges[0]["node"].get("text", "") if edges else ""

    return shortcode, likes, caption_text


def fetch_instagram_posts(username):
    """Récupère les 3 derniers posts via RapidAPI."""
    url = f"https://{RAPIDAPI_HOST}{ENDPOINT_PATH}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    params = {USERNAME_PARAM: username, **EXTRA_PARAMS}

    if HTTP_METHOD == "POST":
        response = requests.post(url, headers=headers, data=params, timeout=30)
    else:
        response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code == 200:
        return extract_posts_list(response.json())[:3]

    # Message détaillé pour comprendre l'erreur
    hint = ""
    if response.status_code in (401, 403):
        hint = " → Vérifie l'abonnement (Pricing) à CETTE API, la clé et le host."
    elif response.status_code == 404:
        hint = " → Endpoint ou chemin incorrect."
    elif response.status_code == 429:
        hint = " → Quota gratuit dépassé."
    raise Exception(f"Erreur API ({response.status_code}){hint} | Réponse : {response.text[:200]}")


# ==========================================
# 🌐 INTERFACE WEB STREAMLIT
# ==========================================
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "hultprize_logo.jpg"
COVER_PATH = BASE_DIR / "hultprize_emsicasa_cover.jpeg"

st.set_page_config(
    page_title="Hult Prize Radar",
    page_icon=Image.open(LOGO_PATH) if LOGO_PATH.exists() else "🎯",
    layout="centered",
)

# ---------- 🎨 STYLE ----------
st.markdown("""
<style>
    .block-container {padding-top: 1.2rem; max-width: 900px;}
    #MainMenu, footer {visibility: hidden;}

    .hp-title {
        font-size: 2.1rem; font-weight: 800; line-height: 1.15; margin: 0;
        background: linear-gradient(90deg, #FF2E93 0%, #B5348F 60%, #6B2A7E 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hp-subtitle {color: #9AA0AE; font-size: 1rem; margin-top: 0.3rem;}

    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 46, 147, 0.35) !important;
    }
    .stTextArea textarea:focus {
        border-color: #FF2E93 !important;
        box-shadow: 0 0 0 2px rgba(255, 46, 147, 0.25) !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #FF2E93, #B5348F);
        color: white; border: none; border-radius: 12px;
        padding: 0.7rem 1.6rem; font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px); color: white;
        box-shadow: 0 8px 22px rgba(255, 46, 147, 0.35);
    }
    div.stButton > button:active {color: white;}

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FF2E93, #6B2A7E);
    }
    div[data-testid="stAlert"] {border-radius: 12px;}
    .hp-divider {height: 1px; margin: 1.2rem 0;
        background: linear-gradient(90deg, transparent, rgba(255,46,147,.5), transparent);}
</style>
""", unsafe_allow_html=True)

# ---------- 🖼️ BANDE EN HAUT ----------
if COVER_PATH.exists():
    st.image(str(COVER_PATH), use_container_width=True)

# ---------- 🏷️ TITRE + LOGO ----------
col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=80)
with col_title:
    st.markdown(
        '<p class="hp-title">Hult Prize Global Radar</p>'
        '<p class="hp-subtitle">Extracteur Instagram → Notion</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="hp-divider"></div>', unsafe_allow_html=True)

st.markdown("Ajoute les pseudonymes Instagram à surveiller (un par ligne) :")
comptes_input = st.text_area("Comptes Instagram", "", height=150)

if st.button("Lancer l'analyse et synchroniser avec Notion"):
    comptes_list = [c.strip().lstrip("@") for c in comptes_input.split('\n') if c.strip()]
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, username in enumerate(comptes_list):
        status_text.text(f"📡 Exploration de @{username} ...")
        try:
            posts = fetch_instagram_posts(username)

            if not posts:
                st.warning(f"🤷 Aucun post trouvé pour @{username} (structure JSON inattendue ?)")

            for raw in posts:
                shortcode, likes, caption_text = parse_post(raw)
                if not shortcode:
                    st.warning(f"⚠️ Post sans shortcode ignoré pour @{username}")
                    continue

                post_url = f"https://www.instagram.com/p/{shortcode}/"
                caption_snippet = (caption_text[:200] + "...") if caption_text else "Pas de texte"

                category = "Marketing / Reel"
                if any(k in caption_text.lower() for k in ["jury", "speaker"]):
                    category = "Jury / Mentors"
                elif any(k in caption_text.lower() for k in ["sponsor", "partner"]):
                    category = "Sponsoring"

                resultat = add_post_to_notion(f"Hult Prize @{username}", "Global", category, post_url, likes, caption_snippet)

                if resultat == "doublon":
                    st.warning(f"⏩ Déjà dans Notion (Doublon ignoré) : @{username}")
                elif resultat == "ajouté":
                    st.success(f"Nouveau post ajouté : @{username}")
                else:
                    st.error(f"Erreur d'injection Notion pour : @{username}")

        except Exception as e:
            st.error(f"⚠️ Échec de la récupération pour @{username}: {e}")

        progress_bar.progress((i + 1) / len(comptes_list))

    status_text.text("Extraction globale terminée !")
