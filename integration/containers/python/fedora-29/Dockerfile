#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM fedora:29

ENV LANG en_US.UTF-8

RUN dnf install -y \
	gcc make python3 python3-wheel git 'dnf-command(builddep)' rsync

CMD ["python3"]
