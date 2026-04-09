import os
import sqlite3
import tempfile
import time
from app.db import db
from pathlib import Path


def test_init_and_insert_gasto():
    # Creamos una base temporal en un archivo temporal
    temp_dir = tempfile.mkdtemp()  # Usamos mkdtemp en lugar de TemporaryDirectory
    test_db_path = Path(temp_dir) / "test_gastos.db"
    original_db_path = db.DB_PATH  # Guardamos la ruta original

    try:
        db.DB_PATH = test_db_path  # Sobrescribimos la ruta para test
        db.init_db()
        assert test_db_path.exists()

        db.insert_gasto(
            concepto="Test Gasto",
            fecha="2025-07-04",
            importe=-15.99,
            saldo=1234.56,
            origen="test",
            archivo="testfile.jpg",
        )

        gastos = db.get_all_gastos()
        assert len(gastos) == 1
        gasto = gastos[0]
        assert gasto["concepto"] == "Test Gasto"
        assert gasto["fecha"] == "2025-07-04"
        assert gasto["importe"] == -15.99
        assert gasto["saldo"] == 1234.56
        assert gasto["origen"] == "test"
        assert gasto["archivo"] == "testfile.jpg"

    finally:
        # Cerramos todas las conexiones posibles
        if hasattr(db, 'conn') and db.conn:
            db.conn.close()
            db.conn = None
        
        # Restauramos la ruta original
        db.DB_PATH = original_db_path
        
        # Esperamos un momento para que se liberen los recursos
        time.sleep(0.5)
        
        # Eliminamos manualmente los archivos
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            os.rmdir(temp_dir)
        except (PermissionError, OSError):
            pass  # Ignoramos errores de limpieza en tests


def test_get_update_delete_and_reclassify_gasto():
    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test_gastos.db"
    original_db_path = db.DB_PATH

    try:
        db.DB_PATH = test_db_path
        db.init_db()

        gasto_id = db.insert_gasto(
            concepto="Compra gasolina",
            fecha="2025-07-05",
            importe=-40.00,
            saldo=960.00,
            origen="test",
            archivo="gasolina.pdf",
            categoria="transporte",
        )

        gasto = db.get_gasto_by_id(gasto_id)
        assert gasto is not None
        assert gasto["concepto"] == "Compra gasolina"

        updated = db.update_gasto(
            gasto_id=gasto_id,
            concepto="Compra gasolina actualizada",
            fecha="2025-07-05",
            importe=-42.00,
            saldo=958.00,
            origen="test",
            archivo="gasolina_actualizada.pdf",
            categoria="transporte",
        )
        assert updated is True

        gasto_actualizado = db.get_gasto_by_id(gasto_id)
        assert gasto_actualizado["concepto"] == "Compra gasolina actualizada"
        assert gasto_actualizado["importe"] == -42.00

        deleted = db.delete_gasto(gasto_id)
        assert deleted is True
        assert db.get_gasto_by_id(gasto_id) is None

    finally:
        db.DB_PATH = original_db_path
        time.sleep(0.5)
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            os.rmdir(temp_dir)
        except (PermissionError, OSError):
            pass


def test_reclassify_functions_update_category():
    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test_gastos.db"
    original_db_path = db.DB_PATH

    try:
        db.DB_PATH = test_db_path
        db.init_db()

        first_id = db.insert_gasto(
            concepto="Supermercado Mercadona",
            fecha="2025-07-05",
            importe=-30.00,
            saldo=930.00,
            origen="test",
            archivo="ticket.jpg",
        )
        second_id = db.insert_gasto(
            concepto="Bizum enviado a Pedro",
            fecha="2025-07-06",
            importe=-15.00,
            saldo=915.00,
            origen="test",
            archivo="bizum.jpg",
        )

        updated_count = db.reclassify_all_gastos()
        assert updated_count == 2

        gasto1 = db.get_gasto_by_id(first_id)
        gasto2 = db.get_gasto_by_id(second_id)
        assert gasto1["categoria"] == "comida"
        assert gasto2["categoria"] == "transferencias"

        manual_update = db.reclassify_gasto(second_id, "regalos")
        assert manual_update is True
        gasto2_manual = db.get_gasto_by_id(second_id)
        assert gasto2_manual["categoria"] == "regalos"

    finally:
        db.DB_PATH = original_db_path
        time.sleep(0.5)
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            os.rmdir(temp_dir)
        except (PermissionError, OSError):
            pass