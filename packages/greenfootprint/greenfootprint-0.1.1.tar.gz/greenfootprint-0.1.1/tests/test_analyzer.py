# tests/test_analyzer.py

from greenpy.analyzer import estimate_energy

def test_energy_calc():
    assert round(estimate_energy(3600), 2) == 15.00  # 1 hour = 15 watt-hours
