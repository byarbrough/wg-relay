FROM alpine:3.11

RUN apk add -U wireguard-lts \
	wireguard-tools-wg

