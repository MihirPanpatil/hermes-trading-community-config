from angel_one_mcp.instrument_master import choose_index, normalize_instrument


def test_normalize_instrument_maps_master_fields():
    row = normalize_instrument({
        "exch_seg": "NSE",
        "instrumenttype": "AMXIDX",
        "name": "NIFTY",
        "symbol": "NIFTY",
        "token": "999",
    })
    assert row == {"exchange": "NSE", "tradingsymbol": "NIFTY", "symboltoken": "999", "name": "NIFTY"}


def test_choose_index_prefers_exact_name_and_index_segment():
    rows = [
        {"exchange": "NSE", "tradingsymbol": "NIFTY1-EQ", "symboltoken": "1", "name": "NIFTY1"},
        {"exchange": "NSE", "tradingsymbol": "Nifty 50", "symboltoken": "999", "name": "NIFTY"},
    ]
    assert choose_index(rows, "NIFTY") == rows[1]


def test_choose_index_returns_none_for_ambiguous_stock_results():
    rows = [
        {"exchange": "NSE", "tradingsymbol": "NIFTY-EQ", "symboltoken": "1", "name": "NIFTY"},
    ]
    assert choose_index(rows, "NIFTY") is None
