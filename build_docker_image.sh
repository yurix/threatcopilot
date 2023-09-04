#!/bin/bash

if [ -z "$1" ]; then
    # Define um valor padrão se o argumento não foi fornecido
    parametro="Dockerfile"
else
    parametro="$1"
fi

cat threatcopilot.ans
echo "Iniciando build de aplicação do Threat Copilot..."
sudo chown -R $USER neo4japoc/
docker build --no-cache -t threatcopilot -f $parametro .

