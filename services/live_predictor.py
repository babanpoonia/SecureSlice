import subprocess
import psycopg2
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import threading

def run_live_predictor():
    model = tf.keras.models.load_model("multiclass_cnn_model.h5")
    scaler = joblib.load("scaler.pkl")
    le = joblib.load("label_encoder.pkl")

    conn = psycopg2.connect(database="secureslice", 
            user="postgres", password="postgres", 
            host="localhost", port="5432")
    cursor = conn.cursor()

    command = [
        "tshark", "-i", "lo", "-T", "fields",
        "-e", "frame.time_relative", "-e", "ip.src", "-e", "ip.dst",
        "-e", "frame.len", "-e", "_ws.col.Protocol",
        "-Y", "ip && frame.len > 0"
    ]

    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as proc:
        for line in proc.stdout:
            try:
                time, src, dst, length, proto = line.strip().split('\t')
                features = pd.DataFrame([{
                    "Flow Duration": float(time),
                    "Total Fwd Packets": float(length),
                    "Protocol_TCP": 1.0 if proto.lower() == "tcp" else 0.0,
                    "Protocol_UDP": 1.0 if proto.lower() == "udp" else 0.0,
                    "Protocol_ICMP": 1.0 if proto.lower() == "icmp" else 0.0
                }])
                features_scaled = scaler.transform(features)
                pred = model.predict(features_scaled).argmax(axis=1)[0]
                label = le.inverse_transform([pred])[0]

                cursor.execute("INSERT INTO predictions (timestamp, src_ip, dst_ip, length, protocol, attack_label) VALUES (NOW(), %s, %s, %s, %s, %s)",
                               (src, dst, length, proto, label))
                conn.commit()

                print(f"[✔] Predicted: {label} | {src} → {dst}")

            except Exception as e:
                print(f"[ERROR] {e}")
