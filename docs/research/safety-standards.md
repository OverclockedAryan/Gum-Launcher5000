# Safety & Standards Research

Last researched: 2026-11-25 (web research; not legal advice; verify against the actual standards)

Scope: a desktop robot that fires one rigid gum pellet (1.2–1.6 g, about 15 × 10 × 7 mm) into an open mouth at 0.5–2 m and 4–7 m/s. **(computed)** marks my own arithmetic. **(unverified)** marks claims I could not source. Most standards are paywalled, so clause text comes from test-lab summaries and regulator documents; read the standard itself before relying on a clause. The full trajectory and error model is in [ballistics.md](ballistics.md).

## Key takeaways for the design

- **By toy-standard energy rules the pellet passes; by their shape rules it fails.** A 1.5 g pellet carries 0.012 J at 4 m/s, 0.027 J at 6 m/s and 0.048 J at 8 m/s (computed). All three are at or below 0.08 J, the point above which toy standards require a soft tip, a limit of 2,500 J/m² and an "aiming at eyes or face" warning. However, ASTM F963 and ISO 8124-1 (= India's IS 9873-1) ban stored-energy projectiles that fit the 31.7 mm small-parts cylinder, and this pellet fits.
- **Toy limits are not eye-safety limits.** Toy standards treat aiming at the face as misuse to warn against, not as intended use. A 50 % risk of corneal abrasion sits at about 1,500 J/m², which is *below* the toy limit of 2,500 J/m². Soft Nerf darts at about 0.12 J (computed) have caused hyphema and retinal tears.
- **Hard cap: exit energy ≤ 0.04 J (40 mJ), set by the heaviest pellet.** That is ≤ 7.0 m/s for 1.6 g (7.3 m/s for 1.5 g, 7.5 m/s for 1.4 g). Run at ≤ 0.03 J (about 6 m/s). Enforce the cap physically: even the worst-case spring, voltage or preload must not exceed it. Chronograph every shot and lock out on over-speed.
- **Velocity consistency is a safety property.** At 2 m and 6 m/s, a +5 % speed error lifts the impact point about 6 cm (computed), which is roughly the mouth-to-eye distance (unverified). At 1 m the same error moves it only about 1.3 cm. A 4 m/s shot cannot reach 2 m at all. So either limit auto-fire to about 1.2–1.5 m, or hold the speed SD to ≤ 1 % and limit drift to ±2 %.
- **Aim low.** Over-speed always lands higher (nose, then eyes) and under-speed lands lower (chin). Bias the aim point into the lower half of the mouth or the front of the tongue, so the likely error lands somewhere harmless.
- **Choking.** The American Academy of Pediatrics (AAP) lists chewing gum as a high-risk choking food, and the pellet is a "small part". Treat the robot as adults-only. Send one pellet per explicit consent, keep a long gap between shots, and never fire when the head is tilted back or the person is reclining.
- **Hardware safety chain.** Wire a keyed ARM switch and a latching E-stop in series with actuator power (IEC 60204-1 stop category 0). Add gate pull-downs so nothing moves during boot, a microcontroller watchdog with its own clock, a heartbeat timeout from the computer, and a manual re-arm after any reset. Stored energy (a cocked spring or a coasting flywheel) must be blocked by a feed gate that fails closed.
- **Food path.** The pellet should touch only removable stainless or PTFE liners, or natural (uncolored) PETG printed with a stainless nozzle. Keep resin prints and carbon-fibre or wood-filled filaments out of it. A "food-safe" filament does not make the printed part certified.
- **Sensors and lasers.** The TF-Luna and TFmini-S (850 nm) and the VL53L1X (940 nm) are Class 1 lasers, which is acceptable near faces as long as the module is unmodified. Use no visible aiming lasers: the FDA says never to aim a laser at a person.
- **The standards are changing.** EN 71-1:2026 is published, but I could not confirm it is harmonised. IS 9873-1:2019 was superseded by a 2025 edition. ISO 8124-1:2022 has an Amendment 1 from 2025. ASTM F963-23 has been mandatory since 2024-04-20. The new EU Toy Safety Regulation 2025/2509 applies from 2030.

## 1. Projectile-toy rules (ASTM F963, EN 71-1, ISO 8124-1, IS 9873-1)

**Status and scope**
- All four standards cover toys for children under 14. An adult-only hobby build is outside their legal scope, but they are the best public benchmarks.
- **ASTM F963-23** is mandatory in the US under 16 CFR 1250 from 20 Apr 2024. Its projectile edits only reorder the bow test in §8.14, and the rule says they "do not change the substantive performance requirements" ([Federal Register 2024-00741](https://www.govinfo.gov/content/pkg/FR-2024-01-18/html/2024-00741.htm)). Projectile toys are §4.21 and need third-party testing ([CPSC chart](https://cpsc.gov/Business--Manufacturing/Business-Education/Toy-Safety/ASTM-F-963-Chart)). I found no F963-25 (unverified).
- **EN 71-1:2014+A1:2018** is still the harmonised edition I could confirm. A1:2018 replaced the old maximum-energy limits with energy per unit area.
  - BS EN 71-1:2026 was published on 31 Jan 2026 and supersedes it in the UK catalogue ([BSI](https://knowledge.bsigroup.com/products/safety-of-toys-mechanical-and-physical-properties-6)).
  - It becomes harmonised only once cited in the EU Official Journal; I could not confirm that citation ([UL](https://www.ul.com/news/toys-new-safety-standard-released-europe), [Bureau Veritas](https://www.cps.bureauveritas.com/newsroom/toy-safety-standard-en71-12026-published)).
  - Summaries list no projectile limit changes in the 2026 edition (unverified).
  - The new EU Toy Safety Regulation 2025/2509 applies from 2030 ([EUR-Lex](https://eur-lex.europa.eu/eli/reg/2025/2509/oj)).
- **ISO 8124-1:2022** is current, and Amendment 1 was published in 2025-10 ([ISO listing](https://www.iso.org/standard/86039.html)). I did not check what Amendment 1 changes.
- **IS 9873 (Part 1):2019** is identical to ISO 8124-1:2018 and was superseded on 26 Dec 2025 by IS 9873 (Part 1):2025 ([listing](https://shop.standards.ie/en-ie/standards/is-9873-part-1-2019-180994_saig_bis_bis_2765594)). BIS's 2024 draft aimed to align it with ISO 8124-1:2022 (final content unverified). India's Toys Quality Control Order makes BIS certification mandatory for toys ([PIB](https://pib.gov.in/PressReleasePage.aspx?PRID=1843543)).

**Requirements for projectile toys with stored energy** (from the [STC comparison of ASTM F963-17, EN 71-1:2014+A1:2018 and ISO 8124-1:2019](https://stc.group/getfile/index/action/images/name/5f582c9f13d91.pdf))
- **ASTM F963 §4.21**
  - A projectile must not fit entirely into the small-parts cylinder in any orientation.
  - If KE > 0.08 J it needs resilient leading edges and a kinetic-energy density (KED) ≤ 2,500 J/m² (§4.21.2.3, tested per §8.14.6).
  - Projectiles at ≤ 0.08 J are exempt from the KED limit. That exemption was omitted by mistake in F963-16 and restored afterwards ([CPSC 2017 letter](https://www.cpsc.gov/s3fs-public/TIA_projectile%20toys_let_3.31.17.pdf)).
  - Projectiles that travel ≤ 300 mm are exempt.
- **EN 71-1:2014+A1:2018 §4.17.3**
  - If KE > 0.08 J it needs (a) a resilient leading part, (b) a warning about aiming at the eyes or face, and (c) KE per unit area ≤ 2,500 J/m².
  - Edges next to the leading part must be visibly rounded.
  - The launcher must not be able to fire improvised projectiles.
- **ISO 8124-1 and IS 9873-1**
  - Projectiles must not fit into the small-parts cylinder.
  - If KE > 0.08 J they need a resilient contact surface, a warning about aiming at the eyes or face (only where the toy can reasonably be aimed at the face), and ≤ 2,500 J/m².
  - Rigid leading edges must not protrude beyond the depth of the test gauge. Corners next to the leading edge must be rounded, and a 0.25 mm radius counts as sufficient.
  - The clause was §4.18 in older editions; check the numbering in the 2022 edition.
- **Superseded limits.** EN 71-1:2005 allowed at most 0.08 J for rigid projectiles, 0.5 J for resilient ones, and 0.16 J/cm² (1,600 J/m²) ([STC 2008](https://www.stc.group/getfile/index/action/images/name/566a2a62651d2.pdf)).
- **Small-parts cylinder.** It is 31.7 mm in diameter and 25.4–57.1 mm deep ([Canada SOR/2011-17](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2011-17/page-3.html)). CPSC says it approximates the fully expanded throat of a child under three ([CPSC](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Small-Parts-for-Toys-and-Childrens-Products)).

**Pellet assessment for a 1.5 g pellet (computed).** Areas are bounding-box projections; the rounded pillow shape is roughly 20 % smaller.

| Exit speed | KE | KE/area, flat face 150 mm² | side 105 mm² | end 70 mm² | edge-first ~40 mm² |
|---|---|---|---|---|---|
| 4 m/s | 0.012 J | 80 J/m² | 114 J/m² | 171 J/m² | 300 J/m² |
| 6 m/s | 0.027 J | 180 J/m² | 257 J/m² | 386 J/m² | 675 J/m² |
| 8 m/s | 0.048 J | 320 J/m² | 457 J/m² | 686 J/m² | 1,200 J/m² |

- KE only reaches 0.08 J at 10.3 m/s for a 1.5 g pellet, or 10.0 m/s for 1.6 g. At 8 m/s, a 1.6 g pellet carries 0.051 J.
- **Verdict.**
  - **Energy: passes** all four standards at 4, 6 and 8 m/s. No resilient-tip, KED or warning requirement is triggered, and even edge-first contact stays below 2,500 J/m².
  - **Shape: fails** ASTM F963 §4.21 and ISO 8124-1 / IS 9873-1, because the pellet fits the small-parts cylinder. I could not confirm an equivalent small-part rule for projectiles in EN 71-1.
- **Improvised projectiles.** Under all three standards the launcher must not fire improvised projectiles, so use a shape-keyed, single-pellet feed that will not accept pebbles or other objects.

## 2. Eye-injury thresholds and the recommended energy cap

**Published thresholds**
- Normalized energy (kinetic energy divided by the projectile's projected area) predicts eye injury better than kinetic energy, mass or velocity ([Duma 2005, PMID 16374288](https://pubmed.ncbi.nlm.nih.gov/16374288/); [Alphonse & Kemper 2013 review](https://vtechworks.lib.vt.edu/bitstream/handle/10919/23814/Alphonse%202.pdf?sequence=1)).
- Duma 2005 fitted BB, metal-rod and foam impacts at 2–122 m/s. The 50 % risk points are:
  - corneal abrasion: **1,503 J/m²**
  - lens dislocation: 19,194 J/m²
  - hyphema: **20,188 J/m²**
  - globe rupture: 23,771 J/m²
  - retinal damage: 30,351 J/m²
- Kennedy 2006 puts globe rupture in human eyes at 50 % risk at **35,519 J/m²** (CI 32,018–40,641) ([SAE 2006-22-0026](https://saemobilus.sae.org/content/2006-22-0026)).
- Kennedy & Duma's 2011 survival curves (approximate, read from the plot in the review) put the 50 % points at about 10,000 J/m² for hyphema, about 19,000–20,000 J/m² for lens and retina damage, and about 37,000 J/m² for globe rupture.
- The corneal-abrasion data came from foam particles (0.034–1.45 J) on pig eyes in situ. A rigid pellet may abrade the cornea at lower energy (unverified).
- **Comparable real-world projectiles**
  - Airsoft pellets (0.2 g, 6 mm) carry about a 100 % risk of corneal abrasion and over 75 % risk of hyphema ([Kennedy 2006](https://pubmed.ncbi.nlm.nih.gov/16817577/)). A finite-element model of 0.2 g at 45–75 m/s (0.2–0.56 J) predicts corneal laceration from 60 m/s ([Takahashi 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7266397)).
  - Foam Nerf darts (about 1.0 g at about 35 mph, roughly 0.12 J and 980 J/m² over 12.7 mm, computed) have caused traumatic hyphema, corneal oedema and retinal tears at 1–8 m in children and adults ([Bizrah & Verma 2017](https://pubmed.ncbi.nlm.nih.gov/28924000/); [Joshi 2023](https://www.eyenews.uk.com/education/case-reports/post/traumatic-injuries-from-foam-nerf-bullets)).

**Recommended cap**
- **Hard cap (survives any single fault, enforced physically): ≤ 0.04 J at the muzzle.** That is v_max = 7.0 m/s for 1.6 g, 7.3 m/s for 1.5 g and 7.5 m/s for 1.4 g. When the chronograph limit is a speed, set it from the heaviest pellet. Reasons:
  - It is half the toy threshold for rigid projectiles (0.08 J).
  - On the pellet's smallest face it gives about 570 J/m², which is ≤ 40 % of the corneal-abrasion 50 % point, about 6 % of the lowest hyphema 50 % point, and ≤ 2.5 % of the globe-rupture 50 % point (computed).
  - It is about one third of the KE of a Nerf dart that has caused hyphema.
- **Operating ceiling: ≤ 0.03 J** (≈ 6.1 m/s at 1.6 g). Prefer 4.5–6 m/s within 1 m. Treat 8 m/s as a fault, never as an operating point.
- **No energy level makes an eye hit acceptable.** I could not find the risk slope below the 50 % abrasion point. The cap limits how bad an injury can be; the aiming geometry has to prevent eye hits in the first place.
- **Testing.** Test on a printed face or mannequin first. Testers should wear impact-rated safety glasses, such as ANSI Z87.1 or EN 166 (exact impact specs unverified).

**Speed sensitivity (computed: muzzle level with the mouth; drag Cd ≈ 1, area ≈ 100 mm², 1.5 g)**

Each cell gives the elevation, the time of flight, and how far the impact point rises for a +5 % speed error.

| Range | 4 m/s | 5 m/s | 6 m/s | 7 m/s |
|---|---|---|---|---|
| 0.5 m | 9.1°, 0.13 s, +0.7 cm | 5.7°, 0.10 s, +0.5 cm | 4.0°, 0.08 s, +0.3 cm | 2.9°, 0.07 s, +0.2 cm |
| 1.0 m | 19.5°, 0.27 s, +3.3 cm | 11.9°, 0.21 s, +2.0 cm | 8.1°, 0.17 s, +1.3 cm | 5.9°, 0.15 s, +1.0 cm |
| 1.5 m | 37.1°, 0.49 s, +10.5 cm | 18.9°, 0.33 s, +4.8 cm | 12.6°, 0.26 s, +3.1 cm | 9.1°, 0.22 s, +2.2 cm |
| 2.0 m | out of reach | 28.1°, 0.47 s, +9.9 cm | 17.6°, 0.36 s, +5.9 cm | 12.5°, 0.31 s, +4.1 cm |

- **Minimum speed for 2 m** is 4.43 m/s with the muzzle level with the mouth, or 4.77 m/s if the mouth is 0.3 m higher (no drag). With the mouth 0.25 m above the muzzle, [ballistics.md](ballistics.md) finds 6 m/s tolerates only 4 % over-speed at 2 m, against 22 % at 1 m.
- **Range error** also tilts the aim. The ±6 cm accuracy of the TF-Luna or TFmini-S works out to about ±2 cm vertically at 2 m and 6 m/s (computed).
- **No abort after release.** Flight takes 0.07–0.49 s, so every check must pass before the pellet leaves.

## 3. Choking and aspiration

- The AAP 2010 policy statement lists chewing gum and hard candy among high-risk choking foods ([AAP policy, mirror](https://www.sbp.com.br/fileadmin/user_upload/pdfs/Policy_Statement-Prevention_of_Choking_Among_Children.pdf)). HealthyChildren.org says to keep high-risk foods from children until at least age 4, and never to let them "run, walk, play or lie down with food in their mouths" ([HealthyChildren](https://www.healthychildren.org/English/health-issues/injuries-emergencies/Pages/Choking-Prevention.aspx)).
- The gum industry body ICGA recommends parental supervision when children chew gum and says the youngest children should not have it ([ICGA](https://www.gumassociation.org/faq/is-there-a-risk-of-choking-when-chewing-gum/)). An "age 5" guideline is widely repeated, but I could not trace it to a primary source (unverified).
- **Gum does get aspirated.** Reported cases include:
  - gum lodged in the airway and removed by bronchoscopic cryoextraction ([Rubio 2013](https://doi.org/10.4103/1817-1737.105721));
  - gum causing upper-airway obstruction in a 15-year-old who nearly needed a tracheotomy ([Fukumasa 2020](https://doi.org/10.1016/j.rmcr.2020.101029));
  - an emergency-department series of 138 choking patients aged 1–88, with 40–59 the largest age group ([Saccomanno 2023](https://doi.org/10.4081/ejtm.2023.11471)).
- Throwing food in the air and catching it in the mouth is listed as a choking-risk behaviour (Drugs.com care notes; seen only as a search snippet because the page blocked fetching: [link](https://www.drugs.com/cg/choking-in-children-ambulatory-care.html)).
- **Why this device adds risk.** A rigid object the size of a small part arrives while the mouth is wide open, possibly during an inhalation (mechanism unverified). A flat or rising path points toward the palate and the back of the mouth. In [ballistics.md](ballistics.md) §5, the pellet is still rising at 1 m when the mouth is 0.25 m above the muzzle.
- **Mitigations** (design reasoning):
  - **Adults only.** Vision cannot verify age, so the key-holder enforces it. Put a choking warning label on the robot.
  - **Aim point.** Aim at the front third of the tongue or the lower-lip line, never at the back of the mouth. Prefer a descending entry, and lower the speed at short range: at 0.5 m, 7 m/s arrives at about 3° while 4 m/s arrives at about 9°.
  - **Posture.** Never fire if the head is pitched back more than about 15°, or the person is reclining, lying down, talking, laughing, eating or drinking.
  - **One pellet at a time.** Allow one pellet per explicit consent and require the mouth to close before the next shot. Keep at least 10 s between shots to the same person, and cap pellets per session (for example 5). The 2 s minimum in REQ-SAF-006 is too short for this.
  - **Instructions.** Tell users to sit upright, keep their mouth open but not inhale sharply, and spit the pellet out if it reaches the back of the throat.
  - **Missed pellets.** Collect them. Sugar-free gum may contain xylitol, which can cause dangerous hypoglycaemia in dogs within 10–60 minutes ([FDA](https://www.fda.gov/consumers/consumer-updates/paws-xylitol-its-dangerous-dogs)). Gums high in polyols carry a laxative warning in the EU (unverified), which is one more reason for a session cap.

## 4. Food-contact safety of 3D-printed parts

- **Parts that touch the pellet:** magazine, feed indexer, chamber, barrel, plunger or flywheel faces, and muzzle. Keep this path short, removable without tools (REQ-FEED-004), and away from grease and electronics.
- **United States**
  - FDA clears *substances*, not printed parts. A material's status depends on every component, including colorants and additives ([FDA](https://www.fda.gov/food/packaging-food-contact-substances-fcs/determining-regulatory-status-components-food-contact-material)).
  - PETG-type copolyesters are covered by [21 CFR 177.1315](https://www.law.cornell.edu/cfr/text/21/177.1315), and PTFE and other perfluorocarbon resins by [21 CFR 177.1550](https://www.law.cornell.edu/cfr/text/21/177.1550).
  - PLA is cleared through resin-specific food-contact notifications, so check the FDA FCN inventory for the exact resin.
  - Neither FDA nor NSF has a certification route for printed parts ([Fictiv](https://www.fictiv.com/articles/food-grade-3dp-manufacturing)).
- **European Union**
  - Regulation 1935/2004 is the framework, and 10/2011 covers plastics: a Union list of allowed substances, an overall migration limit of 10 mg/dm² (Art. 12), and a declaration of compliance ([EC](https://food.ec.europa.eu/food-safety/chemical-safety/food-contact-materials/legislation_en); [Art. 12](https://www.legislation.gov.uk/eur/2011/10/article/12/data.htm)).
  - Bisphenol A has been banned in food-contact plastics, resins, coatings, adhesives and inks since 20 Jan 2025, with transition periods. The ban is Regulation 2024/3190, corrected by 2026/250 ([EU](https://trade.ec.europa.eu/access-to-markets/en/content/eu-prohibition-use-and-trade-bisphenol-20-january-2025); [2026/250](https://eur-lex.europa.eu/eli/reg/2026/250/oj)).
- **Layer lines**
  - In printed PLA, biofilm was thickest between the layers, and "bacteria fill in the valleys". Carbon-fibre and wood-filled PLA supported the most biofilm ([Hall 2021](https://www.frontiersin.org/articles/10.3389/fmicb.2021.646303/full)).
  - Prusa calls the grooves "almost impossible to clean properly". It says brass nozzles wear and are not food-safe, so use stainless steel or titanium. It names natural, uncolored PETG as the "best bet", and it does not recommend prints as food containers ([Prusa](https://help.prusa3d.com/article/food-safe-fdm-printing_112313)).
- **Resin prints:** "No Formlabs resins are food safe unless users take additional steps" ([Formlabs](https://formlabs.com/blog/guide-to-food-safe-3d-printing/)). Keep resin parts out of the food path.
- **Mitigations**
  - **Barrel and feed liner:** off-the-shelf 304/316 stainless tube, or PTFE/FEP tube from a supplier that provides a food-contact declaration.
  - **Printed food-path parts:**
    - Use natural PETG from a filament spool reserved for food parts, printed through a stainless nozzle at a low layer height.
    - The X1 Carbon's stock nozzle is hardened steel (unverified), and its food suitability is unclear.
    - Optionally seal the parts with a food-contact epoxy whose supplier declares compliance (for example 21 CFR 175.300). Coatings wear and need renewing ([Formlabs](https://formlabs.com/blog/guide-to-food-safe-3d-printing/)).
  - **Cleaning:** warm soapy water and a brush, rinse, and dry fully. No dishwasher or hot water: PET- and PLA-type parts soften at about 60–70 °C ([Formlabs](https://formlabs.com/blog/guide-to-food-safe-3d-printing/)). Vendor blogs give glass transition at 55–60 °C for PLA and 80–85 °C for PETG ([QIDI](https://qidi3d.com/blogs/print-lab/is-petg-food-safe-cookie-cutters)). Replace printed food-path parts periodically.
  - **Handling:** coated pellets are dry, which lowers bacterial growth compared with moist food (unverified). Keep the hopper lidded. Throw away any pellet that hit a face, the floor or the table, and load with clean hands.

## 5. Safety architecture

- **Standards framework**
  - ISO 12100:2010 sets the order of risk reduction: inherently safe design first, then safeguards, then information for use. It was confirmed in 2022 and a revision is in progress ([ISO](https://www.iso.org/standard/51528.html)).
  - **IEC 60204-1:2016+A1:2021 §9.2.2** (edition 6.1, [IEC](https://webstore.iec.ch/en/publication/71256)) defines three stop categories ([Schneider FAQ](https://www.se.com/us/en/faqs/FA122781)):
    - Category 0: power to the actuators is removed immediately (an uncontrolled stop).
    - Category 1: a controlled stop, then power is removed.
    - Category 2: a controlled stop with power left on.
    - Emergency stops must be category 0 or 1.
  - **ISO 13850:2015** gives the design principles for emergency stops, with the device itself specified by IEC 60947-5-5, which requires mechanical latching ([ISO](https://www.iso.org/standard/59970.html)). From memory, not checked against the text: the actuator is red on a yellow background, it latches, and resetting it must not restart the machine.
  - **Collaborative-robot practice** treats the eyes and larynx as areas that must never be contacted. This comes from DGUV information sheet FB HM-080 as quoted in a search excerpt; the [PDF](https://www.sifa.dguv.de/medien/fb-holzundmetall/publikationen-dokumente/infoblaetter/infobl_englisch/080_collaborativerobotsystems.pdf) has since moved, so verify. ISO 10218-1:2025 and 10218-2:2025 are the current robot safety editions ([ISO](https://www.iso.org/standard/73934.html)).
  - **Software:** IEC 60730-1 Annex H "Class B" calls for a watchdog with an independent time base plus program-flow and clock monitoring. IEC 60335-1 Annex R builds on it ([Microchip](https://onlinedocs.microchip.com/oxy/GUID-C0410A3B-A192-4F94-A83F-81035433111B-en-US-2/GUID-D646A5B7-88DE-4F25-B72D-1FE01D1A1647.html); [Silicon Labs AN1074](https://www.silabs.com/documents/public/application-notes/an1074-efm8-family-iec60730-library.pdf)).
- **Recommended pattern** (design reasoning):
  1. **Power chain.** Supply → fuse → keyed ARM switch → latching E-stop with normally-closed, direct-opening contacts → actuator rail. The microcontroller only senses the rail. With the rail dead, no firmware bug can fire (category 0).
  2. **Stored energy.** A cocked spring or a coasting flywheel keeps its energy after the power is cut. Use a spring-return feed gate that is closed when unpowered. Never pre-cock while disarmed, and brake the flywheel motors on disarm.
  3. **Fail-safe boot.**
     - Fit pull-down resistors on the driver gates, and avoid strapping pins. ESP32 strapping pins are read at reset, and an Espressif FAQ entry (written for the ESP8266) notes that pin levels "are not controlled by the program during system initialization" ([Espressif](https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/gpio.html); [boot modes](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html)).
     - After any reset or brown-out, require the ARM switch to be cycled off and on again, and never auto-resume.
  4. **Watchdog and heartbeat.**
     - The microcontroller's hardware watchdog must run on its own clock.
     - The computer sends a heartbeat at ≥ 20 Hz with a sequence number and CRC, and the microcontroller disarms after a gap of more than 200 ms.
     - A FIRE command is single-use. It must refer to a camera frame no more than about 100 ms old and is rejected if replayed.
  5. **Dynamic fire enable.** Drive the actuator only while a toggling (charge-pump) signal is present, so a GPIO stuck high cannot fire (common pattern; no source found).
  6. **Rate limiting.** Feed one pellet mechanically per cycle. The firmware enforces at least 10 s between shots to the same person and a per-session cap.
  7. **Chronograph.** Put two IR gates at the muzzle, log every shot, and lock out on over-speed or drift (REQ-SAF-003).
  8. **Consent.**
     - Use an explicit opt-in, such as a button or a distinct gesture held about 1 s, which opens a window of about 5 s for one shot.
     - Within that window, the mouth must be open and steady for 300 ms, the face turned toward the robot, and exactly one face in the firing cone, tracked continuously. Abort the moment any of these is lost.
     - An open mouth alone is not consent: yawns, laughter and speech can also hold it open for 300 ms. This matters most in table-service mode (REQ-MODE-002), where people other than the operator are present.
     - Manual trick-shot mode keeps the energy cap, the ARM switch and every face gate (REQ-MODE-003).
  9. **Pre-fire cue.** Give the same cue before every shot (REQ-SAF-012), and log each shot with its time, range, measured speed and gate results.

## 6. ToF and LiDAR sensors and lasers near faces

- **The three candidate sensors**
  - **TF-Luna:** VCSEL emitter, 850 nm, Class 1 (IEC 60825), 2° field of view, ±6 cm accuracy at 0.2–3 m ([datasheet](https://files.waveshare.com/upload/c/c3/SJ-GU-TF-Luna_A05_Datasheet.pdf)).
  - **TFmini-S:** VCSEL emitter, 850 nm, Class 1 (EN 60825), 2° field of view, ±6 cm accuracy at 0.1–6 m ([datasheet](https://files.waveshare.com/upload/2/26/SJ-PM-TFmini-S-01_A01_Datasheet.pdf)).
  - **VL53L1X:** invisible 940 nm Class 1 emitter ([ST](https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html)). ST states compliance with IEC 60825-1:2014 (3rd edition) for the related VL53L1 ([ST](https://www.st.com/en/imaging-and-photonics-solutions/vl53l1.html)); the VL53L1X wording is unverified. Its wide field of view (about 27°, unverified) cannot isolate a face from its surroundings.
- **IEC 60825-1:2014 (edition 3)** is still the current edition. Europe issued a corrigendum in 2025, and a new edition appears to be in draft ([IEC](https://webstore.iec.ch/en/publication/3587)).
- **What Class 1 means here.** It is designed to be eye-safe under reasonably foreseeable conditions, so ranging a face is acceptable *if the module is unmodified*. Do not add lenses, remove the window, or change how the emitter is driven (standard practice; unverified). Infrared triggers no blink reflex, so never use an infrared emitter that is not Class 1.
- **Visible aiming lasers.**
  - The FDA says "never aim or shine a laser directly at any person or animal". Toy lasers should be Class 1, and you should avoid anything over 5 mW or without a label. Eye damage may cause no pain at first, and reflections are hazardous too ([FDA](https://www.fda.gov/consumers/consumer-updates/laser-toys-how-keep-kids-safe)).
  - Class 2 (≤ 1 mW, visible) relies on the blink reflex (unverified).
  - So: no laser on the turret (REQ-SAF-008). Calibrate with a camera overlay or a paper target. If a laser dot is ever needed on the bench, use a labelled Class 1 or Class 2 module, aim it only at a target board, and keep the launcher disarmed.

## Open questions

- What the EN 71-1:2026 projectile clause says, and when it will be cited in the Official Journal. What IS 9873-1:2025 and ISO 8124-1 Amendment 1:2025 change. Whether EN 71-1 bans small-part projectiles for all ages.
- The full Duma 2005 risk curve: the corneal-abrasion probability at 300–600 J/m², and whether rigid pellets abrade at lower energy than foam.
- Real pellet mass and size spread (weigh and measure 30), coating hardness, and whether the coating chips into fragments on impact.
- Anthropometric data for adult mouth-to-eye and mouth-to-nose distances and the held-open mouth gap. The 6–7 cm used here, and the 65 mm in ballistics.md, are unverified.
- The measured shot-to-shot speed SD of the chosen mechanism against battery voltage, temperature and pellet batch, and how much the pillow shape tumbles.
- How consent works for guests in table-service mode, and whether to ask users to wear glasses.
- My web-search budget ran out before I could re-check: the Class 1 and Class 2 visible power limits, the ISO 13850 actuator details, the ASTM F963-23 clause text, and the polyol laxative-warning rule.
