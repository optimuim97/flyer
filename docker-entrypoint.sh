#!/bin/sh
set -e

cd /app/backend

# Seed (idempotent — update si existe, insert sinon)
echo "==> Seed de la base..."
python seed.py

# Démarrage du serveur (gunicorn ou autre commande passée)
echo "==> Démarrage : $@"
exec "$@"
