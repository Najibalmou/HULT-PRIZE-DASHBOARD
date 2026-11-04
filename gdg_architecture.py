import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

# Couleurs Google Developer Groups
G_BLUE = '#4285F4'
G_RED = '#EA4335'
G_YELLOW = '#FBBC04'
G_GREEN = '#34A853'
DARK_TEXT = '#202124'
WHITE = '#FFFFFF'

nodes = {
    "GOOGLE": {"label": "Google Developer Ecosystem\n(Mentors & Cloud Credits)", "pos": (0.5, 0.88), "size": (0.36, 0.10), "bg": G_BLUE, "text": WHITE, "border": G_BLUE},
    "LEAD": {"label": "GDG On Campus Lead\n(Responsable Chapitre)", "pos": (0.5, 0.62), "size": (0.32, 0.10), "bg": DARK_TEXT, "text": WHITE, "border": G_YELLOW},
    "TECH": {"label": "Pôle Tech & Dev\n(Web, AI, Cloud)", "pos": (0.20, 0.35), "size": (0.26, 0.10), "bg": G_RED, "text": WHITE, "border": G_RED},
    "EVENT": {"label": "Pôle Operations & Logistics\n(Workshops / DevFest)", "pos": (0.50, 0.35), "size": (0.28, 0.10), "bg": G_GREEN, "text": WHITE, "border": G_GREEN},
    "MEDIA": {"label": "Pôle Design & Media\n(Branding & Socials)", "pos": (0.80, 0.35), "size": (0.26, 0.10), "bg": G_YELLOW, "text": DARK_TEXT, "border": G_YELLOW},
    "COMMUNITY": {"label": "Communauté Développeurs / Étudiants Campus\n(Apprentissage Pratique & Projets)", "pos": (0.5, 0.08), "size": (0.86, 0.09), "bg": G_BLUE, "text": WHITE, "border": G_BLUE}
}

edges = [("GOOGLE", "LEAD"), ("LEAD", "TECH"), ("LEAD", "EVENT"), ("LEAD", "MEDIA"), ("TECH", "COMMUNITY"), ("EVENT", "COMMUNITY"), ("MEDIA", "COMMUNITY")]

for parent, child in edges:
    p, c = nodes[parent], nodes[child]
    ax.annotate("", xy=(c["pos"][0], c["pos"][1] + c["size"][1]/2), xytext=(p["pos"][0], p["pos"][1] - p["size"][1]/2),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color=G_BLUE))

for key, data in nodes.items():
    x, y = data["pos"]
    w, h = data["size"]
    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor=data["bg"], edgecolor=data["border"], linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, data["label"], ha='center', va='center', color=data["text"], fontsize=9.5, fontweight='bold', zorder=4)

plt.title("Architecture de Fonctionnement : GDG On Campus Morocco", fontsize=15, fontweight='bold', color=DARK_TEXT, pad=25)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
plt.tight_layout()
plt.savefig("gdg_architecture.png", dpi=300, bbox_inches='tight')
print("Graphique GDG généré sous 'gdg_architecture.png' !")