import numpy as np
import matplotlib.pyplot as plt
from parametres_ligne import R, X, B, Vnom, f


#  ABCD de la ligne modele PI

Z_ligne = complex(R, X)
Y_ligne = complex(0, B)

A_ligne = 1 + Z_ligne*Y_ligne/2
B_ligne = Z_ligne

P_load = 10e6


# Pour un kL donne, trouver V3


#     I3 = P_load/(3*V3) - j*BL*V3

# V2 = A*V3 + B*I3 = A*V3 + B*P_load/(3*V3) - j*B*BL*V3 = (A - j*B*BL)*V3 + B*(P_load/3)/V3


def trouver_V3(kL):
    BL = kL * B
    A_eff = A_ligne - 1j*B_ligne*BL
    magA, alpha = abs(A_eff), np.angle(A_eff)
    magB, beta = abs(B_ligne), np.angle(B_ligne)
    Vs = Vnom / np.sqrt(3)
    Pr = P_load / 3
    K = magA / magB

    a_coef = K**2
    b_coef = 2*Pr*K*np.cos(beta - alpha) - (Vs/magB)**2
    c_coef = Pr**2
    discriminant = b_coef**2 - 4*a_coef*c_coef
    if discriminant < 0:
        raise ValueError("pas de solution stable pour ce kL")

    x_haut = (-b_coef + np.sqrt(discriminant)) / (2*a_coef)
    if x_haut < 0:
        raise ValueError("pas de solution physique")
    return np.sqrt(x_haut) * np.sqrt(3)      # V3 en ligne-ligne (V)


kL_liste = np.arange(0, 71, 5)
ratios = []
V3_liste = []

for kL in kL_liste:
    V3 = trouver_V3(kL / 100)
    V3_liste.append(V3)
    ratios.append(V3 / Vnom)

plt.figure()
plt.plot(kL_liste, ratios, marker="o")
plt.axhline(1.0, color="r", linestyle="--")
plt.xlabel("kL (%)")
plt.ylabel("VB3 / VB2 (pu)")
plt.tight_layout()
plt.savefig("ratio_vs_kL.png", dpi=300, transparent=True)
plt.close()


idx = int(np.argmin(np.abs(np.array(ratios) - 1)))
kL_ret = kL_liste[idx]
V3_ret = V3_liste[idx]

BL = kL_ret / 100 * B
Lcomp = 1 / (2*np.pi*f*BL) * 1000
Qcomp = Vnom**2 * BL / 1e6
Rc = V3_ret**2 / P_load

print(f"kL retenu = {kL_ret} %")
print(f"Rc = {Rc:.1f} ohm")
print(f"Lcomp = {Lcomp:.1f} mH")
print(f"Qcomp = {Qcomp:.2f} MVAR")
print(f"VB3 = {V3_ret/1000:.2f} kV ({V3_ret/Vnom:.4f} pu)")
print(f"VB2 = {Vnom/1000:.2f} kV (1.0000 pu)")
print(f"VB3/VB2 = {V3_ret/Vnom:.4f}")