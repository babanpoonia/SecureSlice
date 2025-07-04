import subprocess
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os
from database.models import Session, PacketLog
import threading
import csv
from io import StringIO
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'rf_bin_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'model', 'rf_bin_scaler.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'model', 'rf_bin_label_encoder.pkl')

EXPECTED_FEATURES = [
    'Seq', 'Dur', 'Mean', 'sTos', 
    'dTos', 'sTtl', 'dTtl', 'TotPkts', 
    'SrcPkts', 'DstPkts', 'TotBytes', 'SrcBytes', 
    'DstBytes', 'Offset', 'Load', 'SrcLoad', 
    'DstLoad', 'Loss', 'SrcLoss', 'DstLoss', 
    'pLoss', 'SrcRate', 'DstRate', 'Rate', 
    'SrcGap', 'DstGap', 'SrcWin', 'DstWin', 
    'TcpRtt', 'State_ACC', 'State_CON', 'State_ECO', 
    'State_FIN', 'State_INT', 'State_NRS', 'State_REQ', 
    'State_RSP', 'State_RST', 'State_TST', 'State_URP', 
    'Proto_arp', 'Proto_icmp', 'Proto_ipv6-icmp', 'Proto_llc', 
    'Proto_lldp', 'Proto_sctp', 'Proto_tcp', 'Proto_udp'
]

