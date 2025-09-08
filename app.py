import docker
from flask import Flask, render_template
from flask_sock import Sock
import threading
import argparse
import os

# --- Setup ---
app = Flask(__name__)
sock = Sock(app)
# Initialize Docker client from environment variables
try:
    client = docker.from_env()
except docker.errors.DockerException:
    print("เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับ Docker daemon ได้")
    print("กรุณาตรวจสอบว่า Docker กำลังทำงานอยู่หรือไม่")
    exit(1)


# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')


@sock.route('/terminal')
def terminal(ws):
    """Handles the WebSocket connection for the terminal."""
    try:
        container = client.containers.run(
            "ubuntu-classroom",
            detach=True,
            tty=True,
            stdin_open=True,
            auto_remove=True  # Let Docker handle container removal
        )
        print(f"Created container for new session: {container.id[:12]}")
    except docker.errors.ImageNotFound:
        print("เกิดข้อผิดพลาด: ไม่พบ Docker image 'ubuntu-classroom'")
        print("กรุณารัน 'python install.py' ก่อนเริ่มใช้งาน")
        ws.close(message="Server configuration error.")
        return

    s = container.attach_socket(params={
        'stdin': 1,
        'stdout': 1,
        'stderr': 1,
        'stream': 1
    })

    container_socket = s._sock
    ws.send('Connected to your personal Linux environment!\r\n\r\n')

    def forward_container_to_ws():
        try:
            while True:
                data = container_socket.recv(1024)
                if not data:
                    ws.close()
                    break
                ws.send(data.decode('utf-8', errors='ignore'))
        except (ConnectionResetError, BrokenPipeError):
            pass # Connection closed by one of the parties
        except Exception as e:
            print(f"Thread error: {e}")

    thread = threading.Thread(target=forward_container_to_ws)
    thread.daemon = True
    thread.start()

    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            container_socket.sendall(data.encode('utf-8'))
    except Exception:
        # Client disconnected
        pass
    finally:
        print(f"Cleaning up container: {container.id[:12]}")
        container_socket.close()
        s.close()
        try:
            container.stop(timeout=5)
            print(f"Container {container.id[:12]} stopped.")
        except docker.errors.NotFound:
            # Container might be already removed by auto_remove
            print(f"Container {container.id[:12]} already removed.")
        except Exception as e:
            print(f"Error stopping container {container.id[:12]}: {e}")

# --- Run the App ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Linux Classroom Web App",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    parser.add_argument(
        '--https',
        action='store_true',
        help='Enable HTTPS mode. Requires --cert and --key.'
    )
    parser.add_argument(
        '--cert',
        type=str,
        default='cert.pem',
        help='Path to SSL certificate file (default: cert.pem)'
    )
    parser.add_argument(
        '--key',
        type=str,
        default='key.pem',
        help='Path to SSL private key file (default: key.pem)'
    )

    args = parser.parse_args()

    ssl_context = None
    if args.https:
        if os.path.exists(args.cert) and os.path.exists(args.key):
            ssl_context = (args.cert, args.key)
            print(f"HTTPS enabled using cert: {args.cert} and key: {args.key}")
        else:
            print("คำเตือน: ต้องการใช้ HTTPS แต่ไม่พบไฟล์ certificate หรือ key")
            print(f"ตรวจสอบที่: {args.cert}, {args.key}")
            print("ไม่สามารถเริ่มระบบในโหมด HTTPS ได้")
            sys.exit(1)

    # Use 'werkzeug' for production, but Flask's default is fine for this use case
    app.run(host=args.host, port=args.port, debug=False, ssl_context=ssl_context)

