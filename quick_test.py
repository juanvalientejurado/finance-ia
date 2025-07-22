from pprint import pprint

from app.db.db import get_all_gastos, init_db, insert_gastos_from_list
from app.ocr.image_reader import extract_text_from_image
from app.ocr.pdf_reader import extract_text_from_pdf
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks


def main():
    # Inicializa la base de datos
    init_db()

    print("📄 Procesando PDF...")
    texto_pdf = extract_text_from_pdf("data/extractDocument_20250704.pdf")
    gastos_pdf = parse_vertical_blocks(texto_pdf)
    insert_gastos_from_list(
        gastos_pdf, origen="pdf", archivo="extractDocument_20250704.pdf"
    )
    print(f"✅ {len(gastos_pdf)} gastos insertados desde PDF.\n")

    print("🖼️ Procesando imagen...")
    texto_img = extract_text_from_image("data/example.jpg")
    gastos_img = parse_expenses(texto_img)
    insert_gastos_from_list(gastos_img, origen="imagen", archivo="example.jpg")
    print(f"✅ {len(gastos_img)} gastos insertados desde imagen.\n")

    print("📊 Gastos totales en la base de datos:\n")
    gastos_total = get_all_gastos()
    pprint(gastos_total)


if __name__ == "__main__":
    main()
