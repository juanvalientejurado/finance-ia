const API_BASE = "/api/v1";
const statusEl = document.getElementById("upload-status");
const tableStatusEl = document.getElementById("table-status");
const tableBody = document.querySelector("#movimientos-table tbody");
const balanceEl = document.getElementById("balance");
const totalGastosEl = document.getElementById("total-gastos");
const totalIngresosEl = document.getElementById("total-ingresos");
const totalMovimientosEl = document.getElementById("total-movimientos");

const tipoFiltro = document.getElementById("tipo-filtro");
const selectAllCheckbox = document.getElementById("select-all");
const btnDeleteSelected = document.getElementById("btn-delete-selected");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const btnUpload = document.getElementById("btn-upload");
const btnRefresh = document.getElementById("btn-refresh");
const btnFilter = document.getElementById("btn-filter");

const panels = document.querySelectorAll(".panel");
const tabButtons = document.querySelectorAll(".tab");
const editPanel = document.getElementById("edit-panel");
const editForm = document.getElementById("edit-form");
const editFields = {
  id: null,
  fecha: document.getElementById("edit-fecha"),
  concepto: document.getElementById("edit-concepto"),
  importe: document.getElementById("edit-importe"),
  origen: document.getElementById("edit-origen"),
};
const editCancel = document.getElementById("edit-cancel");
let currentView = "dashboard";

function openTab(tabName) {
  currentView = tabName;
  panels.forEach((p) => p.classList.toggle("active", p.id === tabName));
  tabButtons.forEach((b) => b.classList.toggle("active", b.dataset.tab === tabName));
  if (tabName === "dashboard" || tabName === "details") {
    renderDashboard(tipoFiltro.value);
  }
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => openTab(button.dataset.tab));
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = event.dataTransfer.files[0];
  if (file) {
    fileInput.files = event.dataTransfer.files;
    statusEl.textContent = `Archivo listo: ${file.name}`;
    statusEl.style.color = "#0a8f44";
  }
});

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
    const saldoTotal = stats.balance;

    balanceEl.textContent = formatCurrency(stats.balance);
    totalGastosEl.textContent = formatCurrency(-stats.gastos.total);
    totalIngresosEl.textContent = formatCurrency(stats.ingresos.total);
    totalMovimientosEl.textContent = stats.total_movimientos;
    document.getElementById("saldo-total").textContent = formatCurrency(saldoTotal);

    const balanceCard = document.getElementById("card-balance");
    const saldoCard = document.getElementById("card-saldo-cuenta");
    const colorClass = saldoTotal >= 0 ? "positive" : "negative";
    balanceCard.classList.toggle("positive", saldoTotal >= 0);
    balanceCard.classList.toggle("negative", saldoTotal < 0);
    saldoCard.classList.toggle("positive", saldoTotal >= 0);
    saldoCard.classList.toggle("negative", saldoTotal < 0);

    await renderMovements(tipo);
  } catch (error) {
    console.error(error);
    tableStatusEl.textContent = `Error al cargar resumen: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
  }
}

async function renderMovements(tipo = "all") {
  try {
    const list = await fetchMovements(tipo);
    const data = list.data || [];

    tableBody.innerHTML = "";
    tableStatusEl.textContent = "";

    if (data.length === 0) {
      tableBody.innerHTML = `<tr><td colspan='6'>No hay movimientos registrados.</td></tr>`;
      return;
    }

    data.forEach((g) => {
      const row = document.createElement("tr");
      row.className = g.importe >= 0 ? "positive-row" : "negative-row";
      row.innerHTML = `
        <td class="select-row"><input type="checkbox" class="check-select" data-id="${g.id}"></td>
        <td>${g.id}</td>
        <td>${g.fecha}</td>
        <td>${g.concepto}</td>
        <td>${formatCurrency(g.importe)}</td>
        <td>${g.origen || "-"}</td>
        <td>
          <button class="action-btn edit" data-id="${g.id}">Editar</button>
          <button class="action-btn delete" data-id="${g.id}">Eliminar</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    tableBody.querySelectorAll(".edit").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        const item = (list.data || []).find((x) => String(x.id) === String(id));
        if (!item) return;
        editFields.id = id;
        editFields.fecha.value = item.fecha;
        editFields.concepto.value = item.concepto;
        editFields.importe.value = item.importe;
        editFields.origen.value = item.origen || "";
        editPanel.hidden = false;
        editFields.fecha.focus();
      });
    });

    selectAllCheckbox.checked = false;

    tableBody.querySelectorAll(".delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!window.confirm("¿Eliminar este movimiento?")) return;
        const id = btn.dataset.id;
        await deleteMovement(id);
      });
    });
  } catch (error) {
    console.error(error);
    tableStatusEl.textContent = `Error al cargar movimientos: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
  }
}

async function deleteMovement(id) {
  try {
    const res = await fetch(`${API_BASE}/expenses/${id}`, { method: "DELETE" });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudo eliminar");
    }

    tableStatusEl.textContent = data.message || "Movimiento eliminado";
    tableStatusEl.style.color = "#0a8f44";
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    tableStatusEl.textContent = `Error: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
  }
}

async function deleteSelectedMovements(ids = []) {
  try {
    const res = await fetch(`${API_BASE}/expenses/batch-delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids }),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudieron eliminar los movimientos");
    }

    tableStatusEl.textContent = data.message || "Movimientos eliminados";
    tableStatusEl.style.color = "#0a8f44";
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    tableStatusEl.textContent = `Error: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
  }
}

async function updateMovement(payload) {
  try {
    const res = await fetch(`${API_BASE}/expenses/${payload.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudo actualizar");
    }

    tableStatusEl.textContent = data.message || "Movimiento actualizado";
    tableStatusEl.style.color = "#0a8f44";
    editPanel.hidden = true;
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    tableStatusEl.textContent = `Error: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
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
      throw new Error(result.detail || result.message || "Error en la subida");
    }

    statusEl.textContent = result.message || "Subida exitosa";
    statusEl.style.color = "#0a8f44";
    fileInput.value = "";
    await renderDashboard(tipoFiltro.value);
    openTab("details");
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.style.color = "#cc0022";
  }
}

btnUpload.addEventListener("click", uploadFile);
btnRefresh.addEventListener("click", () => renderDashboard(tipoFiltro.value));
tipoFiltro.addEventListener("change", () => renderMovements(tipoFiltro.value));
btnFilter.addEventListener("click", () => renderMovements(tipoFiltro.value));
selectAllCheckbox.addEventListener("change", () => {
  const checked = selectAllCheckbox.checked;
  tableBody.querySelectorAll(".check-select").forEach((input) => {
    input.checked = checked;
  });
});

btnDeleteSelected.addEventListener("click", async () => {
  const selected = Array.from(tableBody.querySelectorAll(".check-select:checked")).map((c) => Number(c.dataset.id));
  if (selected.length === 0) {
    tableStatusEl.textContent = "Selecciona al menos un gasto para eliminar.";
    tableStatusEl.style.color = "#cc0022";
    return;
  }
  if (!window.confirm(`Eliminar ${selected.length} gastos seleccionados?`)) return;
  await deleteSelectedMovements(selected);
});

editForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!editFields.id) return;

  const payload = {
    id: Number(editFields.id),
    fecha: editFields.fecha.value,
    concepto: editFields.concepto.value,
    importe: Number(editFields.importe.value),
    origen: editFields.origen.value || null,
    saldo: null,
    archivo: null,
  };

  updateMovement(payload);
});

editCancel.addEventListener("click", () => {
  editPanel.hidden = true;
});

openTab("dashboard");
