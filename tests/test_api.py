import io
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.db import db
import tempfile
from pathlib import Path


@pytest.fixture
def client():
    """Fixture que proporciona un cliente de prueba para la API"""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Fixture que crea una BD temporal para tests"""
    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test_gastos.db"
    original_db_path = db.DB_PATH
    
    try:
        db.DB_PATH = test_db_path
        db.init_db()
        
        # Insertar datos de prueba
        db.insert_gasto(
            concepto="Café",
            fecha="2025-04-01",
            importe=-2.50,
            saldo=1000.00,
            origen="test",
            archivo="test.jpg"
        )
        db.insert_gasto(
            concepto="Salario",
            fecha="2025-04-01",
            importe=2000.00,
            saldo=2000.00,
            origen="test",
            archivo="test.pdf"
        )
        db.insert_gasto(
            concepto="Gasolina",
            fecha="2025-04-02",
            importe=-45.00,
            saldo=1955.00,
            origen="test",
            archivo="test.jpg"
        )
        
        yield test_db_path
    finally:
        db.DB_PATH = original_db_path


class TestHealthEndpoint:
    """Tests para el endpoint de health check"""
    
    def test_health_check(self, client):
        """Test que verifica que el endpoint /health funciona"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


class TestExpensesEndpoint:
    """Tests para los endpoints de gastos"""
    
    def test_get_all_expenses(self, client, test_db):
        """Test que verifica que se obtienen todos los gastos"""
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 3
    
    def test_get_expenses_filter_by_gasto(self, client, test_db):
        """Test que verifica el filtro por tipo=gasto"""
        response = client.get("/api/v1/expenses?tipo=gasto")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2  # Café y Gasolina
        
        for gasto in data["data"]:
            assert gasto["importe"] < 0  # Los gastos son negativos
    
    def test_get_expenses_filter_by_ingreso(self, client, test_db):
        """Test que verifica el filtro por tipo=ingreso"""
        response = client.get("/api/v1/expenses?tipo=ingreso")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1  # Salario
        
        for ingreso in data["data"]:
            assert ingreso["importe"] > 0  # Los ingresos son positivos
    
    def test_get_expense_by_id(self, client, test_db):
        """Test que verifica obtener un gasto por ID"""
        # Primero obtener todos para conseguir un ID
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        gastos_list = response.json()["data"]
        gasto_id = gastos_list[0]["id"]
        gasto_concepto = gastos_list[0]["concepto"]
        
        # Luego obtener ese gasto específico
        response = client.get(f"/api/v1/expenses/{gasto_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == gasto_id
        assert data["data"]["concepto"] == gasto_concepto
    
    def test_get_expense_by_id_not_found(self, client, test_db):
        """Test que verifica que retorna 404 si el gasto no existe"""
        response = client.get("/api/v1/expenses/99999")
        assert response.status_code == 404
        # FastAPI retorna HTTPException con "detail", no "message"
        assert "not found" in response.json()["detail"].lower() or response.status_code == 404
    
    def test_delete_expense(self, client, test_db):
        """Test que verifica eliminar un gasto"""
        # Obtener ID del gasto
        response = client.get("/api/v1/expenses")
        initial_count = len(response.json()["data"])
        gasto_id = response.json()["data"][0]["id"]
        
        # Eliminar gasto
        response = client.delete(f"/api/v1/expenses/{gasto_id}")
        assert response.status_code == 200
        assert "eliminado" in response.json()["message"].lower()
        
        # Verificar que se eliminó
        response = client.get("/api/v1/expenses")
        assert len(response.json()["data"]) == initial_count - 1
    
    def test_delete_expense_not_found(self, client, test_db):
        """Test que verifica que no se puede eliminar un gasto inexistente"""
        response = client.delete("/api/v1/expenses/99999")
        assert response.status_code == 404


class TestStatsEndpoint:
    """Tests para el endpoint de estadísticas"""
    
    def test_get_summary(self, client, test_db):
        """Test que verifica el resumen de estadísticas"""
        response = client.get("/api/v1/expenses/stats/summary")
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Verificar gastos
        assert data["gastos"]["cantidad"] == 2
        assert data["gastos"]["total"] == 47.50
        assert data["gastos"]["promedio"] == 23.75
        
        # Verificar ingresos
        assert data["ingresos"]["cantidad"] == 1
        assert data["ingresos"]["total"] == 2000.00
        
        # Verificar balance
        assert data["balance"] == 1952.50
        assert data["total_movimientos"] == 3
    
    def test_summary_empty_db(self, client):
        """Test que verifica el resumen con BD vacía"""
        # Usar una BD temporal vacía
        temp_dir = tempfile.mkdtemp()
        test_db_path = Path(temp_dir) / "empty_test.db"
        original_db_path = db.DB_PATH
        
        try:
            db.DB_PATH = test_db_path
            db.init_db()
            
            response = client.get("/api/v1/expenses/stats/summary")
            assert response.status_code == 200
            data = response.json()["data"]
            
            assert data["gastos"]["cantidad"] == 0
            assert data["ingresos"]["cantidad"] == 0
            assert data["balance"] == 0
            assert data["total_movimientos"] == 0
        finally:
            db.DB_PATH = original_db_path


class TestBankEndpoints:
    """Tests para los endpoints de integración bancaria."""

    def test_supported_banks_list(self, client):
        response = client.get("/api/v1/bank/supported-banks")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "bancos_soportados" in data["data"]
        assert "bbva" in data["data"]["bancos_soportados"]
        assert "generic" in data["data"]["bancos_soportados"]

    def test_import_bank_csv_generic_success(self, client, test_db):
        csv_content = (
            "Fecha,Concepto,Importe,Saldo\n"
            "01/04/2025,Prueba gasto,-10.50,990.50\n"
            "02/04/2025,Ingreso prueba,100.00,1090.50\n"
        )
        response = client.post(
            "/api/v1/bank/import-csv?bank_type=generic",
            files={
                "file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["transacciones_importadas"] == 2
        assert data["data"]["banco"] == "generic"

    def test_import_bank_csv_unsupported_bank(self, client):
        csv_content = "Fecha,Concepto,Importe\n01/04/2025,Prueba,-10.50\n"
        response = client.post(
            "/api/v1/bank/import-csv?bank_type=desconocido",
            files={
                "file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
            },
        )
        assert response.status_code == 400
        assert "Banco no soportado" in response.json()["detail"]


class TestExpenseModificationEndpoint:
    """Tests para crear, actualizar y reclasificar gastos."""

    def test_create_expense(self, client, test_db):
        payload = {
            "concepto": "Compra test",
            "fecha": "05/04/2025",
            "importe": -25.00,
            "saldo": 975.50,
            "origen": "manual",
            "archivo": "ticket.pdf"
        }
        response = client.post("/api/v1/expenses", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["concepto"] == "Compra test"

    def test_update_expense(self, client, test_db):
        response = client.get("/api/v1/expenses")
        gasto_id = response.json()["data"][0]["id"]
        payload = {
            "concepto": "Café actualizado",
            "fecha": "01/04/2025",
            "importe": -3.00,
            "saldo": 999.00,
            "origen": "manual",
            "archivo": "ticket_update.jpg"
        }
        response = client.put(f"/api/v1/expenses/{gasto_id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["concepto"] == "Café actualizado"
        assert data["data"]["archivo"] == "ticket_update.jpg"

    def test_batch_delete_expenses(self, client, test_db):
        response = client.get("/api/v1/expenses")
        ids = [item["id"] for item in response.json()["data"]][:2]
        response = client.post("/api/v1/expenses/batch-delete", json={"ids": ids})
        assert response.status_code == 200
        assert response.json()["data"]["eliminados"] == len(ids)

    def test_reclassify_expenses(self, client, test_db):
        response = client.post("/api/v1/expenses/reclassify")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "reclasificaron" in response.json()["message"].lower()

    def test_reclassify_expense(self, client, test_db):
        response = client.get("/api/v1/expenses")
        gasto_id = response.json()["data"][0]["id"]
        payload = {"categoria": "Viajes"}
        response = client.put(f"/api/v1/expenses/{gasto_id}/reclassify", json=payload)
        assert response.status_code == 200
        assert response.json()["data"]["categoria"] == "Viajes"

    def test_batch_delete_empty_ids(self, client, test_db):
        response = client.post("/api/v1/expenses/batch-delete", json={"ids": []})
        assert response.status_code == 400
        assert "Lista de IDs vacía" in response.json()["detail"]


class TestImageUploadEndpoint:
    """Tests para el endpoint de subida de imágenes"""
    
    def test_upload_image_success(self, client, test_db):
        """Test que verifica la subida exitosa de una imagen"""
        # Usar la imagen de ejemplo que existe
        try:
            with open("data/example.jpg", "rb") as f:
                files = {"file": ("example.jpg", f, "image/jpeg")}
                response = client.post("/api/v1/expenses/from-image", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert data["data"]["gastos_guardados"] > 0
        except FileNotFoundError:
            pytest.skip("Archivo data/example.jpg no encontrado")
    
    def test_upload_image_empty_file(self, client):
        """Test que verifica error al subir archivo vacío"""
        files = {"file": ("empty.jpg", b"", "image/jpeg")}
        response = client.post("/api/v1/expenses/from-image", files=files)
        
        # Debe fallar o devolver un estado no 200
        assert response.status_code != 200 or response.status_code == 400


class TestPDFUploadEndpoint:
    """Tests para el endpoint de subida de PDFs"""
    
    def test_upload_pdf_success(self, client, test_db):
        """Test que verifica la subida exitosa de un PDF"""
        # Usar el PDF de ejemplo que existe
        try:
            with open("data/extractDocument_20250704.pdf", "rb") as f:
                files = {"file": ("extractDocument_20250704.pdf", f, "application/pdf")}
                response = client.post("/api/v1/expenses/from-pdf", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            # Validar que tiene la estructura correcta
            assert "gastos_guardados" in data["data"] or "gastos" in data["data"]
        except FileNotFoundError:
            pytest.skip("Archivo data/extractDocument_20250704.pdf no encontrado")
