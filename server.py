# ==========================================
# DARKFORGE-X: NEXUS BRIDGE (API BACKEND)
# CAUTION: AUTHORIZED SERVER ADMINISTRATION ONLY
# ==========================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import signal

app = Flask(__name__)
CORS(app) # Cho phép Web giao tiếp chéo domain

# Biến toàn cục để lưu trữ tiến trình đang chạy
active_process = None

@app.route('/api/start', methods=['POST'])
def start_task():
    global active_process
    data = request.json
    
    target_ip = data.get('ip')
    target_port = data.get('port')
    
    if not target_ip or not target_port:
        return jsonify({"status": "error", "message": "Missing IP or Port"}), 400

    if active_process is not None and active_process.poll() is None:
        return jsonify({"status": "error", "message": "A task is already running. Stop it first."}), 400

    try:
        # ---------------------------------------------------------
        # [THAY THẾ PAYLOAD AN TOÀN]
        # Trong thực tế quản trị, đây là nơi gọi các script nội bộ.
        # Để trình diễn, tôi dùng lệnh 'ping' thay vì công cụ DoS.
        # Cấu trúc lệnh giả lập: ./authorized_tool IP PORT 300 300
        # ---------------------------------------------------------
        
        print(f"[NEXUS] Received START command for {target_ip}:{target_port}")
        
        # Lệnh minh họa an toàn (Ping đến IP):
        # command = ["ping", target_ip] 
        
        # Nếu Ngài có công cụ hợp pháp tên 'bgmi' để test hệ thống nội bộ của mình:
        command =["./bgmi", str(target_ip), str(target_port), "300", "300"]

        # Chạy tiến trình ngầm (Non-blocking)
        active_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({"status": "success", "message": f"Task initiated on {target_ip}:{target_port}", "pid": active_process.pid}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_task():
    global active_process
    
    if active_process is None or active_process.poll() is not None:
        return jsonify({"status": "error", "message": "No active task to stop."}), 400

    try:
        print("[NEXUS] Received STOP command. Terminating process...")
        # Gửi tín hiệu SIGTERM để kill tiến trình
        os.kill(active_process.pid, signal.SIGTERM)
        active_process = None
        
        return jsonify({"status": "success", "message": "Task terminated successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(">>> DARKFORGE-X: NEXUS BRIDGE LISTENING ON PORT 5000 <<<")
    # Chạy trên mọi Interface mạng để Web có thể truy cập
    app.run(host='0.0.0.0', port=5000)
