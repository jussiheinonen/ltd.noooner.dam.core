#!/usr/bin/env bash
#
# Front end for managing Docker runtimes

declare -A OPTIONS_CMD OPTIONS_DESC

OPTIONS_CMD[1]="sudo docker run --rm -p 4566:4566 -p 4571:4571 localstack/localstack"
OPTIONS_CMD[2]="sudo docker run --rm --entrypoint /bin/bash -v $(pwd):/usr/app/ --net=host -it wiren:alpine"
OPTIONS_CMD[3]="sudo docker run --rm --entrypoint /bin/bash -v $(pwd):/usr/app/ -v /home/jussi/.aws/:/root/.aws/ --net=host -it wiren:alpine"
OPTIONS_CMD[4]="sudo docker run --rm --entrypoint /bin/bash -v $(pwd):/usr/app/ --net=host -it thumbnailer:local"

OPTIONS_DESC[1]="Localstack backend"
OPTIONS_DESC[2]="Wiren development runtime for local development (local .aws/credentials)"
OPTIONS_DESC[3]="Wiren runtime for AWS API (real .aws/credentials)"
OPTIONS_DESC[4]="Lambda-like dev environment (FROM public.ecr.aws/lambda/python:3.8)"

banner_please() {
    echo  " "
    echo "START DOCKER CONTAINERS"
    echo  " "
    echo "Select one of the following options"
    echo  " "
}

banner_please

for each in ${!OPTIONS_DESC[*]}; do
    echo -e "\t${each}. ${OPTIONS_DESC[${each}]}"
done

echo  " "
read -p "Which container to start? " INDEX

if [[ "${INDEX}" -gt "${#OPTIONS_CMD[*]}" ]]; then 
    echo "No container number ${#OPTIONS_CMD[*]}. Adios amigo."
    exit 1
else
    echo "Starting container ${OPTIONS_DESC[${INDEX}]}"
    ${OPTIONS_CMD[${INDEX}]}
fi
