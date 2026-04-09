"""Endpoints de la API REST de GastaIA."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, List
from pathlib import Path
from PIL import Image
import io

from app.ocr.image_reader import extract_text_from_image
from app.ocr.pdf_reader import extract_text_from_pdf
from app.parser.parser_image import parse_expenses
from app.parser.parser_pdf import parse_vertical_blocks
from app.classifier.model import classify_concept
from app.db import db
from app.schemas import HealthResponse, ExpensesResponse, GastosListResponse, GastoCreate, GastoResponse, ReclassifyRequest
from pydantic import BaseModel


class BatchDeleteRequest(BaseModel):
    ids: List[int]

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
            categoria = classify_concept(
                gasto["concepto"],
                float(gasto["importe"])
            )
            db.insert_gasto(
                concepto=gasto["concepto"],
                fecha=gasto["fecha"],
                importe=float(gasto["importe"]),
                saldo=float(gasto["saldo"]) if gasto.get("saldo") else None,
                origen="imagen",
                archivo=file.filename,
                categoria=categoria
            )
            gasto["categoria"] = categoria
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
            categoria = classify_concept(
                gasto["concepto"],
                float(gasto["importe"])
            )
            db.insert_gasto(
                concepto=gasto["concepto"],
                fecha=gasto["fecha"],
                importe=float(gasto["importe"]),
                saldo=float(gasto["saldo"]) if gasto.get("saldo") else None,
                origen="pdf",
                archivo=file.filename,
                categoria=categoria
            )
            gasto["categoria"] = categoria
        
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
async def get_all_expenses(tipo: Optional[str] = Query(None, description="Filtrar por tipo: 'gasto' o 'ingreso'")):
    """Obtener todos los gastos e ingresos guardados.
    
    Args:
        tipo: Filtro opcional ('gasto', 'ingreso' o None para ambos)
    """
    try:
        gastos = db.get_all_gastos()
        
        # Filtrar por tipo si se especifica
        if tipo:
            if tipo.lower() == "gasto":
                gastos = [g for g in gastos if g["importe"] < 0]
                mensaje = f"Se encontraron {len(gastos)} gastos"
            elif tipo.lower() == "ingreso":
                gastos = [g for g in gastos if g["importe"] > 0]
                mensaje = f"Se encontraron {len(gastos)} ingresos"
            else:
                raise HTTPException(status_code=400, detail="Tipo debe ser 'gasto' o 'ingreso'")
        else:
            mensaje = f"Se encontraron {len(gastos)} movimientos"
        
        return {
            "success": True,
            "message": mensaje,
            "total": len(gastos),
            "data": gastos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener movimientos: {str(e)}")


@router.post("/expenses", response_model=GastoResponse)
async def create_expense(gasto: GastoCreate):
    """Crear un gasto manualmente."""
    try:
        categoria = gasto.categoria if gasto.categoria else classify_concept(gasto.concepto, gasto.importe)
        gasto_id = db.insert_gasto(
            concepto=gasto.concepto,
            fecha=gasto.fecha,
            importe=gasto.importe,
            saldo=gasto.saldo,
            origen=gasto.origen,
            archivo=gasto.archivo,
            categoria=categoria,
        )
        nuevo_gasto = db.get_gasto_by_id(gasto_id)
        return {
            "success": True,
            "message": "Gasto creado correctamente",
            "data": nuevo_gasto
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear gasto: {str(e)}")


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


@router.put("/expenses/{gasto_id}", response_model=GastoResponse)
async def update_expense(gasto_id: int, gasto: GastoCreate):
    """Actualizar datos de un gasto existente."""
    try:
        existing = db.get_gasto_by_id(gasto_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Gasto con ID {gasto_id} no encontrado")

        categoria = gasto.categoria if gasto.categoria else classify_concept(gasto.concepto, gasto.importe)
        updated = db.update_gasto(
            gasto_id=gasto_id,
            concepto=gasto.concepto,
            fecha=gasto.fecha,
            importe=gasto.importe,
            saldo=gasto.saldo,
            origen=gasto.origen,
            archivo=gasto.archivo,
            categoria=categoria,
        )

        if not updated:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el gasto")

        gasto_actualizado = db.get_gasto_by_id(gasto_id)
        return {
            "success": True,
            "message": f"Gasto {gasto_id} actualizado correctamente",
            "data": gasto_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar gasto: {str(e)}")


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


@router.post("/expenses/batch-delete", response_model=ExpensesResponse)
async def batch_delete_expenses(request: BatchDeleteRequest):
    """Eliminar varios gastos de una vez."""
    try:
        ids = request.ids
        if not ids:
            raise HTTPException(status_code=400, detail="Lista de IDs vacía")

        eliminados = 0
        for gasto_id in ids:
            if db.delete_gasto(gasto_id):
                eliminados += 1

        return {
            "success": True,
            "message": f"Se eliminaron {eliminados} registros",
            "data": {"eliminados": eliminados}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en eliminación masiva: {str(e)}")


@router.post("/expenses/reclassify", response_model=ExpensesResponse)
async def reclassify_expenses():
    """Reclasificar todos los gastos existentes usando el clasificador."""
    try:
        actualizados = db.reclassify_all_gastos()
        return {
            "success": True,
            "message": f"Se reclasificaron {actualizados} gastos",
            "data": {"actualizados": actualizados}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reclasificar gastos: {str(e)}")


@router.put("/expenses/{gasto_id}/reclassify", response_model=GastoResponse)
async def reclassify_expense(gasto_id: int, request: ReclassifyRequest):
    """Reclasificar un gasto específico con una categoría manual."""
    try:
        success = db.reclassify_gasto(gasto_id, request.categoria)
        if not success:
            raise HTTPException(status_code=404, detail=f"Gasto con ID {gasto_id} no encontrado")
        
        gasto_actualizado = db.get_gasto_by_id(gasto_id)
        return {
            "success": True,
            "message": f"Gasto {gasto_id} reclasificado correctamente",
            "data": gasto_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reclasificar gasto: {str(e)}")


@router.get("/expenses/stats/summary", response_model=ExpensesResponse)
async def get_expenses_summary():
    """Obtener resumen separado de gastos e ingresos."""
    try:
        todos = db.get_all_gastos()
        
        # Separar gastos e ingresos
        gastos = [g for g in todos if g["importe"] < 0]
        ingresos = [g for g in todos if g["importe"] > 0]
        
        # Calcular estadísticas de gastos
        importes_gastos = [abs(float(g["importe"])) for g in gastos]
        total_gastos = sum(importes_gastos)
        promedio_gastos = total_gastos / len(gastos) if gastos else 0
        mayor_gasto = max(importes_gastos) if gastos else 0
        menor_gasto = min(importes_gastos) if gastos else 0
        
        # Calcular estadísticas de ingresos
        importes_ingresos = [float(g["importe"]) for g in ingresos]
        total_ingresos = sum(importes_ingresos)
        promedio_ingresos = total_ingresos / len(ingresos) if ingresos else 0
        mayor_ingreso = max(importes_ingresos) if ingresos else 0
        menor_ingreso = min(importes_ingresos) if ingresos else 0
        
        # Balance neto
        balance = total_ingresos - total_gastos
        
        return {
            "success": True,
            "message": "Resumen de movimientos calculado",
            "data": {
                "gastos": {
                    "cantidad": len(gastos),
                    "total": round(total_gastos, 2),
                    "promedio": round(promedio_gastos, 2),
                    "mayor": round(mayor_gasto, 2),
                    "menor": round(menor_gasto, 2)
                },
                "ingresos": {
                    "cantidad": len(ingresos),
                    "total": round(total_ingresos, 2),
                    "promedio": round(promedio_ingresos, 2),
                    "mayor": round(mayor_ingreso, 2),
                    "menor": round(menor_ingreso, 2)
                },
                "balance": round(balance, 2),
                "total_movimientos": len(todos)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular resumen: {str(e)}")
