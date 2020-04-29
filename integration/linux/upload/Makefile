.PHONY: all

DOCKERFILES = $(addsuffix /Dockerfile, $(shell find . -maxdepth 1 -mindepth 1 -type d -printf '%P\n'))
DEPS = ../mkdockerfile.sh

all: $(DOCKERFILES)

$(foreach y,$(DOCKERFILES),$(eval $y: Dockerfile-$(firstword $(subst -, ,$(dir $y))).template entrypoint-$(firstword $(subst -, ,$(dir $y))).sh $(DEPS)))

$(DOCKERFILES): %:
	../mkdockerfile.sh $< $@
