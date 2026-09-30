# Carte de visite NFC — Cahier des charges

Version 0.1 — 2026-09-30 — Phase 0 (cadrage)

## 1. Besoin

Permettre à une personne d'accéder au portfolio du propriétaire en approchant simplement un smartphone NFC de la carte, sans batterie, sans alimentation et sans application dédiée.

## 2. Exigences fonctionnelles

| ID | Exigence | Critère de validation |
|---|---|---|
| F1 | Détection par les smartphones NFC courants | Lecture OK sur ≥ 1 iPhone (XS ou plus récent) et ≥ 2 Android de marques différentes |
| F2 | Fonctionnement 100 % passif | Aucun composant d'alimentation sur la carte |
| F3 | Transmission d'une URL | Enregistrement NDEF de type URI, lu correctement par NXP TagInfo |
| F4 | Minimum d'interaction | Android : ouverture directe du navigateur. iPhone : un seul tap sur la notification |
| F5 | Distance de lecture | Minimum 2 cm, objectif 3 cm ou plus, téléphone posé à plat sur la carte |
| F6 | Contenu protégé | Tag verrouillé ou protégé par mot de passe contre la réécriture |
| F7 | Solution de secours | QR code en sérigraphie pointant vers la même URL |
| F8 | Identité visuelle | Utilisable comme carte de visite ou objet de démonstration |

## 3. Contraintes électriques et RF

- Fréquence 13,56 MHz, ISO/IEC 14443 A, NFC Forum Type 2 Tag.
- Puce retenue : NXP NTAG213F, réf. NT2H1311F0DTLH (JLCPCB C2654853). Boîtier HXSON4 2,0 × 1,5 mm : broche 1 GND, 2 LB, 3 FD, 4 LA, plus un pad central.
  - La broche FD est reliée à GND (la datasheet interdit de la laisser flottante). Le mode veille ne doit donc jamais être activé (SLEEP_EN = 0) : avec FD à la masse, la puce deviendrait invisible.
  - Le pad central reste non connecté (recommandation de la datasheet).
