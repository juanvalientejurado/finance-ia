import re
from typing import Dict, List


def parse_expenses(text: str) -> List[Dict[str, str]]:
    """
    Extrae múltiples movimientos desde texto OCR.
    Devuelve una lista de diccionarios con campos: concepto, fecha, importe.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    gastos = []

    i = 0
    while i < len(lines) - 1:
        concepto = lines[i]
        siguiente = lines[i + 1]

        # Buscar fecha e importe en la siguiente línea
        fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", siguiente)
        importe_match = re.search(
            r"([-+]?\d+[.,]\d{2}) ?€?", concepto + " " + siguiente
        )

        if fecha_match and importe_match:
            gasto = {
                "concepto": concepto,
                "fecha": fecha_match.group(1),
                "importe": importe_match.group(1).replace(",", "."),
            }
            gastos.append(gasto)
            i += 2  # Saltar a siguiente par
        else:
            i += 1  # Saltar línea si no encaja

    return gastos
