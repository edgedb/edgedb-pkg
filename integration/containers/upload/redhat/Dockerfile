FROM centos:7

RUN yum install -y openssh-clients

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
