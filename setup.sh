#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up virtual environment..."
python3 -m venv "$DIR/venv"
source "$DIR/venv/bin/activate"
pip install -r "$DIR/requirements.txt"

echo "Setting up PostgreSQL database..."
cp "$DIR/database/setup_db.sql" /tmp/setup_db.sql
sudo -u postgres psql -f /tmp/setup_db.sql
rm /tmp/setup_db.sql

mkdir -p captures

echo "Setup complete!"
