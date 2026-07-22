"""
Comprehensive exhaustive tests for all 8 Kootas + integration tests.

Strategy:
1. Integration tests  – load AstroSage verified cases (astrosage_fixtures.json)
   and confirm our engine's per-koota AND total scores match.
2. Combinatorial unit tests – enumerate EVERY possible input combination for
   each koota (144 rashi pairs, 729 nakshatra pairs) and verify our engine
   is internally consistent with the validated rules.

Running:
    pytest tests/test_comprehensive.py -v
"""
import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import Nakshatra, Rashi, Nadi, Gana
from engine.tables import (
    RASHI_TO_VARNA, RASHI_LORD, RASHI_VASHYA_GROUP,
    NAKSHATRA_TO_GANA, NAKSHATRA_TO_NADI, NAKSHATRA_YONI,
    VASHYA_AFFINITY, GRAHA_MAITRI_SCORES,
    get_vashya_score, get_yoni_score, get_graha_maitri_score,
)
from engine.matching import (
    _compute_varna, _compute_vashya, _compute_tara, _compute_yoni,
    _compute_graha_maitri, _compute_gana, _compute_bhakoot, _compute_nadi,
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
ALL_RASHIS = list(Rashi)
ALL_NAKSHATRAS = list(Nakshatra)
_TARA_INAUSPICIOUS = {1, 3, 5, 7}

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "astrosage_fixtures.json")


def tara_number(from_nak: Nakshatra, to_nak: Nakshatra) -> int:
    """Reference tara formula (validated against AstroSage)."""
    diff = (to_nak.value - from_nak.value) % 27
    raw = diff % 9
    if raw == 0:
        raw = 9
    tara = raw + 2
    if tara > 9:
        tara -= 9
    return tara


def expected_tara_score(bride_nak: Nakshatra, groom_nak: Nakshatra) -> float:
    btg = tara_number(bride_nak, groom_nak)
    gtb = tara_number(groom_nak, bride_nak)
    b_ok = btg not in _TARA_INAUSPICIOUS
    g_ok = gtb not in _TARA_INAUSPICIOUS
    if b_ok and g_ok:
        return 3.0
    elif b_ok or g_ok:
        return 1.5
    return 0.0


# ──────────────────────────────────────────────────────────────────────────────
# 1. AstroSage integration tests (load from fixture JSON)
# ──────────────────────────────────────────────────────────────────────────────
def load_fixtures():
    with open(FIXTURE_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def astrosage_cases():
    return load_fixtures()


def rashi_by_name(name: str) -> Rashi:
    return next(r for r in Rashi if r.name == name)


def nak_by_name(name: str) -> Nakshatra:
    return next(n for n in Nakshatra if n.name == name)


@pytest.mark.parametrize("case", load_fixtures(), ids=lambda c: c["id"])
def test_astrosage_integration(case):
    """Each AstroSage case must match our engine per-koota AND as a total."""
    boy_rashi = rashi_by_name(case["boy_rashi"])
    girl_rashi = rashi_by_name(case["girl_rashi"])
    boy_nak = nak_by_name(case["boy_nakshatra"])
    girl_nak = nak_by_name(case["girl_nakshatra"])
    ref = case["astrosage_result"]

    # bride = girl, groom = boy (standard convention)
    bride_rashi, groom_rashi = girl_rashi, boy_rashi
    bride_nak, groom_nak = girl_nak, boy_nak

    varna = _compute_varna(bride_rashi, groom_rashi)
    vasya = _compute_vashya(bride_rashi, groom_rashi)
    tara = _compute_tara(bride_nak, groom_nak)
    yoni = _compute_yoni(bride_nak, groom_nak)
    maitri = _compute_graha_maitri(bride_rashi, groom_rashi)
    gana = _compute_gana(bride_nak, groom_nak, graha_maitri_score=maitri.points_earned)
    bhakoot, bhakoot_dosha = _compute_bhakoot(bride_rashi, groom_rashi, graha_maitri_score=maitri.points_earned)
    nadi, nadi_dosha = _compute_nadi(bride_nak, groom_nak, bride_rashi, groom_rashi)

    total = (varna.points_earned + vasya.points_earned + tara.points_earned +
             yoni.points_earned + maitri.points_earned + gana.points_earned +
             bhakoot.points_earned + nadi.points_earned)

    assert varna.points_earned == ref["varna"],   f"[{case['id']}] Varna: got {varna.points_earned}, expected {ref['varna']}"
    assert vasya.points_earned == ref["vasya"],   f"[{case['id']}] Vasya: got {vasya.points_earned}, expected {ref['vasya']}"
    assert tara.points_earned  == ref["tara"],    f"[{case['id']}] Tara: got {tara.points_earned}, expected {ref['tara']}"
    assert yoni.points_earned  == ref["yoni"],    f"[{case['id']}] Yoni: got {yoni.points_earned}, expected {ref['yoni']}"
    assert maitri.points_earned == ref["maitri"], f"[{case['id']}] Maitri: got {maitri.points_earned}, expected {ref['maitri']}"
    assert gana.points_earned  == ref["gana"],    f"[{case['id']}] Gana: got {gana.points_earned}, expected {ref['gana']}"
    assert bhakoot.points_earned == ref["bhakoot"], f"[{case['id']}] Bhakoot: got {bhakoot.points_earned}, expected {ref['bhakoot']}"
    assert nadi.points_earned  == ref["nadi"],    f"[{case['id']}] Nadi: got {nadi.points_earned}, expected {ref['nadi']}"
    assert total == ref["total"], f"[{case['id']}] Total: got {total}, expected {ref['total']}"
    print(f"  [{case['id']}] PASS: {total}/36 (expected {ref['total']})")


# ──────────────────────────────────────────────────────────────────────────────
# 2. Combinatorial: Tara (27x27 = 729 pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_tara_all_combinations():
    """Every nakshatra pair: engine score == reference formula score."""
    mismatches = []
    for bride_nak in ALL_NAKSHATRAS:
        for groom_nak in ALL_NAKSHATRAS:
            expected = expected_tara_score(bride_nak, groom_nak)
            result = _compute_tara(bride_nak, groom_nak)
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_nak.name}+{groom_nak.name}: "
                    f"got {result.points_earned}, expected {expected}"
                )
    assert not mismatches, f"Tara mismatches:\n" + "\n".join(mismatches)
    print(f"  Tara: all 729 nakshatra pairs correct.")


