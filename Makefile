.PHONY: build update-images


IMAGE_REGISTRY = containers.magicstack.net/magicstack/edgedb-pkg
SUPPORTED_TARGETS = debian-stretch ubuntu-bionic centos-7
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PLATFORM = $(firstword $(subst -, ,$(TARGET)))

ifeq ($(PLATFORM),ubuntu)
	PLATFORM = debian
endif

ifeq ($(PLATFORM),centos)
	PLATFORM = redhat
endif


build:

ifeq ($(TARGET),)
	$(error "Please specify the TARGET variable.")
endif

ifeq ($(filter $(TARGET),$(SUPPORTED_TARGETS)),)
	$(error Unsupported target: $(TARGET),  \
			supported targets are: $(SUPPORTED_TARGETS))
endif

	docker run -it --rm \
		-v $(ROOT):/build \
		-v /tmp/pkgcache:/root/.cache/ \
		-w /build \
		$(IMAGE_REGISTRY)/build:$(TARGET) \
		/bin/bash integration/$(PLATFORM)/build.sh

update-images:
	make -C integration/containers
