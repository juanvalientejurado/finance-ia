const API_BASE = "/api/v1";
const statusEl = document.getElementById("upload-status");
const tableBody = document.querySelector("#movimientos-table tbody");
const balanceEl = document.getElementById("balance");
const totalGastosEl = document.getElementById("total-gastos");
const totalIngresosEl = document.getElementById("total-ingresos");
const totalMovimientosEl = document.getElementById("total-movimientos");

const tipoFiltro = document.getElementById("tipo-filtro");
const fileInput = document.getElementById("file-input");
const btnUpload = document.getElementById("btn-upload");
const btnRefresh = document.getElementById("btn-refresh");
const btnFilter = document.getElementById("btn-filter");

async function fetchSummary() {
  const res = await fetch(`${API_BASE}/expenses/stats/summary`);
  if (!res.ok) throw new Error("No se pudo obtener resumen");
  return await res.json();
}

async function fetchMovements(tipo = "all") {
  const query = tipo === "all" ? "" : `?tipo=${tipo}`;
  const res = await fetch(`${API_BASE}/expenses${query}`);
  if (!res.ok) throw new Error("No se pudo obtener movimientos");
  return await res.json();
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(value);
}

async function renderDashboard(tipo = "all") {
  try {
    const summary = await fetchSummary();
    const stats = summary.data;
    balanceEl.textContent = formatCurrency(stats.balance);
    totalGastosEl.textContent = formatCurrency(-stats.gastos.total);
    totalIngresosEl.textContent = formatCurrency(stats.ingresos.total);
    totalMovimientosEl.textContent = stats.total_movimientos;

    const list = await fetchMovements(tipo);
    const data = list.data || [];

    tableBody.innerHTML = "";
    if (data.length === 0) {
      tableBody.innerHTML = `<tr><td colspan='5'>No hay movimientos registrados.</td></tr>`;
      return;
    }

    data.forEach((g) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${g.id}</td><td>${g.fecha}</td><td>${g.concepto}</td><td>${formatCurrency(g.importe)}</td><td>${g.origen || "n/a"}</td>`;
      tableBody.appendChild(row);
    });
  } catch (error) {
    console.error(error);
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.style.color = "#cc0022";
  }
}

async function uploadFile() {
  const file = fileInput.files[0];
  if (!file) {
    statusEl.textContent = "Selecciona un archivo (imagen o PDF).";
    statusEl.style.color = "#cc0022";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  const endpoint = file.type === "application/pdf" ? "/expenses/from-pdf" : "/expenses/from-image";

  try {
    statusEl.textContent = "Procesando...";
    statusEl.style.color = "#0a8f44";

    const res = await fetch(`${API_BASE}${endpoint}`, { method: "POST", body: formData });
    const result = await res.json();

    if (!res.ok) {
      throw new Error(result.detail || "Error en la subida");
    }

    statusEl.textContent = result.message || "Subida exitosa";
    statusEl.style.color = "#0a8f44";
    fileInput.value = "";
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.style.color = "#cc0022";
  }
}

btnUpload.addEventListener("click", uploadFile);
btnRefresh.addEventListener("click", () => renderDashboard(tipoFiltro.value));
btnFilter.addEventListener("click", () => renderDashboard(tipoFiltro.value));

// Inicial
renderDashboard();
