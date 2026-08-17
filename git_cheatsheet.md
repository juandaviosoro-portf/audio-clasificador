# 🚀 Guía Definitiva de Git (Súper Fácil)

Git sirve para guardar "fotos" (versiones) de tu código y subirlas a la nube (GitHub) para no perderlas o para usarlas en otra PC.

---

## ⬆️ SUBIR CAMBIOS (Push)
Usá esto en TU PC original cuando hayas modificado código y quieras guardarlo en GitHub.

Abrí la terminal en la carpeta de tu proyecto y ejecutá estos 3 comandos en orden:

```powershell
# 1. Preparar TODOS los archivos modificados
git add .

# 2. Sacar la "foto" y ponerle un mensaje descriptivo
git commit -m "Agregué el botón de inicio"

# 3. Subir la foto a GitHub
git push
```
> [!TIP]
> **Regla de oro:** Siempre es `add`, `commit` y `push`. Memorizá ese trío.

---

## ⬇️ BAJAR PROYECTO NUEVO (Clone)
Usá esto en una PC NUEVA donde **todavía no tenés** el proyecto.

```powershell
# Bajar todo el proyecto a una carpeta nueva
git clone https://github.com/tu-usuario/tu-proyecto.git
```
*(Solo se hace una vez por PC)*

---

## 🔄 ACTUALIZAR CAMBIOS (Pull)
Usá esto en otra PC donde **ya tenés** el proyecto, pero querés traer los cambios nuevos que subiste desde la PC original.

Abrí la terminal en la carpeta del proyecto y ejecutá:

```powershell
# Traer lo nuevo de GitHub a esta PC
git pull
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS COMUNES

> [!WARNING]
> **Error: "Author identity unknown"**
> Git no sabe quién sos. Ejecutá esto una sola vez:
> `git config --global user.email "tu@email.com"`
> `git config --global user.name "Tu Nombre"`

> [!CAUTION]
> **No subir basura (.gitignore)**
> Nunca subas contraseñas, claves API (como tu `.env`) o carpetas pesadas como `venv/`. Para evitarlo, asegurate de que esos nombres estén escritos dentro de un archivo llamado `.gitignore` antes de hacer el `git add .`
