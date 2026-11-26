import numpy as np

f = 60
longueur = 240
Vnom = 230e3


D = 12
d = 0.45
n = 4


diam_ext = 1.424 * 0.0254
r_cond = diam_ext / 2
GMR_cond = 0.0479 * 0.3048
R_cond_50 = 0.0803*0.621371
I_max_cond = 1250


GMR_faisceau = 1.09 * (GMR_cond * d**3) ** 0.25
r_faisceau = 1.09 * (r_cond * d**3) ** 0.25


GMD = (D * D * 2 * D) ** (1 / 3)


Rp = R_cond_50 / n                                          # ohm/km
Lp = 2e-7 * np.log(GMD / GMR_faisceau) * 1000                # H/km
Cp = 2 * np.pi * 8.854e-12 / np.log(GMD / r_faisceau) * 1000  # F/km


R = Rp * longueur
X = 2 * np.pi * f * Lp * longueur
Z = complex(R, X)

B = 2 * np.pi * f * Cp * longueur
Y = complex(0, B)


Zc = np.sqrt(Lp / Cp)
SIL = Vnom ** 2 / Zc / 1e6

I_max = n * I_max_cond

A_ligne = 1 + Z * Y / 2
B_ligne = Z
C_ligne = Y * (1 + Z * Y / 4)
D_ligne = A_ligne

if __name__ == "__main__":
    print(f"GMR faisceau = {GMR_faisceau:.4f} m, rayon eq. faisceau = {r_faisceau:.4f} m")
    print(f"GMD phases = {GMD:.3f} m")
    print(f"R' = {Rp:.5f} ohm/km")
    print(f"L' = {Lp*1000:.5f} mH/km")
    print(f"C' = {Cp*1e6:.5f} uF/km")
    print(f"R total = {R:.8f} ohm")
    print(f"X total = {X:.2f} ohm")
    print(f"Z = {R:.3f} + j{X:.3f} ohm")
    print(f"B total = {B*1e4:.2f} x1e-4 S")
    print(f"Zc = {Zc:.2f} ohm")
    print(f"SIL = {SIL:.8f} MW")
    print(f"|A| = {abs(A_ligne):.4f} pu")
    print(f"|B| = {abs(B_ligne):.2f} ohm")
    print(f"|C| = {abs(C_ligne) * 1e4:.2f} x1e-4 S")
    print(f"|D| = {abs(D_ligne):.4f} pu")
    print(f"Imax du faisceau (30% = {0.3*I_max:.0f} A) = {I_max:.0f} A")
