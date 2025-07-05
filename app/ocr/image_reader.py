import os
from pathlib import Path

import pytesseract
from PIL import Image

# Ruta a Tesseract instalada en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Asegurar que el path a tessdata esté configurado
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


def extract_text_from_image(image: Image.Image ) -> str:
    """
    Extrae texto desde una imagen usando OCR (Tesseract).
    """
    image.show()  # Esto abrirá la imagen en el visor predeterminado
    text = pytesseract.image_to_string(
        image, lang="spa"
    )  # También puedes probar con 'eng' o 'spa+eng'
    return text.strip()
