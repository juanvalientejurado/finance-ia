"""Módulo para integración bancaria - Importación de archivos CSV."""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime

from app.schemas import BankTransaction


def parse_bank_csv(file_content: str, bank_type: str = "generic") -> List[BankTransaction]:
    """
    Parsea un archivo CSV de extracto bancario.
    
    Args:
        file_content: Contenido del archivo CSV como string
        bank_type: Tipo de banco para adaptar el parsing
        
    Returns:
        Lista de transacciones parseadas
    """
    transactions = []
    
    # Detectar delimitador (puede ser ; o , dependiendo del banco)
    sample = file_content[:1024]
    delimiter = ';' if sample.count(';') > sample.count(',') else ','
    
    # Leer CSV
    reader = csv.DictReader(io.StringIO(file_content), delimiter=delimiter)
    
    for row in reader:
        try:
            # Adaptar según el tipo de banco
            if bank_type.lower() == "bbva":
                transaction = _parse_bbva_row(row)
            elif bank_type.lower() == "santander":
                transaction = _parse_santander_row(row)
            elif bank_type.lower() == "bankinter":
                transaction = _parse_bankinter_row(row)
            else:
                transaction = _parse_generic_row(row)
            
            if transaction:
                transactions.append(transaction)
                
        except Exception as e:
            print(f"Error parseando fila: {e}")
            continue
    
    return transactions


def _parse_generic_row(row: Dict[str, Any]) -> BankTransaction:
    """Parse genérico - intenta mapear campos comunes."""
    # Campos comunes que pueden existir
    date_fields = ['fecha', 'date', 'Fecha', 'Date', 'FECHA']
    concept_fields = ['concepto', 'description', 'descripción', 'Concepto', 'Description']
    amount_fields = ['importe', 'amount', 'Importe', 'Amount', 'IMPORTE']
    balance_fields = ['saldo', 'balance', 'Saldo', 'Balance', 'SALDO']
    
    fecha = None
    concepto = None
    importe = None
    saldo = None
    
    # Buscar fecha
    for field in date_fields:
        if field in row and row[field]:
            try:
                # Intentar diferentes formatos de fecha
                fecha = _parse_date(row[field])
                break
            except:
                continue
    
    # Buscar concepto
    for field in concept_fields:
        if field in row and row[field]:
            concepto = row[field].strip()
            break
    
    # Buscar importe
    for field in amount_fields:
        if field in row and row[field]:
            try:
                # Limpiar formato de moneda
                amount_str = row[field].replace('€', '').replace('$', '').replace(',', '.').strip()
                importe = float(amount_str)
                break
            except:
                continue
    
    # Buscar saldo
    for field in balance_fields:
        if field in row and row[field]:
            try:
                balance_str = row[field].replace('€', '').replace('$', '').replace(',', '.').strip()
                saldo = float(balance_str)
                break
            except:
                continue
    
    if fecha and concepto and importe is not None:
        return BankTransaction(
            fecha=fecha,
            concepto=concepto,
            importe=importe,
            saldo=saldo
        )
    
    return None


def _parse_bbva_row(row: Dict[str, Any]) -> BankTransaction:
    """Parse específico para BBVA."""
    # BBVA típicamente usa formato DD/MM/YYYY
    try:
        fecha = _parse_date(row.get('Fecha', ''))
        concepto = row.get('Concepto', '').strip()
        importe = float(row.get('Importe', '0').replace('€', '').replace(',', '.'))
        saldo = float(row.get('Saldo', '0').replace('€', '').replace(',', '.')) if row.get('Saldo') else None
        
        return BankTransaction(
            fecha=fecha,
            concepto=concepto,
            importe=importe,
            saldo=saldo
        )
    except:
        return None


def _parse_santander_row(row: Dict[str, Any]) -> BankTransaction:
    """Parse específico para Santander."""
    # Santander puede usar diferentes formatos
    try:
        fecha = _parse_date(row.get('FECHA', ''))
        concepto = row.get('CONCEPTO', '').strip()
        importe = float(row.get('IMPORTE', '0').replace(',', '.'))
        saldo = None  # Santander no siempre incluye saldo
        
        return BankTransaction(
            fecha=fecha,
            concepto=concepto,
            importe=importe,
            saldo=saldo
        )
    except:
        return None


def _parse_bankinter_row(row: Dict[str, Any]) -> BankTransaction:
    """Parse específico para Bankinter."""
    try:
        fecha = _parse_date(row.get('Fecha', ''))
        concepto = row.get('Concepto', '').strip()
        importe = float(row.get('Importe', '0').replace(',', '.'))
        saldo = float(row.get('Saldo', '0').replace(',', '.')) if row.get('Saldo') else None
        
        return BankTransaction(
            fecha=fecha,
            concepto=concepto,
            importe=importe,
            saldo=saldo
        )
    except:
        return None


def _parse_date(date_str: str) -> str:
    """Parse fecha en diferentes formatos y retorna DD/MM/YYYY."""
    if not date_str:
        raise ValueError("Fecha vacía")
    
    date_str = date_str.strip()
    
    # Intentar diferentes formatos
    formats = [
        '%d/%m/%Y',  # 31/12/2023
        '%Y-%m-%d',  # 2023-12-31
        '%d-%m-%Y',  # 31-12-2023
        '%m/%d/%Y',  # 12/31/2023 (formato US)
        '%Y/%m/%d',  # 2023/12/31
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    raise ValueError(f"Formato de fecha no reconocido: {date_str}")


def get_supported_banks() -> List[str]:
    """Retorna lista de bancos soportados."""
    return [
        "generic",
        "bbva", 
        "santander",
        "bankinter",
        "caixabank",
        "sabadel",
        "ing",
        "openbank"
    ]