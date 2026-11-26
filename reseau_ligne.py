import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. PARAMÈTRES DE LA LIGNE ET DU RÉSEAU
# ==========================================
f = 60.0
longueur = 240.0
Vnom = 230e3  # Tension nominale B2-B3 (V entre phases)

# Géométrie et conducteurs
D = 12.0
d = 0.45
n = 4

diam_ext = 1.424 * 0.0254
r_cond = diam_ext / 2.0
GMR_cond = 0.0479 * 0.3048
R_cond_50 = 0.0803 * 0.621371  # ohm/km à 50°C
I_max_cond = 1250.0

GMR_faisceau = 1.09 * (GMR_cond * d ** 3) ** 0.25
r_faisceau = 1.09 * (r_cond * d ** 3) ** 0.25
GMD = (D * D * 2 * D) ** (1 / 3)

Rp = R_cond_50 / n  # ohm/km
Lp = 2e-7 * np.log(GMD / GMR_faisceau) * 1000  # H/km
Cp = 2 * np.pi * 8.854e-12 / np.log(GMD / r_faisceau) * 1000  # F/km

R = Rp * longueur
X = 2 * np.pi * f * Lp * longueur
B = 2 * np.pi * f * Cp * longueur

Z_ligne = complex(R, X)
Y_ligne = complex(0, B)

Zc = np.sqrt(Lp / Cp)
SIL = (Vnom ** 2) / Zc / 1e6
I_max = n * I_max_cond

# ==========================================
# 2. MODELISATION DU TRANSFORMATEUR (Modèle T)
# ==========================================
Pnom_transfo = 1050e6
V2_transfo = 230e3
R1, X1 = 0.002, 0.08  # pu
R2, X2 = 0.0043218, 0.17287  # pu
Rm, Lm = 500.0, 500.0

Zbase2 = (V2_transfo ** 2) / Pnom_transfo
Ybase2 = 1.0 / Zbase2

Z1_tr = (R1 + 1j * X1) * Zbase2
Z2_tr = (R2 + 1j * X2) * Zbase2
Ym_tr = (1.0 / Rm - 1j / Lm) * Ybase2

A_tr = 1.0 + Z1_tr * Ym_tr
B_tr = Z1_tr + Z2_tr + Z1_tr * Z2_tr * Ym_tr
C_tr = Ym_tr
D_tr = 1.0 + Z2_tr * Ym_tr


# ==========================================
# 3. FONCTIONS POUR MATRICES ET V3
# ==========================================
def matrice_reseau_complet(kc):
    """ Calcule la matrice ABCD globale [Transfo + Ligne compensée] """
    Xc = kc * X

    # Matrice Pi nominale de la ligne
    A_pi = 1.0 + Z_ligne * Y_ligne / 2.0
    B_pi = Z_ligne
    C_pi = Y_ligne * (1.0 + Z_ligne * Y_ligne / 4.0)
    D_pi = A_pi

    # Ligne avec compensation série en bout de ligne
    A_lc = A_pi
    B_lc = A_pi * (-1j * Xc) + B_pi
    C_lc = C_pi
    D_lc = C_pi * (-1j * Xc) + D_pi

    # Cascading avec le transformateur (Transfo x Ligne compensée)
    A_t = A_tr * A_lc + B_tr * C_lc
    B_t = A_tr * B_lc + B_tr * D_lc
    C_t = C_tr * A_lc + D_tr * C_lc
    D_t = C_tr * B_lc + D_tr * D_lc

    return A_t, B_t, C_t, D_t


