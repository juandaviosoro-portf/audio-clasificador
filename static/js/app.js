/* ============================================
   AudioClasifica - JavaScript Principal
   ============================================ */

// --- Variables globales ---
let archivoSeleccionado = null;
let mediaRecorder = null;
let audioChunks = [];
let grabando = false;
let tiempoInterval = null;
let segundosGrabacion = 0;
let blobGrabado = null;

// --- Utilidades ---

function mostrarToast(mensaje, tipo = 'info') {
    const toast = document.getElementById('toast-notificacion');
    const cuerpo = document.getElementById('toast-mensaje');
    
    toast.className = 'toast align-items-center border-0';
    
    const clases = {
        'success': 'text-bg-success',
        'error': 'text-bg-danger',
        'warning': 'text-bg-warning',
        'info': 'text-bg-primary'
    };
    
    toast.classList.add(clases[tipo] || clases['info']);
    cuerpo.textContent = mensaje;
    
    const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();
}

function formatearDuracion(segundos) {
    if (!segundos || segundos === 0) return '—';
    const min = Math.floor(segundos / 60);
    const seg = Math.floor(segundos % 60);
    return `${min}:${seg.toString().padStart(2, '0')}`;
}

function obtenerColorCategoria(cat) {
    const colores = {
        'VENTAS': '#6c5ce7',
        'SOPORTE': '#00b894',
        'FACTURACIÓN': '#d4a017',
        'GARANTÍA': '#74b9ff',
        'INFORMACIÓN': '#a29bfe',
        'RECLAMO': '#e17055',
        'OTRO': '#b2bec3'
    };
    return colores[cat] || '#b2bec3';
}

function obtenerColorPrioridad(prio) {
    const colores = { 'ALTA': '#e74c3c', 'MEDIA': '#f39c12', 'BAJA': '#00b894' };
    return colores[prio] || '#b2bec3';
}

// --- Drag & Drop ---

document.addEventListener('DOMContentLoaded', function() {
    const zonaDrop = document.getElementById('zona-drop');
    const inputArchivo = document.getElementById('input-archivo');

    if (!zonaDrop || !inputArchivo) return;

    zonaDrop.addEventListener('click', () => inputArchivo.click());

    zonaDrop.addEventListener('dragover', (e) => {
        e.preventDefault();
        zonaDrop.classList.add('drag-over');
    });

    zonaDrop.addEventListener('dragleave', () => {
        zonaDrop.classList.remove('drag-over');
    });

    zonaDrop.addEventListener('drop', (e) => {
        e.preventDefault();
        zonaDrop.classList.remove('drag-over');
        
        const archivos = e.dataTransfer.files;
        if (archivos.length > 0) {
            seleccionarArchivo(archivos[0]);
        }
    });

    inputArchivo.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            seleccionarArchivo(e.target.files[0]);
        }
    });

    // Contador de caracteres para textarea
    const inputTexto = document.getElementById('input-texto');
    const btnTexto = document.getElementById('btn-analizar-texto');
    
    if (inputTexto) {
        inputTexto.addEventListener('input', () => {
            const len = inputTexto.value.length;
            document.getElementById('contador-chars').textContent = len;
            btnTexto.disabled = len === 0 || len > 5000;
        });
    }
});

function seleccionarArchivo(archivo) {
    const extensiones = ['mp3', 'wav', 'ogg', 'm4a', 'webm'];
    const ext = archivo.name.split('.').pop().toLowerCase();
    
    if (!extensiones.includes(ext)) {
        mostrarToast('Formato no soportado. Usá MP3, WAV, OGG o M4A.', 'error');
        return;
    }

    if (archivo.size > 50 * 1024 * 1024) {
        mostrarToast('El archivo es muy grande. Máximo 50 MB.', 'error');
        return;
    }

    archivoSeleccionado = archivo;
    
    document.getElementById('nombre-archivo').textContent = archivo.name;
    document.getElementById('tamano-archivo').textContent = (archivo.size / (1024 * 1024)).toFixed(2) + ' MB';
    document.getElementById('archivo-seleccionado').classList.remove('d-none');
    document.getElementById('btn-analizar-audio').disabled = false;
}

function limpiarArchivo() {
    archivoSeleccionado = null;
    document.getElementById('input-archivo').value = '';
    document.getElementById('archivo-seleccionado').classList.add('d-none');
    document.getElementById('btn-analizar-audio').disabled = true;
}

// --- Análisis de Audio ---

async function analizarAudio() {
    if (!archivoSeleccionado) {
        mostrarToast('Seleccioná un archivo primero', 'warning');
        return;
    }

    mostrarLoader('Transcribiendo audio...', 'Esto puede tardar unos segundos');
    
    const formData = new FormData();
    formData.append('audio', archivoSeleccionado);

    try {
        const resp = await fetch('/api/analizar-audio', {
            method: 'POST',
            body: formData
        });

        const datos = await resp.json();

        if (!resp.ok) {
            throw new Error(datos.error || 'Error al procesar el audio');
        }

        mostrarResultados(datos);
        mostrarToast('Audio analizado correctamente', 'success');
        limpiarArchivo();

    } catch (error) {
        ocultarLoader();
        mostrarToast(error.message, 'error');
    }
}

// --- Grabación de Audio ---

async function toggleGrabacion() {
    if (grabando) {
        detenerGrabacion();
    } else {
        iniciarGrabacion();
    }
}

