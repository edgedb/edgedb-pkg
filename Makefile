.PHONY: build test test-published update-images build-images check-target


IMAGE_REGISTRY = containers.magicstack.net/magicstack/edgedb-pkg
SUPPORTED_TARGETS = debian-stretch ubuntu-bionic ubuntu-xenial centos-7 fedora-29
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PLATFORM = $(firstword $(subst -, ,$(TARGET)))
DISTRO = $(lastword $(subst -, ,$(TARGET)))
METAPKG_PYTHON_VERSION = 3.8
OUTPUTDIR := /tmp/artifacts

ifeq ($(METAPKGDEV),true)
	_METAPKG_PATH = $(shell python -c 'import metapkg;print(metapkg.__path__[0])')
	EXTRAVOLUMES = -v $(_METAPKG_PATH):/usr/local/lib/python$(METAPKG_PYTHON_VERSION)/site-packages/metapkg
endif

EXTRAENV =

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
		edgedb-pkg/build:$(TARGET)

test: check-target
	make -C integration/linux/test
	docker build -t edgedb-pkg/test:$(TARGET) integration/linux/test/$(TARGET)
	docker run -it --rm \
		-v $(ROOT):/src \
		-v $(OUTPUTDIR):/artifacts \
		$(EXTRAENV) \
		-e PKG_PLATFORM=$(PLATFORM) \
		-e PKG_PLATFORM_VERSION=$(DISTRO) \
		edgedb-pkg/test:$(TARGET)

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
		edgedb-pkg/testpublished:$(TARGET)
