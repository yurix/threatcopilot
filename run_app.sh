#!/bin/bash
cat threatcopilot.ans
echo "Iniciando stack de aplicação do Threat Copilot..."
docker compose -f docker-compose.yml up

