"""
Mini servidor seguro para MiniApps (YouTube → MP3 y Generador QR)
Sirve la interfaz web y actúa de proxy seguro para evitar bloqueos de CORS.
Ejecutar: python servidor.py
"""
import http.server
import json
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

PORT = int(os.environ.get("PORT", "5050"))
HOST = os.environ.get("HOST", "127.0.0.1")
DIR = os.path.dirname(os.path.abspath(__file__))

# Solo permitir servir archivos estáticos públicos de la interfaz (previene exponer código o .env)
ALLOWED_STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/qr.html": "qr.html",
    "/escaner-qr.html": "escaner-qr.html",
    "/yt-mp3.html": "yt-mp3.html",
    "/imagenes.html": "imagenes.html",
    "/pdf-img.html": "pdf-img.html",
    "/pdf-herramientas.html": "pdf-herramientas.html",
    "/audio-video.html": "audio-video.html",
    "/grabador.html": "grabador.html",
    "/seguridad.html": "seguridad.html",
    "/formatos.html": "formatos.html",
}

DEFAULT_COBALT_APIS = [
    "https://rue-cobalt.xenon.zone",
    "https://cobaltapi.cjs.nz",
    "https://api.cobalt.liubquanti.click",
    "https://cobalt.alpha.wolfy.love",
    "https://cobaltapi.squair.xyz",
    "https://api.qwkuns.me",
    "https://nuko-c.meowing.de",
]

env_apis = os.environ.get("COBALT_APIS", "").strip()
COBALT_APIS = [u.strip().rstrip("/") for u in env_apis.split(",") if u.strip()] if env_apis else DEFAULT_COBALT_APIS
COBALT_API_KEY = os.environ.get("COBALT_API_KEY", "").strip()

YOUTUBE_REGEX = re.compile(
    r"^https?://(www\.)?(youtube\.com/(watch\?.*v=|shorts/|live/)|youtu\.be/)[A-Za-z0-9_\-]+",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """Valida que la URL sea estrictamente de YouTube y segura."""
    if not url or len(url) > 300:
        return False
    return bool(YOUTUBE_REGEX.match(url))


def is_safe_tunnel_url(url: str) -> bool:
    """Previene SSRF validando que el túnel de descarga use HTTPS y no apunte a redes privadas."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        if host in ("localhost", "127.0.0.1", "0.0.0.0", "::1") or host.startswith("192.168.") or host.startswith("10."):
            return False
        return True
    except Exception:
        return False


def cobalt_get_url(yt_url: str):
    """Llama a las instancias configuradas y retorna (tunnel_url, filename) o lanza excepción."""
    if not is_valid_youtube_url(yt_url):
        raise ValueError("URL de YouTube no válida.")

    payload = json.dumps({
        "url":           yt_url,
        "downloadMode":  "audio",
        "audioFormat":   "mp3",
        "audioBitrate":  "320",
        "filenameStyle": "pretty",
    }).encode("utf-8")

    headers = {
        "Accept":       "application/json",
        "Content-Type": "application/json",
        "User-Agent":   "Mozilla/5.0",
    }
    if COBALT_API_KEY:
        headers["Authorization"] = f"Api-Key {COBALT_API_KEY}"

    last_err = "Sin respuesta de los servidores de conversión."
    for api in COBALT_APIS:
        try:
            req = urllib.request.Request(api + "/", data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))

            status = data.get("status", "")
            tunnel_url = data.get("url", "")
            if status in ("tunnel", "redirect") and tunnel_url and is_safe_tunnel_url(tunnel_url):
                return tunnel_url, data.get("filename", "audio.mp3")

            last_err = data.get("error", {}).get("code", "error") if status == "error" else f"estado: {status}"
        except Exception as e:
            last_err = str(e)

    raise RuntimeError(last_err)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)

    def log_message(self, fmt, *args):
        pass  # silenciar logs en consola

    def end_headers(self):
        # Cabeceras de ciberseguridad en cada respuesta
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)

        # /api/download?url=... → proxy directo para descargar el MP3
        if parsed_path.path == "/api/download":
            params = urllib.parse.parse_qs(parsed_path.query)
            yt_url = params.get("url", [""])[0].strip()

            if not is_valid_youtube_url(yt_url):
                self.send_error(400, "URL de YouTube invalida")
                return

            try:
                tunnel_url, filename = cobalt_get_url(yt_url)
            except Exception as e:
                self.send_error(502, f"No se pudo obtener el audio: {e}")
                return

            try:
                req = urllib.request.Request(tunnel_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as remote:
                    # Limpiar nombre de archivo para evitar inyección de cabeceras HTTP
                    safe_name = re.sub(r'[^\w\s\-\.\(\)\[\]]', '', filename).strip() or "audio.mp3"
                    if not safe_name.lower().endswith(".mp3"):
                        safe_name += ".mp3"

                    self.send_response(200)
                    self.send_header("Content-Type", "audio/mpeg")
                    self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
                    cl = remote.headers.get("Content-Length")
                    if cl and cl.isdigit():
                        self.send_header("Content-Length", cl)
                    self.end_headers()
                    while chunk := remote.read(65536):
                        self.wfile.write(chunk)
            except Exception:
                self.send_error(502, "Error al transmitir el archivo de audio")
            return

        # Servir únicamente archivos permitidos en la lista blanca
        target_file = ALLOWED_STATIC_FILES.get(parsed_path.path)
        if not target_file:
            self.send_error(404, "Archivo no encontrado")
            return

        self.path = "/" + target_file
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/convert":
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 4096:
                self.send_error(413, "Solicitud demasiado grande o vacia")
                return

            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                yt_url = str(body.get("url", "")).strip()
            except Exception:
                self.send_error(400, "JSON malformado")
                return

            try:
                tunnel_url, filename = cobalt_get_url(yt_url)
                resp = json.dumps({"url": tunnel_url, "filename": filename}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)

            except Exception as e:
                resp = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)

        else:
            self.send_error(404, "Ruta no encontrada")


def open_browser():
    import time
    time.sleep(0.8)
    # Solo abre navegador automáticamente si se ejecuta en entorno local
    if HOST in ("127.0.0.1", "localhost") and not os.environ.get("RENDER"):
        webbrowser.open(f"http://localhost:{PORT}/")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"✅  Servidor seguro activo en http://{HOST}:{PORT}/")
    print(f"   • Portal:        http://localhost:{PORT}/")
    print(f"   • Generador QR:  http://localhost:{PORT}/qr.html")
    print(f"   • YouTube → MP3: http://localhost:{PORT}/yt-mp3.html")
    print("   Presiona Ctrl+C para detener.\n")

    with http.server.ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido.")
