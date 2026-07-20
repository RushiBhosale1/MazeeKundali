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
    # Aries and Scorpio are 6/8. But lord of both is Mars.
    koota, dosha = _compute_bhakoot(Rashi.ARIES, Rashi.SCORPIO, graha_maitri_score=4)
    assert dosha.is_present == True, "Bhakoot dosha should be present (6/8)"
    assert dosha.is_cancelled == True, "Bhakoot dosha should be cancelled (Same Lord: Mars)"
    assert koota.points_earned == 7.0, "Should get full points"
    print("test_bhakoot_cancellation PASSED")

def test_gana_cancellation():
    # Deva and Rakshasa is 0 points. But if Graha maitri is 5, it should cancel.
    koota = _compute_gana(Nakshatra.ASHWINI, Nakshatra.KRITTIKA, graha_maitri_score=5)
    assert koota.points_earned == 6.0, "Gana dosha should be cancelled and get full points"
    print("test_gana_cancellation PASSED")

if __name__ == "__main__":
    test_nadi_dosha_pada_cancellation()
    test_bhakoot_cancellation()
    test_gana_cancellation()
    print("ALL TESTS PASSED!")
