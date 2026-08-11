#!/usr/bin/env python3
"""
Berry Coffee Photo Booth — Print Server
Statik dosyaları servis eder + /print endpoint'i ile sessiz baskı yapar.

Kullanim: python server.py [port]
"""

import os, sys, json, base64, tempfile, subprocess, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Yazici ayari ──────────────────────────────────────────
# None = Windows varsayilan yazicisini kullan
# Ornek: PRINTER_NAME = "Canon SELPHY CP1300"
PRINTER_NAME = None
# ─────────────────────────────────────────────────────────

def get_default_printer():
    """Windows varsayilan yazici adini döndürür."""
    try:
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command',
             '(Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=$true").Name'],
            capture_output=True, text=True, timeout=5
        )
        name = result.stdout.strip()
        return name if name else None
    except Exception:
        return None

def print_photo(img_path, printer=None):
    """
    Windows'ta dialog açmadan sessiz baskı yapar.
    PowerShell + System.Drawing kullanır — sürücü yüklü her yaziciya çalışır.
    """
    printer_name = printer or PRINTER_NAME or get_default_printer()

    ps_lines = [
        "Add-Type -AssemblyName System.Drawing",
        f'$img = [System.Drawing.Image]::FromFile("{img_path.replace(chr(92), "/")}")',
        "$pd  = New-Object System.Drawing.Printing.PrintDocument",
    ]
    if printer_name:
        ps_lines.append(f'$pd.PrinterSettings.PrinterName = "{printer_name}"')

    ps_lines += [
        "$pd.DefaultPageSettings.Margins = New-Object System.Drawing.Printing.Margins(0,0,0,0)",
        "$pd.add_PrintPage({",
        "    param($s,$e)",
        "    $rect = $e.MarginBounds",
        "    $e.Graphics.DrawImage($img, $rect)",
        "})",
        "$pd.Print()",
        "$img.Dispose()",
    ]

    ps_script = "\n".join(ps_lines)

    try:
        subprocess.run(
            ["powershell", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
            timeout=30,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        print(f"[PRINT] OK → {printer_name or 'default'}")
    except Exception as e:
        print(f"[PRINT ERROR] {e}")
    finally:
        time.sleep(8)
        try:
            os.remove(img_path)
        except Exception:
            pass


class BoothHandler(SimpleHTTPRequestHandler):
    """Statik dosyalar + /print POST endpoint'i."""

    def log_message(self, fmt, *args):
        # Sadece önemli logları göster
        if "/print" in (args[0] if args else ""):
            print(f"[{self.address_string()}] {args[0]} → {args[1]}")

    def do_OPTIONS(self):
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == "/print":
            self._handle_print()
        else:
            self.send_error(404, "Not found")

    def _cors(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _handle_print(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            data   = json.loads(body)

            # base64 görüntüyü çöz
            img_b64 = data.get("image", "")
            if "," in img_b64:
                img_b64 = img_b64.split(",", 1)[1]
            img_bytes = base64.b64decode(img_b64)

            # Geçici dosyaya kaydet
            tmp = tempfile.NamedTemporaryFile(
                suffix=".jpg", dir=BASE_DIR, delete=False, prefix="print_"
            )
            tmp.write(img_bytes)
            tmp.close()

            printer = data.get("printer") or None

            # Arka planda sessiz baskı başlat
            threading.Thread(
                target=print_photo,
                args=(tmp.name, printer),
                daemon=True,
            ).start()

            self._json_response(200, {"ok": True, "msg": "Printing started"})

        except Exception as e:
            print(f"[/print ERROR] {e}")
            self._json_response(500, {"ok": False, "error": str(e)})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    os.chdir(BASE_DIR)

    server = HTTPServer(("", port), BoothHandler)

    default_p = PRINTER_NAME or get_default_printer() or "(not found)"
    print("=" * 50)
    print("  Berry Coffee Photo Booth — Print Server")
    print("=" * 50)
    print(f"  URL     : http://localhost:{port}")
    print(f"  Yazici  : {default_p}")
    print(f"  Klasor  : {BASE_DIR}")
    print("  Durdurmak icin Ctrl+C")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
