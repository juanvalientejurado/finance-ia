import pytest
from app.bank_integration import parse_bank_csv, get_supported_banks


def test_get_supported_banks_contains_common_values():
    banks = get_supported_banks()
    assert isinstance(banks, list)
    assert "generic" in banks
    assert "bbva" in banks
    assert "santander" in banks
    assert "bankinter" in banks


def test_parse_bank_csv_generic_rows():
    csv_text = (
        "Fecha,Concepto,Importe,Saldo\n"
        "01/04/2025,Supermercado,-25.30,974.70\n"
        "02/04/2025,Nomina,1500.00,2474.70\n"
    )

    transactions = parse_bank_csv(csv_text, bank_type="generic")

    assert len(transactions) == 2
    assert transactions[0].concepto == "Supermercado"
    assert transactions[0].importe == -25.30
    assert transactions[0].saldo == 974.70
    assert transactions[1].concepto == "Nomina"
    assert transactions[1].importe == 1500.00


def test_parse_bank_csv_bbva_semicolon_and_comma():
    csv_text = (
        "Fecha;Concepto;Importe;Saldo\n"
        "01/04/2025;Café;-12,50;987,50\n"
    )

    transactions = parse_bank_csv(csv_text, bank_type="bbva")
    assert len(transactions) == 1
    assert transactions[0].concepto == "Café"
    assert transactions[0].importe == -12.5
    assert transactions[0].saldo == 987.5


def test_parse_bank_csv_santander_uppercase_headers():
    csv_text = (
        "FECHA,CONCEPTO,IMPORTE\n"
        "01/04/2025,Gasolina,-45.00\n"
    )

    transactions = parse_bank_csv(csv_text, bank_type="santander")
    assert len(transactions) == 1
    assert transactions[0].concepto == "Gasolina"
    assert transactions[0].importe == -45.0
    assert transactions[0].saldo is None


def test_parse_bank_csv_unknown_bank_returns_generic():
    csv_text = (
        "date,description,amount,balance\n"
        "2025-04-01,Taxi,-18.20,982.80\n"
    )
    transactions = parse_bank_csv(csv_text, bank_type="unknown")
    assert len(transactions) == 1
    assert transactions[0].concepto == "Taxi"
    assert transactions[0].importe == -18.2
    assert transactions[0].saldo == 982.8
