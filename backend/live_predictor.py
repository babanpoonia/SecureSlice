import subprocess
import psycopg2
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os
from database.models import Session, PacketLog
import threading

MODEL_PATH = 'model/multiclass_cnn_model.h5'
SCALER_PATH = 'model/scaler.pkl'
ENCODER_PATH = 'model/label_encoder.pkl'

def run_predictor(interface='lo'):
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(ENCODER_PATH)

    command = [
        "tshark", "-i", interface, "-T", "fields",
        "-e", "frame.time_relative",
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "frame.len",
        "-e", "_ws.col.Protocol",
        "-Y", "ip && frame.len > 0"
    ]

    print(f"📡 Starting live predictor on interface: {interface}")
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as proc:
        for line in proc.stdout:
            try:
                time, src_ip, dst_ip, length, proto = line.strip().split('\t')

                # Feature vector must match training
                df = pd.DataFrame([{
                    "Flow Duration": float(time),
                    "Total Fwd Packets": float(length),
                    "Protocol_TCP": 1.0 if proto.lower() == "tcp" else 0.0,
                    "Protocol_UDP": 1.0 if proto.lower() == "udp" else 0.0,
                    "Protocol_ICMP": 1.0 if proto.lower() == "icmp" else 0.0
                }])
                X_scaled = scaler.transform(df)
                pred = model.predict(X_scaled).argmax(axis=1)[0]
                label = label_encoder.inverse_transform([pred])[0]

                # Save to PostgreSQL
                session = Session()
                pkt = PacketLog(
					source_ip=src_ip,
					dest_ip=dst_ip,
					protocol=proto,
					length=int(float(length)),
					attack_label=label
				)
                session.add(pkt)
                session.commit()
                session.close()

                print(f"[✔] {src_ip} → {dst_ip} | {proto} | Predicted: {label}")

            except Exception as e:
                print(f"[ERROR] {e}")

