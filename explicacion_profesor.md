# 🎓 Guía de Presentación del Proyecto (Para el Profesor)

Este documento está pensado para ayudarte a explicar cómo funciona tu proyecto de principio a fin durante la presentación.

---

## 1. ¿Qué es este proyecto? (El "Elevator Pitch")

Es un **Sistema Inteligente de Clasificación de Audios**. Su objetivo principal es automatizar la atención al cliente: escucha el audio de un usuario, lo convierte a texto y utiliza Inteligencia Artificial para entender la intención del cliente, clasificándolo en categorías (Ventas, Soporte, Reclamo, etc.) y asignándole una prioridad (Alta, Media, Baja).

---

## 2. Tecnologías Utilizadas (El "Stack")

Si el profesor te pregunta con qué lo hiciste, esta es la respuesta:

*   **Backend (Servidor):** Python 3.11 con el framework **Flask**. Elegido por ser rápido, ligero y excelente para integrar modelos de IA.
*   **Base de Datos:** SQLite (mediante **SQLAlchemy** como ORM). No requiere un servidor aparte y guarda todo en un archivo local (`app.db`), ideal para prototipos.
*   **Frontend (Interfaz):** HTML5, CSS3 y JavaScript (Vanilla), utilizando **Bootstrap 5** para que el diseño sea responsive (se adapte a celulares) y moderno.
*   **Modelos de Inteligencia Artificial:**
    *   **OpenAI Whisper (`base`):** Es el modelo encargado de la transcripción (*Speech-to-Text*). Escucha el audio y lo pasa a texto con alta precisión.
    *   **Google Gemini (API):** Es el modelo de Lenguaje Grande (LLM). Recibe el texto, lo analiza semánticamente y devuelve un JSON estructurado con la categoría, prioridad, nivel de confianza y un resumen.

---

## 3. Flujo de Datos (Cómo viaja la información)

Esta es la explicación técnica paso a paso de lo que ocurre cuando el usuario graba un audio:

1.  **Captura (Frontend):** El usuario graba un audio en el navegador (usando la API de `MediaRecorder` de JavaScript).
2.  **Envío (Red):** El navegador empaqueta el audio y lo envía al servidor Flask mediante una petición `POST` asíncrona (AJAX/Fetch).
3.  **Procesamiento (Backend):**
    *   El servidor guarda temporalmente el archivo en la carpeta `uploads/`.
    *   Llama al módulo `transcriptor.py`, el cual usa **Whisper** (y FFmpeg) para convertir el audio en texto.
    *   Le pasa ese texto al módulo `clasificador.py`, el cual se conecta con la API de **Gemini**. A Gemini se le envía un *Prompt* estructurado diciéndole que actúe como un clasificador estricto y devuelva solo formato JSON.
4.  **Almacenamiento (Base de Datos):** La información procesada (texto, categoría, prioridad) se guarda en SQLite usando SQLAlchemy.
5.  **Respuesta (Frontend):** El servidor devuelve los datos procesados en formato JSON al navegador, y JavaScript actualiza la pantalla sin tener que recargar la página.

---

## 4. Arquitectura de Software (Estructura)

El proyecto utiliza un patrón inspirado en **MVC (Modelo-Vista-Controlador)** para mantener el código ordenado:

*   `app.py`: Es el corazón (Controlador). Define las rutas web y las APIs.
*   `config.py`: Centraliza la configuración (variables de entorno, base de datos).
*   `models/`: (Modelo)
    *   `consulta.py`: Define cómo se guardan los datos en SQLite.
*   `services/`: (Lógica de Negocio / Servicios)
    *   `transcriptor.py`: Lógica pura de Whisper.
    *   `clasificador.py`: Lógica pura de Gemini (incluye un "Plan B" o *Fallback* que clasifica por palabras clave si no hay internet).
    *   `exportador.py`: Lógica para exportar a Excel.
*   `templates/`: (Vistas)
    *   Archivos HTML usando el motor de plantillas **Jinja2** (permite reciclar código como la barra de navegación usando `base.html`).
*   `static/`:
    *   `css/` y `js/`: Estilos visuales y scripts del navegador.

---

## 5. Puntos Fuertes del Proyecto (Para presumir)

*   **Tolerancia a fallos (*Fallback*):** Si la API de Gemini se cae o no hay internet, la aplicación no "crashea". Tiene un clasificador local que lee el texto, cuenta palabras clave y asigna una categoría para que el sistema siga funcionando.
*   **Asincronismo:** El usuario no se queda esperando frente a una pantalla congelada; se usan Promesas de JavaScript para mostrar *loaders* (ruedas de carga) mientras la IA piensa.
*   **Seguridad y Portabilidad:** Las claves (API Keys) no están quemadas en el código, se usan variables de entorno (`.env`). Además, incluye un *script* automatizado en `.bat` para instalarse en cualquier PC de forma desatendida.
