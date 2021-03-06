FROM alpine:3.11

RUN apk update && apk add -U wireguard-tools

# destinations for config files
RUN umask 077 && mkdir -p /etc/wireguard

# file with Interface and Peers
COPY playbooks/files/wg0.conf /etc/wireguard/wg0.conf
# alpine wg interface file
# COPY playbooks/config/interfaces /etc/network/interfaces

# wg defualt port
EXPOSE 51820/udp
