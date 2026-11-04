import os
import requests
import instaloader

# ==========================================
# ⚙️ CONFIGURATION NOTION API
# ==========================================
NOTION_TOKEN = "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"  # Ton secret (ntn_... ou secret_...)
DATABASE_ID = "40e3b91d19d280e484f3da2ca4e2de1a"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Initialisation du scraper Instaloader
L = instaloader.Instaloader(
    download_videos=False,
    download_video_thumbnails=False,
    save_metadata=False,
    download_comments=False
)

def add_post_to_notion(program_name, region, category, post_url, likes, caption_snippet):
    """Envoie une entrée collectée directement dans la base de données Notion."""
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Program Name": {
                "title": [{"text": {"content": program_name}}]
            },
            "Région": {
                "select": {"name": region}
            },
            "Catégorie": {
                "multi_select": [{"name": category}]
            },
            "Lien IG / LinkedIn": {
                "url": post_url
            },
            "Note Impact": {
                "select": {"name": "⭐⭐⭐⭐"}
            },
            "Faisabilité EMSI": {
                "select": {"name": "Moyen"}
            },
            "Statut": {
                "select": {"name": "À évaluer"}  # Correction du type "select"
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "📌 Analyse Automatique"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"Likes: {likes}\n\nLégende extraite:\n{caption_snippet}"}}]
                }
            }
        ]
    }
    
    res = requests.post(url, headers=NOTION_HEADERS, json=payload)
    if res.status_code in [200, 201]:
        print(f"  [✓] Synchronisé sur Notion : {program_name}")
    else:
        print(f"  [X] Erreur API Notion ({res.status_code}): {res.text}")

def run_pipeline():
    print("🚀 Lancement de la collecte automatique Hult Prize Radar...")
    
    # Liste des comptes officiels Hult Prize actifs
    target_accounts = [
        {"username": "hultprize", "region": "Global"},
        {"username": "hultprize.eg", "region": "MEA"},
        {"username": "hultprize.emsicasa", "region": "MEA"},
        {"username": "hultprizeunilag", "region": "MEA"},
        {"username": "hult.prize.fsjesm", "region": "MEA"}
    ]
    
    for account in target_accounts:
        username = account["username"]
        region = account["region"]
        print(f"\n📡 Exploration du compte Instagram @{username}...")
        
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            posts = profile.get_posts()
            count = 0
            
            for post in posts:
                if count >= 3:  # Limite à 3 posts récents par compte
                    break
                
                prog_name = f"Hult Prize @{username}"
                post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                likes = post.likes
                caption = (post.caption[:200] + "...") if post.caption else "Pas de texte"
                
                category = "Marketing / Reel"
                if caption and any(k in caption.lower() for k in ["jury", "speaker", "judge"]):
                    category = "Jury / Mentors"
                elif caption and any(k in caption.lower() for k in ["sponsor", "partner"]):
                    category = "Sponsoring"
                
                add_post_to_notion(prog_name, region, category, post_url, likes, caption)
                count += 1
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction de @{username}: {e}")

if __name__ == "__main__":
    run_pipeline()