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
const btnReclassify = document.getElementById("btn-reclassify");
const manualForm = document.getElementById("manual-form");
const manualStatus = document.getElementById("manual-status");
const manualFecha = document.getElementById("manual-fecha");
const manualConcepto = document.getElementById("manual-concepto");
const manualCategoria = document.getElementById("manual-categoria");
const manualImporte = document.getElementById("manual-importe");
const manualOrigen = document.getElementById("manual-origen");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const btnUpload = document.getElementById("btn-upload");
const btnRefresh = document.getElementById("btn-refresh");
const btnFilter = document.getElementById("btn-filter");
let currentCategoryFilter = null;

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
  categoria: document.getElementById("edit-categoria"),
  saldo: null,
  archivo: null,
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

function getNormalizedCategory(categoria) {
  return categoria && String(categoria).trim() ? String(categoria).trim().toLowerCase() : "otros";
}

function applyCategoryFilter(categoria) {
  if (currentCategoryFilter === categoria) {
    currentCategoryFilter = null;
    tableStatusEl.textContent = "Filtro de categoría desactivado.";
  } else {
    currentCategoryFilter = categoria;
    tableStatusEl.textContent = `Filtrando categoría: ${categoria}`;
  }

  const chartRoot = document.getElementById("category-chart");
  if (chartRoot) {
    chartRoot.querySelectorAll(".pie-legend-item").forEach((item) => {
      item.classList.toggle("selected", item.dataset.category === currentCategoryFilter);
    });
  }

  renderMovements(tipoFiltro.value);
}

