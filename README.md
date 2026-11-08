# ✨ Mis MiniApps (Generador QR + YouTube → MP3)

Colección de mini-aplicaciones web ligeras, rápidas y diseñadas con prácticas de **ciberseguridad**.

## 🌐 Acceso Web Directo (GitHub Pages)

- **🏠 Portal Principal:** [https://silvermast1.github.io/miniapps/](https://silvermast1.github.io/miniapps/)
- **💕 Generador de Códigos QR:** [https://silvermast1.github.io/miniapps/qr.html](https://silvermast1.github.io/miniapps/qr.html) *(100% funcional directo en el navegador sin servidor)*
- **🎵 YouTube → MP3:** [https://silvermast1.github.io/miniapps/yt-mp3.html](https://silvermast1.github.io/miniapps/yt-mp3.html)

---

## 🚀 Cómo ejecutar YouTube → MP3 en tu ordenador

Dado que los navegadores bloquean por seguridad (CORS) las descargas directas de audio entre distintos dominios, el conversor de YouTube a MP3 incluye un micro-servidor local en Python (`servidor.py`) sin dependencias externas.

### En Windows:
Haz doble clic sobre el archivo **`abrir-yt-mp3.bat`** (o desde tu carpeta sincronizada con *Google Drive para Escritorio*).

### En cualquier sistema (Windows / Linux / macOS):
```bash
python servidor.py
```
Se abrirá automáticamente `http://localhost:5050` con ambas herramientas funcionando al 100%.

---

## 🔒 Medidas de Ciberseguridad Implementadas

1. **Cero Secretos en el Código:** Ninguna contraseña, token o clave privada está almacenada en el repositorio. Se incluye `.gitignore` estricto y `.env.example` para configuraciones privadas opcionales.
2. **Subresource Integrity (SRI):** La librería externa de códigos QR se verifica mediante hash criptográfico `sha384` para impedir manipulaciones de CDN.
3. **Content Security Policy (CSP) y Cabeceras HTTP:** Protección activa contra inyección de scripts (XSS), Clickjacking (`X-Frame-Options: DENY`) y filtrado de referencias (`no-referrer`).
4. **Lista Blanca de Archivos y Prevención de SSRF:** `servidor.py` solo sirve los archivos HTML autorizados (`index.html`, `qr.html`, `yt-mp3.html`), bloqueando el acceso a archivos del sistema o de configuración, y valida estrictamente los dominios de entrada y salida.
