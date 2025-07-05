from app.ocr.pdf_reader import extract_text_from_pdf
from app.ocr.image_reader import extract_text_from_image
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks
from app.utils.text import normalize_ocr_output
from app.utils.preprocess_image import preprocess_image_grays_to_black

# OCR desde imagen
preprocessed_image = preprocess_image_grays_to_black("data/example.jpg")
texto = extract_text_from_image(preprocessed_image)
norm_text = normalize_ocr_output(texto)
gastos = parse_expenses(norm_text)

print("Gastos extraídos:", gastos)

# OCR desde PDF
texto_pdf = extract_text_from_pdf("data/extractDocument_20250704.pdf")
norm_text = normalize_ocr_output(texto_pdf)
gastos_pdf = parse_vertical_blocks(norm_text)

print("Gastos extraídos:", gastos_pdf)

