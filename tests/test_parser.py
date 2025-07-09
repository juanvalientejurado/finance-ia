from app.ocr.image_reader import extract_text_from_image
from app.ocr.pdf_reader import extract_text_from_pdf
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks


def test_pdf_parser_ok():
    texto = extract_text_from_pdf("data/extractDocument_20250704.pdf")
    gastos = parse_vertical_blocks(texto)

    assert isinstance(gastos, list)
    assert len(gastos) > 0

    # Ejemplo de gasto esperado
    ejemplo = gastos[0]
    assert "concepto" in ejemplo
    assert "fecha" in ejemplo
    assert "importe" in ejemplo
    assert "saldo" in ejemplo

    # Verificar valores esperados (puedes ajustar según lo que da tu OCR)
    assert ejemplo["concepto"].lower() in texto[0].lower()


def test_image_parser_ok():
    texto = extract_text_from_image("data/example.jpg")
    gastos = parse_expenses(texto)

    assert isinstance(gastos, list)
    assert len(gastos) > 0

    # Validar estructura
    for gasto in gastos:
        assert "concepto" in gasto
        assert "fecha" in gasto
        assert "importe" in gasto
        assert "saldo" in gasto

    # Validar un gasto específico
    cafet = [g for g in gastos if "CAFET" in g["concepto"].upper()]
    assert cafet, "No se encontró el gasto de CAFET"
    assert cafet[0]["importe"] == "-1.50"
    assert cafet[0]["fecha"] == "02/07/2025"
    assert float(cafet[0]["saldo"]) > 1000
