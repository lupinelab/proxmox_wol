FROM ubuntu

COPY ./bin/proxmox_wol ./

RUN chmod +x ./proxmox_wol

ENTRYPOINT [ "./proxmox_wol" ]

STOPSIGNAL SIGINT