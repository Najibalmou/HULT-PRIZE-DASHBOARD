import hmac
from datetime import datetime, timezone
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

# ---- 🌍 RÉGIONS : compte Instagram -> région (modifie librement) ----
ACCOUNT_REGIONS = {
    "hultprize": "Global",
    "hultprize.eg": "MEA",
    "hultprize.emsicasa": "MEA",
    "hult.prize.fsjesm": "MEA",
    "hultprize.encgo": "MEA",
    "hultprizeunilag": "MEA",
    "hultprize_aui": "MEA",
    "hprize.ensabm": "MEA",
    "hprizeemsirabat": "MEA",
    "hult_prize_uir": "MEA",
}
DEFAULT_REGION = "Global"


def post_exists_in_notion(post_url):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"filter": {"property": "Lien IG / LinkedIn", "url": {"equals": post_url}}}
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    if response.status_code == 200:
        return len(response.json().get("results", [])) > 0
    return False


def add_post_to_notion(program_name, region, category, post_url, post):
    """post = dict normalisé (likes, comments, views, type, date, cover, caption)."""
    if post_exists_in_notion(post_url):
        return "doublon"

    caption_text = post["caption"]
    caption_snippet = (caption_text[:200] + "...") if caption_text else "Pas de texte"

    properties = {
        "Program Name": {"title": [{"text": {"content": program_name}}]},
        "Région": {"select": {"name": region}},
        "Catégorie": {"multi_select": [{"name": category}]},
        "Lien IG / LinkedIn": {"url": post_url},
        "Note Impact": {"select": {"name": "⭐⭐⭐⭐"}},
        "Faisabilité EMSI": {"select": {"name": "Moyen"}},
        "Statut": {"select": {"name": "À évaluer"}},
        "Likes": {"number": post["likes"]},
        "Commentaires": {"number": post["comments"]},
        "Type": {"select": {"name": post["type"]}},
    }
    if post["views"] is not None:
        properties["Vues"] = {"number": post["views"]}
    if post["date"]:
        properties["Date du post"] = {"date": {"start": post["date"]}}

    views_txt = post["views"] if post["views"] is not None else "n/a"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": "📌 Analyse Automatique"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": (
                    f"Likes: {post['likes']} | Commentaires: {post['comments']} | Vues: {views_txt}"
                    f"\n\nLégende extraite:\n{caption_snippet}"
                )}}]}
            }
        ]
    }
    if post["cover"]:
        payload["cover"] = {"type": "external", "external": {"url": post["cover"]}}

    res = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=payload)
    if res.status_code in [200, 201]:
        return "ajouté"
    return f"erreur Notion {res.status_code} : {res.text[:200]}"


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


def _first(d, *keys):
    """Retourne la première valeur non vide parmi plusieurs clés possibles."""
    for k in keys:
        v = d.get(k)
        if v not in (None, "", []):
            return v
    return None


def parse_post(raw):
    """Normalise un post : shortcode, likes, comments, views, type, date, cover, caption."""
    p = raw.get("node", raw) if isinstance(raw, dict) else {}

    shortcode = _first(p, "code", "shortcode")

    likes = _first(p, "like_count")
    if likes is None:
        likes = (p.get("edge_media_preview_like") or p.get("edge_liked_by") or {}).get("count", 0)

    comments = _first(p, "comment_count")
    if comments is None:
        comments = (p.get("edge_media_to_comment") or p.get("edge_media_preview_comment") or {}).get("count", 0)

    views = _first(p, "play_count", "video_view_count", "view_count", "video_play_count")

    # Type : Reel / Carrousel / Vidéo / Photo
    typename = str(p.get("__typename", ""))
    product = str(p.get("product_type", ""))
    media_type = p.get("media_type")
    if product == "clips":
        post_type = "Reel"
    elif "Sidecar" in typename or product == "carousel_container" or media_type == 8 or p.get("carousel_media"):
        post_type = "Carrousel"
    elif p.get("is_video") or "Video" in typename or media_type == 2:
        post_type = "Vidéo"
    else:
        post_type = "Photo"

    # Date (timestamp Unix -> ISO)
    ts = _first(p, "taken_at_timestamp", "taken_at", "timestamp")
    date_iso = None
    if isinstance(ts, (int, float)):
        date_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    elif isinstance(ts, str):
        date_iso = ts

    # Miniature
    cover = _first(p, "display_url", "thumbnail_src", "thumbnail_url")
    if not cover:
        cands = (p.get("image_versions2") or {}).get("candidates", [])
        cover = cands[0].get("url") if cands else None

    # Légende
    caption = p.get("caption")
    if isinstance(caption, dict):
        caption_text = caption.get("text", "")
    elif caption:
        caption_text = str(caption)
    else:
        edges = (p.get("edge_media_to_caption") or {}).get("edges", [])
        caption_text = edges[0]["node"].get("text", "") if edges else ""

    return {
        "shortcode": shortcode, "likes": likes or 0, "comments": comments or 0,
        "views": views, "type": post_type, "date": date_iso,
        "cover": cover, "caption": caption_text,
    }