# ──────────────────────────────────────────────────────────────────────────────
# 3. Combinatorial: Vasya (12x12 = 144 rashi pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_vasya_all_combinations():
    """Every rashi pair: Vasya score is 0, 1, or 2 and matches table."""
    mismatches = []
    for bride_rashi in ALL_RASHIS:
        for groom_rashi in ALL_RASHIS:
            bg = RASHI_VASHYA_GROUP[bride_rashi]
            gg = RASHI_VASHYA_GROUP[groom_rashi]
            if bg == gg:
                expected = 2
            else:
                expected = VASHYA_AFFINITY.get((bg, gg), 0)
            result = _compute_vashya(bride_rashi, groom_rashi)
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_rashi.name}({bg})+{groom_rashi.name}({gg}): "
                    f"got {result.points_earned}, expected {expected}"
                )
    assert not mismatches, "Vasya mismatches:\n" + "\n".join(mismatches)
    print(f"  Vasya: all 144 rashi pairs correct.")


# ──────────────────────────────────────────────────────────────────────────────
# 4. Combinatorial: Nadi (27x27 = 729 pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_nadi_all_combinations():
    """Same Nadi → 0 (dosha), different Nadi → 8.
    We pass distinct rashis to avoid triggering same-rashi cancellation.
    """
    mismatches = []
    for bride_nak in ALL_NAKSHATRAS:
        for groom_nak in ALL_NAKSHATRAS:
            bride_nadi = NAKSHATRA_TO_NADI[bride_nak]
            groom_nadi = NAKSHATRA_TO_NADI[groom_nak]
            expected = 0.0 if bride_nadi == groom_nadi else 8.0
            # Pass deliberately distinct rashis and NO padas to avoid cancellation
            # rules 1 and 2 from masking the base dosha logic
            result, dosha = _compute_nadi(
                bride_nak, groom_nak,
                Rashi.ARIES, Rashi.SCORPIO,  # always different rashis
                bride_pada=None, groom_pada=None
            )
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_nak.name}({bride_nadi.name})+{groom_nak.name}({groom_nadi.name}): "
                    f"got {result.points_earned}, expected {expected}"
                )
    assert not mismatches, "Nadi mismatches:\n" + "\n".join(mismatches)
    print(f"  Nadi: all 729 nakshatra pairs correct.")


