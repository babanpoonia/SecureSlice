import subprocess
import json
import requests

def parse_packet(packet):
    ip = packet.get('_source', {}).get('layers', {}).get('ip', {})
    src = ip.get('ip.src', '')
    dst = ip.get('ip.dst', '')
    if src and dst:
        data = {'src': src, 'dst': dst, 'score': 0.5}
        requests.post('http://127.0.0.1:5000/api/packet', json=data)

proc = subprocess.Popen(['tshark', '-i', 'any', '-Y', 'ngap || s1ap || gtpu', '-T', 'ek'],
                        stdout=subprocess.PIPE, text=True)

for line in proc.stdout:
    try:
        packet = json.loads(line.strip())
        parse_packet(packet)
    except json.JSONDecodeError:
        continue
