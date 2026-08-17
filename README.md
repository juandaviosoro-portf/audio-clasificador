# AudioClasifica — Sistema de Clasificación de Audios con IA

Sistema web que permite subir o grabar audios de clientes, transcribirlos automáticamente usando **OpenAI Whisper** y clasificar la intención del cliente con **Google Gemini**. Incluye historial, dashboard de estadísticas y exportación a Excel.

---

## Qué hace

1. Recibe un audio (subido o grabado desde el navegador) o un texto escrito.
2. Transcribe el audio a texto con Whisper.
3. Analiza el texto con Gemini (o con un clasificador local si no hay API key).
4. Clasifica en una de estas categorías: **VENTAS, SOPORTE, FACTURACIÓN, GARANTÍA, INFORMACIÓN, RECLAMO, OTRO**.
5. Asigna nivel de confianza (0-100%), prioridad (ALTA/MEDIA/BAJA) y genera un resumen.
6. Guarda todo en una base de datos SQLite.
7. Muestra resultados en tiempo real, con historial y gráficos.

---

## Requisitos del Sistema

| Requisito | Detalle |
|---|---|
| Python | 3.11 o superior |
| FFmpeg | Necesario para Whisper |
| Espacio en disco | ~2 GB (modelo Whisper `base` + dependencias) |
| RAM | Mínimo 4 GB (8 GB recomendado) |
| Navegador | Chrome, Firefox, Edge (versión reciente) |
| Internet | Solo para la clasificación con Gemini API |

---

## Instalación Paso a Paso

### 1. Instalar Python

Si no tenés Python instalado:

