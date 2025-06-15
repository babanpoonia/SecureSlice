import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from threading import Thread
from datetime import datetime
import time
import random
# from database.models import Session, PacketLog

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Mock Data
ue_list = [
    {"imsi": "001010000000001"}, 
    {"imsi": "001010000000002"},
    {"imsi": "001010000000003"}
]

threat_logs = []

# Background thread to add mock data
def generate_mock_threats():
    while True:
        time.sleep(4)
        new_log = {
            "time": datetime.now().strftime('%H:%M:%S'),
            "message": random.choice([
                "DoS Detected", "Suspicious GTP Packet", "Abnormal NGAP Activity", "Possible MITM Attack"
            ]),
            "score": round(random.uniform(0.4, 0.95), 2)
        }
        threat_logs.append(new_log)
        # Keep only latest 20 logs
        # if len(threat_logs) > 20:
            # threat_logs.pop(0)

def start_background_thread():
    thread = Thread(target=generate_mock_threats)
    thread.daemon = True
    thread.start()

@app.route('/')
def dashboard():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ue-list')
def get_ue_list():
    return jsonify(ue_list)

@app.route('/api/threats')
def get_threats():
    # session = Session()
    # logs = session.query(PacketLog).all()
    # data = [{
        # 'id': log.id,
        # 'timestamp': log.timestamp.isoformat(),
        # 'source_ip': log.source_ip,
        # 'dest_ip': log.dest_ip,
        # 'protocol': log.protocol,
        # 'length': log.length
    # } for log in logs]
    # session.close()
    # return jsonify(data)
    return jsonify(threat_logs)

@app.route('/status')
def status():
    return jsonify({"status": "OK"})

# Static JS and CSS (optional, if browser doesn't find them)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    start_background_thread()
    app.run(debug=True)
