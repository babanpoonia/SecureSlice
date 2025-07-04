import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from threading import Thread
from datetime import datetime
import time
import random
from database.models import Session, PacketLog
from backend.live_predictor import run_predictor
from pymongo import MongoClient

app = Flask(__name__, static_folder='../frontend', static_url_path='')

def start_background_thread():
    thread = Thread(target=run_predictor, kwargs={'interface': 'upfgtp'})
    thread.daemon = True
    thread.start()

@app.route('/')
def dashboard():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ue-list')
def get_ue_list():
    client = MongoClient("mongodb://localhost:27017")
    db = client["free5gc"]
    amData = db["subscriptionData.provisionedData.amData"]

    ue_list = []
    for ue in amData.find({}, {"ueId": 1, "_id": 0}):
        ue_list.append({"imsi": ue.get("ueId", "")})
    client.close()
    return jsonify(ue_list)

@app.route('/api/threats')
def get_threats():
    session = Session()
    logs = session.query(PacketLog).filter(PacketLog.attack_label != 'Benign').order_by(PacketLog.timestamp.desc()).limit(100).all()
    data = [{
        'id': log.id,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else None,
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
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
