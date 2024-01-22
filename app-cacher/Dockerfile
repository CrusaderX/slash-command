FROM golang:1.18 as builder

WORKDIR /go/src/app

COPY . .

RUN go get -d -v ./... && \
    go install -v ./... && \
    GOOS=linux GARCH=amd64 CGO_ENABLED=0 go build -o main cmd/cacher/main.go


FROM alpine:latest

COPY --from=builder /go/src/app/main /usr/bin/cacher

USER nobody

ENTRYPOINT ["cacher"]