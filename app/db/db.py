import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from app.classifier.model import classify_concept

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
                categoria TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        _ensure_categoria_column(conn)


def _ensure_categoria_column(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(gastos)")
    columns = [row[1] for row in cursor.fetchall()]
    if "categoria" not in columns:
        cursor.execute("ALTER TABLE gastos ADD COLUMN categoria TEXT")
        conn.commit()


def insert_gasto(
        concepto: str,
        fecha: str,
        importe: float,
        saldo: Optional[float] = None,
        origen: Optional[str] = None,
        archivo: Optional[str] = None,
        categoria: Optional[str] = None,
) -> int:
    "Insertamos un gasto en la base de datos"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gastos (fecha, concepto, importe, saldo, origen, archivo, categoria)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fecha, concepto, importe, saldo, origen, archivo, categoria))
        conn.commit()
        return cursor.lastrowid

def insert_gastos_from_list(gastos: List[Dict[str, str]], origen = None, archivo = None):
    
    "Insertamos una lista de gastos en la base de datos"

    for gasto in gastos:
        insert_gasto(
            concepto=gasto.get("concepto", ""),
            fecha=gasto.get("fecha", ""),
            importe=float(gasto.get("importe", 0)),
            saldo=float(gasto.get("saldo", 0)) if gasto.get("saldo") else None,
            origen=origen,
            archivo=archivo,
            categoria=gasto.get("categoria")
        )

def get_all_gastos() -> List[Dict[str, str]]:
    "Obtenemos todos los gastos de la base de datos"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC")
        rows = [dict(row) for row in cursor.fetchall()]

        missing = [row for row in rows if not row.get("categoria")]
        if missing:
            for gasto in missing:
                categoria = classify_concept(gasto["concepto"], float(gasto["importe"]))
                gasto["categoria"] = categoria
                cursor.execute(
                    "UPDATE gastos SET categoria = ? WHERE id = ?",
                    (categoria, gasto["id"]),
                )
            conn.commit()

        return rows


def reclassify_all_gastos() -> int:
    "Reclasifica todos los gastos existentes y actualiza su categoría"

    updated = 0
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, concepto, importe FROM gastos")
        for row in cursor.fetchall():
            original = dict(row)
            nueva_categoria = classify_concept(original["concepto"], float(original["importe"]))
            cursor.execute(
                "UPDATE gastos SET categoria = ? WHERE id = ?",
                (nueva_categoria, original["id"]),
            )
            updated += cursor.rowcount
        conn.commit()

    return updated


def reclassify_gasto(gasto_id: int, categoria: str) -> bool:
    "Reclasifica un gasto específico por su ID con una categoría manual"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE gastos SET categoria = ? WHERE id = ?",
            (categoria, gasto_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_gasto_by_id(gasto_id: int) -> Optional[Dict[str, str]]:
    "Obtenemos un gasto específico por su ID"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gastos WHERE id = ?", (gasto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_gasto(gasto_id: int) -> bool:
    "Eliminamos un gasto por su ID"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
        conn.commit()
        return cursor.rowcount > 0


def update_gasto(
        gasto_id: int,
        concepto: str,
        fecha: str,
        importe: float,
        saldo: Optional[float] = None,
        origen: Optional[str] = None,
        archivo: Optional[str] = None,
        categoria: Optional[str] = None,
):
    "Actualiza un gasto por su ID"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE gastos
            SET concepto = ?, fecha = ?, importe = ?, saldo = ?, origen = ?, archivo = ?, categoria = ?
            WHERE id = ?
            """,
            (concepto, fecha, importe, saldo, origen, archivo, categoria, gasto_id),
        )
        conn.commit()
        return cursor.rowcount > 0
