# Guía para mi presentación

Acá anoto lo más importante para acordarme qué decir cuando tenga que presentar el proyecto.

## 1. ¿Qué es esto? (Resumen rápido)
Es un sistema que hice para automatizar la atención al cliente. Básicamente, agarra un audio (o texto), lo lee, y usa inteligencia artificial para entender qué quiere el cliente. Te dice si es una venta, un reclamo, soporte, y además te marca la prioridad para saber a quién atender primero.

## 2. ¿Con qué lo armé? (Tecnologías)
- **Backend:** Usé Python con Flask porque es súper rápido para armar servidores y se lleva muy bien con las librerías de IA.
- **Base de datos:** SQLite. No quería complicarme armando un servidor SQL aparte, así que guardo todo local para que la app sea fácil de mover.
- **Frontend:** HTML, CSS y JavaScript puro con Bootstrap para que se vea lindo y moderno sin volverme loco con los estilos.
- **La IA:**
  - **Whisper (OpenAI):** Este es el modelo que pasa la voz a texto. Es gratis y súper preciso.
  - **Gemini (Google):** A esta API le mando el texto y le pido que analice la intención y me devuelva un JSON con la categoría y la prioridad.

## 3. ¿Cómo es el recorrido del dato?
1. El usuario graba en la web.
2. El navegador le manda ese archivo a Flask.
3. Flask llama a Whisper para sacar el texto.
4. Flask le manda el texto a Gemini.
5. Gemini me devuelve la respuesta, la guardo en la base de datos y se la muestro al usuario sin tener que recargar la página (usando JavaScript asíncrono).

## 4. ¿Cómo ordené el código?
Traté de separarlo un poco estilo MVC para que no sea un fideo:
- `app.py` tiene las rutas principales.
- En la carpeta `services/` metí toda la lógica pesada separada: `transcriptor.py` (lo de Whisper) y `clasificador.py` (lo de Gemini).
- Y en `templates/` y `static/` están las vistas de la web.

## 5. El detalle que suma puntos
- **El Plan B (Fallback):** Si se me cae el internet o la API de Gemini falla en la presentación, armé un sistema básico que cuenta palabras clave y trata de adivinar la categoría igual. Así la app no se rompe nunca.
- **Fácil instalación:** Armé un script (`instalar_y_ejecutar.bat`) que instala Python, las librerías, levanta el servidor y abre el navegador con un solo doble clic. Ideal para no estar escribiendo comandos frente a todo el mundo.
