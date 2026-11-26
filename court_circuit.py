import numpy as np
from parametres_ligne import R as R_ligne_ohm, X as X_ligne_ohm

f = 60
Sbase = 1050e6
Vbase_gen = 13.8e3
Vbase_ligne = 230e3

Xdpp_gen = 0.15


Zbase_gen = Vbase_gen ** 2 / Sbase
Xdpp_gen_ohm = Xdpp_gen * Zbase_gen
Ldpp_gen = Xdpp_gen_ohm / (2 * np.pi * f)

R1_transfo, X1_transfo = 0.002, 0.08
R2_transfo, X2_transfo = 0.0043218, 0.17287
R_transfo = R1_transfo + R2_transfo
X_transfo = X1_transfo + X2_transfo

Zbase_ligne = Vbase_ligne ** 2 / Sbase
R_ligne_pu = R_ligne_ohm / Zbase_ligne
X_ligne_pu = X_ligne_ohm / Zbase_ligne

Rtot = R_transfo + R_ligne_pu
Xtot = Xdpp_gen + X_transfo + X_ligne_pu

R_defaut_ohm = 1e-5
Rtot += R_defaut_ohm / Zbase_ligne

Ztot = complex(Rtot, Xtot)

Eg = 1.0

Iss_pu = Eg / abs(Ztot)

Ibase_ligne = Sbase / (np.sqrt(3) * Vbase_ligne)
Iss = Iss_pu * Ibase_ligne

Ta = Xtot / (2 * np.pi * f * Rtot)
T_demi_cycle = 1 / (2 * f)
T_3cycles = 3 / f

Imax = np.sqrt(2) * Iss * (1 + np.exp(-T_demi_cycle / Ta))

Iint = Iss * np.sqrt(1 + 2 * np.exp(-2 * T_3cycles / Ta))

print(f"X/R total = {Xtot/Rtot:.2f}")
print(f"Iss = {Iss_pu:.4f} pu = {Iss:.1f} A")
print(f"Imax (1/2 cycle) = {Imax:.1f} A")
print(f"Iint (3 cycles) = {Iint:.1f} A")

print(f"\nZbase = {Zbase_gen:.5f} ohm")
print(f"X'' generatrice = {Xdpp_gen_ohm*1000:.4f} mohm = {Ldpp_gen*1e6:.2f} uH")

T = 1 / f
theta = np.arctan2(Xtot, Rtot)
t0_theorique = theta / (2 * np.pi * f)

print(f"\nAngle de Ztot (theta) = {np.degrees(theta):.2f} deg")
print(f"t0 theorique = {t0_theorique*1000:.4f} ms")

dephasage_transfo = np.radians(30)
t0_simulation = np.mod(theta - dephasage_transfo, np.pi) / (2 * np.pi * f)

print(f"t0 pour Simulink = {t0_simulation*1000:.4f} ms")
print(f"(periode T = {T*1000:.4f} ms)")