from angel_one_mcp.server import normalize_gainers_losers_request


def test_normalizes_legacy_price_mover_aliases():
    assert normalize_gainers_losers_request("PercGainers", "NEAR") == {
        "datatype": "PercPriceGainers",
        "expirytype": "NEAR",
    }
    assert normalize_gainers_losers_request("PercLosers", "NEXT") == {
        "datatype": "PercPriceLosers",
        "expirytype": "NEXT",
    }


def test_accepts_documented_datatypes_and_rejects_unknown_values():
    assert normalize_gainers_losers_request("PercOIGainers", "FAR")["datatype"] == "PercOIGainers"
    try:
        normalize_gainers_losers_request("not-valid", "NEAR")
    except ValueError as exc:
        assert "PercPriceGainers" in str(exc)
    else:
        raise AssertionError("invalid datatype should be rejected")
