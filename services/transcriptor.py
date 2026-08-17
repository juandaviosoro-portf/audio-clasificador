import whisper
import os
import time
import logging

logger = logging.getLogger(__name__)

_modelo_cargado = None
_nombre_modelo = None


def cargar_modelo(nombre_modelo='base'):
    """
    Carga el modelo de Whisper en memoria.
    Usa un singleton para no recargarlo en cada petición.
    """
    global _modelo_cargado, _nombre_modelo

    if _modelo_cargado is not None and _nombre_modelo == nombre_modelo:
        return _modelo_cargado

    logger.info(f"Cargando modelo Whisper '{nombre_modelo}'... esto puede tardar un momento.")
    try:
        _modelo_cargado = whisper.load_model(nombre_modelo)
        _nombre_modelo = nombre_modelo
        logger.info(f"Modelo Whisper '{nombre_modelo}' cargado correctamente.")
        return _modelo_cargado
    except Exception as e:
        logger.error(f"Error al cargar el modelo Whisper: {e}")
        raise


def transcribir_audio(ruta_archivo, nombre_modelo='base'):
    """
    Transcribe un archivo de audio usando Whisper.
    Retorna un diccionario con la transcripción, duración y modelo utilizado.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    modelo = cargar_modelo(nombre_modelo)

    logger.info(f"Transcribiendo archivo: {os.path.basename(ruta_archivo)}")
    inicio = time.time()

    try:
        resultado = modelo.transcribe(
            ruta_archivo,
            language='es',
            fp16=False  # usar fp32 para compatibilidad con CPU
        )

        duracion = time.time() - inicio
        texto = resultado.get('text', '').strip()

        if not texto:
            texto = "[No se detectó habla en el audio]"

        # Calcular la duración del audio a partir de los segmentos
        duracion_audio = 0
        segmentos = resultado.get('segments', [])
        if segmentos:
            duracion_audio = segmentos[-1].get('end', 0)

        logger.info(f"Transcripción completada en {duracion:.1f}s - {len(texto)} caracteres")

        return {
            'texto': texto,
            'duracion_audio': duracion_audio,
            'modelo': nombre_modelo,
            'tiempo_proceso': round(duracion, 2)
        }

    except Exception as e:
        logger.error(f"Error en la transcripción: {e}")
        raise Exception(f"Error al transcribir el audio: {str(e)}")
