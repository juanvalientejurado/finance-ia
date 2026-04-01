"""Esquemas Pydantic para la API REST."""

from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str
    message: str


class GastoBase(BaseModel):
    """Esquema base para un gasto."""
    concepto: str = Field(..., min_length=1, description="Concepto o descripción del gasto")
    fecha: str = Field(..., description="Fecha en formato DD/MM/YYYY")
    importe: float = Field(..., description="Importe del gasto (negativo para gastos, positivo para ingresos)")
    saldo: Optional[float] = Field(None, description="Saldo después del gasto")
    origen: Optional[str] = Field(None, description="Origen del gasto (ej: OCR, manual, PDF)")
    archivo: Optional[str] = Field(None, description="Nombre del archivo adjunto")
    categoria: Optional[str] = Field(None, description="Categoría del gasto (ej: comida, transporte)")


class GastoCreate(GastoBase):
    """Esquema para crear un gasto."""
    pass


class Gasto(GastoBase):
    """Esquema de gasto con ID."""
    id: int = Field(..., description="ID único del gasto")
    created_at: str = Field(..., description="Fecha de creación del gasto")

    class Config:
        from_attributes = True


class ExpensesResponse(BaseModel):
    """Respuesta general de la API."""
    success: bool
    message: str
    data: Optional[Any] = None


class GastoResponse(BaseModel):
    """Respuesta con información de un gasto."""
    success: bool
    message: str
    data: Optional[Gasto] = None


class GastosListResponse(BaseModel):
    """Respuesta con lista de gastos."""
    success: bool
    message: str
    total: int
    data: List[Gasto]


class OCRResult(BaseModel):
    """Resultado de OCR de una imagen."""
    texto_extraido: str = Field(..., description="Texto extraído de la imagen")
    gastos: List[GastoBase] = Field(..., description="Gastos parseados del texto")


class OCRResponse(BaseModel):
    """Respuesta del endpoint de OCR."""
    success: bool
    message: str
    data: Optional[OCRResult] = None


class ParseResult(BaseModel):
    """Resultado del parseo de texto."""
    gastos: List[GastoBase] = Field(..., description="Gastos extraídos del texto")


class ParseResponse(BaseModel):
    """Respuesta del endpoint de parseo."""
    success: bool
    message: str
    data: Optional[ParseResult] = None


class ClasificacionResult(BaseModel):
    """Resultado de clasificación de un gasto."""
    categoria: str = Field(..., description="Categoría asignada al concepto")
    confianza: Optional[float] = Field(None, description="Nivel de confianza (0-1)")


class ClasificacionResponse(BaseModel):
    """Respuesta del endpoint de clasificación."""
    success: bool
    message: str
    data: Optional[ClasificacionResult] = None


class Estadistica(BaseModel):
    """Estadística de gastos."""
    total_gastos: int
    cantidad_gastos: int
    importe_promedio: float
    importe_maximo: float
    importe_minimo: float
    por_categoria: Optional[dict] = None


class EstadisticaResponse(BaseModel):
    """Respuesta del endpoint de estadísticas."""
    success: bool
    message: str
    data: Optional[Estadistica] = None


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