function renderCategoryChart(data) {
  const chartRoot = document.getElementById("category-chart");
  if (!chartRoot) return;

  if (!data || data.length === 0) {
    chartRoot.innerHTML = `<div class="category-empty">No hay datos para mostrar.</div>`;
    return;
  }

  const totals = data.reduce((acc, item) => {
    const categoria = getNormalizedCategory(item.categoria);
    const importe = Number(item.importe) || 0;
    acc[categoria] = (acc[categoria] || 0) + Math.abs(importe);
    return acc;
  }, {});

  const entries = Object.entries(totals)
    .filter(([, value]) => value > 0)
    .sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    chartRoot.innerHTML = `<div class="category-empty">No hay movimientos con importe válido.</div>`;
    return;
  }

  const totalAmount = entries.reduce((sum, [, value]) => sum + value, 0);
  const visibleEntries = entries.slice(0, 8);
  const remaining = entries.slice(8);

  if (remaining.length > 0) {
    const remainingTotal = remaining.reduce((sum, [, value]) => sum + value, 0);
    visibleEntries.push(["otros", remainingTotal]);
  }

  const colors = [
    "#3b76f6",
    "#2a9d8f",
    "#fca311",
    "#e63946",
    "#8d99ae",
    "#9d4edd",
    "#f77f00",
    "#4361ee",
  ];

  let startAngle = 0;
  const radius = 80;
  const cx = 90;
  const cy = 90;

  const slices = visibleEntries
    .map(([categoria, value], index) => {
      const percentage = totalAmount ? value / totalAmount : 0;
      const sliceAngle = percentage * Math.PI * 2;
      const endAngle = startAngle + sliceAngle;
      const x1 = cx + radius * Math.cos(startAngle);
      const y1 = cy + radius * Math.sin(startAngle);
      const x2 = cx + radius * Math.cos(endAngle);
      const y2 = cy + radius * Math.sin(endAngle);
      const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;
      const pathData = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
      startAngle = endAngle;
      return `
        <path d="${pathData}" fill="${colors[index % colors.length]}" />
      `;
    })
    .join("");

  const legendItems = visibleEntries
    .map(([categoria, value], index) => {
      const porcentaje = totalAmount ? Math.round((value / totalAmount) * 100) : 0;
      return `
        <div class="pie-legend-item" data-category="${categoria}">
          <span class="pie-swatch" style="background:${colors[index % colors.length]}"></span>
          <span class="pie-category">${categoria}</span>
          <span class="pie-value">${porcentaje}%</span>
        </div>
      `;
    })
    .join("");

  chartRoot.innerHTML = `
    <div class="pie-chart-wrapper">
      <svg viewBox="0 0 180 180" class="pie-chart-svg" aria-label="Gráfico de categorías">
        ${slices}
      </svg>
      <div class="pie-legend">${legendItems}</div>
    </div>
  `;

  chartRoot.querySelectorAll(".pie-legend-item").forEach((item) => {
    item.addEventListener("click", () => {
      const category = item.dataset.category;
      applyCategoryFilter(category);
    });
  });
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
    let data = list.data || [];

    tableBody.innerHTML = "";
    tableStatusEl.textContent = "";

    if (currentCategoryFilter) {
      const normalized = currentCategoryFilter.toLowerCase();
      data = data.filter((g) => getNormalizedCategory(g.categoria) === normalized);
      tableStatusEl.textContent = `Filtrando categoría: ${currentCategoryFilter}`;
    }

    if (data.length === 0) {
      tableBody.innerHTML = `<tr><td colspan='7'>No hay movimientos registrados.</td></tr>`;
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
        <td class="categoria-cell" data-id="${g.id}">${g.categoria || '<span class="categoria-placeholder">Sin categoría</span>'}</td>
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
        editFields.categoria.value = item.categoria || "";
        editFields.saldo = item.saldo || null;
        editFields.archivo = item.archivo || null;
        editPanel.hidden = false;
        editFields.fecha.focus();
      });
    });

    selectAllCheckbox.checked = false;
    renderCategoryChart(data);

    tableBody.querySelectorAll(".delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!window.confirm("¿Eliminar este movimiento?")) return;
        const id = btn.dataset.id;
        await deleteMovement(id);
      });
    });

    tableBody.querySelectorAll(".categoria-cell").forEach((cell) => {
      cell.addEventListener("click", () => {
        const id = cell.dataset.id;
        // Obtener el texto actual, manejando el caso del placeholder
        let currentText = "";
        if (cell.querySelector('.categoria-placeholder')) {
          currentText = ""; // Está vacío
        } else {
          currentText = cell.textContent.trim();
        }
        
        // Crear input
        const input = document.createElement("input");
        input.type = "text";
        input.value = currentText;
        input.className = "categoria-input";
        input.dataset.id = id;
        
        // Reemplazar celda con input
        cell.innerHTML = "";
        cell.appendChild(input);
        input.focus();
        input.select();
        
        const saveAndClose = async () => {
          const nuevaCategoria = input.value.trim();
          cell.innerHTML = nuevaCategoria || '<span class="categoria-placeholder">Sin categoría</span>';
          
          if (nuevaCategoria !== currentText) {
            await reclassifyMovement(id, nuevaCategoria);
          }
        };
        
        const cancelAndClose = () => {
          cell.innerHTML = currentText || '<span class="categoria-placeholder">Sin categoría</span>';
        };
        
        input.addEventListener("blur", saveAndClose);
        input.addEventListener("keydown", (e) => {
          if (e.key === "Enter") {
            saveAndClose();
          } else if (e.key === "Escape") {
            cancelAndClose();
          }
        });
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

async function reclassifyMovement(id, categoria) {
  try {
    const res = await fetch(`${API_BASE}/expenses/${id}/reclassify`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categoria }),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudo reclasificar");
    }

    tableStatusEl.textContent = data.message || "Movimiento reclasificado";
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

async function createMovement(payload) {
  try {
    const res = await fetch(`${API_BASE}/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudo crear el movimiento");
    }
    manualStatus.textContent = data.message || "Movimiento agregado";
    manualStatus.style.color = "#0a8f44";
    manualForm.reset();
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    manualStatus.textContent = `Error: ${error.message}`;
    manualStatus.style.color = "#cc0022";
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
    categoria: editFields.categoria.value || null,
    saldo: editFields.saldo,
    archivo: editFields.archivo,
  };

  updateMovement(payload);
});

manualForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = {
    fecha: manualFecha.value,
    concepto: manualConcepto.value,
    importe: Number(manualImporte.value),
    origen: manualOrigen.value || null,
    categoria: manualCategoria.value || null,
    saldo: null,
    archivo: null,
  };
  createMovement(payload);
});

btnReclassify.addEventListener("click", async () => {
  try {
    const res = await fetch(`${API_BASE}/expenses/reclassify`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || data.message || "No se pudo reclasificar");
    }
    tableStatusEl.textContent = data.message || "Reclasificación completada";
    tableStatusEl.style.color = "#0a8f44";
    await renderDashboard(tipoFiltro.value);
  } catch (error) {
    tableStatusEl.textContent = `Error: ${error.message}`;
    tableStatusEl.style.color = "#cc0022";
  }
});

editCancel.addEventListener("click", () => {
  editPanel.hidden = true;
});

openTab("dashboard");
