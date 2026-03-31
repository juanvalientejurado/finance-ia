



def main():
    print("Hello from finance-ia!")
    from app.ocr.image_reader import extract_text_from_image
    from app.parser.parser_image import parse_expenses
    from app.db.db import init_db, insert_gasto

    # Inicializar DB
    init_db()

    # OCR de imagen
    text = extract_text_from_image("data/example.jpg")
    print("Texto extraído:", text)

    # Parsear gastos
    gastos = parse_expenses(text)
    print("Gastos parseados:", gastos)

    # Guardar en DB
    for gasto in gastos:
        insert_gasto(
            concepto=gasto["concepto"],
            fecha=gasto["fecha"],
            importe=float(gasto["importe"]),
            saldo=float(gasto["saldo"]),
            origen="manual",
            archivo="data/example.jpg"
        )
    print("Gastos guardados en DB")


if __name__ == "__main__":
    main()


