# Guía para mi presentación

Acá anoto lo más importante para acordarme qué decir cuando tenga que explicarle el proyecto al profesor.

## 1. ¿Qué es esto? (Resumen rápido)
Es un sistema diseñado para automatizar la atención al cliente. Toma un audio (o texto), lo transcribe a texto y usa inteligencia artificial (LLMs) para entender la intención del cliente. Clasifica el mensaje (ej: Venta, Soporte, Reclamo) y le asigna una prioridad para saber a quién atender primero.

## 2. Tecnologías utilizadas
Elegí estas herramientas por ser modernas y eficientes:
- **Backend:** Python con Flask. Es ideal y rápido para integrar modelos de IA.
- **Base de datos:** SQLite con SQLAlchemy (ORM). Así la base de datos es un archivo local y la app es 100% portable.
- **Frontend:** HTML5, CSS y JavaScript Vanilla, usando Bootstrap 5 para el diseño responsive.
- **Inteligencia Artificial:**
  - **Whisper (OpenAI):** Usado para *Speech-to-Text* (pasar la voz a texto localmente).
  - **Gemini (Google):** Usado para analizar la semántica del texto y devolver un JSON estructurado con la clasificación.

## 3. ¿Cómo viajan los datos? (El flujo)
1. El usuario graba un audio en el navegador usando la API de JavaScript.
2. El frontend envía el audio por POST (AJAX) al backend (`app.py`).
3. Flask le pasa el audio a Whisper, que devuelve el texto.
4. Flask le envía ese texto a la API de Gemini con un *prompt* estricto.
5. Gemini devuelve un JSON con la categoría y prioridad, Flask lo guarda en SQLite y se lo manda de vuelta al frontend para mostrarlo en pantalla.

## 4. Estructura del código (Cómo está organizado)
Para que el código sea profesional y no un "fideo", separé las responsabilidades (similar a MVC):

- **`app.py` (Controlador):** Es el corazón. Recibe las peticiones web, llama a las IAs, guarda en la base de datos y devuelve la respuesta.
- **`services/transcriptor.py`:** Se encarga exclusivamente de usar Whisper para convertir el archivo de audio en texto.
- **`services/clasificador.py`:** Se conecta con la API de Gemini enviándole el texto y estructurando su respuesta.
- **`models/consulta.py` (Modelo):** Define la estructura de las tablas de la base de datos usando SQLAlchemy.
- **`templates/` y `static/` (Vistas):** Tienen el HTML (con Jinja2), CSS y JS para la interfaz del usuario.

## 5. El detalle que suma puntos (Para presumir)
- **Tolerancia a fallos (Fallback):** Si me quedo sin internet en la presentación o la API de Gemini falla, programé un algoritmo local de respaldo. Este lee el texto, busca palabras clave y adivina la categoría, evitando que la app "crashee".
- **Despliegue automático:** Programé el script `instalar_y_ejecutar.bat` que instala Python, las dependencias y levanta el servidor con un doble clic. Así no tengo que configurar nada a mano frente al profesor.
