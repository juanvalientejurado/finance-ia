"""Endpoints de la API REST de GastaIA."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from PIL import Image
import io

from app.ocr.image_reader import extract_text_from_image
from app.ocr.pdf_reader import extract_text_from_pdf
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks
from app.db import db
from app.schemas import HealthResponse, ExpensesResponse, GastosListResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificar que la API está funcionando."""
    return {
        "status": "ok",
        "message": "GastaIA API está activa y funcionando"
    }


@router.post("/expenses/from-image", response_model=ExpensesResponse)
async def upload_expense_image(file: UploadFile = File(...)):
    """
    Subir una imagen de ticket/extracto.
    Realiza OCR, parsea los gastos y los guarda en BD.
    """
    try:
        # Leer archivo
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # OCR
        text = extract_text_from_image(image)
        if not text.strip():
            raise ValueError("No se pudo extraer texto de la imagen")
        
        # Parse
        gastos = parse_expenses(text)
        if not gastos:
            raise ValueError("No se encontraron gastos en el texto extraído")
        
        # Guardar en BD
        saved_gastos = []
        for gasto in gastos:
            db.insert_gasto(
                concepto=gasto["concepto"],
                fecha=gasto["fecha"],
                importe=float(gasto["importe"]),
                saldo=float(gasto["saldo"]) if gasto.get("saldo") else None,
                origen="imagen",
                archivo=file.filename
            )
            saved_gastos.append(gasto)
        
        return {
            "success": True,
            "message": f"Se han guardado {len(saved_gastos)} gastos de la imagen",
            "data": {"gastos_guardados": len(saved_gastos), "gastos": saved_gastos}
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar imagen: {str(e)}")


@router.post("/expenses/from-pdf", response_model=ExpensesResponse)
async def upload_expense_pdf(file: UploadFile = File(...)):
    """
    Subir un PDF de extracto bancario.
    Realiza OCR, parsea los gastos y los guarda en BD.
    """
    try:
        # Guardar archivo temporalmente
        temp_path = Path(f"/tmp/{file.filename}")
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # OCR desde PDF
        text_pages = extract_text_from_pdf(str(temp_path))
        if not text_pages:
            raise ValueError("No se pudo extraer texto del PDF")
        
        full_text = "\n".join(text_pages)
        
        # Parse
        gastos = parse_vertical_blocks(full_text)
        if not gastos:
            raise ValueError("No se encontraron gastos en el PDF")
        
        # Guardar en BD
        for gasto in gastos:
            db.insert_gasto(
                concepto=gasto["concepto"],
                fecha=gasto["fecha"],
                importe=float(gasto["importe"]),
                saldo=float(gasto["saldo"]) if gasto.get("saldo") else None,
                origen="pdf",
                archivo=file.filename
            )
        
        # Limpiar
        temp_path.unlink()
        
        return {
            "success": True,
            "message": f"Se han guardado {len(gastos)} gastos del PDF",
            "data": {"gastos_guardados": len(gastos), "gastos": gastos}
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar PDF: {str(e)}")


@router.get("/expenses", response_model=GastosListResponse)
async def get_all_expenses():
    """Obtener todos los gastos guardados."""
    try:
        gastos = db.get_all_gastos()
        return {
            "success": True,
            "message": f"Se encontraron {len(gastos)} gastos",
            "total": len(gastos),
            "data": gastos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener gastos: {str(e)}")


@router.get("/expenses/{gasto_id}", response_model=ExpensesResponse)
async def get_expense(gasto_id: int):
    """Obtener un gasto específico por ID."""
    try:
        gasto = db.get_gasto_by_id(gasto_id)
        if not gasto:
            raise HTTPException(status_code=404, detail=f"Gasto con ID {gasto_id} no encontrado")
        
        return {
            "success": True,
            "message": f"Gasto {gasto_id} encontrado",
            "data": gasto
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener gasto: {str(e)}")


@router.delete("/expenses/{gasto_id}", response_model=ExpensesResponse)
async def delete_expense(gasto_id: int):
    """Eliminar un gasto por ID."""
    try:
        # Verificar que existe
        gasto = db.get_gasto_by_id(gasto_id)
        if not gasto:
            raise HTTPException(status_code=404, detail=f"Gasto con ID {gasto_id} no encontrado")
        
        # Eliminar
        db.delete_gasto(gasto_id)
        
        return {
            "success": True,
            "message": f"Gasto {gasto_id} eliminado correctamente",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar gasto: {str(e)}")


@router.get("/expenses/stats/summary", response_model=ExpensesResponse)
async def get_expenses_summary():
    """Obtener resumen de gastos (total, cantidad, promedio)."""
    try:
        gastos = db.get_all_gastos()
        
        if not gastos:
            return {
                "success": True,
                "message": "No hay gastos registrados",
                "data": {
                    "total_gastos": 0,
                    "cantidad": 0,
                    "promedio": 0,
                    "mayorgasto": 0,
                    "menorgasto": 0
                }
            }
        
        importes = [float(g["importe"]) for g in gastos]
        total = sum(importes)
        cantidad = len(gastos)
        promedio = total / cantidad if cantidad > 0 else 0
        
        return {
            "success": True,
            "message": "Resumen de gastos calculado",
            "data": {
                "total_gastos": round(total, 2),
                "cantidad": cantidad,
                "promedio": round(promedio, 2),
                "mayorgasto": round(max(importes), 2),
                "menorgasto": round(min(importes), 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular resumen: {str(e)}")
