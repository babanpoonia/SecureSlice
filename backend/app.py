import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from database.models import Session, PacketLog

app = Flask(__name__)

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
        'length': log.length
    } for log in logs]
    session.close()
    return jsonify(data)

@app.route('/status')
def status():
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    app.run(debug=True)
