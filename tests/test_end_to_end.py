import os

from app.ocr.reader import extract_text_from_image
from app.parser.parser import parse_expenses


def test_ocr_and_parse_with_real_image():
    # Asegurar rutas de Tesseract en entorno Windows
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

    # OCR desde imagen real
    text = extract_text_from_image("data\\example.jpg")
    gastos = parse_expenses(text)

    assert isinstance(gastos, list)
    assert len(gastos) > 0
    assert all("concepto" in g for g in gastos)
    assert all("fecha" in g for g in gastos)
    assert all("importe" in g for g in gastos)
