FROM ubuntu

RUN apt update && apt install -y iputils-ping

COPY ./bin/proxmox_wol ./

RUN chmod +x ./proxmox_wol

CMD [ "./proxmox_wol" ]

STOPSIGNAL SIGINT