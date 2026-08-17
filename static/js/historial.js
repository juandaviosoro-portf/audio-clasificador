/* ============================================
   AudioClasifica - Historial
   ============================================ */

let todasLasConsultas = [];
let paginaActual = 1;
const porPagina = 15;

document.addEventListener('DOMContentLoaded', function() {
    cargarHistorial();

    // Listeners para filtros
    document.getElementById('filtro-busqueda').addEventListener('input', debounce(aplicarFiltros, 400));
    document.getElementById('filtro-categoria').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-tipo').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-fecha-inicio').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-fecha-fin').addEventListener('change', aplicarFiltros);
});

function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

async function cargarHistorial() {
    try {
        const resp = await fetch('/api/historial');
        const datos = await resp.json();

        if (!resp.ok) {
            throw new Error(datos.error || 'Error al cargar historial');
        }

        todasLasConsultas = datos.consultas || [];
        paginaActual = 1;
        renderizarTabla(todasLasConsultas);

    } catch (error) {
        console.error('Error cargando historial:', error);
        document.getElementById('tbody-historial').innerHTML = `
            <tr><td colspan="8" class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle me-2"></i>Error al cargar el historial
            </td></tr>`;
    }
}

function aplicarFiltros() {
    const busqueda = document.getElementById('filtro-busqueda').value.toLowerCase().trim();
    const categoria = document.getElementById('filtro-categoria').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const fechaInicio = document.getElementById('filtro-fecha-inicio').value;
    const fechaFin = document.getElementById('filtro-fecha-fin').value;

    let filtradas = todasLasConsultas.filter(c => {
        // Búsqueda de texto
        if (busqueda) {
            const texto = (c.transcripcion || '').toLowerCase() + ' ' + (c.resumen || '').toLowerCase();
            if (!texto.includes(busqueda)) return false;
        }

        // Categoría
        if (categoria && categoria !== 'TODAS' && c.categoria !== categoria) return false;

        // Tipo
        if (tipo && tipo !== 'todos' && c.tipo_entrada !== tipo) return false;

        // Fechas
        if (fechaInicio && c.fecha < fechaInicio) return false;
        if (fechaFin && c.fecha > fechaFin + ' 23:59:59') return false;

        return true;
    });

    paginaActual = 1;
    renderizarTabla(filtradas);
}

function limpiarFiltros() {
    document.getElementById('filtro-busqueda').value = '';
    document.getElementById('filtro-categoria').value = 'TODAS';
    document.getElementById('filtro-tipo').value = 'todos';
    document.getElementById('filtro-fecha-inicio').value = '';
    document.getElementById('filtro-fecha-fin').value = '';
    paginaActual = 1;
    renderizarTabla(todasLasConsultas);
}

function renderizarTabla(consultas) {
    const tbody = document.getElementById('tbody-historial');
    document.getElementById('total-resultados').textContent = consultas.length;

    if (consultas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-body-secondary py-5">
            <i class="bi bi-inbox display-6 d-block mb-2"></i>No se encontraron resultados
        </td></tr>`;
        document.getElementById('paginacion-container').innerHTML = '';
        return;
    }

    // Paginación
    const totalPaginas = Math.ceil(consultas.length / porPagina);
    const inicio = (paginaActual - 1) * porPagina;
    const fin = inicio + porPagina;
    const pagina = consultas.slice(inicio, fin);

    tbody.innerHTML = pagina.map(c => {
        const iconoTipo = c.tipo_entrada === 'audio' ? 'mic' : 'chat-text';
        const resumenCorto = (c.resumen || '—').length > 60
            ? (c.resumen || '—').substring(0, 60) + '...'
            : (c.resumen || '—');

        return `
        <tr>
            <td class="text-body-secondary">${c.id}</td>
            <td><small>${c.fecha ? c.fecha.substring(0, 16) : '—'}</small></td>
            <td><i class="bi bi-${iconoTipo} me-1"></i></td>
            <td><span class="cat-badge badge-${c.categoria}">${c.categoria}</span></td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="progress flex-grow-1" style="height: 5px; width: 50px;">
                        <div class="progress-bar ${c.confianza >= 80 ? 'bg-success' : c.confianza >= 50 ? 'bg-warning' : 'bg-danger'}" 
                             style="width: ${c.confianza}%"></div>
                    </div>
                    <small class="fw-semibold">${c.confianza}%</small>
                </div>
            </td>
            <td><span class="prio-badge badge-${c.prioridad}">${c.prioridad}</span></td>
            <td><small>${resumenCorto}</small></td>
            <td>
                <button class="btn btn-outline-primary btn-detalle" onclick='verDetalle(${JSON.stringify(c).replace(/'/g, "&#39;")})' title="Ver detalle">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        </tr>`;
    }).join('');

    // Renderizar paginación
    renderizarPaginacion(totalPaginas, consultas);
}

