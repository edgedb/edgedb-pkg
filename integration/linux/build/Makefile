.PHONY: all

DOCKERFILES = $(addsuffix /Dockerfile, $(shell find . -maxdepth 1 -mindepth 1 -type d -printf '%P\n'))
DEPS = ./update.sh ./entrypoint.sh

all: $(DOCKERFILES)

$(foreach y,$(DOCKERFILES),$(eval $y: Dockerfile-$(firstword $(subst -, ,$(dir $y))).template $(DEPS)))

$(DOCKERFILES): %:
	./update.sh $< $@
