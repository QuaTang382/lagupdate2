from flask import Flask, request
import subprocess
import os

app = Flask(__name__)
PROC = None

@app.route('/')
def ping():
    return "ALIVE", 200

@app.route('/cmd')
def cmd():
    global PROC
    mode = request.args.get('m')
    
    if mode == 'on':
        ip = request.args.get('ip')
        port = request.args.get('p')
        
        # Kill cũ
        if PROC:
            try: PROC.terminate()
            except: pass
        os.system("pkill -f bgmi")

        print(f"STARTING: ./bgmi {ip} {port} 200 200")
        # Chạy file tool
        PROC = subprocess.Popen(["./bgmi", ip, port, "200", "200"])
        return "STARTED", 200

    elif mode == 'off':
        if PROC:
            try: PROC.terminate()
            except: pass
            PROC = None
        os.system("pkill -f bgmi") # Kill sạch sẽ
        print("STOPPED")
        return "KILLED", 200

    return "ERR", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
