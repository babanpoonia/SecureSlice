import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from threading import Thread
from datetime import datetime
import time
import random
from database.models import Session, PacketLog
from backend.live_predictor import run_predictor

app = Flask(__name__, static_folder='../frontend', static_url_path='')

def start_background_thread():
    thread = Thread(target=run_predictor, kwargs={'interface': 'lo'})
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
    session = Session()
    logs = session.query(PacketLog).all()
    data = [{
        'id': log.id,
        'timestamp': log.timestamp.isoformat(),
        'source_ip': log.source_ip,
        'dest_ip': log.dest_ip,
        'protocol': log.protocol,
        'length': log.length,
        'label': log.attack_label
    } for log in logs]
    session.close()
    return jsonify(data)

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
