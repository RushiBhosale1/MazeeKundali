"""
Cross-Validation Test Suite for MazeeKundali Engine
=====================================================
Compares our engine output against known reference data from AstroSage.com.

Reference Case 1: Rushikesh + Priti  (verified by user against AstroSage screenshots)
  Boy: Rushikesh, 8 Mar 2002, 10:00 AM, Satara (17N40, 73E58)
  Girl: Priti,    24 Mar 2004, 2:00 PM,  Pune   (18N31, 73E51)

  AstroSage Expected:
    Total Score:    19/36
    Varna:          Kshatriya + Kshatriya  = 1/1
    Vasya:          Chatushpada+Chatushpada = 2/2
    Tara:           PurvaAshadha+Bharani    = 3/3
    Yoni:           Monkey+Elephant         = 2/4
    Graha Maitri:   Jupiter+Mars            = 5/5
    Gana:           Manushya+Manushya       = 6/6
    Bhakoot:        Sagittarius+Aries       = 0/7
    Nadi:           Madhya+Madhya           = 0/8
    Rushikesh Mangal Dosha: Low (MILD)
    Priti Mangal Dosha:     None

Run from backend/:
    python validation/cross_check.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.matching import compute_match
from engine.models import KundaliResult, Nakshatra, Rashi, Planet
from engine.mangal_dosha import compute_mangal_dosha, MANGAL_DOSHA_HOUSES

# ── colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"; RESET = "\033[0m"
PASS_S = GREEN  + "PASS" + RESET
FAIL_S = RED    + "FAIL" + RESET
WARN_S = YELLOW + "WARN" + RESET

pass_count = fail_count = 0


def check(label, got, expected, tol=0.0):
    global pass_count, fail_count
    if isinstance(expected, float) or isinstance(got, float):
        ok = abs(float(got) - float(expected)) <= tol
    else:
        ok = (got == expected)
    tag = PASS_S if ok else FAIL_S
    if ok:
        pass_count += 1
    else:
        fail_count += 1
    print("  [{tag}]  {label}:  got={got!r}  expected={expected!r}".format(
        tag=tag, label=label, got=got, expected=expected))


class PP:
    def __init__(self, p, r, lon=0.0, retro=False):
        self.planet = p; self.rashi = r
        self.longitude = lon; self.retrograde = retro


def make_kundali(nakshatra, rashi, planets=None, lagna=None):
    k = KundaliResult.__new__(KundaliResult)
    k.nakshatra          = nakshatra
    k.rashi              = rashi
    k.nakshatra_pada     = 2
    k.lagna              = lagna
    k.planet_positions   = planets or []
    k.navamsa_positions  = []
    k.mangal_dosha       = None
    k.d1_svg             = None
    k.d9_svg             = None
    return k


# ═════════════════════════════════════════════════════════════════════════════
# CASE 1 — Ashtakoot Koota Scores (source: AstroSage screenshots)
# ═════════════════════════════════════════════════════════════════════════════
print("=" * 68)
print("CASE 1 — Ashtakoot Koota Scores  (Reference: AstroSage.com)")
print("=" * 68)

# Known from AstroSage Guna Milan table in screenshot:
#   Boy  (Groom)  Moon = Sagittarius, Nakshatra = Purva Ashadha  (pada 2)
#   Girl (Bride)  Moon = Aries,       Nakshatra = Bharani         (pada 2)
#
# IMPORTANT: compute_match(bride_kundali, groom_kundali) — bride FIRST
#   This matches the router: compute_ashtakoot(bride_result, groom_result)
rushi = make_kundali(Nakshatra.PURVA_ASHADHA, Rashi.SAGITTARIUS, lagna=Rashi.CANCER)  # groom
priti = make_kundali(Nakshatra.BHARANI,       Rashi.ARIES,       lagna=Rashi.LEO)     # bride

try:
    res = compute_match(priti, rushi)   # bride=priti, groom=rushi
    print()
    print("  [ Scores ]")
    check("Total Score  (max 36)", res.total_score,              19.0, tol=0.1)
    check("Varna        (max  1)", res.varna.points_earned,       1.0)
    check("Vasya        (max  2)", res.vashya.points_earned,      2.0)
    check("Tara         (max  3)", res.tara.points_earned,        3.0, tol=0.1)
    check("Yoni         (max  4)", res.yoni.points_earned,        2.0)
    check("Graha Maitri (max  5)", res.graha_maitri.points_earned,5.0)
    check("Gana         (max  6)", res.gana.points_earned,        6.0)
    check("Bhakoot      (max  7)", res.bhakoot.points_earned,     0.0)
    check("Nadi         (max  8)", res.nadi.points_earned,        0.0)

    print()
    print("  [ Boy (Rushikesh / Groom) traits — from boy_trait field ]")
    # Traits are stored in Marathi by the engine
    check("Varna  boy  (Kshatriya)",  res.varna.boy_trait,        "क्षत्रिय")
    check("Yoni   boy  (Monkey)",     res.yoni.boy_trait.lower(), "monkey")   # Purva Ashadha = Monkey
    check("Gana   boy  (Manushya)",   res.gana.boy_trait,         "मनुष्य")
    check("Nadi   boy  (Madhya)",     res.nadi.boy_trait,         "मध्य")

    print()
    print("  [ Girl (Priti / Bride) traits — from girl_trait field ]")
    check("Varna  girl (Kshatriya)",  res.varna.girl_trait,       "क्षत्रिय")
    check("Yoni   girl (Elephant)",   res.yoni.girl_trait.lower(),"elephant")  # Bharani = Elephant
    check("Gana   girl (Manushya)",   res.gana.girl_trait,        "मनुष्य")
    check("Nadi   girl (Madhya)",     res.nadi.girl_trait,        "मध्य")

    print()
    print("  [ Doshas ]")
    nd = res.nadi_dosha
    if nd:
        check("Nadi Dosha present",    nd.is_present,   True)
        check("Nadi Dosha NOT cancelled", nd.is_cancelled, False)
    bk = res.bhakoot_dosha
    if bk:
        check("Bhakoot Dosha present", bk.is_present,   True)
        # Sagittarius-Aries is a 5/9 pair; Graha Maitri 5/5 cancels it per standard rule
        check("Bhakoot Dosha cancelled", bk.is_cancelled, True)

except Exception as e:
    import traceback
    print("  [" + FAIL_S + "]  compute_match CRASHED: " + str(e))
    traceback.print_exc()
    fail_count += 1

# ═════════════════════════════════════════════════════════════════════════════
# CASE 2 — Mangal Dosha logic  (planet positions from 2002/2004 ephemeris)
# ═════════════════════════════════════════════════════════════════════════════
print()
print("=" * 68)
print("CASE 2 — Mangal Dosha  (Reference: AstroSage.com)")
print("=" * 68)
print()

# Approximate planet positions inferred from AstroSage output + standard ephemeris:
#   Rushikesh (Mar 2002): Mars ~ Pisces, Moon=Sagittarius, Lagna=Cancer
#     Jupiter in Gemini (sidereal 2002): mars_from_jup=((11-2)%12)+1=10, not in {5,7,9} -> no cancel
#     Mars(Pisces=11) from Moon(Sagittarius=8): house 4 -> DOSHA  (4 in {1,4,7,8,12})
#     Mars(Pisces=11) from Lagna(Cancer=3):     house 9 -> no dosha
#   -> Expected: Low Mangal Dosha (1 reference = MILD)

rushi_planets = [
    PP(Planet.MARS,    Rashi.PISCES),
    PP(Planet.MOON,    Rashi.SAGITTARIUS),
    PP(Planet.VENUS,   Rashi.CAPRICORN),
    PP(Planet.JUPITER, Rashi.GEMINI),
    PP(Planet.SUN,     Rashi.AQUARIUS),
    PP(Planet.SATURN,  Rashi.TAURUS),
    PP(Planet.MERCURY, Rashi.PISCES),
]

print("  Rushikesh: Lagna=Cancer, Moon=Sagittarius, Mars=Pisces")
print("  Reference: AstroSage = 'Low Mangal Dosha'")
r_md = compute_mangal_dosha(rushi_planets, lagna_rashi=Rashi.CANCER)
check("Rushikesh is_manglik", r_md.is_manglik, True)
check("Rushikesh severity",   r_md.severity,   "MILD")
check("Rushikesh triggered from Moon", "Moon" in r_md.reference_point, True)
print("  Detail:", r_md.explanation_en[:110])

print()

#   Priti (Mar 2004): Mars ~ Taurus, Moon=Aries, Lagna~Leo
#     Mars(Taurus=1) from Moon(Aries=0): house 2 -> NOT in {1,4,7,8,12} -> no dosha
#     Mars(Taurus=1) from Lagna(Leo=4):  house ((1-4+12)%12)+1=10 -> no dosha
#   -> Expected: No Mangal Dosha

priti_planets = [
    PP(Planet.MARS,    Rashi.TAURUS),
    PP(Planet.MOON,    Rashi.ARIES),
    PP(Planet.VENUS,   Rashi.ARIES),
    PP(Planet.JUPITER, Rashi.LEO),
    PP(Planet.SUN,     Rashi.PISCES),
    PP(Planet.SATURN,  Rashi.GEMINI),
    PP(Planet.MERCURY, Rashi.AQUARIUS),
]

print("  Priti: Lagna=Leo, Moon=Aries, Mars=Taurus")
print("  Reference: AstroSage = 'No Mangal Dosha'")
p_md = compute_mangal_dosha(priti_planets, lagna_rashi=Rashi.LEO)
check("Priti is_manglik", p_md.is_manglik, False)
check("Priti severity",   p_md.severity,   "NONE")
print("  Detail:", p_md.explanation_en[:110])

# ═════════════════════════════════════════════════════════════════════════════
# CASE 3 — Classic Ashtakoot table spot-checks
# ═════════════════════════════════════════════════════════════════════════════
print()
print("=" * 68)
print("CASE 3 — Classic Ashtakoot Table Spot-Checks")
print("=" * 68)
print()

classic_cases = [
    # ( boy_nak, girl_nak, boy_rashi, girl_rashi, expected_nadi, expected_gana, description )
    (Nakshatra.ASHWINI,   Nakshatra.ARDRA,    Rashi.ARIES,  Rashi.GEMINI,
     {"nadi": 0.0, "nadi_dosha_present": True},
     "Same Nadi (Adi+Adi) -> 0 Nadi + Nadi Dosha"),

    (Nakshatra.ASHWINI,   Nakshatra.PUSHYA,   Rashi.ARIES,  Rashi.CANCER,
     {"nadi": 8.0, "nadi_dosha_present": False},
     "Different Nadi (Adi vs Madhya) -> 8/8"),

    (Nakshatra.ROHINI,    Nakshatra.ROHINI,   Rashi.TAURUS, Rashi.TAURUS,
     {"nadi": 0.0, "nadi_dosha_present": True},
     "Same Nakshatra (Rohini+Rohini) -> Nadi Dosha"),

    (Nakshatra.ASHWINI,   Nakshatra.HASTA,    Rashi.ARIES,  Rashi.VIRGO,
     {"gana": 6.0},
     "Deva+Deva Gana (Ashwini+Hasta) -> 6/6"),

    (Nakshatra.ASHWINI,   Nakshatra.BHARANI,  Rashi.ARIES,  Rashi.ARIES,
     {"bhakoot": 7.0, "varna": 1.0},
     "Same Rashi (Aries+Aries) -> Bhakoot 7/7, Varna 1/1"),
]

for boy_nak, girl_nak, boy_rashi, girl_rashi, expected_map, desc in classic_cases:
    bk = make_kundali(boy_nak, boy_rashi)
    gk = make_kundali(girl_nak, girl_rashi)
    try:
        r = compute_match(bk, gk)
        print("  Case: " + desc)
        for key, exp in expected_map.items():
            if key == "nadi_dosha_present":
                got = r.nadi_dosha.is_present if r.nadi_dosha else None
                check("    nadi_dosha.is_present", got, exp)
            elif key == "bhakoot_dosha_present":
                got = r.bhakoot_dosha.is_present if r.bhakoot_dosha else None
                check("    bhakoot_dosha.is_present", got, exp)
            else:
                got = getattr(r, key).points_earned
                check("    " + key, got, exp, tol=0.1)
        print()
    except Exception as e:
        print("  [" + FAIL_S + "]  CRASHED for: " + desc + "  error=" + str(e))
        fail_count += 1
        print()

# ═════════════════════════════════════════════════════════════════════════════
# CASE 4 — Configuration sanity checks
# ═════════════════════════════════════════════════════════════════════════════
print("=" * 68)
print("CASE 4 — Configuration Sanity Checks")
print("=" * 68)
print()
check("MANGAL_DOSHA_HOUSES = {1,4,7,8,12}",   MANGAL_DOSHA_HOUSES, {1,4,7,8,12})
check("2nd house NOT in dosha set",             2 not in MANGAL_DOSHA_HOUSES, True)
check("7th house IN dosha set",                 7 in MANGAL_DOSHA_HOUSES, True)
check("8th house IN dosha set",                 8 in MANGAL_DOSHA_HOUSES, True)
check("12th house IN dosha set",               12 in MANGAL_DOSHA_HOUSES, True)

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
total = pass_count + fail_count
print()
print("=" * 68)
print("RESULT: {p}/{t} PASSED  ({f} FAILED)".format(
    p=pass_count, t=total, f=fail_count))
if fail_count == 0:
    print(GREEN + "  ALL TESTS PASS — Engine matches AstroSage reference data" + RESET)
else:
    print(RED + "  " + str(fail_count) + " TESTS FAILED — review above" + RESET)
print("=" * 68)
