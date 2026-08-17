import pandas as pd
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def exportar_a_excel(consultas):
    """
    Exporta una lista de consultas a un archivo Excel en memoria.
    Retorna un BytesIO listo para enviar como descarga.
    """
    if not consultas:
        # Crear un Excel vacío con las columnas esperadas
        datos = []
    else:
        datos = []
        for c in consultas:
            fila = c if isinstance(c, dict) else c.to_dict()
            datos.append({
                'ID': fila.get('id', ''),
                'Fecha': fila.get('fecha', ''),
                'Tipo': fila.get('tipo_entrada', ''),
                'Categoría': fila.get('categoria', ''),
                'Confianza (%)': fila.get('confianza', ''),
                'Prioridad': fila.get('prioridad', ''),
                'Transcripción': fila.get('transcripcion', ''),
                'Resumen': fila.get('resumen', ''),
                'Archivo': fila.get('archivo_audio', ''),
                'Duración (seg)': fila.get('duracion_audio', '')
            })

    df = pd.DataFrame(datos)

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Historial')

        # Ajustar anchos de columna
        hoja = writer.sheets['Historial']
        for i, columna in enumerate(df.columns):
            ancho_max = max(
                len(str(columna)),
                df[columna].astype(str).str.len().max() if len(df) > 0 else 0
            )
            # Limitar el ancho máximo para que no se vea raro
            ancho_max = min(ancho_max + 3, 60)
            hoja.column_dimensions[chr(65 + i)].width = ancho_max

    buffer.seek(0)
    logger.info(f"Excel generado con {len(datos)} registros")
    return buffer