# ──────────────────────────────────────────────────────────────────────────────
# 5. Combinatorial: Gana (27x27 = 729 pairs)
# ──────────────────────────────────────────────────────────────────────────────
GANA_EXPECTED = {
    (Gana.DEVA, Gana.DEVA): 6,
    (Gana.MANUSHYA, Gana.MANUSHYA): 6,
    (Gana.RAKSHASA, Gana.RAKSHASA): 6,
    (Gana.DEVA, Gana.MANUSHYA): 5,
    (Gana.MANUSHYA, Gana.DEVA): 5,
    (Gana.MANUSHYA, Gana.RAKSHASA): 1,
    (Gana.RAKSHASA, Gana.MANUSHYA): 0,
    (Gana.DEVA, Gana.RAKSHASA): 0,
    (Gana.RAKSHASA, Gana.DEVA): 0,
}


def test_gana_all_combinations():
    """Every nakshatra pair: Gana score follows the 9-entry scoring table."""
    mismatches = []
    for bride_nak in ALL_NAKSHATRAS:
        for groom_nak in ALL_NAKSHATRAS:
            bg = NAKSHATRA_TO_GANA[bride_nak]
            gg = NAKSHATRA_TO_GANA[groom_nak]
            expected = GANA_EXPECTED[(bg, gg)]
            result = _compute_gana(bride_nak, groom_nak, graha_maitri_score=0.0)
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_nak.name}({bg.name})+{groom_nak.name}({gg.name}): "
                    f"got {result.points_earned}, expected {expected}"
                )
    assert not mismatches, "Gana mismatches:\n" + "\n".join(mismatches)
    print(f"  Gana: all 729 nakshatra pairs correct.")


# ──────────────────────────────────────────────────────────────────────────────
# 6. Combinatorial: Bhakoot (12x12 = 144 rashi pairs)
# ──────────────────────────────────────────────────────────────────────────────
BHAKOOT_DOSHA_PAIRS = {(2, 12), (6, 8), (5, 9), (12, 2), (8, 6), (9, 5)}


def test_bhakoot_all_combinations():
    """Every rashi pair: dosha detection correct, no cancellation applied."""
    mismatches = []
    for bride_rashi in ALL_RASHIS:
        for groom_rashi in ALL_RASHIS:
            dist_bg = ((groom_rashi.value - bride_rashi.value) % 12) + 1
            dist_gb = ((bride_rashi.value - groom_rashi.value) % 12) + 1
            is_dosha = (dist_bg, dist_gb) in BHAKOOT_DOSHA_PAIRS
            expected = 0.0 if is_dosha else 7.0
            result, dosha = _compute_bhakoot(bride_rashi, groom_rashi, graha_maitri_score=5.0)
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_rashi.name}+{groom_rashi.name} ({dist_bg}/{dist_gb}): "
                    f"got {result.points_earned}, expected {expected}"
                )
            if dosha.is_cancelled:
                mismatches.append(
                    f"{bride_rashi.name}+{groom_rashi.name}: Bhakoot was cancelled (should never cancel)"
                )
    assert not mismatches, "Bhakoot mismatches:\n" + "\n".join(mismatches)
    print(f"  Bhakoot: all 144 rashi pairs correct (including no-cancel with Maitri=5).")


# ──────────────────────────────────────────────────────────────────────────────
# 7. Combinatorial: Yoni (27x27 = 729 pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_yoni_all_combinations():
    """Every nakshatra pair: Yoni score is 0-4 and is symmetric."""
    mismatches = []
    for bride_nak in ALL_NAKSHATRAS:
        for groom_nak in ALL_NAKSHATRAS:
            score_ab = get_yoni_score(bride_nak, groom_nak)
            score_ba = get_yoni_score(groom_nak, bride_nak)
            # Yoni is symmetric: swapping bride/groom gives same score
            if score_ab != score_ba:
                mismatches.append(
                    f"{bride_nak.name}+{groom_nak.name}: {score_ab} != {score_ba} (not symmetric)"
                )
            if score_ab not in range(5):
                mismatches.append(f"{bride_nak.name}+{groom_nak.name}: score {score_ab} out of range 0-4")
    assert not mismatches, "Yoni mismatches:\n" + "\n".join(mismatches)
    print(f"  Yoni: all 729 pairs in range [0,4] and symmetric.")


