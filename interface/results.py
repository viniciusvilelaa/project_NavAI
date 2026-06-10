def normalize_result(result: str) -> str:
    text = str(result).strip().lower()
    if text in {"miss", "agua", "water"}:
        return "agua"
    if text in {"hit", "acerto"}:
        return "acerto"
    if text in {"sunk", "afundado"}:
        return "afundado"
    if text in {"repeated", "tiro repetido"} or "repetido" in text:
        return "tiro repetido"
    return text


def display_result(result: str) -> str:
    labels = {
        "agua": "água",
        "acerto": "acerto",
        "afundado": "afundado",
        "tiro repetido": "tiro repetido",
    }
    return labels.get(str(result).strip().lower(), str(result))
