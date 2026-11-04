import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
ax.set_facecolor('#FDF8FA')
fig.patch.set_facecolor('#FDF8FA')

# Couleurs Hult Prize
HULT_PINK = '#E4007C'
HULT_PURPLE = '#4A006A'
LIGHT_PINK = '#FCE4EC'
WHITE = '#FFFFFF'

nodes = {
    "HQ": {"label": "EF Hult Prize Global HQ\n(Thème Annuel & Directives)", "pos": (0.5, 0.88), "size": (0.36, 0.10), "bg": HULT_PURPLE, "text": WHITE, "border": HULT_PINK},
    "CD": {"label": "Campus Director (CD)\n(Organisateur Local Maroc)", "pos": (0.5, 0.62), "size": (0.34, 0.10), "bg": HULT_PINK, "text": WHITE, "border": HULT_PURPLE},
    "OPS": {"label": "Pôle Logistique & Pitchs\n(Organisation de la Compétition)", "pos": (0.22, 0.35), "size": (0.30, 0.10), "bg": LIGHT_PINK, "text": HULT_PURPLE, "border": HULT_PINK},
    "CORP": {"label": "Pôle Partenariats & Jury\n(Recrutement Mentors/Entreprises)", "pos": (0.78, 0.35), "size": (0.30, 0.10), "bg": LIGHT_PINK, "text": HULT_PURPLE, "border": HULT_PINK},
    "WINNER": {"label": "Équipes Étudiantes On-Campus\n(Projets Social Impact -> Qualification Régionale)", "pos": (0.5, 0.08), "size": (0.86, 0.09), "bg": HULT_PURPLE, "text": WHITE, "border": HULT_PINK}
}

edges = [("HQ", "CD"), ("CD", "OPS"), ("CD", "CORP"), ("OPS", "WINNER"), ("CORP", "WINNER")]

for parent, child in edges:
    p, c = nodes[parent], nodes[child]
    ax.annotate("", xy=(c["pos"][0], c["pos"][1] + c["size"][1]/2), xytext=(p["pos"][0], p["pos"][1] - p["size"][1]/2),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color=HULT_PINK))

for key, data in nodes.items():
    x, y = data["pos"]
    w, h = data["size"]
    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor=data["bg"], edgecolor=data["border"], linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, data["label"], ha='center', va='center', color=data["text"], fontsize=9.5, fontweight='bold', zorder=4)

plt.title("Architecture de Fonctionnement : EF Hult Prize On-Campus", fontsize=15, fontweight='bold', color=HULT_PURPLE, pad=25)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
plt.tight_layout()
plt.savefig("hult_prize_architecture.png", dpi=300, bbox_inches='tight')
print("Graphique Hult Prize généré sous 'hult_prize_architecture.png' !")