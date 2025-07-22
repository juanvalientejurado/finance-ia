import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/gastos.db")

def init_db():
    "Creamos la tabla si no existe"

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                concepto TEXT NOT NULL,
                importe REAL NOT NULL,
                saldo REAL,
                origen TEXT,
                archivo TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def insert_gasto(
        concepto: str,
        fecha: str,
        importe: float,
        saldo: Optional[float] = None,
        origen: Optional[str] = None,
        archivo: Optional[str] = None
):
    "Insertamos un gasto en la base de datos"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gastos (fecha, concepto, importe, saldo, origen, archivo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha, concepto, importe, saldo, origen, archivo))
        conn.commit()

def insert_gastos_from_list(gastos: List[Dict[str, str]], origen = None, archivo = None):
    
    "Insertamos una lista de gastos en la base de datos"

    for gasto in gastos:
        insert_gasto(
            concepto=gasto.get("concepto", ""),
            fecha=gasto.get("fecha", ""),
            importe=float(gasto.get("importe", 0)),
            saldo=float(gasto.get("saldo", 0)) if gasto.get("saldo") else None,
            origen=origen,
            archivo=archivo
        )

def get_all_gastos() -> List[Dict[str, str]]:
    "Obtenemos todos los gastos de la base de datos"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC")
        return [dict(row) for row in cursor.fetchall()]
       