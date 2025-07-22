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