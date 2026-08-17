# 🎙️ AudioClasifica

Un sistema que armé para escuchar (o leer) los mensajes de los clientes y clasificarlos automáticamente con inteligencia artificial. Sirve para saber si un cliente tiene una queja, una duda de ventas o necesita soporte técnico, y te avisa qué tan urgente es.

---

## ⚡ ¿Cómo funciona?

1. El usuario graba un audio en la web.
2. El sistema usa **Whisper** para pasar esa voz a texto.
3. Luego, le manda el texto a **Gemini** (la IA de Google) para que analice qué quiere el cliente.
4. Gemini devuelve la categoría (Ventas, Soporte, etc.) y la prioridad. Todo se guarda para poder ver estadísticas.

---

## 🛠️ Cómo instalarlo (Paso a paso fácil)

Armé esto para que sea súper fácil de instalar, incluso para personas que no programan seguido. Solo hay que seguir estos comandos.

### 1. Lo que necesitás tener instalado
- **Python**: Descargalo de python.org. Al instalarlo, asegurate de marcar la casilla que dice "Add Python to PATH".
- **Git**: Para poder descargar el proyecto.
- **FFmpeg**: Esto es clave. Sin esto, la IA no puede escuchar los audios. Si estás en Windows, abrí una terminal (PowerShell) y ejecutá este comando:
  ```powershell
  winget install ffmpeg
  ```
  *(Ojo: Después de que termine de instalar, cerrá la terminal).*

### 2. Descargar el proyecto
Abrí una nueva terminal y escribí este comando para bajar todo el código a tu PC:
```powershell
git clone https://github.com/juandaviosoro-portf/audio-clasificador.git
```
Una vez que termine, entrá a la carpeta que se descargó:
```powershell
cd audio-clasificador
```

### 3. Instalación automática
En vez de volverte loco instalando mil cosas a mano, armé un script que hace todo el trabajo aburrido por vos.
Desde tus carpetas, buscá el proyecto y hacé **doble clic en el archivo `instalar_y_ejecutar.bat`**.

Ese archivo va a:
- Instalar todas las librerías necesarias.
- Preparar la base de datos.
- Prender el servidor web.
- Abrirte la página automáticamente en tu navegador (`http://localhost:5000`).

*(Paciencia: La primera vez que le des doble clic, va a tardar un par de minutos descargando cosas pesadas como Whisper).*

### 4. Conectar la Inteligencia Artificial (El toque final)
Para que el sistema piense de verdad, necesita conectarse a Google.
1. El script del paso anterior te va a crear un archivo llamado `.env`.
2. Abrilo con el Bloc de notas.
3. Vas a ver una línea que dice `GEMINI_API_KEY=tu_api_key_de_gemini_aqui`. Borrá ese texto y pegá ahí tu clave real de Google Gemini.
4. Guardá el archivo.

Listo. Si la ventanita negra se había cerrado, volvé a hacerle doble clic a `instalar_y_ejecutar.bat` y el servidor va a arrancar al instante usando tu clave.

---

## 📂 ¿Cómo ordené el código?

Si te da curiosidad ver cómo está hecho por dentro:
- `app.py`: Es el archivo principal que arranca la página web.
- `instalar_y_ejecutar.bat`: El script automático que mencioné arriba.
- `services/`: Acá adentro separé la lógica pesada. Hay un archivo para Whisper y otro para Gemini.
- `database/`: Acá se guardan todas las consultas de los clientes para armar los gráficos.
