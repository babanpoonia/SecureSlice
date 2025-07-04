CREATE DATABASE secure_slice_db;;
\c secure_slice_db;

CREATE TABLE IF NOT EXISTS packet_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(50),
    dest_ip VARCHAR(50),
    protocol VARCHAR(20),
    length INTEGER
);

ALTER TABLE packet_logs ADD COLUMN attack_label VARCHAR(50);