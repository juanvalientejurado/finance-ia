import re
from typing import Optional, Dict


def parse_expense(text: str) -> Optional[Dict[str, str]]:
    """
    Extrae importe, fecha y concepto desde un texto OCR.
    Retorna un diccionario con los campos o None si no encuentra datos.
    """
    # Buscar importe tipo 12,34 o 12.34
    importe_match = re.search(r"(\d+[.,]\d{2})", text)
    importe = importe_match.group(1).replace(",", ".") if importe_match else None

    # Buscar fecha en formato DD/MM/YYYY o similar
    fecha_match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", text)
    fecha = fecha_match.group(1) if fecha_match else None

    # Concepto: línea más larga del texto que no contenga el importe ni fecha
    lineas = [l.strip() for l in text.splitlines() if l.strip()]
    concepto = max(
        (l for l in lineas if (importe not in l if importe else True) and (fecha not in l if fecha else True)),
        key=len,
        default=None
    )

    if not any([importe, fecha, concepto]):
        return None

    return {
        "importe": importe,
        "fecha": fecha,
        "concepto": concepto,
    }