function renderizarPaginacion(totalPaginas, consultas) {
    const container = document.getElementById('paginacion-container');

    if (totalPaginas <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';
    
    html += `<button class="btn btn-outline-secondary btn-sm" onclick="cambiarPagina(${paginaActual - 1})" ${paginaActual === 1 ? 'disabled' : ''}>
        <i class="bi bi-chevron-left"></i>
    </button>`;

    const maxVisible = 5;
    let inicio = Math.max(1, paginaActual - Math.floor(maxVisible / 2));
    let fin = Math.min(totalPaginas, inicio + maxVisible - 1);
    inicio = Math.max(1, fin - maxVisible + 1);

    for (let i = inicio; i <= fin; i++) {
        html += `<button class="btn btn-sm ${i === paginaActual ? 'btn-primary' : 'btn-outline-secondary'}" 
                  onclick="cambiarPagina(${i})">${i}</button>`;
    }

    html += `<button class="btn btn-outline-secondary btn-sm" onclick="cambiarPagina(${paginaActual + 1})" ${paginaActual === totalPaginas ? 'disabled' : ''}>
        <i class="bi bi-chevron-right"></i>
    </button>`;

    container.innerHTML = html;

    // Guardar referencia para la paginación
    container.dataset.consultas = JSON.stringify(consultas);
}

function cambiarPagina(pagina) {
    const container = document.getElementById('paginacion-container');
    const consultas = JSON.parse(container.dataset.consultas || '[]');
    const totalPaginas = Math.ceil(consultas.length / porPagina);

    if (pagina < 1 || pagina > totalPaginas) return;

    paginaActual = pagina;
    renderizarTabla(consultas);
    
    // Scroll suave al top de la tabla
    document.getElementById('tabla-historial').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function verDetalle(consulta) {
    document.getElementById('modal-id').textContent = consulta.id;
    document.getElementById('modal-categoria').textContent = consulta.categoria;
    document.getElementById('modal-categoria').style.color = obtenerColorCategoria(consulta.categoria);
    document.getElementById('modal-confianza').textContent = consulta.confianza + '%';
    document.getElementById('modal-prioridad').textContent = consulta.prioridad;
    document.getElementById('modal-prioridad').style.color = obtenerColorPrioridad(consulta.prioridad);
    document.getElementById('modal-tipo').textContent = consulta.tipo_entrada;
    document.getElementById('modal-resumen').textContent = consulta.resumen || '—';
    document.getElementById('modal-transcripcion').textContent = consulta.transcripcion || '—';

    const modal = new bootstrap.Modal(document.getElementById('modal-detalle'));
    modal.show();
}

function obtenerColorCategoria(cat) {
    const colores = {
        'VENTAS': '#6c5ce7', 'SOPORTE': '#00b894', 'FACTURACIÓN': '#d4a017',
        'GARANTÍA': '#74b9ff', 'INFORMACIÓN': '#a29bfe', 'RECLAMO': '#e17055', 'OTRO': '#b2bec3'
    };
    return colores[cat] || '#b2bec3';
}

function obtenerColorPrioridad(prio) {
    const colores = { 'ALTA': '#e74c3c', 'MEDIA': '#f39c12', 'BAJA': '#00b894' };
    return colores[prio] || '#b2bec3';
}

async function exportarExcel() {
    try {
        const resp = await fetch('/api/exportar');
        
        if (!resp.ok) {
            throw new Error('Error al generar el Excel');
        }

        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `historial_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        // Mostrar toast
        const toast = document.getElementById('toast-notificacion');
        if (toast) {
            const cuerpo = document.getElementById('toast-mensaje');
            toast.className = 'toast align-items-center border-0 text-bg-success';
            cuerpo.textContent = 'Excel exportado correctamente';
            new bootstrap.Toast(toast).show();
        }

    } catch (error) {
        console.error('Error exportando:', error);
        const toast = document.getElementById('toast-notificacion');
        if (toast) {
            const cuerpo = document.getElementById('toast-mensaje');
            toast.className = 'toast align-items-center border-0 text-bg-danger';
            cuerpo.textContent = 'Error al exportar el Excel';
            new bootstrap.Toast(toast).show();
        }
    }
}
