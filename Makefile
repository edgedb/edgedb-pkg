.PHONY: build test test-systemd test-published update-images check-target


SUPPORTED_TARGETS = debian-stretch debian-buster \
					ubuntu-bionic ubuntu-xenial \
					centos-7 centos-8 fedora-29

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PLATFORM = $(firstword $(subst -, ,$(TARGET)))
DISTRO = $(lastword $(subst -, ,$(TARGET)))
OUTPUTDIR := /tmp/artifacts
GET_SHELL :=

EXTRAENV =
EXTRAVOLUMES =

ifeq ($(METAPKGDEV),true)
	_METAPKG_PATH = $(shell python -c 'import metapkg;print(metapkg.__path__[0])')
	EXTRAVOLUMES += -v $(_METAPKG_PATH):/metapkg
	EXTRAENV += -e METAPKG_PATH=/metapkg
endif

ifeq ($(GET_SHELL),true)
	COMMAND = bash
endif

ifneq ($(SRC_REVISION),)
	EXTRAENV += -e SRC_REVISION=$(SRC_REVISION)
endif

ifneq ($(PKG_VERSION_SLOT),)
	EXTRAENV += -e PKG_VERSION_SLOT=$(PKG_VERSION_SLOT)
endif

ifneq ($(PKG_REVISION),)
	EXTRAENV += -e PKG_REVISION=$(PKG_REVISION)
endif

ifneq ($(PKG_SUBDIST),)
	EXTRAENV += -e PKG_SUBDIST=$(PKG_SUBDIST)
endif

ifneq ($(EXTRA_OPTIMIZATIONS),)
	EXTRAENV += -e EXTRA_OPTIMIZATIONS=true
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
	make -C integration/linux/build
	docker build -t edgedb-pkg/build:$(TARGET) integration/linux/build/$(TARGET)
	docker run -it --rm \
		-v $(ROOT):/src \
		-v /tmp/pkgcache:/root/.cache/ \
		-v $(OUTPUTDIR):/src/artifacts \
		$(EXTRAVOLUMES) \
		$(EXTRAENV) \
		-e PKG_PLATFORM=$(PLATFORM) \
		-e PKG_PLATFORM_VERSION=$(DISTRO) \
		-e PYTHONPATH=/src \
		-w /src \
		edgedb-pkg/build:$(TARGET) \
		$(COMMAND)

test: check-target
	make -C integration/linux/test
	docker build -t edgedb-pkg/test:$(TARGET) integration/linux/test/$(TARGET)
	docker run -it --rm \
		-v $(ROOT):/src \
		-v $(OUTPUTDIR):/artifacts \
		$(EXTRAENV) \
		-e PKG_PLATFORM=$(PLATFORM) \
		-e PKG_PLATFORM_VERSION=$(DISTRO) \
		edgedb-pkg/test:$(TARGET) \
		$(COMMAND)

test-systemd: check-target
	make -C integration/linux/test-systemd
	docker build -t edgedb-pkg/test-systemd:$(TARGET) integration/linux/test-systemd/$(TARGET)
	docker run -it --rm \
		--cap-add SYS_ADMIN \
		-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
		-v $(ROOT):/src \
		-v $(OUTPUTDIR):/artifacts \
		$(EXTRAENV) \
		-e PKG_PLATFORM=$(PLATFORM) \
		-e PKG_PLATFORM_VERSION=$(DISTRO) \
		edgedb-pkg/test-systemd:$(TARGET)

test-published: check-target
	make -C integration/linux/testpublished
	docker build -t edgedb-pkg/testpublished:$(TARGET) integration/linux/testpublished/$(TARGET)
	docker run -it --rm \
		$(EXTRAENV) \
		-e PKG_PLATFORM=$(PLATFORM) \
		-e PKG_PLATFORM_VERSION=$(DISTRO) \
		-v $(ROOT):/src \
		edgedb-pkg/testpublished:$(TARGET) \
		$(COMMAND)
