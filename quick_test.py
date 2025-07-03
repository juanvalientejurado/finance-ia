from app.ocr.reader import extract_text_from_image
from app.parser.parser import parse_expense

texto = extract_text_from_image("data/example.jpg")
print("Texto OCR:", texto)

gasto = parse_expense(texto)
print("Gasto estructurado:", gasto)