from app.ocr.reader import extract_text_from_image
from app.parser.parser import parse_expenses

texto = extract_text_from_image("data/example.jpg")
print("Texto OCR:", texto)

gastos = parse_expenses(texto)
print("Gasto estructurado:", gastos)