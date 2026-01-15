
from app import format_korean_currency

def test_currency():
    print("Testing Currency Formatting...")
    # Exact matches
    assert format_korean_currency(5000) == "5,000", f"Got {format_korean_currency(5000)}"
    assert format_korean_currency(10000) == "1만", f"Got {format_korean_currency(10000)}"
    assert format_korean_currency(15000) == "1.5만", f"Got {format_korean_currency(15000)}"
    assert format_korean_currency(25000000) == "2,500만", f"Got {format_korean_currency(25000000)}"
    assert format_korean_currency(350000000) == "3.5억", f"Got {format_korean_currency(350000000)}"
    print("✅ Currency Tests Passed")

if __name__ == "__main__":
    try:
        test_currency()
        print("🎉 ALL TESTS PASSED")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        exit(1)
