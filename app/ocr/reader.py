from PIL import Image
import pytesseract
from pathlib import Path


def extract_text_from_image(image_path: str) -> str:
    """
    Extrae texto desde una imagen usando OCR (Tesseract).
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")

    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang="spa")  # Puedes cambiar a "eng" o "spa+eng"
    return text.strip()