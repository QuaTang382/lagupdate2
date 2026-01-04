from flask import Flask, request, render_template_string
import subprocess
import threading

app = Flask(__name__)

# Hàm chạy lệnh trong nền để không làm treo web
def run_bgmi(ip, port):
    try:
        # Lệnh: ./bgmi ip port 300 300
        cmd = ["./bgmi", ip, port, "300", "300"]
        print(f"Dang chay lenh: {' '.join(cmd)}")
        subprocess.Popen(cmd) 
    except Exception as e:
        print(f"Loi: {e}")

# Giao diện HTML đơn giản nhúng trực tiếp
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; padding: 20px; background: #1e1e1e; color: white; }
        input { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
        button { padding: 15px; width: 100%; background: #007acc; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #005f9e; }
        .status { margin-top: 20px; color: #0f0; }
    </style>
</head>
<body>
    <h2>🚀 Control Center</h2>
    <form action="/start" method="post">
        <label>IP Address:</label>
        <input type="text" name="ip" placeholder="Nhập IP..." required>
        <label>Port:</label>
        <input type="text" name="port" placeholder="Nhập Port..." required>
        <br><br>
        <button type="submit">START</button>
    </form>
    {% if message %}
        <div class="status">{{ message }}</div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/start', methods=['POST'])
def start():
    ip = request.form.get('ip')
    port = request.form.get('port')
    
    if ip and port:
        # Chạy lệnh
        run_bgmi(ip, port)
        msg = f"Đã gửi lệnh tới: {ip}:{port} (300 300)"
    else:
        msg = "Thiếu IP hoặc Port!"
        
    return render_template_string(HTML_PAGE, message=msg)

if __name__ == '__main__':
    # Chạy server ở port 8080
    app.run(host='0.0.0.0', port=8080)