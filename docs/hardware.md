# Hardware design walkthrough

How the card went from requirements to a manufacturable KiCad 10 project. The
physics behind every number is in [physics.md](physics.md).

## 1. Requirements

| # | Requirement |
|---|---|
| F1 | Read by common NFC phones (iPhone XS and newer, Android) |
| F2 | Fully passive: no battery, no microcontroller, no external supply |
| F3 | Transmits the portfolio URL as a standard NDEF URI record |
| F4 | Opens the portfolio with minimal interaction (no app) |
| F5 | Read distance of at least 2 cm, 3 cm or more targeted |
| F6 | Content protected against rewriting |
| F7 | QR code fallback for phones without NFC |
| F8 | Looks like a business card: ISO ID-1 format, black and gold |

The original (French) specification and decision log is kept in
[00_cahier_des_charges.md](00_cahier_des_charges.md).

## 2. Chip selection

The obvious candidate, the NXP **NTAG213**, turned out to be sold only as
**bare wafers or MOA8 modules** for card and inlay manufacturers. Neither can
be reflow-soldered by a PCB assembler.

Its sibling, the **NTAG213F**, has the same memory (144 bytes), the same
50 pF input capacitance and the same NFC Forum Type 2 compliance. It comes in
a solderable **HXSON4** package (2.0 × 1.5 mm) and is stocked by JLCPCB/LCSC:

| Item | Value |
|---|---|
| Part | NXP NT2H1311F0DTLH (NTAG213F) |
| JLCPCB / LCSC | C2654853 (Extended part, Standard PCBA only) |
| Pins | 1 GND · 2 LB · 3 FD · 4 LA · exposed pad |
| Input capacitance | 50 pF |
| User memory | 144 bytes (enough for a 28-byte URL message) |

The "F" adds a *field detect* output (FD), meant to wake up a microcontroller.
This card has no microcontroller, which brings two datasheet constraints:

* **FD must not float.** It is tied to the chip's own GND pin. This is safe
  because FD is an open-drain output and the sleep mode is disabled by default.
  The one consequence is a rule for programming: **never enable `SLEEP_EN`**,
  or the tag would hide itself after the next field reset.
* **The exposed pad must be left floating.** It is soldered for mechanical
  strength but connected to nothing.

## 3. Schematic

```
 net LA ──┬────────────┬────────────┬──── U1 pin 4 (LA)
          │            │            │
         AE1          C1           C2          C1, C2: 0603 C0G, DNP
       antenna      tuning       tuning        (hand-fitted during tuning)
          │            │            │
 net LB ──┴────────────┴────────────┴──── U1 pin 2 (LB)

 U1 pin 3 (FD) ─── U1 pin 1 (GND)             net TAG_GND, nothing else
 U1 pin 5 (EP) ─── not connected
```

* The antenna is a `Device:Antenna_Loop` symbol, excluded from the BOM and the
  placement files: it is copper, not a part to buy.
* C1 and C2 are marked *Do Not Populate*, so the assembler leaves their
  (pre-tinned) pads empty.
* The NTAG213F symbol carries an `LCSC` field so the BOM exports with the part
  number.

## 4. Footprints

### NTAG213F (HXSON4)

KiCad has no HXSON4 footprint, so one was drawn from the JLCPCB/EasyEDA land
pattern and checked against the NXP package outline (SOT1312AB2). Using the
same orientation as JLCPCB's library means no rotation correction is needed in
the placement file. KiCad coordinates in mm, y pointing down:

| Pad | X | Y | Size |
|---|---|---|---|
| 1 | −0.25 | +1.00 | 0.25 × 0.70 |
| 2 | +0.25 | +1.00 | 0.25 × 0.70 |
| 3 | +0.25 | −1.00 | 0.25 × 0.70 |
| 4 | −0.25 | −1.00 | 0.25 × 0.70 |
| 5 (EP) | 0 | 0 | 1.00 × 0.80 |

### Antenna as a *net-tie* footprint

At DC a coil is a short circuit between LA and LB. Drawn as ordinary tracks,
it would be a DRC error. The antenna is therefore a footprint containing:

* the 4-turn spiral drawn as **16 copper graphic lines** (1.0 mm wide) on F.Cu,
  from a 17-point polyline centred on the card;
* **pad 1**, an SMD pad on F.Cu only (no paste, no mask opening), at the inner
  end (−33.5, 19);
* **pad 2**, a plated through-hole (Ø 1.0 mm, 0.4 mm drill), at the outer end
  (−39.5, 23.5), which is the entry point of the back-side bridge;
* the footprint property **net tie pad groups = `1, 2`**, which tells KiCad
  the short is intentional.

