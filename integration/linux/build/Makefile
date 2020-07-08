.PHONY: all

DOCKERFILES = $(addsuffix /Dockerfile, $(shell ../find.sh))
DEPS = ./update.sh ./entrypoint.sh

all: $(DOCKERFILES)

$(foreach y,$(DOCKERFILES),$(eval $y: Dockerfile-$(firstword $(subst -, ,$(dir $y))).template $(DEPS)))

$(DOCKERFILES): %:
	./update.sh $< $@
