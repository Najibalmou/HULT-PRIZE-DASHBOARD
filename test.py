import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la figure aux dimensions d'une diapositive (16:9)
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
ax.set_facecolor('#F8F9FA')  # Fond gris très clair / propre
fig.patch.set_facecolor('#F8F9FA')

# Palette de couleurs officielles FORWARD
COLOR_PRIMARY = '#003399'    # Bleu FORWARD
COLOR_ACCENT = '#FFCC00'     # Jaune FORWARD
COLOR_LIGHT_BLUE = '#E6ECF5' # Bleu très clair pour fond de blocs
COLOR_WHITE = '#FFFFFF'
COLOR_TEXT_DARK = '#1A1A1A'

# Dictionnaire des nœuds avec position hiérarchique (x, y) et dimensions
nodes = {
    "HQ": {"label": "FRWD HQ\n(Direction Globale)", "pos": (0.5, 0.88), "size": (0.28, 0.10), "bg": COLOR_PRIMARY, "text": COLOR_WHITE, "border": COLOR_ACCENT},
    "CD": {"label": "FRWD Campus Director\n(Responsable Antenne)", "pos": (0.5, 0.62), "size": (0.32, 0.10), "bg": COLOR_PRIMARY, "text": COLOR_WHITE, "border": COLOR_ACCENT},
    "TECH": {"label": "Pôle Tech & Workshops\n(Formations / Hackathons)", "pos": (0.20, 0.35), "size": (0.26, 0.10), "bg": COLOR_LIGHT_BLUE, "text": COLOR_PRIMARY, "border": COLOR_PRIMARY},
    "CORP": {"label": "Pôle Corporate & Partenariats\n(Relations Entreprises)", "pos": (0.50, 0.35), "size": (0.26, 0.10), "bg": COLOR_LIGHT_BLUE, "text": COLOR_PRIMARY, "border": COLOR_PRIMARY},
    "MEDIA": {"label": "Pôle Media & Com\n(Communication Campus)", "pos": (0.80, 0.35), "size": (0.26, 0.10), "bg": COLOR_LIGHT_BLUE, "text": COLOR_PRIMARY, "border": COLOR_PRIMARY},
    "STUDENTS": {"label": "Communauté Étudiante Campus\n(Participants / Membres)", "pos": (0.5, 0.08), "size": (0.86, 0.09), "bg": COLOR_ACCENT, "text": COLOR_PRIMARY, "border": COLOR_PRIMARY}
}

# Dessin des connexions (flèches hiérarchiques)
edges = [
    ("HQ", "CD"),
    ("CD", "TECH"),
    ("CD", "CORP"),
    ("CD", "MEDIA"),
    ("TECH", "STUDENTS"),
    ("CORP", "STUDENTS"),
    ("MEDIA", "STUDENTS")
]

# Tracer les flèches d'abord pour qu'elles restent sous les blocs
for parent_key, child_key in edges:
    p = nodes[parent_key]
    c = nodes[child_key]
    
    start_x, start_y = p["pos"][0], p["pos"][1] - (p["size"][1] / 2)
    end_x, end_y = c["pos"][0], c["pos"][1] + (c["size"][1] / 2)
    
    # Flèche nette vers le bas
    ax.annotate(
        "", xy=(end_x, end_y), xytext=(start_x, start_y),
        arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                        lw=2, color=COLOR_PRIMARY, shrinkA=0, shrinkB=0)
    )

# Tracer les blocs de texte
for key, data in nodes.items():
    x, y = data["pos"]
    w, h = data["size"]
    
    # Création du rectangle arrondi
    box = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=data["bg"],
        edgecolor=data["border"],
        linewidth=2.5,
        zorder=3
    )
    ax.add_patch(box)
    
    # Ajout du texte centré
    ax.text(
        x, y, data["label"],
        ha='center', va='center',
        color=data["text"],
        fontsize=10, fontweight='bold',
        zorder=4,
        wrap=True
    )

# Titre du schéma
plt.title("Architecture de Déploiement : FRWD Campus Program", 
          fontsize=16, fontweight='bold', color=COLOR_PRIMARY, pad=25)

# Masquage des axes matplotlib
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Sauvegarde de l'image en haute résolution
plt.tight_layout()
plt.savefig("frwd_campus_architecture.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Nouvelle architecture générée sous 'frwd_campus_architecture.png' !")