# ──────────────────────────────────────────────────────────────────────────────
# 8. Combinatorial: Graha Maitri (12x12 = 144 rashi pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_graha_maitri_all_combinations():
    """Every rashi pair: Maitri score is in {0, 0.5, 1, 3, 4, 5}."""
    VALID_SCORES = {0.0, 0.5, 1.0, 3.0, 4.0, 5.0}
    mismatches = []
    for bride_rashi in ALL_RASHIS:
        for groom_rashi in ALL_RASHIS:
            score = get_graha_maitri_score(bride_rashi, groom_rashi)
            if score not in VALID_SCORES:
                mismatches.append(f"{bride_rashi.name}+{groom_rashi.name}: invalid score {score}")
    assert not mismatches, "Graha Maitri mismatches:\n" + "\n".join(mismatches)
    print(f"  Graha Maitri: all 144 rashi pairs produce valid scores.")


# ──────────────────────────────────────────────────────────────────────────────
# 9. Combinatorial: Varna (12x12 = 144 rashi pairs)
# ──────────────────────────────────────────────────────────────────────────────
def test_varna_all_combinations():
    """Every rashi pair: Varna score is 0 or 1, groom rank >= bride rank → 1."""
    mismatches = []
    for bride_rashi in ALL_RASHIS:
        for groom_rashi in ALL_RASHIS:
            bv = RASHI_TO_VARNA[bride_rashi]
            gv = RASHI_TO_VARNA[groom_rashi]
            expected = 1 if gv.rank >= bv.rank else 0
            result = _compute_varna(bride_rashi, groom_rashi)
            if result.points_earned != expected:
                mismatches.append(
                    f"{bride_rashi.name}({bv.name},{bv.rank})+{groom_rashi.name}({gv.name},{gv.rank}): "
                    f"got {result.points_earned}, expected {expected}"
                )
    assert not mismatches, "Varna mismatches:\n" + "\n".join(mismatches)
    print(f"  Varna: all 144 rashi pairs correct.")


# ──────────────────────────────────────────────────────────────────────────────
# 10. Score range validation: total must be in [0, 36]
# ──────────────────────────────────────────────────────────────────────────────
def test_total_score_always_valid():
    """
    For a representative sample of 100 random rashi+nakshatra combos,
    the total score must always be in [0.0, 36.0].
    Uses deterministic sampling (no random seed needed).
    """
    import itertools
    errors = []
    # Sample: every 3rd nakshatra pair (27//3 = 9 per axis → 81 pairs)
    sample_naks = ALL_NAKSHATRAS[::3]
    sample_rashis = ALL_RASHIS[::2]
    for bride_nak in sample_naks:
        for groom_nak in sample_naks:
            # Derive a plausible rashi from the nakshatra (deterministic)
            bride_rashi = sample_rashis[bride_nak.value % len(sample_rashis)]
            groom_rashi = sample_rashis[groom_nak.value % len(sample_rashis)]
            maitri = _compute_graha_maitri(bride_rashi, groom_rashi)
            total = sum([
                _compute_varna(bride_rashi, groom_rashi).points_earned,
                _compute_vashya(bride_rashi, groom_rashi).points_earned,
                _compute_tara(bride_nak, groom_nak).points_earned,
                _compute_yoni(bride_nak, groom_nak).points_earned,
                maitri.points_earned,
                _compute_gana(bride_nak, groom_nak, maitri.points_earned).points_earned,
                _compute_bhakoot(bride_rashi, groom_rashi, maitri.points_earned)[0].points_earned,
                _compute_nadi(bride_nak, groom_nak, bride_rashi, groom_rashi)[0].points_earned,
            ])
            if not (0.0 <= total <= 36.0):
                errors.append(f"Total {total} out of range for {bride_nak.name}/{bride_rashi.name} + {groom_nak.name}/{groom_rashi.name}")
    assert not errors, "\n".join(errors)
    print(f"  Score range: all sampled pairs produce totals in [0, 36].")


# ──────────────────────────────────────────────────────────────────────────────
# Quick standalone run
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running exhaustive combinatorial tests...\n")
    test_astrosage_integration(load_fixtures()[0])
    test_astrosage_integration(load_fixtures()[1])
    test_astrosage_integration(load_fixtures()[2])
    test_tara_all_combinations()
    test_vasya_all_combinations()
    test_nadi_all_combinations()
    test_gana_all_combinations()
    test_bhakoot_all_combinations()
    test_yoni_all_combinations()
    test_graha_maitri_all_combinations()
    test_varna_all_combinations()
    test_total_score_always_valid()
    print("\nAll tests passed!")
