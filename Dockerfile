FROM alpine:3.11

RUN apk add -U wireguard-lts \
	wireguard-tools-wg

# destinations for config files
RUN umaskmkdir -p /etc/wireguard && chmod /etc/wireguard 700

# file with Interface and Peers
COPY config/wg0.conf /etc/wireguard/wg0.conf