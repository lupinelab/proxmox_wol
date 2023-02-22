import sys
import re
from os import system
import socket
from proxmoxer import ProxmoxAPI
from config import pm_user, pm_token_name, pm_token, pm_nodes, wol_port

def proxmoxer_connection(node):
    connection = ProxmoxAPI(node.ip, user=pm_user, token_name=pm_token_name, token_value=pm_token, verify_ssl=False)
    return connection

class Node:
    def __init__(self, ip, status = ""):
        self.ip = ip
        self.status = status

class VM:
    def __init__(self, vm, name, node, vmtype, macs, status = ""):
        self.vmid = vm
        self.name = name
        self.node = node
        self.type = vmtype
        self.macs = macs
        self.status = status

    def start(self):
        if self.type == "qemu":
            proxmoxer_connection(nodes[self.node]).nodes(self.node).qemu(self.vmid).status.start.post()
        elif self.type == "lxc":
            proxmoxer_connection(nodes[self.node]).nodes(self.node).lxc(self.vmid).status.start.post()

def checknodestatus(ip):
    ping = f"ping -c 1 -W 2 {ip} > /dev/null"
    if system(ping) == 0:
        return "started"
    else:
        return "stopped"

def checkvmstatus(vm):
    if vm.type == "qemu":
        status = proxmoxer_connection(nodes[vm.node]).nodes(vm.node).qemu(vm.vmid).status.current.get()
    elif vm.type == "lxc":
        status = proxmoxer_connection(nodes[vm.node]).nodes(vm.node).lxc(vm.vmid).status.current.get()
    return status["status"]

def getnodes():
    global nodes
    nodes = {}
    for node in pm_nodes:
        if checknodestatus(pm_nodes[node]["ip"]) == "stopped":
            pass
        else:
            nodes[node]=Node(pm_nodes[node]["ip"], checknodestatus(pm_nodes[node]["ip"]))

def getvms():
    global vms
    loadvms = []
    vmidpernodedict = {}
    if nodes == []:
        return
    for vm in proxmoxer_connection(nodes[list(nodes.keys())[0]]).cluster.resources.get(type="vm"):
        vmidpernodedict[vm["vmid"]] = {}
        vmidpernodedict[vm["vmid"]]["node"] = vm["node"]
        vmidpernodedict[vm["vmid"]]["type"] = vm["type"]
    for vmid in vmidpernodedict:
        if vmidpernodedict[vmid]["node"] in nodes:
            macs = []
            if vmidpernodedict[vmid]["type"] == "qemu":
                config = proxmoxer_connection(nodes[vmidpernodedict[vmid]["node"]]).nodes(vmidpernodedict[vmid]["node"]).qemu(vmid).config.get()
                for line in config:
                    if line.startswith("net"):
                        macs.append(config.get(line).split(",")[0].split("=")[1])
                loadvms.append(VM(str(vmid), config.get("name"), vmidpernodedict[vmid]["node"], vmidpernodedict[vmid]["type"], macs))
            if vmidpernodedict[vmid]["type"] == "lxc":
                config = proxmoxer_connection(nodes[vmidpernodedict[vmid]["node"]]).nodes(vmidpernodedict[vmid]["node"]).lxc(vmid).config.get()
                for line in config:
                    if line.startswith("net"):
                        for i in config.get(line).split(","):
                            if i.startswith("hwaddr"):
                                macs.append(i.split("=")[1])
                loadvms.append(VM(str(vmid), config.get("hostname"), vmidpernodedict[vmid]["node"], vmidpernodedict[vmid]["type"], macs))
    for vm in loadvms:
        vm.status = checkvmstatus(vm)
    vms = loadvms

def wol_listener(port):
    host = ""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((host, port))
        except PermissionError:
            print("Please run as elevated user")
            sys.exit(2)
        while True:
            magic_packet = s.recv(1024).hex()
            raw_mac = magic_packet[-12:].upper()
            mac = ':'.join(raw_mac[i:i+2] for i in range(0, len(raw_mac), 2))
            return mac

def refresh():
    getnodes()
    getvms()

while True:
    print(f"Listening for magic packets on port {wol_port}:")
    receivedmac = wol_listener(wol_port)
    if re.search("^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$", receivedmac) == None:
        print("Heard an invalid mac address")
    else:
        print(f"Heard {receivedmac}")
        refresh()
        for vm in vms:
            if receivedmac in vm.macs:
                print(f"Resource {vm.name} is currently {vm.status}")
                if vm.status != "running":
                    vm.start()
                    print(f"Starting {vm.name}")
                    break