def run_predictor(interface='upfgtp'):
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(ENCODER_PATH)

    print(f"🚀 Starting tshark on interface: {interface}")

    tshark_proc = subprocess.Popen(
        ["tshark", "-i", interface, 
        "-d", "udp.port==2152,gtp",
        "-Y", "ip",
        "-w", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    
    # Start argus capturing on interface
    argus_proc = subprocess.Popen(
        ["sudo", "argus", "-r", "-", "-w", "-"],
        stdin=tshark_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    # Start ra to generate flows in CSV
    ra_proc = subprocess.Popen(
        ["ra", "-r", "-", 
         "-s", "seq dur mean stos dtos pkts spkts dpkts bytes sbytes dbytes sttl dttl offset load sload dload loss sloss dloss ploss rate srate drate sgap dgap swin dwin tcprtt state proto", 
         "-c", ",",
         # "-u", 
         # "-F", ",", 
         # "-Z 1"
        ],
        stdin=argus_proc.stdout, stdout=subprocess.PIPE, text=True
    )

    csv_reader = csv.reader(ra_proc.stdout)

    # SEQ = 1

    # Skip header
    header = next(csv_reader, None)
    # print(header)

    for row in csv_reader:
        try:
            # print(row)
            # Map the output of ra to a dict
            # Dur, Mean, TotPkts, SrcPkts, DstPkts, SrcBytes, DstBytes,
            # sTtl, dTtl, Rate, SrcRate, DstRate, SrcGap, DstGap, State, Proto
            
            (seq, dur, mean, stos, dtos, pkts,
             spkts, dpkts, byts, sbytes, dbytes, sttl, dttl, 
             offset, load, sload, dload, loss, sloss, dloss, ploss,
             rate, srate, drate, sgap, dgap, swin, dwin, tcprtt,
             state, proto) = row

            # Build feature dict
            f = {
                'seq': int(seq) if seq != '' else 0,
                'dur': float(dur) if dur != '' else 0,
                'mean': float(mean) if mean != '' else 0,
                'stos': float(stos) if stos != '' else 0,
                'dtos': float(dtos) if dtos != '' else 0,
                'pkts': int(pkts) if pkts != '' else 0,
                'spkts': int(spkts) if spkts != '' else 0,
                'dpkts': int(dpkts) if dpkts != '' else 0,
                'bytes': int(byts) if byts != '' else 0,
                'sbytes': int(sbytes) if sbytes != '' else 0,
                'dbytes': int(dbytes) if dbytes != '' else 0,
                'sttl': int(sttl) if sttl != '' else 0,
                'dttl': int(dttl) if dttl != '' else 0,
                'offset': float(offset) if offset != '' else 0,
                'load': float(load) if load != '' else 0,
                'sload': float(sload) if sload != '' else 0,
                'dload': float(dload) if dload != '' else 0,
                'loss': float(loss) if loss != '' else 0,
                'sloss': float(sloss) if sloss != '' else 0,
                'dloss': float(dloss) if dloss != '' else 0,
                'ploss': float(ploss) if ploss != '' else 0,
                'rate': float(rate) if rate != '' else 0,
                'srate': float(srate) if srate != '' else 0,
                'drate': float(drate) if drate != '' else 0,
                'sgap': float(sgap) if sgap != '' else 0,
                'dgap': float(dgap) if dgap != '' else 0,
                'swin': float(swin) if swin != '' else 0,
                'dwin': float(dwin) if dwin != '' else 0,
                'tcprtt': float(tcprtt) if tcprtt != '' else 0,
                'state': state.lower(),  # crude encode state string length
                'proto': proto.lower()
            }

            row_data = {
                'Seq': f['seq'], 'Dur': f['dur'], 'Mean': f['mean'], 'sTos': f['stos'], 
                'dTos': f['dtos'], 'sTtl': f['sttl'], 'dTtl': f['dttl'], 'TotPkts': f['pkts'], 
                'SrcPkts': f['spkts'], 'DstPkts': f['dpkts'], 'TotBytes': f['bytes'], 'SrcBytes': f['sbytes'], 
                'DstBytes': f['dbytes'], 'Offset': f['offset'], 'Load': f['load'],  'SrcLoad': f['sload'], 
                'DstLoad': f['dload'], 'Loss': f['loss'], 'SrcLoss': f['sloss'], 'DstLoss': f['dloss'], 
                'pLoss': f['ploss'], 'SrcRate': f['srate'], 'DstRate': f['drate'], 'Rate': f['rate'], 
                'SrcGap': f['sgap'], 'DstGap': f['dgap'], 'SrcWin': f['swin'], 'DstWin': f['dwin'],
                'TcpRtt': f['tcprtt'], 
                'State_ACC': 1 if f['state'] == 'acc' else 0, 
                'State_CON': 1 if f['state'] == 'con' else 0, 
                'State_ECO': 1 if f['state'] == 'eco' else 0, 
                'State_FIN': 1 if f['state'] == 'fin' else 0, 
                'State_INT': 1 if f['state'] == 'int' else 0, 
                'State_NRS': 1 if f['state'] == 'nrs' else 0, 
                'State_REQ': 1 if f['state'] == 'req' else 0, 
                'State_RSP': 1 if f['state'] == 'rsp' else 0, 
                'State_RST': 1 if f['state'] == 'rst' else 0, 
                'State_TST': 1 if f['state'] == 'tst' else 0, 
                'State_URP': 1 if f['state'] == 'urp' else 0,
                'Proto_arp': 1 if f['proto'] == 'arp' else 0,
                'Proto_icmp': 1 if f['proto'] == 'icmp' else 0,
                'Proto_ipv6-icmp': 1 if f['proto'] == 'ipv6-icmp' else 0,
                'Proto_llc': 1 if f['proto'] == 'llc' else 0,
                'Proto_lldp': 1 if f['proto'] == 'lldp' else 0,
                'Proto_sctp': 1 if f['proto'] == 'sctp' else 0,
                'Proto_tcp': 1 if f['proto'] == 'tcp' else 0,
                'Proto_udp': 1 if f['proto'] == 'udp' else 0,
            }

            df = pd.DataFrame([row_data])[EXPECTED_FEATURES]
            scaled = scaler.transform(df)
            pred = model.predict(scaled)[0]
            label = label_encoder.inverse_transform([pred])[0]

            # Save to DB
            session = Session()
            pkt = PacketLog(
                timestamp=datetime.now(),
                source_ip="-",
                dest_ip="-",
                protocol=str(f['proto']),
                length=int(f['sbytes']+f['dbytes']),
                attack_label=label
            )
            session.add(pkt)
            session.commit()
            session.close()

            print(f"[✔] Seq {f['seq']}: Dur={f['dur']} | TotPkts={f['pkts']} | Predicted: {label}")
            # SEQ += 1

        except Exception as e:
            print(f"[ERROR] {e}")