def resolve_region(username, override=None):
    """Région : valeur saisie > dictionnaire > défaut."""
    return override or ACCOUNT_REGIONS.get(username.lower(), DEFAULT_REGION)


def check_password():
    """Bloque l'app tant que le bon mot de passe n'est pas saisi."""
    expected = st.secrets.get("APP_PASSWORD")
    if not expected:
        st.error("🔒 Mot de passe non configuré : ajoute APP_PASSWORD dans les secrets.")
        st.stop()
    if st.session_state.get("auth_ok"):
        return
    pwd = st.text_input("🔒 Mot de passe", type="password")
    if pwd:
        if hmac.compare_digest(pwd, str(expected)):
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()


def fetch_instagram_posts(username, nb_posts=3):
    """Récupère les 3 derniers posts via RapidAPI."""
    url = f"https://{RAPIDAPI_HOST}{ENDPOINT_PATH}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    params = {USERNAME_PARAM: username, **EXTRA_PARAMS, "amount": str(nb_posts)}

    if HTTP_METHOD == "POST":
        response = requests.post(url, headers=headers, data=params, timeout=30)
    else:
        response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code == 200:
        return extract_posts_list(response.json())[:nb_posts]

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

check_password()

st.markdown("Ajoute les pseudonymes Instagram à surveiller (un par ligne). "
            "Région optionnelle : `pseudo | région`")
comptes_input = st.text_area(
    "Comptes Instagram",
    "hultprize\nhultprize.eg\nhultprize.emsicasa\nhultprizeunilag",
    height=150,
)

col_a, col_b = st.columns(2)
with col_a:
    nb_posts = st.slider("Nombre de posts par compte", min_value=1, max_value=5, value=5)
with col_b:
    debug_mode = st.checkbox("🛠️ Mode debug (voir le JSON brut du 1er post)")

if st.button("🚀 Lancer l'analyse et synchroniser avec Notion"):
    comptes_list = []
    for line in comptes_input.split("\n"):
        if not line.strip():
            continue
        pseudo, _, region_txt = line.partition("|")
        comptes_list.append((pseudo.strip().lstrip("@"), region_txt.strip() or None))

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (username, region_override) in enumerate(comptes_list):
        status_text.text(f"📡 Exploration de @{username} via RapidAPI...")
        try:
            posts = fetch_instagram_posts(username, nb_posts)

            if not posts:
                st.warning(f"🤷 Aucun post trouvé pour @{username} (structure JSON inattendue ?)")
            elif debug_mode:
                with st.expander(f"JSON brut du 1er post de @{username}"):
                    st.json(posts[0])

            for raw in posts:
                post = parse_post(raw)
                if not post["shortcode"]:
                    st.warning(f"⚠️ Post sans shortcode ignoré pour @{username}")
                    continue

                post_url = f"https://www.instagram.com/p/{post['shortcode']}/"
                caption_lower = post["caption"].lower()

                category = "Marketing / Reel"
                if any(k in caption_lower for k in ["jury", "speaker"]):
                    category = "Jury / Mentors"
                elif any(k in caption_lower for k in ["sponsor", "partner"]):
                    category = "Sponsoring"

                region = resolve_region(username, region_override)
                resultat = add_post_to_notion(f"Hult Prize @{username}", region, category, post_url, post)

                if resultat == "doublon":
                    st.warning(f"⏩ Déjà dans Notion (Doublon ignoré) : @{username}")
                elif resultat == "ajouté":
                    st.success(f"✅ Nouveau post ajouté : @{username} ({post['type']} · {region})")
                else:
                    st.error(f"❌ Erreur d'injection Notion pour @{username} → {resultat}")

        except Exception as e:
            st.error(f"⚠️ Échec de la récupération pour @{username}: {e}")

        progress_bar.progress((i + 1) / len(comptes_list))

    status_text.text("🎉 Extraction globale terminée !")
