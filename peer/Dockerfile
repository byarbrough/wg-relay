FROM alpine:3.11

RUN apk update && apk add -U wireguard-tools

# destinations for config files
RUN umask 077 && mkdir -p /etc/wireguard

# file with Interface and Peers
COPY config/wg2.conf /etc/wireguard/wg0.conf

# wg defualt port
EXPOSE 51820/udp
