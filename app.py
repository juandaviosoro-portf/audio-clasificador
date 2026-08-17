import os
import uuid
import logging
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify, send_file
)
from werkzeug.utils import secure_filename

from config import Config
from models.consulta import db, Consulta
from services.transcriptor import transcribir_audio
from services.clasificador import clasificar_texto, configurar_gemini
from services.exportador import exportar_a_excel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Crear carpetas necesarias si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATABASE_FOLDER'], exist_ok=True)

    # Inicializar base de datos
    db.init_app(app)
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada correctamente.")

    # Configurar Gemini si hay API key
    if app.config['GEMINI_API_KEY']:
        configurar_gemini(app.config['GEMINI_API_KEY'])

    return app


app = crear_app()


def extension_permitida(nombre_archivo):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ==============================================
# RUTAS DE PÁGINAS
# ==============================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/historial')
def historial():
    return render_template('historial.html')


# ==============================================
# API - ANÁLISIS
# ==============================================

@app.route('/api/analizar-audio', methods=['POST'])
def analizar_audio():
    """
    Recibe un archivo de audio, lo transcribe con Whisper
    y lo clasifica con Gemini (o fallback local).
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo de audio'}), 400

    archivo = request.files['audio']

    if archivo.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    # Generar nombre único para el archivo
    extension = ''
    if archivo.filename and '.' in archivo.filename:
        extension = archivo.filename.rsplit('.', 1)[1].lower()
    else:
        extension = 'webm'  # Default para grabaciones del navegador

    if extension not in Config.ALLOWED_EXTENSIONS:
        return jsonify({
            'error': f'Formato no soportado: .{extension}. Usa: {", ".join(Config.ALLOWED_EXTENSIONS)}'
        }), 400

    nombre_unico = f"{uuid.uuid4().hex[:12]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    nombre_seguro = secure_filename(nombre_unico)
    ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)

    try:
        archivo.save(ruta_archivo)
        logger.info(f"Archivo guardado: {nombre_seguro}")

        # Transcribir con Whisper
        resultado_transcripcion = transcribir_audio(
            ruta_archivo,
            nombre_modelo=Config.WHISPER_MODEL
        )

        texto = resultado_transcripcion['texto']

        # Clasificar con IA
        resultado_clasificacion = clasificar_texto(texto, Config.GEMINI_API_KEY)

        # Guardar en base de datos
        consulta = Consulta(
            tipo_entrada='audio',
            archivo_audio=nombre_seguro,
            transcripcion=texto,
            categoria=resultado_clasificacion['categoria'],
            confianza=resultado_clasificacion['confianza'],
            prioridad=resultado_clasificacion['prioridad'],
            resumen=resultado_clasificacion['resumen'],
            duracion_audio=resultado_transcripcion.get('duracion_audio', 0),
            modelo_whisper=resultado_transcripcion.get('modelo', Config.WHISPER_MODEL)
        )
        db.session.add(consulta)
        db.session.commit()

        logger.info(f"Consulta #{consulta.id} guardada - Categoría: {consulta.categoria}")

        return jsonify({
            'id': consulta.id,
            'transcripcion': texto,
            'categoria': resultado_clasificacion['categoria'],
            'confianza': resultado_clasificacion['confianza'],
            'prioridad': resultado_clasificacion['prioridad'],
            'resumen': resultado_clasificacion['resumen'],
            'duracion_audio': resultado_transcripcion.get('duracion_audio', 0),
            'tiempo_proceso': resultado_transcripcion.get('tiempo_proceso', 0)
        })

    except Exception as e:
        logger.error(f"Error al procesar audio: {e}")
        return jsonify({'error': f'Error al procesar el audio: {str(e)}'}), 500


@app.route('/api/analizar-texto', methods=['POST'])
def analizar_texto():
    """
    Recibe un texto y lo clasifica directamente con IA.
    Útil para pruebas rápidas sin necesidad de audio.
    """
    datos = request.get_json()

    if not datos or 'texto' not in datos:
        return jsonify({'error': 'No se proporcionó texto para analizar'}), 400

    texto = datos['texto'].strip()

    if not texto:
        return jsonify({'error': 'El texto está vacío'}), 400

    if len(texto) > 5000:
        return jsonify({'error': 'El texto es demasiado largo (máx. 5000 caracteres)'}), 400

    try:
        resultado = clasificar_texto(texto, Config.GEMINI_API_KEY)

        # Guardar en base de datos
        consulta = Consulta(
            tipo_entrada='texto',
            transcripcion=texto,
            categoria=resultado['categoria'],
            confianza=resultado['confianza'],
            prioridad=resultado['prioridad'],
            resumen=resultado['resumen']
        )
        db.session.add(consulta)
        db.session.commit()

        logger.info(f"Consulta de texto #{consulta.id} guardada - Categoría: {consulta.categoria}")

        return jsonify({
            'id': consulta.id,
            'transcripcion': texto,
            'categoria': resultado['categoria'],
            'confianza': resultado['confianza'],
            'prioridad': resultado['prioridad'],
            'resumen': resultado['resumen']
        })

    except Exception as e:
        logger.error(f"Error al analizar texto: {e}")
        return jsonify({'error': f'Error al clasificar el texto: {str(e)}'}), 500


# ==============================================
# API - HISTORIAL Y ESTADÍSTICAS
# ==============================================

@app.route('/api/historial')
def api_historial():
    """Retorna el historial de consultas con filtros opcionales."""
    try:
        query = Consulta.query

        # Filtro por categoría
        categoria = request.args.get('categoria')
        if categoria and categoria != 'TODAS':
            query = query.filter(Consulta.categoria == categoria)

        # Filtro por tipo de entrada
        tipo = request.args.get('tipo')
        if tipo and tipo != 'todos':
            query = query.filter(Consulta.tipo_entrada == tipo)

        # Filtro por fecha inicio
        fecha_inicio = request.args.get('fecha_inicio')
        if fecha_inicio:
            try:
                inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                query = query.filter(Consulta.fecha >= inicio)
            except ValueError:
                pass

        # Filtro por fecha fin
        fecha_fin = request.args.get('fecha_fin')
        if fecha_fin:
            try:
                fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                fin = fin.replace(hour=23, minute=59, second=59)
                query = query.filter(Consulta.fecha <= fin)
            except ValueError:
                pass

        # Búsqueda por texto
        busqueda = request.args.get('busqueda')
        if busqueda:
            patron = f'%{busqueda}%'
            query = query.filter(
                db.or_(
                    Consulta.transcripcion.ilike(patron),
                    Consulta.resumen.ilike(patron)
                )
            )

        consultas = query.order_by(Consulta.fecha.desc()).all()

        return jsonify({
            'total': len(consultas),
            'consultas': [c.to_dict() for c in consultas]
        })

    except Exception as e:
        logger.error(f"Error al obtener historial: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard')
def api_dashboard():
    """Retorna estadísticas para el dashboard."""
    try:
        total_consultas = Consulta.query.count()
        total_audios = Consulta.query.filter_by(tipo_entrada='audio').count()
        total_textos = Consulta.query.filter_by(tipo_entrada='texto').count()

        # Distribución por categoría
        categorias = {}
        for cat in Config.CATEGORIAS:
            cantidad = Consulta.query.filter_by(categoria=cat).count()
            if cantidad > 0:
                categorias[cat] = cantidad

        # Categoría más frecuente
        cat_top = max(categorias, key=categorias.get) if categorias else 'N/A'

        # Confianza promedio
        from sqlalchemy import func
        confianza_prom = db.session.query(
            func.avg(Consulta.confianza)
        ).scalar() or 0

        # Distribución por prioridad
        prioridades = {}
        for prio in Config.PRIORIDADES:
            cantidad = Consulta.query.filter_by(prioridad=prio).count()
            if cantidad > 0:
                prioridades[prio] = cantidad

        # Últimas consultas
        ultimas = Consulta.query.order_by(
            Consulta.fecha.desc()
        ).limit(10).all()

        # Consultas por día (últimos 7 días)
        from datetime import timedelta
        hoy = datetime.utcnow().date()
        consultas_por_dia = []
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            dia_inicio = datetime.combine(dia, datetime.min.time())
            dia_fin = datetime.combine(dia, datetime.max.time())
            cantidad = Consulta.query.filter(
                Consulta.fecha >= dia_inicio,
                Consulta.fecha <= dia_fin
            ).count()
            consultas_por_dia.append({
                'fecha': dia.strftime('%d/%m'),
                'cantidad': cantidad
            })

        return jsonify({
            'total_consultas': total_consultas,
            'total_audios': total_audios,
            'total_textos': total_textos,
            'categorias': categorias,
            'categoria_top': cat_top,
            'confianza_promedio': round(confianza_prom, 1),
            'prioridades': prioridades,
            'ultimas_consultas': [c.to_dict() for c in ultimas],
            'consultas_por_dia': consultas_por_dia
        })

    except Exception as e:
        logger.error(f"Error al obtener dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/exportar')
def api_exportar():
    """Exporta el historial a un archivo Excel."""
    try:
        consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
        buffer = exportar_a_excel(consultas)

        nombre = f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            buffer,
            as_attachment=True,
            download_name=nombre,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Error al exportar: {e}")
        return jsonify({'error': str(e)}), 500


# ==============================================
# ARRANQUE
# ==============================================

if __name__ == '__main__':
    print("\n" + "=" * 55)
    print("  Sistema de Clasificación de Audios de Clientes")
    print("=" * 55)
    print(f"  Whisper modelo: {Config.WHISPER_MODEL}")
    print(f"  Gemini API:     {'Configurada' if Config.GEMINI_API_KEY else 'No configurada (modo local)'}")
    print(f"  Base de datos:  database/app.db")
    print(f"  Archivos:       uploads/")
    print("=" * 55)
    print("  Abrí tu navegador en: http://localhost:5000")
    print("=" * 55 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
