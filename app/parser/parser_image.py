import re
from typing import List, Dict


def parse_expenses(text: str) -> List[Dict[str, str]]:
    """
    Parser para OCR de imágenes tipo ImaginBank.
    Línea 1: concepto + importe
    Línea 2: fecha + saldo
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    gastos = []

    i = 0
    while i < len(lines) - 1:
        linea_concepto = lines[i]
        linea_datos = lines[i + 1]

        # Buscar fecha y saldo en línea_datos
        fecha_match = re.search(r"\d{2}/\d{2}/\d{4}", linea_datos)
        saldo_match = re.search(r"\d{1,3}(?:[.,]\d{3})*[.,]\d{2}", linea_datos)

        # Buscar importe en la línea del concepto
        importe_match = re.search(r"[-+]?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}", linea_concepto)

        if fecha_match and importe_match and saldo_match:
            concepto = re.sub(r"[-+]?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}", "", linea_concepto).strip()
            gastos.append({
                "concepto": concepto,
                "fecha": fecha_match.group(0),
                "importe": importe_match.group(0).replace(".", "").replace(",", "."),
                "saldo": saldo_match.group(0).replace(".", "").replace(",", ".")
            })
            i += 2
        else:
            i += 1

    return gastos