The footprint has no courtyard, because the chip and capacitors sit inside
the loop.

## 5. PCB layout

![Back of the card (KiCad 3D render)](images/card_back.png)

| Setting | Value |
|---|---|
| Stackup | 2 layers, FR-4, 0.8 mm, 1 oz copper |
| Outline | 85.6 × 53.98 mm rounded rectangle (r = 3.18 mm), centred on (150, 100) |
| Design rules | clearance 0.15 mm (net class 0.2), track 0.3 mm, via 0.6 / 0.3 mm, copper-to-edge 0.5 mm |
| Placement | antenna centred and locked, U1 at (128, 112) rotated 180°, C1/C2 at (122.5, 112.6) and (125, 112.6) rotated 90° |

Rotating the chip by 180° and the capacitors by 90° puts every **LB** terminal
on top and every **LA** terminal at the bottom. The routing is then two
parallel rails that the three components tap into:

* **LB:** from the antenna's outer pad, a back-side bridge runs at 45° under
  the four turns to a via at (119, 111), then a front rail leads to U1 pin 2.
* **LA:** from the antenna's inner pad to C1, C2 and U1 pin 4, all on the front.
* **FD–GND:** on this package these two pins are diagonal to each other, as
  are LA and LB, so the two connections must cross. The tie goes through two
  vias and a short back-side track under the chip.

Nothing is poured: the board has no ground plane and no copper inside the
antenna loop.

## 6. Artwork

![Front of the card (KiCad 3D render)](images/card_front.png)

* **Front (B side):** name, title and e-mail in white silkscreen.
  Bahnschrift for the name and title, Consolas for the address, plus a
  10 × 0.25 mm rule. The texts are mirrored in KiCad because this face is seen
  from below. KiCad's text size is the capital height (3.0 / 1.8 / 1.6 mm),
  and strokes are at least about 0.16 mm, above JLCPCB's 0.153 mm silkscreen
  minimum.
* **Back (F side):** KiCad 10's native QR code generator, as a 17.5 mm
  *knockout* on F.Silkscreen, with "Tap your phone or scan" and the URL
  underneath. The four antenna turns show through the black mask as a subtle
  frame.
* **Colours:** black solder mask, white silkscreen, ENIG (gold) finish. The
  antenna stays under the mask.

## 7. Manufacturing (JLCPCB)

Fabrication files are generated with the KiCad *Fabrication Toolkit* plugin
into [`Carte_NFC_KiCad/production/`](../Carte_NFC_KiCad/production):
Gerbers and drill files (zip), `bom.csv` (U1 only is placed) and
`positions.csv` (U1 at 180°).

| Option | Choice | Why |
|---|---|---|
| Thickness / colour / finish | 0.8 mm / black / ENIG | Card feel and look; ENIG also gives flat pads for the tiny 0.25 mm HXSON4 pads |
| Via covering | Tented | Hidden under the black mask |
| Mark on PCB | Remove mark | Otherwise an order number is printed on the card |
| Confirm production file | Yes | Check the silkscreen and panelisation before production |
| PCBA type | Standard | Required by this part |
| Edge rails | Added by JLCPCB | Mandatory: the card is less than 70 mm wide |
| Confirm parts placement | Yes | An engineer checks the chip orientation |

The edge rails are attached by small break-away tabs. The long edges will need
a light wet-sanding after delivery.

## 8. KiCad lessons learned

* **Net tie with a long spiral.** `kicad-cli pcb drc` flags a *shorting items*
  error between the spiral and the second pad of the net-tie group. KiCad
  associates the chain of graphic segments with a single pad's net. The DRC in
  the PCB editor does not report it; the connection is intentional.
* **TrueType silkscreen text.** The *text thickness* check reports every
  Bahnschrift and Consolas string. Bahnschrift is a variable font with
  overlapping contours, and the results even change non-monotonically with the
  threshold. The strokes, measured on renders, are about 0.16 mm or more. These
  warnings were reviewed and excluded.
* **QR code knockout.** Without the *knockout* option, the code prints as white
  modules on black, i.e. inverted, which many phone scanners reject.
* **Router and vias.** Pressing `V` only works while a track is being routed.
  Placing a free via at the end of a finished track also works, and it inherits
  the track's net.

## 9. Programming (planned)

With NXP TagWriter (Android/iOS):

1. Write a single URI record, `https://pierrehlr.github.io/` (28 bytes in total).
2. Check with NXP TagInfo that the capability container and the NDEF message
   are valid.
3. Make the tag read-only (permanent lock), or protect the configuration pages
   with a password. `SLEEP_EN` must stay 0, because FD is tied to ground.
