# ✨ Mis MiniApps (Generador QR + YouTube → MP3)

Colección de mini-aplicaciones web ligeras, rápidas y diseñadas con prácticas de **ciberseguridad**, listas para funcionar **100% online desde GitHub Pages** en cualquier navegador o celular sin necesidad de instalar nada.

## 🌐 Acceso Web Directo (GitHub Pages - 100% Funcional)

- **🏠 Portal Principal:** [https://silvermast1.github.io/miniapps/](https://silvermast1.github.io/miniapps/)
- **💕 Generador de Códigos QR:** [https://silvermast1.github.io/miniapps/qr.html](https://silvermast1.github.io/miniapps/qr.html) *(100% funcional directo en el navegador)*
- **🎵 YouTube → MP3 (320 kbps):** [https://silvermast1.github.io/miniapps/yt-mp3.html](https://silvermast1.github.io/miniapps/yt-mp3.html) *(100% funcional directo en GitHub Pages gracias a instancias con soporte CORS nativo)*

---

## 💻 Uso Local Opcional

Si en algún momento deseas ejecutarlas localmente desde tu PC:
- Puedes abrir `qr.html` o `yt-mp3.html` directamente en tu navegador, o ejecutar `abrir-yt-mp3.bat` (`python servidor.py`) como respaldo local en `http://localhost:5050`.

---

## 🔒 Medidas de Ciberseguridad Implementadas

1. **Cero Secretos en el Código:** Ninguna contraseña, token o clave privada está almacenada en el repositorio. Se incluye `.gitignore` estricto y `.env.example`.
2. **Subresource Integrity (SRI):** La librería externa de códigos QR se verifica mediante hash criptográfico `sha384` para impedir manipulaciones de CDN.
3. **Content Security Policy (CSP) Estricta:** Cada página restringe mediante `connect-src` y `script-src` exactamente los orígenes HTTPS autorizados, bloqueando inyección de scripts (XSS) y filtración de referencias (`referrer="no-referrer"`).
4. **Validación de Protocolos y Enlaces:** Tanto el generador QR como el descargador de MP3 validan estrictamente los dominios de entrada y que los túneles de descarga operen exclusivamente bajo `https://`.
