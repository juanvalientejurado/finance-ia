from app.parser.parser import parse_expenses


def test_parser_with_fixture(sample_text):
    resultado = parse_expenses(sample_text)
    assert resultado == [
        {
            "concepto": "CAFET CXB LAS ROZ -1,50€",
            "fecha": "02/07/2025",
            "importe": "-1.50",
        },
        {"concepto": "BIZUM ENVIADO -3,00€", "fecha": "01/07/2025", "importe": "-3.00"},
        {
            "concepto": "BIZUM RECIBIDO +30,36€",
            "fecha": "01/07/2025",
            "importe": "+30.36",
        },
    ]
