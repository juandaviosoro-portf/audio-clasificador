import json
import re
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

_modelo_gemini = None

# Palabras clave para el clasificador de respaldo (sin API)
PALABRAS_CLAVE = {
    'VENTAS': [
        'comprar', 'precio', 'costo', 'cotización', 'cotizar', 'catálogo',
        'producto', 'oferta', 'descuento', 'promoción', 'vender', 'adquirir',
        'pedido', 'orden', 'presupuesto', 'tarifa', 'disponible', 'stock'
    ],
    'SOPORTE': [
        'ayuda', 'problema', 'error', 'falla', 'no funciona', 'soporte',
        'técnico', 'reparar', 'arreglar', 'configurar', 'instalar',
        'actualizar', 'reiniciar', 'lento', 'bloqueado', 'caído'
    ],
    'FACTURACIÓN': [
        'factura', 'pago', 'cobro', 'recibo', 'cuenta', 'estado de cuenta',
        'cargo', 'débito', 'crédito', 'mensualidad', 'cuota', 'deuda',
        'vencimiento', 'mora', 'saldo', 'reembolso', 'devolución dinero'
    ],
    'GARANTÍA': [
        'garantía', 'defecto', 'cambio', 'reemplazo', 'dañado', 'roto',
        'defectuoso', 'malogrado', 'cobertura', 'póliza', 'vigencia',
        'reclamar garantía', 'aplica garantía'
    ],
    'INFORMACIÓN': [
        'información', 'horario', 'dirección', 'ubicación', 'teléfono',
        'contacto', 'sucursal', 'sede', 'saber', 'consulta', 'pregunta',
        'cómo funciona', 'requisitos', 'documentos', 'trámite'
    ],
    'RECLAMO': [
        'reclamo', 'queja', 'inconformidad', 'molesto', 'enojado',
        'insatisfecho', 'mal servicio', 'pésimo', 'inaceptable', 'abuso',
        'denuncia', 'negligencia', 'incumplimiento', 'demanda', 'fraude'
    ]
}


def configurar_gemini(api_key):
    """Configura la conexión con Gemini."""
    global _modelo_gemini

    if not api_key:
        logger.warning("No se proporcionó API key de Gemini. Se usará clasificador local.")
        return False

    try:
        genai.configure(api_key=api_key)
        _modelo_gemini = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Gemini configurado correctamente.")
        return True
    except Exception as e:
        logger.error(f"Error al configurar Gemini: {e}")
        return False


def clasificar_con_gemini(texto):
    """
    Clasifica el texto utilizando la API de Gemini.
    Envía un prompt estructurado y parsea la respuesta JSON.
    """
    if _modelo_gemini is None:
        raise Exception("Gemini no está configurado")

    prompt = f"""Analiza el siguiente texto de un cliente y clasifícalo.

TEXTO DEL CLIENTE:
\"{texto}\"

Debes responder ÚNICAMENTE con un JSON válido (sin markdown, sin texto adicional) con esta estructura exacta:
{{
    "categoria": "UNA_DE_ESTAS: VENTAS, SOPORTE, FACTURACIÓN, GARANTÍA, INFORMACIÓN, RECLAMO, OTRO",
    "confianza": NUMERO_ENTERO_DE_0_A_100,
    "prioridad": "UNA_DE_ESTAS: ALTA, MEDIA, BAJA",
    "resumen": "Resumen breve de máximo 2 oraciones describiendo lo que solicita el cliente"
}}

Criterios para la prioridad:
- ALTA: El cliente tiene un problema urgente, está molesto, o necesita atención inmediata
- MEDIA: Consulta normal que requiere seguimiento
- BAJA: Consulta informativa o de baja urgencia

Criterios para la categoría:
- VENTAS: Consultas sobre precios, productos, compras, cotizaciones
- SOPORTE: Problemas técnicos, errores, fallas, ayuda con el servicio
- FACTURACIÓN: Pagos, facturas, cobros, estados de cuenta
- GARANTÍA: Garantías, defectos, cambios, reemplazos de productos
- INFORMACIÓN: Consultas generales, horarios, ubicaciones, requisitos
- RECLAMO: Quejas, inconformidades, mal servicio
- OTRO: No encaja en ninguna categoría anterior"""

    try:
        respuesta = _modelo_gemini.generate_content(prompt)
        texto_respuesta = respuesta.text.strip()

        # Limpiar posibles bloques de código markdown
        texto_respuesta = re.sub(r'^```(?:json)?\s*', '', texto_respuesta)
        texto_respuesta = re.sub(r'\s*```$', '', texto_respuesta)
        texto_respuesta = texto_respuesta.strip()

        resultado = json.loads(texto_respuesta)

        # Validar que tenga los campos esperados
        categorias_validas = ['VENTAS', 'SOPORTE', 'FACTURACIÓN', 'GARANTÍA',
                              'INFORMACIÓN', 'RECLAMO', 'OTRO']
        prioridades_validas = ['ALTA', 'MEDIA', 'BAJA']

        categoria = resultado.get('categoria', 'OTRO').upper()
        if categoria not in categorias_validas:
            categoria = 'OTRO'

        confianza = resultado.get('confianza', 50)
        if not isinstance(confianza, (int, float)):
            confianza = 50
        confianza = max(0, min(100, int(confianza)))

        prioridad = resultado.get('prioridad', 'MEDIA').upper()
        if prioridad not in prioridades_validas:
            prioridad = 'MEDIA'

        resumen = resultado.get('resumen', 'Sin resumen disponible')

        return {
            'categoria': categoria,
            'confianza': confianza,
            'prioridad': prioridad,
            'resumen': resumen
        }

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear respuesta de Gemini: {e}")
        logger.debug(f"Respuesta recibida: {texto_respuesta}")
        # Si Gemini responde pero no en JSON válido, usar fallback
        return clasificar_local(texto)
    except Exception as e:
        logger.error(f"Error al clasificar con Gemini: {e}")
        raise


