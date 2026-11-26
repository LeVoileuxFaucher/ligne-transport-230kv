import numpy as np
import matplotlib.pyplot as plt
from parametres_ligne import R, X, B, Vnom, f, SIL, I_max


#  ABCD du transformateur modele en T

# Z1 (serie, primaire) -- Ym (shunt, magnetisation) -- Z2 (serie, secondaire)


Pnom_transfo = 1050e6
V2_transfo = 230e3
R1, X1 = 0.002, 0.08            #  13,8 kV, en pu
R2, X2 = 0.0043218, 0.17287     #  230 kV, en pu
Rm, Lm = 500, 500

Zbase2 = V2_transfo**2 / Pnom_transfo
Ybase2 = 1 / Zbase2

Z1 = (R1 + 1j*X1) * Zbase2
Z2 = (R2 + 1j*X2) * Zbase2
Ym = (1/Rm - 1j/Lm) * Ybase2


A_tr = 1 + Z1*Ym
B_tr = Z1 + Z2 + Z1*Z2*Ym
C_tr = Ym
D_tr = 1 + Z2*Ym

print("Matrice ABCD du transformateur :")
print(f"  |A| = {abs(A_tr):.4f} pu   |B| = {abs(B_tr):.2f} ohm   "
      f"|C| = {abs(C_tr)*1e4:.4f} x1e-4 S   |D| = {abs(D_tr):.4f} pu")


# ABCD de la ligne + compensation serie (kc)

Z_ligne = complex(R, X)
Y_ligne = complex(0, B)

def matrice_ligne_compensee(kc):
    Xc = kc * X

    # matrice PI de la ligne
    A_pi = 1 + Z_ligne*Y_ligne/2
    B_pi = Z_ligne
    C_pi = Y_ligne * (1 + Z_ligne*Y_ligne/4)
    D_pi = A_pi


    A = A_pi
    Bc = A_pi*(-1j*Xc) + B_pi
    C = C_pi
    Dc = C_pi*(-1j*Xc) + D_pi
    return A, Bc, C, Dc

# matrice totale du reseaua kc = 10 %
A_lc, B_lc, C_lc, D_lc = matrice_ligne_compensee(0.10)
A_t = A_tr*A_lc + B_tr*C_lc
B_t = A_tr*B_lc + B_tr*D_lc
C_t = C_tr*A_lc + D_tr*C_lc
D_t = C_tr*B_lc + D_tr*D_lc

print("\nMatrice ABCD du reseau total, kc = 10 % :")
print(f"  |A| = {abs(A_t):.4f} pu   |B| = {abs(B_t):.2f} ohm   "
      f"|C| = {abs(C_t)*1e4:.4f} x1e-4 S   |D| = {abs(D_t):.4f} pu")


# Pour un P3 et un kc donnes, trouver V3

# V2 = A*V3 + B*I3,  avec I3 = P3 / (3*V3)


def trouver_V3(P3_W, kc):
    A, Bp, _, _ = matrice_ligne_compensee(kc)
    magA, alpha = abs(A), np.angle(A)
    magB, beta = abs(Bp), np.angle(Bp)
    Vs = Vnom / np.sqrt(3)
    Pr = P3_W / 3
    K = magA / magB

    a_coef = K**2
    b_coef = 2*Pr*K*np.cos(beta - alpha) - (Vs/magB)**2
    c_coef = Pr**2
    discriminant = b_coef**2 - 4*a_coef*c_coef
    if discriminant < 0:
        raise ValueError("au-dela du nez de la courbe P-V (limite de stabilite)")

    x_haut = (-b_coef + np.sqrt(discriminant)) / (2*a_coef)
    if x_haut < 0:
        raise ValueError("pas de solution physique")
    return np.sqrt(x_haut) * np.sqrt(3)


kc_liste = [0, 10, 20, 30, 40, 50, 60, 70]
pas_P3 = 5
P3_min = 0.8 * SIL
P3_max = 5 * SIL



resultats = {kc: {"P": [], "V3": [], "dV": [], "angle": [], "I3": []} for kc in kc_liste}

for kc in kc_liste:
    P3 = P3_min
    while P3 < P3_max:
        try:
            V3 = trouver_V3(P3 * 1e6, kc / 100)
        except ValueError:
            break

        A, Bp, _, _ = matrice_ligne_compensee(kc / 100)
        V3_ln = complex(V3 / np.sqrt(3), 0)
        I3 = P3 * 1e6 / (3 * V3_ln)
        V2_ln = A*V3_ln + Bp*I3

        resultats[kc]["P"].append(P3)
        resultats[kc]["V3"].append(V3 / Vnom)
        resultats[kc]["dV"].append(abs(Vnom - V3) / Vnom * 100)
        resultats[kc]["angle"].append(np.degrees(np.angle(V2_ln)))
        resultats[kc]["I3"].append(abs(I3))

        P3 += pas_P3

def tracer(cle, ylabel, limite_haute, nom_fichier, limite_basse=None, ylim=None):
    plt.figure()
    for kc in kc_liste:
        plt.plot(resultats[kc]["P"], resultats[kc][cle], label=f"kc={kc}%")
    if limite_haute is not None:
        plt.axhline(limite_haute, color="r", linestyle="--")
    if limite_basse is not None:
        plt.axhline(limite_basse, color="r", linestyle="--")
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("P_B3 (MW)")
    plt.ylabel(ylabel)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(nom_fichier, dpi=300, transparent=True)
    plt.close()

tracer("V3", "V_B3 (pu)", 1.05, "VB3_vs_PB3.png", limite_basse=0.95)
tracer("dV", "|(VB2-VB3)/VB2| (%)", 5, "dV_vs_PB3.png")
tracer("angle", "delta_B2 - delta_B3 (deg)", 35, "angle_vs_PB3.png")
tracer("I3", "I_B3 (A)", 0.3 * I_max, "IB3_vs_PB3.png", ylim=(0, 2.0 * 0.3 * I_max))


print(f"\n{'kc(%)':>6} {'Ccomp(uF)':>10} {'Rc(ohm)':>9} {'Pmax(MW)':>9} "
      f"{'dV(%)':>7} {'V3(pu)':>7} {'angle(deg)':>11} {'I3(A)':>8}")

for kc in kc_liste:
    idx_max = None
    for i in range(len(resultats[kc]["P"])):
        respecte_tension = 0.95 <= resultats[kc]["V3"][i] <= 1.05
        respecte_chute = resultats[kc]["dV"][i] <= 5
        respecte_angle = abs(resultats[kc]["angle"][i]) <= 35
        respecte_courant = resultats[kc]["I3"][i] <= 0.3 * I_max
        if not (respecte_tension and respecte_chute and respecte_angle and respecte_courant):
            break
        idx_max = i

    if idx_max is None:
        print(f"{kc:>6}  aucune puissance testee ne respecte les contraintes")
        continue

    Xc = kc / 100 * X
    Ccomp = 1e6 / (2*np.pi*f*Xc) if Xc > 0 else float("inf")
    V3 = resultats[kc]["V3"][idx_max] * Vnom
    P3 = resultats[kc]["P"][idx_max]
    Rc = V3**2 / (P3 * 1e6)

    print(f"{kc:>6} {Ccomp:>10.2f} {Rc:>9.2f} {P3:>9.1f} "
          f"{resultats[kc]['dV'][idx_max]:>7.2f} {resultats[kc]['V3'][idx_max]:>7.4f} "
          f"{resultats[kc]['angle'][idx_max]:>11.2f} {resultats[kc]['I3'][idx_max]:>8.1f}")