- **Windows**: Descargá desde [python.org](https://www.python.org/downloads/). **Importante**: marcá la casilla "Add Python to PATH" durante la instalación.
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11 python3.11-venv python3-pip`

Para verificar:
```bash
python --version
```

### 2. Instalar FFmpeg

FFmpeg es necesario para que Whisper pueda procesar los audios.

**Windows:**
```bash
# Con Chocolatey (recomendado)
choco install ffmpeg

# O con winget
winget install ffmpeg
```

Si no tenés Chocolatey ni winget, descargá FFmpeg de [ffmpeg.org](https://ffmpeg.org/download.html), extraé el ZIP, y agregá la carpeta `bin` a la variable de entorno PATH.

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

Para verificar:
```bash
ffmpeg -version
```

### 3. Clonar o copiar el proyecto

```bash
# Si tenés Git:
git clone <URL_DEL_REPOSITORIO>
cd audio-clasificador

# Si lo copiás desde un USB:
# Simplemente copiá la carpeta "audio-clasificador" a tu computador
```

### 4. Crear entorno virtual

```bash
python -m venv venv
```

Activar:
```bash
# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Vas a ver `(venv)` al inicio de la línea de comandos.

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto va a tardar unos minutos porque descarga el modelo de Whisper.

### 6. Configurar variables de entorno

Copiá el archivo de ejemplo:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Editá el archivo `.env` con tu API key:
```env
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
SECRET_KEY=una-clave-cualquiera-para-flask
WHISPER_MODEL=base
```

**¿Cómo consigo la API key de Gemini?**
1. Entrá a [Google AI Studio](https://aistudio.google.com/)
2. Iniciá sesión con tu cuenta de Google
3. Clic en "Get API Key" → "Create API Key"
4. Copiá la key y pegala en el `.env`

> **Nota**: Si no configurás la API key, la app va a funcionar igual usando un clasificador local basado en palabras clave. Es menos preciso pero sirve para probar.

### 7. Ejecutar la aplicación

```bash
python app.py
```

Vas a ver algo así:
```
=======================================================
  Sistema de Clasificación de Audios de Clientes
=======================================================
  Whisper modelo: base
  Gemini API:     Configurada
  Base de datos:  database/app.db
  Archivos:       uploads/
=======================================================
  Abrí tu navegador en: http://localhost:5000
=======================================================
```

### 8. Abrir en el navegador

Entrá a: **http://localhost:5000**

---

## Ejecución con Docker (Alternativa)

Si preferís usar Docker:

```bash
# Asegurate de tener el archivo .env configurado
docker compose up --build
```

La app va a estar disponible en `http://localhost:5000`.

Para detener:
```bash
docker compose down
```

---

## Estructura del Proyecto

```
audio-clasificador/
│
├── app.py                  # Aplicación Flask principal
├── config.py               # Configuración centralizada
├── requirements.txt        # Dependencias Python
├── .env.example            # Plantilla de variables de entorno
├── .env                    # Variables de entorno (no se sube a Git)
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Orquestación Docker
│
├── database/               # Base de datos SQLite (se crea sola)
│   └── app.db
│
├── uploads/                # Audios subidos (se crea sola)
│
├── models/
│   └── consulta.py         # Modelo de base de datos
│
├── services/
│   ├── transcriptor.py     # Transcripción con Whisper
│   ├── clasificador.py     # Clasificación con Gemini + fallback local
│   └── exportador.py       # Exportación a Excel
│
├── templates/
│   ├── base.html           # Layout base
│   ├── index.html          # Página principal
│   ├── dashboard.html      # Dashboard de estadísticas
│   └── historial.html      # Historial de consultas
│
├── static/
│   ├── css/style.css       # Estilos personalizados
│   └── js/
│       ├── app.js          # Lógica principal
│       ├── dashboard.js    # Lógica del dashboard
│       └── historial.js    # Lógica del historial
│
└── tests/
    ├── test_api.py         # Tests de endpoints
    ├── test_audio.py       # Tests del clasificador
    └── datos_prueba.json   # Casos de prueba
```

---

## API

### POST /api/analizar-audio

Sube y analiza un archivo de audio.

**Request**: `multipart/form-data` con campo `audio`

**Response**:
```json
{
    "id": 1,
    "transcripcion": "Quiero saber el precio del producto",
    "categoria": "VENTAS",
    "confianza": 96,
    "prioridad": "MEDIA",
    "resumen": "Cliente solicita información comercial",
    "duracion_audio": 5.2,
    "tiempo_proceso": 3.1
}
```

### POST /api/analizar-texto

Clasifica un texto directamente (sin audio).

**Request**:
```json
{
    "texto": "Necesito soporte técnico para mi equipo"
}
```

### GET /api/historial

Retorna el historial con filtros opcionales: `categoria`, `tipo`, `fecha_inicio`, `fecha_fin`, `busqueda`.

### GET /api/dashboard

Retorna estadísticas: totales, distribución por categoría, tendencia temporal.

### GET /api/exportar

Descarga el historial completo en formato Excel (.xlsx).

---

## Ejecutar Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Solución de Problemas

### Error: "No module named 'whisper'"
```bash
pip install openai-whisper
```

### Error: "ffmpeg not found" o "FileNotFoundError: ffmpeg"
FFmpeg no está instalado o no está en el PATH. Seguí las instrucciones de instalación de la sección 2.

En Windows, después de instalarlo, cerrá y volvé a abrir la terminal.

### Error: "GEMINI_API_KEY not set" o clasificación incorrecta
- Verificá que el archivo `.env` existe y tiene la key correcta.
- Probá la key en [Google AI Studio](https://aistudio.google.com/) para confirmar que funciona.
- Si no tenés key, la app va a usar el clasificador local (menos preciso pero funcional).

### Error: "Address already in use" (puerto 5000 ocupado)
Otro programa está usando el puerto 5000. Opciones:
```bash
# Opción 1: Cerrar lo que esté usando el puerto
# Windows
netstat -ano | findstr :5000
taskkill /PID <numero> /F

# Opción 2: Cambiar el puerto en app.py (última línea)
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Error: "ModuleNotFoundError" en general
Asegurate de tener el entorno virtual activado:
```bash
# Windows
venv\Scripts\activate
# Reinstalar
pip install -r requirements.txt
```

### El audio se transcribe pero la clasificación da "OTRO"
- Si estás usando el clasificador local (sin API key), es normal que algunos textos ambiguos caigan en OTRO.
- Configurá la API key de Gemini para obtener clasificaciones más precisas.

### La grabación no funciona
- Asegurate de estar usando HTTPS o localhost (el micrófono solo funciona en contextos seguros).
- Revisá que el navegador tenga permisos de micrófono habilitados.

---

## Guía para Presentación Universitaria

Procedimiento exacto para llevar el proyecto a otro computador:

### Preparar en tu computador

1. Asegurate de que todo funcione ejecutando `python app.py`
2. Copiá **toda** la carpeta `audio-clasificador` a un USB
   - Si querés un historial limpio, borrá `database/app.db` antes de copiar
   - La BD se va a crear sola al arrancar la app

### En el computador de la presentación

1. **Verificar Python**:
   ```bash
   python --version
   ```
   Si no está instalado, instalarlo desde python.org

2. **Verificar FFmpeg**:
   ```bash
   ffmpeg -version
   ```
   Si no está instalado:
   - Windows: `choco install ffmpeg` o descargar manualmente
   - La app va a funcionar para análisis de texto sin FFmpeg

3. **Copiar el proyecto desde el USB** a una carpeta en el escritorio

4. **Abrir terminal** en la carpeta del proyecto

5. **Crear entorno virtual e instalar**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

6. **Configurar .env**:
   ```bash
   copy .env.example .env
   ```
   Editá el `.env` y poné tu API key de Gemini

7. **Ejecutar**:
   ```bash
   python app.py
   ```

8. **Abrir** http://localhost:5000 en el navegador

### Demostración sugerida

1. Empezá mostrando el **análisis de texto** (es instantáneo y no necesita micrófono)
2. Luego mostrá la **grabación de audio** (necesita micrófono)
3. Subí un **archivo de audio** de ejemplo
4. Mostrá el **dashboard** con los datos que se fueron acumulando
5. Mostrá el **historial** y los filtros
6. Exportá a **Excel**
7. Mostrá el **modo oscuro/claro**

---

## Checklist de Verificación

Antes de presentar, confirmá que todo funcione:

- [ ] La aplicación inicia sin errores (`python app.py`)
- [ ] La base de datos se crea automáticamente (`database/app.db`)
- [ ] Se puede subir un archivo de audio y se procesa
- [ ] Se puede grabar audio desde el navegador
- [ ] El análisis de texto funciona correctamente
- [ ] La IA clasifica en las categorías correctas
- [ ] El historial muestra todas las consultas
- [ ] Los filtros del historial funcionan
- [ ] El dashboard muestra estadísticas y gráficos
- [ ] La exportación a Excel genera el archivo
- [ ] El modo oscuro/claro funciona
- [ ] La interfaz se ve bien en diferentes tamaños de pantalla

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Backend | Python 3.11 + Flask |
| Base de Datos | SQLite + SQLAlchemy |
| Transcripción | OpenAI Whisper |
| Clasificación IA | Google Gemini API |
| Frontend | HTML5 + Bootstrap 5 + JavaScript |
| Gráficos | Chart.js |
| Exportación | Pandas + OpenPyXL |
| Contenedores | Docker |
