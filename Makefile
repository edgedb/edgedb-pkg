.PHONY: build test test-published update-images build-images check-target


IMAGE_REGISTRY = containers.magicstack.net/magicstack/edgedb-pkg
SUPPORTED_TARGETS = debian-stretch ubuntu-bionic ubuntu-xenial centos-7 fedora-29
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PLATFORM = $(firstword $(subst -, ,$(TARGET)))
DISTRO = $(lastword $(subst -, ,$(TARGET)))

ifeq ($(PLATFORM),ubuntu)
	PLATFORM = debian
endif

ifeq ($(PLATFORM),centos)
	PLATFORM = redhat
endif

ifeq ($(PLATFORM),fedora)
	PLATFORM = redhat
endif

ifeq ($(METAPKGDEV),true)
	_METAPKG_PATH = $(shell python -c 'import metapkg;print(metapkg.__path__[0])')
	EXTRAVOLUMES = -v $(_METAPKG_PATH):/usr/local/lib/python3.7/site-packages/metapkg
endif


check-target:
ifeq ($(TARGET),)
	$(error "Please specify the TARGET variable.")
endif

ifeq ($(filter $(TARGET),$(SUPPORTED_TARGETS)),)
	$(error Unsupported target: $(TARGET),  \
			supported targets are: $(SUPPORTED_TARGETS))
endif


build: check-target
	docker run -it --rm \
		-v $(ROOT):/src \
		-v /tmp/pkgcache:/root/.cache/ \
		-v /tmp/artifacts:/src/artifacts \
		$(EXTRAVOLUMES) \
		-e PYTHONPATH=/src \
		-w /src \
		$(IMAGE_REGISTRY)/build:$(TARGET) \
		/bin/bash integration/$(PLATFORM)/build.sh

test: check-target
	docker run -it --rm \
		--cap-add SYS_ADMIN \
		-v $(ROOT):/src \
		-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
		-v /tmp/artifacts:/artifacts \
		$(IMAGE_REGISTRY)/test:$(TARGET) \
		/bin/bash /src/integration/$(PLATFORM)/test.sh

test-published: check-target
	docker run -it --rm \
		-e DISTRO=$(DISTRO) \
		-v $(ROOT):/src \
		$(IMAGE_REGISTRY)/testpublished:$(TARGET) \
		/bin/bash /src/integration/$(PLATFORM)/test-published.sh

update-images:
	make -C integration/containers

build-images:
	CI_REGISTRY_IMAGE=containers.magicstack.net/magicstack/edgedb-pkg \
		integration/build-images.sh
