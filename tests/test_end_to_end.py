import os

from app.ocr.image_reader import extract_text_from_image
from app.parser.parser_image import parse_expenses


def test_ocr_and_parse_with_real_image():
    # Asegurar rutas de Tesseract en entorno macOS
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
    os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/Cellar/tesseract/5.5.2/share/tessdata"

    # OCR desde imagen real
    text = extract_text_from_image("data/example.jpg")

    gastos = parse_expenses(text)

    assert isinstance(gastos, list)
    assert len(gastos) > 0
    assert all("concepto" in g for g in gastos)
    assert all("fecha" in g for g in gastos)
    assert all("importe" in g for g in gastos)
