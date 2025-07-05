from pdf2image import convert_from_path
from pathlib import Path
import pytesseract
from typing import List
import os

# Ruta a Tesseract instalada en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Asegurar que el path a tessdata esté configurado
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

def extract_text_from_pdf(pdf_path: str, lang: str = "spa") -> List[str]:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")

    # Convertir páginas a imágenes
    images = convert_from_path(pdf_path)

    # Extraer texto con OCR página por página
    extracted_text = []
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image, lang=lang)
        extracted_text.append(text)

    return extracted_text
