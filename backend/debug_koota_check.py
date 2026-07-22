"""
Debug script: compute all 8 kootas for the two known test cases
and show exactly where we differ from AstroSage.

AstroSage reference results:
  Case 1 - Suraj(Scorpio/Jyeshtha) + Sonali(Scorpio/Jyeshtha) = 28/36
  Case 2 - Rushikesh(Cancer/Ashlesha) + Aishwarya(Scorpio/Jyeshtha) = 26/36
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from engine.models import Nakshatra, Rashi, Nadi, Gana
from engine.tables import (
    RASHI_TO_VARNA, RASHI_LORD, RASHI_VASHYA_GROUP,
    NAKSHATRA_TO_GANA, NAKSHATRA_TO_NADI, NAKSHATRA_YONI,
    VASHYA_AFFINITY, GRAHA_MAITRI_SCORES,
    get_vashya_score, get_yoni_score, get_graha_maitri_score,
)

TARA_INAUSPICIOUS = {1, 3, 5, 7}

def tara_num(from_nak, to_nak):
    diff = (to_nak.value - from_nak.value) % 27
    t = diff % 9
    return t if t != 0 else 9

def compute_koota(label, bride_rashi, groom_rashi, bride_nak, groom_nak,
                  bride_pada=None, groom_pada=None):
    print(f"\n{'='*60}")
    print(f"  Bride: Rashi={bride_rashi.name}, Nak={bride_nak.name}")
    print(f"  Groom: Rashi={groom_rashi.name}, Nak={groom_nak.name}")
    print(f"{'='*60}")

    # Varna
    bv = RASHI_TO_VARNA[bride_rashi]
    gv = RASHI_TO_VARNA[groom_rashi]
    varna_score = 1 if gv.rank >= bv.rank else 0
    print(f"Varna:       bride={bv.name}({bv.rank}), groom={gv.name}({gv.rank}) → {varna_score}/1")

    # Vasya
    bg = RASHI_VASHYA_GROUP[bride_rashi]
    gg = RASHI_VASHYA_GROUP[groom_rashi]
    v_score = get_vashya_score(bride_rashi, groom_rashi)
    print(f"Vasya:       bride={bg}, groom={gg} → {v_score}/2")
    print(f"  VASHYA_AFFINITY[({bg},{gg})] = {VASHYA_AFFINITY.get((bg,gg), 'NOT IN TABLE → 0')}")
    print(f"  VASHYA_AFFINITY[({gg},{bg})] = {VASHYA_AFFINITY.get((gg,bg), 'NOT IN TABLE → 0')}")

    # Tara
    btg = tara_num(bride_nak, groom_nak)
    gtb = tara_num(groom_nak, bride_nak)
    b2g_ok = btg not in TARA_INAUSPICIOUS
    g2b_ok = gtb not in TARA_INAUSPICIOUS
    if b2g_ok and g2b_ok: t_score = 3.0
    elif b2g_ok or g2b_ok: t_score = 1.5
    else: t_score = 0.0
    print(f"Tara:        bride→groom={btg}({'auspicious' if b2g_ok else 'INAUSPICIOUS'}), "
          f"groom→bride={gtb}({'auspicious' if g2b_ok else 'INAUSPICIOUS'}) → {t_score}/3")

    # Yoni
    y_score = get_yoni_score(bride_nak, groom_nak)
    ba, _ = NAKSHATRA_YONI[bride_nak]
    ga, _ = NAKSHATRA_YONI[groom_nak]
    print(f"Yoni:        bride={ba}, groom={ga} → {y_score}/4")

    # Graha Maitri
    bl = RASHI_LORD[bride_rashi]
    gl = RASHI_LORD[groom_rashi]
    gm_score = get_graha_maitri_score(bride_rashi, groom_rashi)
    gm_b2g = GRAHA_MAITRI_SCORES.get((bl, gl), "N/A")
    gm_g2b = GRAHA_MAITRI_SCORES.get((gl, bl), "N/A")
    print(f"Maitri:      bride_lord={bl.name}, groom_lord={gl.name}")
    print(f"  Score table ({bl.name},{gl.name})={gm_b2g}, ({gl.name},{bl.name})={gm_g2b} → {gm_score}/5")

    # Gana
    bg_g = NAKSHATRA_TO_GANA[bride_nak]
    gg_g = NAKSHATRA_TO_GANA[groom_nak]
    gana_scores = {
        (Gana.DEVA, Gana.DEVA): 6, (Gana.MANUSHYA, Gana.MANUSHYA): 6,
        (Gana.RAKSHASA, Gana.RAKSHASA): 6,
        (Gana.DEVA, Gana.MANUSHYA): 5, (Gana.MANUSHYA, Gana.DEVA): 5,
        (Gana.MANUSHYA, Gana.RAKSHASA): 1, (Gana.RAKSHASA, Gana.MANUSHYA): 0,
        (Gana.DEVA, Gana.RAKSHASA): 0, (Gana.RAKSHASA, Gana.DEVA): 0,
    }
    g_score = gana_scores.get((bg_g, gg_g), 0)
    print(f"Gana:        bride={bg_g.name}, groom={gg_g.name} → {g_score}/6")

    # Bhakoot
    dist_bg = ((groom_rashi.value - bride_rashi.value) % 12) + 1
    dist_gb = ((bride_rashi.value - groom_rashi.value) % 12) + 1
    dosha_pairs = {(2,12),(6,8),(5,9),(12,2),(8,6),(9,5)}
    is_dosha = (dist_bg, dist_gb) in dosha_pairs
    if is_dosha:
        can_cancel = gm_score >= 4
        b_score_current = 7.0 if can_cancel else 0.0
        b_score_nocancer = 0.0
        print(f"Bhakoot:     {dist_bg}/{dist_gb} pair — DOSHA PRESENT (5/9 type: {dist_bg},{dist_gb})")
        print(f"  With cancellation (Maitri≥4): {b_score_current}/7")
        print(f"  Without cancellation (strict): {b_score_nocancer}/7")
    else:
        b_score_current = 7.0
        b_score_nocancer = 7.0
        print(f"Bhakoot:     {dist_bg}/{dist_gb} — No dosha → 7/7")

    # Nadi
    bn = NAKSHATRA_TO_NADI[bride_nak]
    gn = NAKSHATRA_TO_NADI[groom_nak]
    is_nadi_dosha = (bn == gn)
    n_score = 0.0 if is_nadi_dosha else 8.0
    print(f"Nadi:        bride={bn.name}, groom={gn.name} {'DOSHA' if is_nadi_dosha else 'OK'} → {n_score}/8")

    # Totals
    total_with_cancel = sum([varna_score, v_score, t_score, y_score, gm_score, g_score, b_score_current, n_score])
    total_no_cancel   = sum([varna_score, v_score, t_score, y_score, gm_score, g_score, b_score_nocancer, n_score])
    print(f"\n  TOTAL (with Bhakoot cancellation):    {total_with_cancel}/36")
    print(f"  TOTAL (without Bhakoot cancellation): {total_no_cancel}/36")

print("\n" + "="*70)
print("TEST CASE 1: Suraj(Scorpio/Jyeshtha) + Sonali(Scorpio/Jyeshtha)")
print("AstroSage expected: 28/36")
compute_koota("Case1", Rashi.SCORPIO, Rashi.SCORPIO, Nakshatra.JYESHTHA, Nakshatra.JYESHTHA)

print("\n\n" + "="*70)
print("TEST CASE 2: Aishwarya(Scorpio/Jyeshtha) BRIDE + Rushikesh(Cancer/Ashlesha) GROOM")
print("AstroSage expected: 26/36")
compute_koota("Case2", Rashi.SCORPIO, Rashi.CANCER, Nakshatra.JYESHTHA, Nakshatra.ASHLESHA)

print("\n\n--- KEY ISSUES IDENTIFIED ---")
print("Check above output for Vasya and Bhakoot discrepancies vs AstroSage.")
