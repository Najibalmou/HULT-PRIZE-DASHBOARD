import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
ax.set_facecolor('#FFFDF5')
fig.patch.set_facecolor('#FFFDF5')

# Couleurs Enactus
ENACTUS_YELLOW = '#FFC20E'
ENACTUS_ORANGE = '#F58220'
ENACTUS_BLACK = '#000000'
WHITE = '#FFFFFF'

nodes = {
    "NAT": {"label": "Enactus Morocco (Siège National)\n(Coordination, Formations & National Competition)", "pos": (0.5, 0.88), "size": (0.42, 0.10), "bg": ENACTUS_BLACK, "text": WHITE, "border": ENACTUS_YELLOW},
    "CLUB": {"label": "Bureau Exécutif Club Campus\n(Président, Pôles Projets & Supports)", "pos": (0.5, 0.62), "size": (0.36, 0.10), "bg": ENACTUS_YELLOW, "text": ENACTUS_BLACK, "border": ENACTUS_BLACK},
    "PROJ": {"label": "Chefs de Projets & Équipes Terrain\n(Idéation, MVP & Impact Social)", "pos": (0.22, 0.35), "size": (0.32, 0.10), "bg": ENACTUS_ORANGE, "text": WHITE, "border": ENACTUS_BLACK},
    "ADVISORS": {"label": "Conseillers Académiques & Business Mentors\n(Accompagnement Projets & Pitchs)", "pos": (0.78, 0.35), "size": (0.34, 0.10), "bg": ENACTUS_BLACK, "text": WHITE, "border": ENACTUS_YELLOW},
    "IMPACT": {"label": "Bénéficiaires & Compétition Nationale\n(Projets Pérennes & Impact Social Mesurable)", "pos": (0.5, 0.08), "size": (0.86, 0.09), "bg": ENACTUS_YELLOW, "text": ENACTUS_BLACK, "border": ENACTUS_BLACK}
}

edges = [("NAT", "CLUB"), ("CLUB", "PROJ"), ("CLUB", "ADVISORS"), ("PROJ", "IMPACT"), ("ADVISORS", "IMPACT")]

for parent, child in edges:
    p, c = nodes[parent], nodes[child]
    ax.annotate("", xy=(c["pos"][0], c["pos"][1] + c["size"][1]/2), xytext=(p["pos"][0], p["pos"][1] - p["size"][1]/2),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color=ENACTUS_BLACK))

for key, data in nodes.items():
    x, y = data["pos"]
    w, h = data["size"]
    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor=data["bg"], edgecolor=data["border"], linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, data["label"], ha='center', va='center', color=data["text"], fontsize=9.5, fontweight='bold', zorder=4)

plt.title("Architecture de Fonctionnement : Enactus Morocco", fontsize=15, fontweight='bold', color=ENACTUS_BLACK, pad=25)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
plt.tight_layout()
plt.savefig("enactus_architecture.png", dpi=300, bbox_inches='tight')
print("Graphique Enactus généré sous 'enactus_architecture.png' !")