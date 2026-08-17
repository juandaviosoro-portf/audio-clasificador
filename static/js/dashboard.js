/* ============================================
   AudioClasifica - Dashboard
   ============================================ */

let chartCategorias = null;
let chartTendencia = null;

const COLORES_CATEGORIAS = {
    'VENTAS': '#6c5ce7',
    'SOPORTE': '#00b894',
    'FACTURACIÓN': '#fdcb6e',
    'GARANTÍA': '#74b9ff',
    'INFORMACIÓN': '#a29bfe',
    'RECLAMO': '#e17055',
    'OTRO': '#b2bec3'
};

document.addEventListener('DOMContentLoaded', cargarDashboard);

async function cargarDashboard() {
    try {
        const resp = await fetch('/api/dashboard');
        const datos = await resp.json();

        if (!resp.ok) {
            throw new Error(datos.error || 'Error al cargar el dashboard');
        }

        actualizarKPIs(datos);
        renderizarGraficoCategorias(datos.categorias);
        renderizarGraficoTendencia(datos.consultas_por_dia);
        actualizarPrioridades(datos.prioridades, datos.total_consultas);
        renderizarUltimasConsultas(datos.ultimas_consultas);

    } catch (error) {
        console.error('Error cargando dashboard:', error);
    }
}

function actualizarKPIs(datos) {
    animarNumero('kpi-total', datos.total_consultas);
    animarNumero('kpi-audios', datos.total_audios);
    
    document.getElementById('kpi-top-cat').textContent = datos.categoria_top;
    document.getElementById('kpi-confianza').textContent = datos.confianza_promedio + '%';
}

function animarNumero(elementoId, valorFinal) {
    const el = document.getElementById(elementoId);
    const duracion = 800;
    const inicio = performance.now();
    const valorInicial = 0;

    function step(timestamp) {
        const progreso = Math.min((timestamp - inicio) / duracion, 1);
        const eased = 1 - Math.pow(1 - progreso, 3); // easeOutCubic
        el.textContent = Math.round(valorInicial + (valorFinal - valorInicial) * eased);
        
        if (progreso < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

function renderizarGraficoCategorias(categorias) {
    const canvas = document.getElementById('chart-categorias');
    const sinDatos = document.getElementById('sin-datos-categorias');

    if (!categorias || Object.keys(categorias).length === 0) {
        canvas.style.display = 'none';
        sinDatos.classList.remove('d-none');
        return;
    }

    canvas.style.display = 'block';
    sinDatos.classList.add('d-none');

    const labels = Object.keys(categorias);
    const valores = Object.values(categorias);
    const colores = labels.map(l => COLORES_CATEGORIAS[l] || '#b2bec3');

    if (chartCategorias) chartCategorias.destroy();

    chartCategorias = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: colores,
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                        font: { family: "'Inter', sans-serif", size: 12 }
                    }
                }
            }
        }
    });
}

function renderizarGraficoTendencia(datos) {
    const canvas = document.getElementById('chart-tendencia');

    if (!datos || datos.length === 0) return;

    const labels = datos.map(d => d.fecha);
    const valores = datos.map(d => d.cantidad);

    if (chartTendencia) chartTendencia.destroy();

    const ctx = canvas.getContext('2d');
    const gradiente = ctx.createLinearGradient(0, 0, 0, 280);
    gradiente.addColorStop(0, 'rgba(108, 92, 231, 0.3)');
    gradiente.addColorStop(1, 'rgba(108, 92, 231, 0.0)');

    chartTendencia = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Consultas',
                data: valores,
                borderColor: '#6c5ce7',
                backgroundColor: gradiente,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#6c5ce7',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: { family: "'Inter', sans-serif", size: 11 }
                    },
                    grid: { color: 'rgba(128,128,128,0.1)' }
                },
                x: {
                    ticks: {
                        font: { family: "'Inter', sans-serif", size: 11 }
                    },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function actualizarPrioridades(prioridades, total) {
    if (!prioridades || total === 0) return;

    const alta = prioridades['ALTA'] || 0;
    const media = prioridades['MEDIA'] || 0;
    const baja = prioridades['BAJA'] || 0;

    document.getElementById('prio-alta').textContent = alta;
    document.getElementById('prio-media').textContent = media;
    document.getElementById('prio-baja').textContent = baja;

    document.getElementById('prio-alta-bar').style.width = (alta / total * 100) + '%';
    document.getElementById('prio-media-bar').style.width = (media / total * 100) + '%';
    document.getElementById('prio-baja-bar').style.width = (baja / total * 100) + '%';
}

function renderizarUltimasConsultas(consultas) {
    const tbody = document.getElementById('tbody-ultimas');

    if (!consultas || consultas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-body-secondary py-4">
            <i class="bi bi-inbox me-2"></i>No hay consultas todavía</td></tr>`;
        return;
    }

    tbody.innerHTML = consultas.map(c => `
        <tr>
            <td><small>${c.fecha ? c.fecha.substring(5, 16) : '—'}</small></td>
            <td><i class="bi bi-${c.tipo_entrada === 'audio' ? 'mic' : 'chat-text'} me-1"></i>${c.tipo_entrada}</td>
            <td><span class="cat-badge badge-${c.categoria}">${c.categoria}</span></td>
            <td><strong>${c.confianza}%</strong></td>
            <td><span class="prio-badge badge-${c.prioridad}">${c.prioridad}</span></td>
        </tr>
    `).join('');
}