async function iniciarGrabacion() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                ? 'audio/webm;codecs=opus' 
                : 'audio/webm'
        });
        
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                audioChunks.push(e.data);
            }
        };

        mediaRecorder.onstop = () => {
            blobGrabado = new Blob(audioChunks, { type: 'audio/webm' });
            const url = URL.createObjectURL(blobGrabado);
            
            const player = document.getElementById('player-grabado');
            player.src = url;
            document.getElementById('audio-grabado').classList.remove('d-none');
            
            // Detener tracks del micrófono
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        grabando = true;
        segundosGrabacion = 0;

        const btnGrabar = document.getElementById('btn-grabar');
        btnGrabar.classList.add('grabando');
        document.getElementById('icono-grabar').className = 'bi bi-stop-fill';
        document.getElementById('estado-grabacion').textContent = 'Grabando...';
        document.getElementById('audio-grabado').classList.add('d-none');

        tiempoInterval = setInterval(() => {
            segundosGrabacion++;
            document.getElementById('tiempo-grabacion').textContent = formatearDuracion(segundosGrabacion);
        }, 1000);

    } catch (error) {
        mostrarToast('No se pudo acceder al micrófono. Revisá los permisos del navegador.', 'error');
    }
}

function detenerGrabacion() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    grabando = false;
    clearInterval(tiempoInterval);
    
    const btnGrabar = document.getElementById('btn-grabar');
    btnGrabar.classList.remove('grabando');
    document.getElementById('icono-grabar').className = 'bi bi-mic-fill';
    document.getElementById('estado-grabacion').textContent = 'Grabación completada';
}

async function analizarGrabacion() {
    if (!blobGrabado) {
        mostrarToast('No hay grabación para analizar', 'warning');
        return;
    }

    mostrarLoader('Procesando grabación...', 'Transcribiendo con Whisper');
    
    const formData = new FormData();
    formData.append('audio', blobGrabado, 'grabacion.webm');

    try {
        const resp = await fetch('/api/analizar-audio', {
            method: 'POST',
            body: formData
        });

        const datos = await resp.json();

        if (!resp.ok) {
            throw new Error(datos.error || 'Error al procesar la grabación');
        }

        mostrarResultados(datos);
        mostrarToast('Grabación analizada correctamente', 'success');

        // Limpiar la grabación
        blobGrabado = null;
        document.getElementById('audio-grabado').classList.add('d-none');
        document.getElementById('estado-grabacion').textContent = 'Presioná para grabar';
        document.getElementById('tiempo-grabacion').textContent = '00:00';

    } catch (error) {
        ocultarLoader();
        mostrarToast(error.message, 'error');
    }
}

// --- Análisis de Texto ---

async function analizarTexto() {
    const inputTexto = document.getElementById('input-texto');
    const texto = inputTexto.value.trim();
    
    if (!texto) {
        mostrarToast('Escribí algo para analizar', 'warning');
        return;
    }

    mostrarLoader('Clasificando texto...', 'Analizando con IA');

    try {
        const resp = await fetch('/api/analizar-texto', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: texto })
        });

        const datos = await resp.json();

        if (!resp.ok) {
            throw new Error(datos.error || 'Error al clasificar el texto');
        }

        mostrarResultados(datos);
        mostrarToast('Texto clasificado correctamente', 'success');
        inputTexto.value = '';
        document.getElementById('contador-chars').textContent = '0';
        document.getElementById('btn-analizar-texto').disabled = true;

    } catch (error) {
        ocultarLoader();
        mostrarToast(error.message, 'error');
    }
}

// --- Loader ---

function mostrarLoader(titulo, detalle) {
    document.getElementById('loader-titulo').textContent = titulo;
    document.getElementById('loader-detalle').textContent = detalle;
    document.getElementById('loader-analisis').classList.remove('d-none');
    document.getElementById('seccion-resultados').classList.add('d-none');
    document.getElementById('estado-vacio').classList.add('d-none');
}

function ocultarLoader() {
    document.getElementById('loader-analisis').classList.add('d-none');
}

// --- Resultados ---

function mostrarResultados(datos) {
    ocultarLoader();
    
    const seccion = document.getElementById('seccion-resultados');
    seccion.classList.remove('d-none');
    document.getElementById('estado-vacio').classList.add('d-none');

    // Categoría
    const resCat = document.getElementById('res-categoria');
    resCat.textContent = datos.categoria;
    resCat.style.color = obtenerColorCategoria(datos.categoria);
    
    const badgeCat = document.getElementById('badge-categoria');
    badgeCat.innerHTML = `<span class="cat-badge badge-${datos.categoria}">${datos.categoria}</span>`;

    // Confianza
    const confianza = datos.confianza || 0;
    document.getElementById('res-confianza').textContent = confianza + '%';
    
    const barra = document.getElementById('barra-confianza');
    barra.style.width = confianza + '%';
    barra.className = 'progress-bar';
    if (confianza >= 80) barra.classList.add('bg-success');
    else if (confianza >= 50) barra.classList.add('bg-warning');
    else barra.classList.add('bg-danger');

    // Prioridad
    const resPrio = document.getElementById('res-prioridad');
    resPrio.textContent = datos.prioridad;
    resPrio.style.color = obtenerColorPrioridad(datos.prioridad);

    // Duración
    const duracion = datos.duracion_audio;
    document.getElementById('res-duracion').textContent = duracion ? formatearDuracion(duracion) : 'N/A';

    // Resumen y transcripción
    document.getElementById('res-resumen').textContent = datos.resumen || '—';
    document.getElementById('res-transcripcion').textContent = datos.transcripcion || '—';

    // Re-trigger animaciones
    seccion.querySelectorAll('.slide-up').forEach(el => {
        el.style.animation = 'none';
        el.offsetHeight; // reflow
        el.style.animation = '';
    });
}
