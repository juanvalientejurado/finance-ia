from app.classifier.model import classify_concept, DEFAULT_CATEGORY


def test_classify_concept_food_keyword():
    categoria = classify_concept("Cena en restaurante italiano", -45.00)
    assert categoria == "comida"


def test_classify_concept_bizum_negative_is_transferencias():
    categoria = classify_concept("Bizum enviado a Juan", -10.00)
    assert categoria == "transferencias"


def test_classify_concept_positive_importe_returns_ingreso():
    categoria = classify_concept("Salario mensual", 2000.00)
    assert categoria == "ingreso"


def test_classify_concept_no_keyword_returns_otros():
    categoria = classify_concept("Pago desconocido", -5.00)
    assert categoria == DEFAULT_CATEGORY


def test_classify_concept_none_text_returns_otros():
    categoria = classify_concept(None, None)
    assert categoria == DEFAULT_CATEGORY