def trouver_V3(P3_W, A_t, B_t):
    """
    Résout l'équation quadratique de tension au nœud B3
    utilisant la matrice globale du réseau (A_t, B_t).
    """
    magA, alpha = abs(A_t), np.angle(A_t)
    magB, beta = abs(B_t), np.angle(B_t)
    Vs = Vnom / np.sqrt(3)  # Tension simple nominale au nœud B2
    Pr = P3_W / 3.0  # Puissance par phase
    K = magA / magB

    a_coef = K ** 2
    b_coef = 2 * Pr * K * np.cos(beta - alpha) - (Vs / magB) ** 2
    c_coef = Pr ** 2
    discriminant = b_coef ** 2 - 4 * a_coef * c_coef

    if discriminant < 0:
        raise ValueError("Au-delà de la limite de stabilité P-V")

    x_haut = (-b_coef + np.sqrt(discriminant)) / (2 * a_coef)
    if x_haut < 0:
        raise ValueError("Pas de solution physique")

    return np.sqrt(x_haut) * np.sqrt(3)


# ==========================================
# 4. BALAYAGE DE PUISSANCE ET CONTRAINTES
# ==========================================
kc_liste = [0, 10, 20, 30, 40, 50, 60, 70]
pas_P3 = 1.0  # Pas plus fin (1 MW) pour obtenir la précision exacte
P3_min = 0.8 * SIL
P3_max = 950.0  # Puissance max disponible de la centrale (3x350 MVA - 100 MW)

resultats = {kc: {"P": [], "V3": [], "dV": [], "angle": [], "I3": []} for kc in kc_liste}

for kc in kc_liste:
    A_t, B_t, _, _ = matrice_reseau_complet(kc / 100.0)
    P3 = P3_min
    while P3 <= P3_max:
        try:
            V3 = trouver_V3(P3 * 1e6, A_t, B_t)
        except ValueError:
            break

        V3_ln = complex(V3 / np.sqrt(3), 0.0)
        I3_ln = (P3 * 1e6 / 3.0) / V3_ln
        V2_ln = A_t * V3_ln + B_t * I3_ln

        # Calcul des métriques
        V2_abs = abs(V2_ln) * np.sqrt(3)
        resultats[kc]["P"].append(P3)
        resultats[kc]["V3"].append(V3 / Vnom)
        resultats[kc]["dV"].append(abs(V2_abs - V3) / V2_abs * 100.0)
        resultats[kc]["angle"].append(np.degrees(np.angle(V2_ln)))
        resultats[kc]["I3"].append(abs(I3_ln))

        P3 += pas_P3

# ==========================================
# 5. IMPRESSION DU TABLEAU 2 CORRIGÉ
# ==========================================
print(f"\n{'kc(%)':>6} {'Ccomp(uF)':>10} {'Rc(ohm)':>9} {'Pmax(MW)':>9} "
      f"{'dV(%)':>7} {'V3(pu)':>7} {'angle(deg)':>11} {'I3(A)':>8}")

for kc in kc_liste:
    idx_max = None
    for i in range(len(resultats[kc]["P"])):
        respecte_tension = 0.95 <= resultats[kc]["V3"][i] <= 1.05
        respecte_chute = resultats[kc]["dV"][i] <= 5.0
        respecte_angle = abs(resultats[kc]["angle"][i]) <= 35.0
        respecte_courant = resultats[kc]["I3"][i] <= 0.3 * I_max

        if not (respecte_tension and respecte_chute and respecte_angle and respecte_courant):
            break
        idx_max = i

    if idx_max is None:
        print(f"{kc:>6}  Aucune puissance testée ne respecte les contraintes")
        continue

    Xc = (kc / 100.0) * X
    Ccomp = 1e6 / (2 * np.pi * f * Xc) if Xc > 0 else float("inf")
    V3_volts = resultats[kc]["V3"][idx_max] * Vnom
    P3_watts = resultats[kc]["P"][idx_max] * 1e6
    Rc = (V3_volts ** 2) / P3_watts

    print(f"{kc:>6} {Ccomp:>10.2f} {Rc:>9.2f} {resultats[kc]['P'][idx_max]:>9.1f} "
          f"{resultats[kc]['dV'][idx_max]:>7.2f} {resultats[kc]['V3'][idx_max]:>7.4f} "
          f"{resultats[kc]['angle'][idx_max]:>11.2f} {resultats[kc]['I3'][idx_max]:>8.1f}")