- Antenne gravée sur le PCB. Inductance cible ≈ 2,5 à 2,7 µH, à recalculer avec la capacité d'entrée de la puce retenue (≈ 50 pF pour les NTAG21x).
- Résonance à vide visée légèrement au-dessus de 13,56 MHz (≈ 14 à 15 MHz), puis ajustement vers le bas par un condensateur d'accord.
- Antenne retenue (option A, géométrie proche d'une antenne ISO 14443 classe 1, comme une carte bancaire) :
  - spirale rectangulaire de 80 × 48 mm (bords extérieurs des pistes), 4 spires, piste de 1,0 mm, écart de 0,5 mm ;
  - zone intérieure libre de 69 × 37 mm ; longueur ≈ 934 mm ; R continue ≈ 0,46 Ω ;
  - L = 2,24 µH (méthode de Greenhouse) et 2,18 µH (formule ST AN2972), soit 2,7 % d'écart ;
  - capacité parasite ≈ 2,5 pF, d'où f0 à vide ≈ 14,7 MHz (14,3 à 15,0 MHz selon la tolérance de Ci) ;
  - 13,56 MHz atteint avec environ 8 à 10 pF d'accord ;
  - scripts de calcul : `calc/` (détail dans `docs/physics.md`).
- Aucun microcontrôleur, aucune batterie, aucune alimentation externe.
- Aucun aplat de cuivre ni boucle de cuivre fermée à l'intérieur de l'antenne.

## 4. Contraintes mécaniques

- Format ID-1 (carte bancaire) : 85,60 × 53,98 mm, rayon des coins 3,18 mm.
- FR-4, 0,8 mm d'épaisseur, 2 couches.
- Composants CMS sur une seule face (laquelle : décidé en phase 4).
- Rien qui dépasse ni qui accroche : la carte doit pouvoir tenir dans un portefeuille.

## 5. Fabrication

- Logiciel de CAO : KiCad (dernière version stable).
- Fabricant pressenti : JLCPCB (PCB, assemblage CMS, composants LCSC). L'épaisseur de 0,8 mm est compatible avec leur assemblage.
- Assemblage : la puce NFC est posée par le fabricant. Sur le prototype, les condensateurs d'accord sont en 0603 pour pouvoir être soudés à la main.
- Finition : économique pour le prototype v0, soignée pour la version finale (couleur de masque, dorure ENIG…, voir phase 4).

## 6. Stratégie d'accord sans analyseur de réseau

Sans NanoVNA, on ne mesure pas directement la fréquence de résonance. On s'appuie sur trois leviers :

1. **Calcul recoupé.** L'inductance de l'antenne est calculée par plusieurs méthodes (formules analytiques et calculateur en ligne ST eDesignSuite). On ne retient la géométrie que si ces méthodes concordent.
2. **Marge vers le haut.** L'antenne est conçue pour résonner légèrement au-dessus de 13,56 MHz sans condensateur. Deux emplacements 0603 en parallèle, non montés par défaut, permettent de redescendre.
3. **Balayage empirique sur le prototype v0.** Chaque carte reçoit une valeur de condensateur différente (par ex. 0 / 3,3 / 6,8 / 10 / 15 pF). On mesure la distance de lecture maximale avec un smartphone et une règle. Le maximum de distance indique le meilleur accord, qui devient la valeur de la version finale.

## 7. Points ouverts

- [x] Portfolio : https://pierrehlr.github.io/ (GitHub Pages, pas de domaine perso)
- [x] URL programmée et gravée en QR code : `https://pierrehlr.github.io/` (racine)
- [x] Quantités : 5 cartes de prototype v0, puis 5 cartes finales
- [x] Budget : « pas déraisonnable » (ordre de grandeur 40 à 80 € par commande de 5 cartes assemblées)
- [x] Fabricant : JLCPCB
- [x] Identité visuelle : vernis noir, finition ENIG dorée, sérigraphie blanche, antenne sous le vernis
- [x] Répartition : recto (face B) = nom, titre, mail ; verso (face F) = QR code, URL, puce
- [x] Police : Bahnschrift (nom, titre), Consolas (mail, URL)
- [x] Textes : « Pierre HILAIREAU », « Embedded systems student », « pierre.hilaireau@edu.ece.fr » ; au verso, « Tap your phone or scan » et « pierrehlr.github.io » sous le QR code (maquette validée le 2026-09-30)
- [ ] Contenu retenu : nom et titre, adresse mail, QR code de secours (pas de logo ni de pictogramme NFC)

## 8. Journal des décisions

| Date | Décision | Raison |
|---|---|---|
| 2026-09-30 | CAO sous KiCad, réalisée par le porteur du projet | Gratuit et très répandu. Claude guide, fait ou vérifie les calculs et relit les fichiers |
| 2026-09-30 | Puce posée par le fabricant | Permet un boîtier minuscule (≈ 1,6 mm) quasi invisible |
| 2026-09-30 | Format ID-1, 0,8 mm | Tient dans un portefeuille, format universel de carte de visite |
| 2026-09-30 | Pas de VNA : accord empirique au smartphone | Pas d'instrument disponible ; compensé par la stratégie de la section 6 |
| 2026-09-30 | Fabricant JLCPCB | Tarifs bas pour de petites séries ; la puce NFC candidate est dans leur catalogue d'assemblage |
| 2026-09-30 | Deux commandes de 5 cartes (proto v0 puis finale) | Valider l'antenne et l'accord avant de payer la finition soignée |
| 2026-09-30 | URL programmée : `https://pierrehlr.github.io/` | Choix du porteur : adresse directe, sans page de redirection |
| 2026-09-30 | Antenne sur tout le pourtour : 80 × 48 mm, 4 spires, piste 1 mm, écart 0,5 mm | Même géométrie qu'une carte sans contact (lue par tous les téléphones), lecture sur toute la surface ; f0 à vide ≈ 14,7 MHz, laisse de la marge pour l'accord vers le bas |
| 2026-09-30 | Vernis noir, ENIG doré, antenne sous le vernis | Rendu sobre et haut de gamme ; l'ENIG donne aussi des pads plats pour la petite puce |
| 2026-09-30 | Contenu : nom, titre, e-mail, QR code | Choix du porteur ; le QR code couvre l'exigence F7 |
| 2026-09-30 | QR code encodé en majuscules (`HTTPS://PIERREHLR.GITHUB.IO/`, correction M, 17,5 mm, en négatif sur F.Silkscreen) | Mode alphanumérique plus compact ; testé sur écran avec le téléphone du porteur : OK |
| 2026-09-30 | Prototype commandé directement en noir et ENIG, 5 cartes assemblées (remplace le « v0 finition simple ») | Seulement 5 cartes voulues : si le prototype fonctionne, il devient la série finale, sans payer deux fois les frais fixes d'assemblage ; l'ENIG est aussi préférable pour les pads de 0,25 mm |
| 2026-09-30 | Puce NTAG213F (NT2H1311F0DTLH) | La NTAG213 classique n'existe qu'en wafer ou en module, impossible à assembler sur PCB. La variante F existe en boîtier soudable et est disponible chez JLCPCB |
