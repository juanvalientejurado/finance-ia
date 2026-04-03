import os
from pathlib import Path

import pytesseract
from PIL import Image

# Ruta a Tesseract instalada en macOS (usando Homebrew)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Asegurar que el path a tessdata esté configurado
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/Cellar/tesseract/5.5.2/share/tessdata"


def extract_text_from_image(image: Image.Image) -> str:
    """
    Extrae texto desde una imagen usando OCR (Tesseract).
    """
    text = pytesseract.image_to_string(
        image, lang="spa"
    )  # También puedes probar con 'eng' o 'spa+eng'
    return text.strip()
