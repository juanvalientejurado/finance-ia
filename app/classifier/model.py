import re

CATEGORY_KEYWORDS = {
    "comida": ["restaurante", "bar", "café", "cafetería", "supermercado", "mercado", "kebab", "pizzería", "pizza", "hamburguesa", "sushi", "comida", "panadería", "pastelería"],
    "transporte": ["metro", "bus", "autobús", "taxi", "uber", "cabify", "tren", "gasolina", "petrol", "parking", "estación"],
    "hogar": ["luz", "agua", "gas", "internet", "alquiler", "hipoteca", "mantenimiento", "electricidad", "calefacción"],
    "seguros": ["seguros", "mapfre", "allianz", "axa", "generali", "reaseguradora"],
    "salud": ["farmacia", "hospital", "clínica", "dentista", "oftalmólogo", "médico", "salud", "optica", "tratamiento"],
    "ocio": ["cine", "teatro", "netflix", "spotify", "gym", "gimnasio", "streaming", "ocio", "viaje", "vacac", "hotel", "resto"],
    "compras": ["amazon", "el corte inglés", "zara", "hm", "media markt", "tienda", "compras", "mercadona", "decathlon"],
    "educación": ["campus", "universidad", "curso", "formación", "academia", "libro", "colegio", "escuela"],
    "transferencias": ["bizum", "transferencia", "trf", "envío", "recibido", "recibida", "pago electrónico"],
    "ingreso": ["salario", "nomina", "nómina", "sueldo", "ingreso", "devolución", "reembolso", "pago recibido"],
    "servicios": ["amazon prime", "netflix", "spotify", "movistar", "vodafone", "orange", "sky", "telefonía"],
}
DEFAULT_CATEGORY = "otros"


def classify_concept(concepto: str, importe: float | None = None) -> str:
    """Asigna una categoría básica según el texto del concepto."""
    if concepto is None:
        return DEFAULT_CATEGORY

    texto = concepto.lower()
    texto = re.sub(r"[^\w\sáéíóúñüÁÉÍÓÚÑÜ]", " ", texto)

    if importe is not None and importe < 0 and "bizum" in texto:
        return "transferencias"

    for categoria, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in texto:
                return categoria

    if importe is not None and importe > 0:
        return "ingreso"

    return DEFAULT_CATEGORY
