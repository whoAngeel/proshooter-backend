#!/bin/bash
MAX_ATTEMPTS=20
ATTEMPT=1

until docker compose build --no-cache; do
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "Fallo tras $MAX_ATTEMPTS intentos."
        exit 1
    fi
    echo "Intento $ATTEMPT fallido. Reintentando en 10 segundos..."
    ATTEMPT=$((ATTEMPT+1))
    sleep 10
done

# ...código existente...

echo "¡Construcción completada exitosamente!"
curl -s -X POST "https://api.telegram.org/bot8325017828:AAFZJhGyW1usC_smbZOXFqgJN6sz-zI1cys/sendMessage" -d chat_id=5436840782 -d text="¡Construcción completada exitosamente en ProShooter!"
