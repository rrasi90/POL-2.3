#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="/var/lib/postgresql/certs"
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$CERT_DIR/server.key"

mkdir -p "$CERT_DIR"

if [ ! -s "$CERT_FILE" ] || [ ! -s "$KEY_FILE" ]; then
    openssl req -new -x509 -nodes -days 825 \
        -subj "/CN=pol-postgres" \
        -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE"
    chown postgres:postgres "$CERT_FILE" "$KEY_FILE"
    chmod 0644 "$CERT_FILE"
    chmod 0600 "$KEY_FILE"
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"
