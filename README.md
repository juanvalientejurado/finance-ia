# 💸 GastaIA – Gestor Inteligente de Gastos Personales con IA

**GastaIA** es un sistema local, privado y extensible para ayudarte a registrar, clasificar y analizar tus gastos de forma automática utilizando inteligencia artificial (OCR, NLP y LLMs locales).  
Ideal para personas que quieren tener el control completo de sus finanzas sin depender de servicios en la nube.

---

## ✨ Características

- 📸 OCR local de capturas de pantalla y tickets
- 📄 Lectura de extractos bancarios en PDF
- 🤖 Clasificación automática por categoría de gasto
- 💬 Preguntas en lenguaje natural sobre tus finanzas
- 📊 Visualización y análisis interactivo con Streamlit
- 🔐 Privacidad total: todo se ejecuta en local
- ⚙️ Arquitectura escalable y testeada

---

## 🚀 Instalación rápida

1. Asegúrate de tener [`uv`](https://github.com/astral-sh/uv) instalado:
   ```bash
   uv --version
   ```

2. Inicializa el entorno:
   ```bash
   uv init
   ```

3. Añade dependencias principales:
   ```bash
   uv sync
   ```
4. Dependencias extra:
   tesseract-ocr: https://github.com/UB-Mannheim/tesseract/wiki
   complemento español: https://github.com/tesseract-ocr/tessdata/blob/main/spa.traineddata?raw=true
   poppler: Desvargar (https://github.com/oschwartz10612/poppler-windows/releases), poner en C:\ProgramFiles . Añadir al PATH C:\Program Files\poppler-24.08.0\Library\bin . Reiniciar editor o terminal

5. Ejecuta la app (Streamlit):
   ```bash
   streamlit run main.py
   ```

---

## 🖥️ Nueva interfaz web local (front-end + API)

Se ha añadido un front-end estático que se sirve desde FastAPI:

- `frontend/index.html` (estructura + elementos de UI)
- `frontend/style.css` (diseño visual)
- `frontend/app.js` (lógica JS, fetch al backend y render)

Y el backend ahora monta los archivos estáticos:
- `app/api/main.py`: `app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")`

### ✨ Ejecutar en modo API + UI

1. Activar virtualenv:
```bash
source .venv/bin/activate
```
2. Ejecutar FastAPI:
```bash
.venv/bin/python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```
3. Abrir en navegador:
- `http://127.0.0.1:8000/`

### 🧪 Comprobar API (opcional)
```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/expenses/stats/summary
```

### 📁 Endpoints principales usados por el front-end
- `GET /api/v1/expenses` (listar movimientos)
- `GET /api/v1/expenses/stats/summary` (métricas de balance)
- `POST /api/v1/expenses/from-image` (subir imagen)
- `POST /api/v1/expenses/from-pdf` (subir PDF)

---

## 🧱 Estructura del proyecto

```
gastaia/
│   main.py            # Punto de entrada
│   README.md          # Documentación del proyecto
│
├── app/
│   ├── ocr/           # Lógica de OCR para imágenes y capturas de pantalla
│   ├── parser/        # Extracción de datos (importe, concepto, fecha) desde texto OCR
│   ├── classifier/    # Clasificación automática de gastos por categoría
│   ├── llm/           # Interacción con modelo de lenguaje para consultas inteligentes
│   ├── storage/       # Gestión de datos (guardado en SQLite o JSON)
│   └── dashboard/     # Interfaz web con Streamlit
│
├── tests/             # Pruebas unitarias y de integración (Pytest)
├── data/              # Datos de ejemplo, capturas de pantalla, PDFs de prueba
├── .venv/             # Entorno virtual (añadir a .gitignore)
├── uv.lock            # Archivo de bloqueo generado por `uv`
└── pyproject.toml     # Declaración de dependencias y configuración del proyecto
```

---

## 🧪 Testing

```bash
pytest
```

Para ejecutar todos los tests definidos en `/tests`.

---

## 🧹 Código limpio

```bash
black .
flake8 .
isort .
```

---

## 📍 Roadmap (resumen de fases)

1. ✅ OCR + carga de PDFs
2. ✅ Clasificación de gastos por IA
3. ✅ Interfaz web local con Streamlit
4. 🔄 Preguntas en lenguaje natural (RAG + LLM local con Ollama)
5. 📊 Visualización mensual y por categoría
6. 📤 Exportación de reportes
7. 📱 Empaquetado como app móvil en Flutter o PWA (futuro)

---

## 🛡️ Privacidad y seguridad

Este proyecto **nunca envía datos fuera de tu dispositivo**.  
Todo el procesamiento (incluyendo OCR y modelos de lenguaje) se hace en local, sin nube, sin dependencias externas.

---

## 🤝 Contribución

Este repositorio está pensado para desarrolladores que quieran aprender y construir su propio asistente de finanzas.  
Si deseas contribuir, puedes abrir una issue, hacer pull requests o clonar para uso personal.

---

## 📘 Licencia

MIT © 2025 [Tu Nombre o Alias]

---


uv run python main.py
# O directamente:
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Testing 
uv run pytest tests/test_api.py -v