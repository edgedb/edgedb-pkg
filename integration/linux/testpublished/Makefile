.PHONY: all

DOCKERFILES = $(addsuffix /Dockerfile, $(shell ../find.sh))
DEPS = ../mkdockerfile.sh

all: $(DOCKERFILES)

$(foreach y,$(DOCKERFILES),$(eval $y: Dockerfile-$(firstword $(subst -, ,$(dir $y))).template entrypoint-$(firstword $(subst -, ,$(dir $y))).sh $(DEPS)))

$(DOCKERFILES): %:
	../mkdockerfile.sh $< $@
