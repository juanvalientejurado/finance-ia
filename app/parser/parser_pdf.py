from typing import List, Dict

def parse_vertical_blocks(text: str | list[str]) -> List[Dict[str, str]]:
    import re
    if isinstance(text, list):
        text = "\n".join(text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    conceptos, fechas, importes, saldos = [], [], [], []

    sec = None
    for line in lines:
        if "Concepto" in line:
            sec = "concepto"
            continue
        elif "Fecha" in line:
            sec = "fecha"
            continue
        elif "Importe" in line:
            sec = "importe"
            continue
        elif "Saldo" in line:
            sec = "saldo"
            continue

        if sec == "concepto":
            conceptos.append(line)
        elif sec == "fecha":
            fechas.append(line)
        elif sec == "importe":
            m = re.search(r"[-+]?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}", line)
            if m:
                raw = m.group(0).replace(".", "").replace(",", ".")
                importes.append(raw)
        elif sec == "saldo":
            m = re.search(r"\d{1,3}(?:[.,]\d{3})*[.,]\d{2}", line)
            if m:
                raw = m.group(0).replace(".", "").replace(",", ".")
                saldos.append(raw)

    gastos = []
    for concepto, fecha, importe, saldo in zip(conceptos, fechas, importes, saldos):
        gastos.append({
            "concepto": concepto,
            "fecha": fecha,
            "importe": importe,
            "saldo": saldo
        })

    return gastos
