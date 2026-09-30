"""Prints every number quoted in docs/physics.md.

    python calc/report.py
"""
import math

import antenna as a

MM = 1e-3
N, OX, OY, W, S = 4, 80 * MM, 48 * MM, 1.0 * MM, 0.5 * MM
C_PADS = 0.5e-12   # pads, tuning-capacitor footprints and short tracks (estimate)


def section(title):
    print(f"\n=== {title}")


def main():
    section("Near field")
    lam = 299_792_458 / a.F_NFC
    print(f"wavelength = {lam:.1f} m, near-field limit lambda/2pi = {lam / (2 * math.pi):.2f} m")

    section("Code validation (50 mm square loop, 0.5 mm trace)")
    side, w0 = 50 * MM, 0.5 * MM
    h = side / 2
    loop = [(-h, h), (-h, -h), (h, -h), (h, h), (-h, h)]
    print(f"Greenhouse = {a.inductance_greenhouse(loop, w0) * 1e9:.1f} nH, "
          f"closed form = {a.square_loop_reference(side, w0) * 1e9:.1f} nH")

    section("Target inductance")
    for label, c in (("chip only", a.C_CHIP), ("chip + ~3 pF parasitics", a.C_CHIP + 3e-12)):
        print(f"L for 13.56 MHz with {label}: {a.capacitance_for(c, a.F_NFC) * 1e6:.2f} uH")

    section("Design space: 80 x 48 mm outline")
    print(" N  w[mm]  L_Greenhouse  L_empirical   f0(chip+par)")
    for n in (3, 4, 5):
        for w in (0.5, 0.8, 1.0):
            pts = a.card_spiral(n, OX, OY, w * MM, S)
            lg = a.inductance_greenhouse(pts, w * MM)
            le = a.inductance_empirical(OX, OY, n, w * MM, S)
            c = a.C_CHIP + a.interturn_capacitance(pts, n, w * MM, S) + C_PADS
            print(f" {n}  {w:4.1f}   {lg * 1e6:6.2f} uH    {le * 1e6:6.2f} uH    {a.resonance(lg, c) / 1e6:6.2f} MHz")

    section("Selected antenna: 4 turns, 1.0 mm trace, 0.5 mm gap")
    pts = a.card_spiral(N, OX, OY, W, S)
    lg = a.inductance_greenhouse(pts, W)
    le = a.inductance_empirical(OX, OY, N, W, S)
    cpm = a.coplanar_capacitance_per_m(W, S)
    cpar = a.interturn_capacitance(pts, N, W, S)
    ctot = a.C_CHIP + cpar + C_PADS
    inner = (OX - 2 * N * W - 2 * (N - 1) * S, OY - 2 * N * W - 2 * (N - 1) * S)
    print(f"trace length = {a.length(pts) / MM:.0f} mm, inner opening = {inner[0] / MM:.0f} x {inner[1] / MM:.0f} mm")
    print(f"L Greenhouse = {lg * 1e6:.3f} uH, L empirical = {le * 1e6:.3f} uH, difference = {100 * (lg - le) / lg:.1f} %")
    print(f"coplanar C' = {cpm * 1e12:.1f} pF/m, inter-turn C = {cpar * 1e12:.2f} pF, "
          f"+ pads {C_PADS * 1e12:.1f} pF, total C = {ctot * 1e12:.1f} pF")
    print(f"f0 (no tuning capacitor) = {a.resonance(lg, ctot) / 1e6:.2f} MHz")
    for k, lab in ((0.95, "L -5 %"), (1.05, "L +5 %")):
        print(f"  {lab}: {a.resonance(lg * k, ctot) / 1e6:.2f} MHz")
    for k, lab in ((0.95, "Ci -5 %"), (1.05, "Ci +5 %")):
        print(f"  {lab}: {a.resonance(lg, a.C_CHIP * k + cpar + C_PADS) / 1e6:.2f} MHz")
    need = a.capacitance_for(lg, a.F_NFC) - ctot
    print(f"extra capacitance to reach 13.56 MHz = {need * 1e12:.1f} pF")

    section("Tuning sweep (C1 + C2)")
    for ct in (0, 2.2, 3.3, 4.7, 6.8, 8.2, 10, 12, 15):
        print(f"  {ct:5.1f} pF -> {a.resonance(lg, ctot + ct * 1e-12) / 1e6:.2f} MHz")

    section("Losses")
    delta = a.skin_depth(a.F_NFC)
    rdc = a.resistance_dc(pts, W)
    rac = a.resistance_ac(pts, W, a.F_NFC)
    q = 2 * math.pi * a.F_NFC * lg / rac
    print(f"skin depth at 13.56 MHz = {delta * 1e6:.1f} um (copper is {a.T_CU * 1e6:.0f} um thick)")
    print(f"R_dc = {rdc:.2f} ohm, R_ac (skin effect) = {rac:.2f} ohm, unloaded Q = {q:.0f}")
    thin = a.card_spiral(N, OX, OY, 0.2 * MM, 1.3 * MM)
    print(f"for comparison, 0.2 mm traces: R_dc = {a.resistance_dc(thin, 0.2 * MM):.2f} ohm, "
          f"L = {a.inductance_greenhouse(thin, 0.2 * MM) * 1e6:.2f} uH")

    section("Energy harvesting (Faraday)")
    areas = a.turn_areas(N, OX, OY, W, S)
    print("turn areas [mm2] = " + ", ".join(f"{x / MM ** 2:.0f}" for x in areas) + f", sum = {sum(areas) / MM ** 2:.0f}")
    for hrms in (1.5, 7.5):
        print(f"H = {hrms} A/m rms -> open-circuit EMF = {a.induced_emf(hrms, areas):.2f} V rms")

    section("NDEF message size")
    url_body = "pierrehlr.github.io/"          # 'https://' is abbreviated by prefix code 0x04
    payload = 1 + len(url_body)
    record = 1 + 1 + 1 + 1 + payload          # header, type length, payload length, type 'U'
    tlv = 1 + 1 + record + 1                  # 0x03, length, record, terminator 0xFE
    print(f"payload = {payload} B, record = {record} B, TLV = {tlv} B of 144 B ({100 * tlv / 144:.0f} %)")

    section("QR code capacity")
    text = "HTTPS://PIERREHLR.GITHUB.IO/"
    n = len(text)
    alnum_bits = 4 + 9 + 11 * (n // 2) + 6 * (n % 2)
    byte_bits = 4 + 8 + 8 * n
    print(f"{n} characters: alphanumeric mode = {alnum_bits} bits = {math.ceil(alnum_bits / 8)} codewords, "
          f"byte mode = {byte_bits} bits = {math.ceil(byte_bits / 8)} codewords")
    print("version 2-M holds 28 data codewords -> uppercase fits in 25x25, lowercase needs version 3 (29x29)")
    print(f"module size = 17.5 mm / 25 = {17.5 / 25:.2f} mm")


if __name__ == "__main__":
    main()
