FROM 3.12.0a1-alpine3.16

COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "./proxmox_wol.py" ]