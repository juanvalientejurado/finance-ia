import os
from pathlib import Path

import pytesseract
from PIL import Image

# Ruta a Tesseract instalada en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Asegurar que el path a tessdata esté configurado
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


def extract_text_from_image(image_path: str) -> str:
    """
    Extrae texto desde una imagen usando OCR (Tesseract).
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")

    image = Image.open(image_path)
    text = pytesseract.image_to_string(
        image, lang="spa"
    )  # También puedes probar con 'eng' o 'spa+eng'
    return text.strip()
