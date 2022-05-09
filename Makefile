BUILDX_VER=v0.3.0

install:
	mkdir -vp ~/.docker/cli-plugins/ ~/dockercache
	curl --silent -L "https://github.com/docker/buildx/releases/download/${BUILDX_VER}/buildx-${BUILDX_VER}.linux-amd64" > ~/.docker/cli-plugins/docker-buildx
	chmod a+x ~/.docker/cli-plugins/docker-buildx

prepare: install
	docker buildx create --use

build:
	docker buildx build --push \
		--platform ${PLATFORMS} \
		-t ${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_VERSION} \
		.
push:
	docker push ghcr.io/{DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_VERSION}
