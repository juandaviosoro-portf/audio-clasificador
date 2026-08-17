# 🎙️ AudioClasifica

Un proyecto que hice para clasificar automáticamente qué quieren los clientes usando audios o texto. Básicamente: escucha (o lee) al cliente y te dice si es una queja, una venta, una duda, etc.

---

## ⚡ ¿Qué hace?

1. Grabás un audio (o lo escribís).
2. El sistema lo pasa a texto usando **Whisper**.
3. Se lo manda a **Gemini** (la IA de Google) para que analice la intención.
4. Te dice si es urgente o no y te hace un resumen.
5. Guarda todo en un historial que podés ver en gráficos o bajar en Excel.

---

## 🛠️ Cómo instalarlo y usarlo

Hice un script para que sea súper fácil de correr en cualquier PC con Windows.

### Requisitos previos
Solo necesitás tener instalado **Python** (acordate de marcar la casilla "Add Python to PATH" cuando lo instales).

### Pasos

1. Cloná o descargá este repositorio.
2. Hacé **doble clic en `instalar_y_ejecutar.bat`**.
3. La primera vez va a tardar un ratito descargando todo (Whisper, Flask, etc.). Dejalo que termine.
4. Cuando termine, te va a abrir el navegador en `http://localhost:5000`.

### El tema de la API Key (Importante)
Para que Gemini funcione y sea preciso, necesitás poner tu clave de Google.
- El script `.bat` te crea un archivo llamado `.env`.
- Abrilo con el Bloc de notas y pegá tu clave de Gemini donde dice `GEMINI_API_KEY=...`
- Si no le ponés clave, el sistema igual funciona pero usando un clasificador básico por palabras clave (menos inteligente).

---

## 📂 Archivos principales

Para que se entienda rápido cómo armé el código:

- `app.py`: Es el archivo principal que levanta el servidor web.
- `services/transcriptor.py`: Acá está la lógica de Whisper para pasar de audio a texto.
- `services/clasificador.py`: Acá me conecto con Gemini para que lea el texto y lo clasifique.
- `instalar_y_ejecutar.bat`: El script mágico que automatiza toda la instalación para no tener que escribir comandos.

---

Si tienen problemas instalando Whisper, prueben instalando FFmpeg (`winget install ffmpeg` en la terminal) y reinicien.
