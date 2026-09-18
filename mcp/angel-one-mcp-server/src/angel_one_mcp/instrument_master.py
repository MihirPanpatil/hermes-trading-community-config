"""Instrument-master normalization and conservative index selection."""

from typing import Any


def normalize_instrument(row: dict[str, Any]) -> dict[str, str]:
    exchange = str(row.get("exch_seg") or row.get("exchange") or "").upper()
    symbol = str(row.get("symbol") or row.get("tradingsymbol") or "")
    name = str(row.get("name") or symbol)
    token = str(row.get("token") or row.get("symboltoken") or "")
    return {"exchange": exchange, "tradingsymbol": symbol, "symboltoken": token, "name": name}


def choose_index(rows: list[dict[str, str]], index_name: str) -> dict[str, str] | None:
    wanted = index_name.upper().replace(" ", "")
    candidates = []
    for row in rows:
        symbol = row["tradingsymbol"].upper().replace(" ", "")
        name = row["name"].upper().replace(" ", "")
        if wanted not in symbol and wanted not in name:
            continue
        # Equity instruments are not indices; reject common equity suffixes.
        if symbol.endswith(("-EQ", "-BE", "-BL", "-AF", "-RL", "-IQ")):
            continue
        candidates.append(row)
    exact = [r for r in candidates if r["name"].upper().replace(" ", "") == wanted]
    if len(exact) == 1:
        return exact[0]
    if len(candidates) == 1:
        return candidates[0]
    return None
