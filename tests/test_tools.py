from src.tools.calculator import calculate
def test_calc():
    assert calculate("2+2")=="4"
    assert "error" in calculate("1/0") or "Zero" in calculate("1/0")
