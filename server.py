import http.server
import socketserver
import socket
import json
import os
import sys
import webbrowser

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tus_data.json')

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class TUSTrackerHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable aggressive caching for API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        data = f.read()
                    self.wfile.write(data.encode('utf-8'))
                except Exception as e:
                    self.wfile.write(b'[]')
            else:
                self.wfile.write(b'[]')
            return

        elif self.path == '/api/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            info = {
                'ip': get_local_ip(),
                'port': self.server.server_address[1]
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))
            return

        # Default static file serving
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/data':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                # Validate JSON before writing
                parsed = json.loads(body)
                temp_file = DATA_FILE + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed, f, ensure_ascii=False, indent=2)
                # Atomic replace
                if os.path.exists(DATA_FILE):
                    os.replace(temp_file, DATA_FILE)
                else:
                    os.rename(temp_file, DATA_FILE)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base_port = 8080
    max_port = 8095
    httpd = None
    used_port = base_port

    for port in range(base_port, max_port + 1):
        try:
            httpd = socketserver.TCPServer(('0.0.0.0', port), TUSTrackerHandler)
            used_port = port
            break
        except OSError:
            continue

    if not httpd:
        print(f"Xəta: {base_port}-{max_port} portları məşğuldur.")
        sys.exit(1)

    local_ip = get_local_ip()
    pc_url = f"http://localhost:{used_port}"
    network_url = f"http://{local_ip}:{used_port}"

    print("\n" + "=" * 64)
    print("  🩺 TUS TƏKRAR İZLƏYİCİSİ UĞURLA İŞƏ DÜŞDÜ!")
    print("=" * 64)
    print(f"  💻 Kompüterdə açmaq üçün:")
    print(f"     👉 {pc_url}")
    print()
    print(f"  📱 iPhone, iPad və ya Android Planşetdə açmaq üçün (eyni Wi-Fi-da):")
    print(f"     👉 {network_url}")
    print()
    print(f"  💾 Bütün qeydləriniz və təkrarlarınız bu faylda saxlanılır:")
    print(f"     {DATA_FILE}")
    print("=" * 64)
    print("  💡 ƏGƏR TELEFON VƏ YA PLANŞET QOŞULA BİLMİRSƏ:")
    print("     1. Kompüter və telefonun eyni ev Wi-Fi şəbəkəsində olduğunu yoxlayın.")
    print("     2. Windows Firewall soruşarsa 'İcazə ver' (Allow) seçin.")
    print("     3. Kompüter olmadan da 'Yedək/Bərpa' menyusundan kodu kopyalayaraq")
    print("        məlumatları cihazlar arasında saniyələr içində ötürə bilərsiniz.")
    print("=" * 64)
    print("  Serveri dayandırmaq üçün Ctrl + C basın.\n")

    # Open default browser on PC
    try:
        webbrowser.open(pc_url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dayandırıldı.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
