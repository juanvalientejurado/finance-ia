from app.ocr.image_reader import extract_text_from_image
from app.ocr.pdf_reader import extract_text_from_pdf
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks
from app.utils.preprocess_image import preprocess_image_grays_to_black
from app.utils.text import normalize_ocr_output

# OCR desde imagen
preprocessed_image = preprocess_image_grays_to_black("data/example.jpg")
texto = extract_text_from_image(preprocessed_image)
norm_text = normalize_ocr_output(texto)
gastos = parse_expenses(norm_text)

import pprint

pprint.pprint(gastos)

# OCR desde PDF
texto_pdf = extract_text_from_pdf("data/extractDocument_20250704.pdf")
norm_text = normalize_ocr_output(texto_pdf)
gastos_pdf = parse_vertical_blocks(norm_text)

pprint.pprint(gastos_pdf)
