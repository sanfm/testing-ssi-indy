#!/bin/bash

imagen=$1


if [ "$(docker images | grep $imagen)" ]; then
    echo "Ya existe imagen docker $imagen"
elif [ $imagen = 'issuer-cred' ] || [ $imagen = 'holder-cred' ] || [ $imagen = 'issuer-proof' ] || [ $imagen = 'holder-proof' ]; then
    echo "Preparando imagen..."
    docker build -q -t $imagen -f dockerfile.$imagen .
    # echo "docker build -q -t $imagen -f dockerfile.$imagen ."
else
    echo "Por favor, seleccione uno de los agentes: 'issuer-cred', 'holder-cred', 'issuer-proof' o 'holder-proof'"
    exit 1
fi


docker run --name controller-$imagen --rm -it --network="host" $imagen
