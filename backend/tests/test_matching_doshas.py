import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import Nakshatra, Rashi
from engine.matching import _compute_nadi, _compute_bhakoot, _compute_gana

def test_nadi_dosha_pada_cancellation():
    # Same nakshatra (Ashwini), different padas (1 and 2). Both are Aries.
    koota, dosha = _compute_nadi(Nakshatra.ASHWINI, Nakshatra.ASHWINI, Rashi.ARIES, Rashi.ARIES, bride_pada=1, groom_pada=2)
    assert dosha.is_present == True, "Nadi dosha should be present"
    assert dosha.is_cancelled == True, "Nadi dosha should be cancelled because of different padas"
    assert koota.points_earned == 8.0, "Should get full points"
    print("test_nadi_dosha_pada_cancellation PASSED")

def test_bhakoot_cancellation():
    # Aries and Scorpio are 6/8. Even though both lords are Mars (same lord),
    # Bhakoot dosha is NOT cancelled in standard implementations (AstroSage behavior).
    koota, dosha = _compute_bhakoot(Rashi.ARIES, Rashi.SCORPIO, graha_maitri_score=4)
    assert dosha.is_present == True, "Bhakoot dosha should be present (6/8)"
    assert dosha.is_cancelled == False, "Bhakoot dosha should NOT be cancelled (strict mode, matches AstroSage)"
    assert koota.points_earned == 0.0, "Should get 0 points for Bhakoot dosha"
    print("test_bhakoot_cancellation PASSED")

def test_gana_cancellation():
    # Deva and Rakshasa is 0 points. Even with Graha maitri=5, AstroSage does NOT cancel Gana Dosha.
    # Case 3 (Sujata/Suraj): Devta+Rakshas, Maitri=5 (Mercury+Venus) → Gana=0, NOT 6.
    koota = _compute_gana(Nakshatra.ASHWINI, Nakshatra.KRITTIKA, graha_maitri_score=5)
    assert koota.points_earned == 0.0, "Gana dosha should NOT be cancelled (matches AstroSage behavior)"
    print("test_gana_cancellation PASSED")

if __name__ == "__main__":
    test_nadi_dosha_pada_cancellation()
    test_bhakoot_cancellation()
    test_gana_cancellation()
    print("ALL TESTS PASSED!")
