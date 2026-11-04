import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
ax.set_facecolor('#F4F7F6')
fig.patch.set_facecolor('#F4F7F6')

# Couleurs Epik Leaders
EPIK_BLUE = '#0B4F6C'
EPIK_RED = '#D62828'
EPIK_LIGHT_BLUE = '#E0F2F1'
DARK_TEXT = '#111111'
WHITE = '#FFFFFF'

nodes = {
    "NAT": {"label": "Epik Leaders Morocco\n(Direction Nationale & Mentors)", "pos": (0.5, 0.88), "size": (0.38, 0.10), "bg": EPIK_BLUE, "text": WHITE, "border": EPIK_RED},
    "AMB": {"label": "Campus Ambassadeurs & Fellowship\n(Représentants Établissements)", "pos": (0.5, 0.62), "size": (0.38, 0.10), "bg": EPIK_RED, "text": WHITE, "border": EPIK_BLUE},
    "LEAD": {"label": "Pôle Leadership & Soft Skills\n(Ateliers & Prise de parole)", "pos": (0.22, 0.35), "size": (0.30, 0.10), "bg": EPIK_LIGHT_BLUE, "text": EPIK_BLUE, "border": EPIK_BLUE},
    "CIVIC": {"label": "Pôle Action Civique & Impact\n(Projets Communautaires)", "pos": (0.78, 0.35), "size": (0.30, 0.10), "bg": EPIK_LIGHT_BLUE, "text": EPIK_BLUE, "border": EPIK_BLUE},
    "STUDENTS": {"label": "Étudiants Beneficiaires & Futurs Leaders\n(Montée en compétences & Réseau)", "pos": (0.5, 0.08), "size": (0.86, 0.09), "bg": EPIK_BLUE, "text": WHITE, "border": EPIK_RED}
}

edges = [("NAT", "AMB"), ("AMB", "LEAD"), ("AMB", "CIVIC"), ("LEAD", "STUDENTS"), ("CIVIC", "STUDENTS")]

for parent, child in edges:
    p, c = nodes[parent], nodes[child]
    ax.annotate("", xy=(c["pos"][0], c["pos"][1] + c["size"][1]/2), xytext=(p["pos"][0], p["pos"][1] - p["size"][1]/2),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color=EPIK_BLUE))

for key, data in nodes.items():
    x, y = data["pos"]
    w, h = data["size"]
    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor=data["bg"], edgecolor=data["border"], linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, data["label"], ha='center', va='center', color=data["text"], fontsize=9.5, fontweight='bold', zorder=4)

plt.title("Architecture de Déploiement : Epik Leaders Morocco", fontsize=15, fontweight='bold', color=EPIK_BLUE, pad=25)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
plt.tight_layout()
plt.savefig("epik_leaders_architecture.png", dpi=300, bbox_inches='tight')
print("Graphique Epik Leaders généré sous 'epik_leaders_architecture.png' !")