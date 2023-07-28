#!/bin/bash

docker run \
	--name finales_tenant \
	-p 8888:8888 \
	-p 13371:13371 \
	--add-host=host.docker.internal:host-gateway \
	aiida_finales_image
