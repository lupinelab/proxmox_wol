FROM python:3.12.0a1-alpine3.16

COPY ./ ./proxmox_wol-clone

RUN mv ./proxmox_wol-clone/bin/proxmox_wol ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "./proxmox_wol" ]

STOPSIGNAL SIGINT