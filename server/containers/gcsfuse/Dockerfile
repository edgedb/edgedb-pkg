FROM golang:1-alpine
RUN apk add --no-cache git
ENV GOPATH /go
RUN go get -u github.com/googlecloudplatform/gcsfuse

FROM alpine
RUN apk add --no-cache ca-certificates fuse shadow \
    && groupadd --gid 2000 mounter \
    && useradd --uid 2000 --gid 2000 mounter \
    && apk del shadow \
    && rm -rf /tmp/*
COPY --from=0 /go/bin/gcsfuse /usr/local/bin
WORKDIR /
CMD ["gcsfuse"]
