# proxmox_wol

A containerized utility enabling a magic packet sent to the broadcast address of a network to start a proxmox resource (qemu or lxc)

# Configuration:
- Create a proxmox pam user 'proxmox_wol'
- Create a 'Role' in proxmox called 'proxmox_wol' and give it the following privileges: VM.Audit, VM.PowerMgmt
- Create a 'User Permission' (Permissions) at both '/nodes' and '/vms' for 'proxmox_wol@pam' and assign the role created above, set Propagate to 'true'.
- Create an API Token for the promox_wol user, set Token ID to 'proxmox_wol', disable 'Privilege Separation'. Note down the API token somewhere.
- Create a config.py with values appropriate for your setup (you will be passing this into your docker container as a volume so locate it accordingly):
  ```
  pm_user = "proxmox_wol@pam"
  pm_token_name = "proxmox_wol"
  pm_token = "<proxmox-api-token-goes-here>"
  pm_nodes = {
       "proxmoxnode-01": {"ip": "192.168.20.2"},
       "proxmoxnode-02": {"ip": "192.168.20.3"}
  }
  wol_port = 7   ## this could be 7 or 9 depending on the wakeonlan client you are using to send magic packets
  ```
  Example docker compose file:
  
  ```version: '3.3'
  services:
    proxmox_wol:
        container_name: proxmox_wol
        ports:
            - '7:7'
            - '9:9'
        volumes:
            - '/path/to/config.py:/config.py'
        network_mode: host
        restart: unless-stopped
        image: lupinelab/proxmox_wol
  ```
  Start the container: 
  ```
  docker-compose up -d
  ```
# Notes:
  - The container must have the network_mode set to 'host' as magic packets are not forwarded when using the default bridged network driver
  - The container (and therefore docker host) must be in the same VLAN that you are sending magic packets from, although I'm sure it is possible to forward magic packets across VLANs through a variety of methods it's probably more convenient to setup an LCX container in the appropriate VLAN and have it run the container.
