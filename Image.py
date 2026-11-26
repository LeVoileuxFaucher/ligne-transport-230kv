import matplotlib.pyplot as plt
import matplotlib.patches as patches

from compensation_shunt import ratios

fig, ax = plt.subplots(figsize=(14, 5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.axis('off')

y_bus = 20

def dashed_box(x0, x1, y0, y1, label):
    rect = patches.Rectangle(
        (x0, y0), x1 - x0, y1 - y0,
        fill=False, linestyle='--',
        edgecolor='black', linewidth=1.1
    )
    ax.add_patch(rect)
    ax.text((x0+x1)/2, y1+1.3, label,
            ha='center', va='bottom',
            fontsize=10.5, fontweight='bold')

def breaker(x, y):
    # Connexions de ligne
    ax.plot([x-1.5, x-0.45], [y, y],
            color='black', linewidth=1.4)
    ax.plot([x+0.45, x+1.5], [y, y],
            color='black', linewidth=1.4)

    # Boîtier du disjoncteur
    rect = patches.Rectangle(
        (x-0.45, y-0.7),
        0.9, 1.4,
        fill=False,
        edgecolor='black',
        linewidth=1.2
    )
    ax.add_patch(rect)

    # Contact mobile incliné
    ax.plot([x-0.25, x+0.25],
            [y-0.35, y+0.35],
            color='black',
            linewidth=1.5)

    # Petits points de contact
    ax.plot(x-0.25, y-0.35,
            marker='o',
            markersize=2.5,
            color='black')

    ax.plot(x+0.25, y+0.35,
            marker='o',
            markersize=2.5,
            color='black')

    # Indicateur mécanique au-dessus
    ax.plot([x, x],
            [y+0.7, y+1.1],
            color='black',
            linewidth=1.0)

    ax.plot([x-0.25, x+0.25],
            [y+1.1, y+1.1],
            color='black',
            linewidth=1.0)

    rect = patches.Rectangle(
        (x-0.35, y-0.45),
        0.7, 0.9,
        fill=False,
        edgecolor='black',
        linewidth=1.2
    )
    ax.add_patch(rect)

def generator(x, y, r=1.9):
    circ = patches.Circle(
        (x, y), r,
        fill=False,
        edgecolor='black',
        linewidth=1.2
    )
    ax.add_patch(circ)
    ax.text(x, y, "G", ha='center', va='center', fontsize=11)

def transfo(x, y):
    c1 = patches.Circle((x-1.1, y), 1.6, fill=False,
                        edgecolor='black', linewidth=1.2)
    c2 = patches.Circle((x+1.1, y), 1.6, fill=False,
                        edgecolor='black', linewidth=1.2)
    ax.add_patch(c1)
    ax.add_patch(c2)

def ground_symbol(x, y_top, size=0.9):
    ax.plot([x, x], [y_top, y_top-size*0.6],
            color='black', linewidth=1.0)

    for k, w in zip([0.0, 0.70, 1.4], [0.70, 0.40, 0.15]):
        yy = y_top - size*0.6 - size*0.35*k
        ax.plot([x-w*size/1.3, x+w*size/1.3], [yy, yy],
                color='black', linewidth=1.0)

def pylon(x, y, h=6):
    ax.plot([x, x], [y, y+h], color='black', linewidth=1.2)
    for k, w in zip([0.35, 0.6, 0.85], [3.2, 2.2, 1.2]):
        yy = y + h*k
        ax.plot([x-w/2, x+w/2], [yy, yy],
                color='black', linewidth=1.0)

def bus(x, y0, y1, label):
    ax.plot([x, x], [y0, y1],
            color='black', linewidth=2.2, zorder=4)
    ax.text(x, y0-2.3, label,
            ha='center', va='top',
            fontsize=10.5, fontweight='bold')

# ======================================================
# Centrale
# ======================================================

dashed_box(2, 22, y_bus-8, y_bus+8, "Centrale de production")

generator(8, y_bus+5.2)
generator(8, y_bus)
generator(8, y_bus-5.2)

ax.text(14.2, y_bus,
        "3 x 350 MVA\n13,8 kV",
        ha='center', va='center', fontsize=9)

ax.plot([9.9,20],[y_bus+5.2,y_bus],color='black',linewidth=0.9)
ax.plot([10.3,20],[y_bus,y_bus],color='black',linewidth=0.9)
ax.plot([9.9,20],[y_bus-5.2,y_bus],color='black',linewidth=0.9)

ax.plot([20,24],[y_bus,y_bus],color='black',linewidth=1.4)

# B1 centré
bus(24, y_bus-5, y_bus+5, "B1")
ax.text(24, y_bus+6.3, "13,8 kV",
        ha='center', va='bottom',
        fontsize=8, style='italic')

# ======================================================
# Poste de transformation
# ======================================================

dashed_box(26,46,y_bus-8,y_bus+8,"Poste de transformation")

ax.plot([24,30],[y_bus,y_bus],color='black',linewidth=1.4)

breaker(41, y_bus)



ax.annotate(
    "Disjoncteur",
    xy=(41, y_bus+1),
    xytext=(41, y_bus+5),
    ha='center',
    va='bottom',
    fontsize=9,
    color='#1a3fae',
    fontweight='bold',
    arrowprops=dict(
        arrowstyle='->',
        color='#1a3fae',
        linewidth=1.3
    )
)

ax.plot([30,33.2],[y_bus,y_bus],color='black',linewidth=1.4)

# transfo déplacé vers la gauche
transfo(36,y_bus)
ground_symbol(36, y_bus-1.6, size=2)

ax.text(36,y_bus-4.6,
        "Yg--d11\nneutre à la terre",
        ha='center',va='top',fontsize=8.3)

ax.plot([38.8,40],[y_bus,y_bus],
        color='black',linewidth=1.4)
ax.plot([42,48],[y_bus,y_bus],
        color='black',linewidth=1.4)
# B2 centré entre les deux boîtes
bus(48,y_bus-5,y_bus+5,"B2")
ax.text(48,y_bus+6.3,"230 kV",
        ha='center',va='bottom',
        fontsize=8,style='italic')

# ======================================================
# Ligne de transport
# ======================================================

dashed_box(50,68,y_bus-8,y_bus+8,"Ligne de transport")

ax.plot([47,52],[y_bus,y_bus],color='black',linewidth=1.4)

pylon(56,y_bus-2)
pylon(62,y_bus-2)

ax.plot([52,56],[y_bus,y_bus+4],color='black',linewidth=1.0)
ax.plot([56,62],[y_bus+4,y_bus+4],color='black',linewidth=1.0)
ax.plot([62,66],[y_bus+4,y_bus],color='black',linewidth=1.0)

ax.text(59,y_bus-6.8,"240 km",
        ha='center',fontsize=9)

ax.plot([66,70],[y_bus,y_bus],color='black',linewidth=1.4)

# ======================================================
# Point de raccordement
# ======================================================

bus(70,y_bus-5,y_bus+5,"B3")

ax.annotate(
    "Point de\nraccordement\n(230 kV)",
    xy=(70,y_bus+5),
    xytext=(70,y_bus+9),
    ha='center',
    va='bottom',
    fontsize=9.5,
    fontweight='bold',
    color='#1a3fae',
    arrowprops=dict(
        arrowstyle='->',
        color='#1a3fae',
        linewidth=1.3
    )
)

# ======================================================
# Réseau de transport
# ======================================================

dashed_box(72,94,y_bus-8,y_bus+8,"Réseau de transport")

ax.plot([70,75],[y_bus,y_bus],color='black',linewidth=1.4)

breaker(76, y_bus)

ax.annotate(
    "Disjoncteur",
    xy=(76, y_bus+1),
    xytext=(76, y_bus+5),
    ha='center',
    va='bottom',
    fontsize=9,
    color='#1a3fae',
    fontweight='bold',
    arrowprops=dict(
        arrowstyle='->',
        color='#1a3fae',
        linewidth=1.3
    )
)

ax.plot([77,79],[y_bus,y_bus],color='black',linewidth=1.4)

for xx in [79,83,87]:
    ax.plot([xx,xx],[y_bus-3,y_bus+3],
            color='black',linewidth=1.0)

ax.plot([78,87],[y_bus,y_bus],
        color='black',linewidth=1.4)

ax.plot([77,89],[y_bus+3,y_bus+3],
        color='black',linewidth=0.6,
        linestyle=':')

ax.plot([77,89],[y_bus-3,y_bus-3],
        color='black',linewidth=0.6,
        linestyle=':')

plt.tight_layout()
plt.savefig(
    "schema_unifilaire.png",
    dpi=300,
    transparent=True,
    bbox_inches='tight'
)

print("schema_unifilaire.png généré")