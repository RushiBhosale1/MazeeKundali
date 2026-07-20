"""Quick ephemeris smoke test"""
import swisseph as swe

swe.set_ephe_path('./static/ephemeris')
swe.set_sid_mode(1)  # Lahiri

# June 15 1990, 10:30 IST = 05:00 UTC
jd = swe.julday(1990, 6, 15, 5.0)
ayanamsa = swe.get_ayanamsa_ut(jd)
print(f"Ayanamsa (Lahiri): {ayanamsa:.4f}")

xx, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
moon_tropical = xx[0]
moon_sidereal = (moon_tropical - ayanamsa) % 360
rashi_idx = int(moon_sidereal / 30)
nak_idx = int(moon_sidereal / (360/27))

rashis = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
naks = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha',
        'Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha',
        'Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha',
        'Purva Bhadrapada','Uttara Bhadrapada','Revati']

print(f"Moon tropical: {moon_tropical:.4f} deg")
print(f"Moon sidereal: {moon_sidereal:.4f} deg")
print(f"Rashi: {rashis[rashi_idx]} (index {rashi_idx})")
print(f"Nakshatra: {naks[nak_idx]} (index {nak_idx})")

# Ascendant
houses, ascmc = swe.houses(jd, 18.5204, 73.8567, b'W')
lagna_trop = ascmc[0]
lagna_sid = (lagna_trop - ayanamsa) % 360
lagna_idx = int(lagna_sid / 30)
print(f"Lagna sidereal: {lagna_sid:.4f} deg -> {rashis[lagna_idx]}")

print("\nEphemeris smoke test PASSED")
