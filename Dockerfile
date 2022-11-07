FROM python:3

RUN apt update && apt install -y iputils-ping

COPY proxmox_wol.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

ENTRYPOINT [ "python", "./proxmox_wol.py" ]

STOPSIGNAL SIGINT