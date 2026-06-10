def normalize_result(result: str) -> str:
    text = str(result).strip().lower()
    if text in {"miss", "agua", "water"}:
        return "agua"
    if text in {"hit", "acerto"}:
        return "acerto"
    if text in {"sunk", "afundado"}:
        return "afundado"
    if "repetido" in text:
        return "tiro repetido"
    return text