def clasificar_local(texto):
    """
    Clasificador de respaldo basado en palabras clave.
    Se usa cuando Gemini no está disponible o falla.
    """
    texto_lower = texto.lower()
    puntuaciones = {}

    for categoria, palabras in PALABRAS_CLAVE.items():
        puntaje = 0
        for palabra in palabras:
            if palabra in texto_lower:
                puntaje += 1
        puntuaciones[categoria] = puntaje

    mejor_categoria = max(puntuaciones, key=puntuaciones.get)
    mejor_puntaje = puntuaciones[mejor_categoria]

    # Si no hay coincidencias claras, clasificar como OTRO
    if mejor_puntaje == 0:
        return {
            'categoria': 'OTRO',
            'confianza': 30,
            'prioridad': 'BAJA',
            'resumen': 'No se pudo determinar la intención del cliente con certeza (clasificación local)'
        }

    # Calcular confianza basada en la cantidad de coincidencias
    total_palabras_cat = len(PALABRAS_CLAVE[mejor_categoria])
    confianza = min(85, int((mejor_puntaje / max(total_palabras_cat, 1)) * 100) + 40)

    # Determinar prioridad basada en la categoría
    prioridades_por_cat = {
        'RECLAMO': 'ALTA',
        'SOPORTE': 'ALTA',
        'GARANTÍA': 'MEDIA',
        'FACTURACIÓN': 'MEDIA',
        'VENTAS': 'MEDIA',
        'INFORMACIÓN': 'BAJA',
        'OTRO': 'BAJA'
    }

    return {
        'categoria': mejor_categoria,
        'confianza': confianza,
        'prioridad': prioridades_por_cat.get(mejor_categoria, 'MEDIA'),
        'resumen': f'Cliente con consulta relacionada a {mejor_categoria.lower()} (clasificación local)'
    }


def clasificar_texto(texto, api_key=None):
    """
    Función principal de clasificación.
    Intenta con Gemini primero, y si no está disponible usa el clasificador local.
    """
    if not texto or not texto.strip():
        return {
            'categoria': 'OTRO',
            'confianza': 0,
            'prioridad': 'BAJA',
            'resumen': 'No se proporcionó texto para analizar'
        }

    # Intentar con Gemini si hay API key
    if api_key and api_key.strip():
        configurar_gemini(api_key)

    if _modelo_gemini is not None:
        try:
            return clasificar_con_gemini(texto)
        except Exception as e:
            logger.warning(f"Gemini falló, usando clasificador local: {e}")
            return clasificar_local(texto)
    else:
        logger.info("Usando clasificador local (sin API key de Gemini)")
        return clasificar_local(texto)
