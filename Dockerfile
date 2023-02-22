FROM python:3-alpine

RUN apk update && apk add iputils

COPY proxmox_wol.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

ENTRYPOINT [ "python", "-u", "./proxmox_wol.py" ]

STOPSIGNAL SIGINT