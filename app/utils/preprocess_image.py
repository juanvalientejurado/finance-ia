import cv2
import numpy as np
from PIL import Image


def preprocess_image_grays_to_black(path: str) -> Image.Image:
    # Cargar imagen en escala de grises
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    # Umbral invertido: todo lo más claro que X pasa a negro
    threshold = 200  # ajusta según necesites
    _, processed = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)

    # Combinar con imagen original (resaltamos lo claro sin borrar lo oscuro)
    result = cv2.bitwise_or(image, processed)

    return Image.fromarray(processed)
