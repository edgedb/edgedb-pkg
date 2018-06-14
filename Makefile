.PHONY: build


SUPPORTED_TARGETS = debian-stretch ubuntu-bionic centos-7
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))


ifeq ($(TARGET),debian-stretch)
	IMAGE = python:3.6-stretch
endif

ifeq ($(TARGET),ubuntu-bionic)
	IMAGE = python:3.6-stretch
endif

ifeq ($(TARGET),centos-7)
	IMAGE = containers.magicstack.net/magicstack/docker-python:3.7-centos-7
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
		-v /home/elvis/dev/magic/metapkg:/metapkg \
		-v /tmp/pkgcache:/root/.cache/ \
		-v /tmp/pkgcache/metapkg:/tmp/metapkg/ \
		$(IMAGE) \
		/bin/bash -c \
			'pip install /metapkg \
			 && PYTHONPATH=/build python -m metapkg \
			 	build edgedbpkg.edgedb:EdgeDB'
