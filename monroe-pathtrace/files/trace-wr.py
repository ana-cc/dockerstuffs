#!/usr/bin/python
# vim: expandtab tabstop=4 syntax=python
import logging
import sys
import subprocess
from pyroute2 import IPDB
import os
import json
from scapy.all import *
from scapy.config import *
import socket
import ipaddress

def emit_slow(intface, codepoint, filename, ifname, tl):
    sp = 63000 + codepoint
    pkts = []
    with open(filename) as f:
        for line in f:
            target = json.loads(line)
            if "." in target["ip"]:
                tf = codepoint << 2
                pkt = IP(dst=target["ip"], tos=tf, ttl=tl) / TCP(sport=sp, dport=48010)
                send(pkt, iface=ifname)
                time.sleep(0.3)


def emit(intface, codepoint, filename, ifname, tl):
    sp = 63000 + codepoint
    pkts = []
    with open(filename) as f:
        for line in f:
            target = json.loads(line)
            if "." in target["ip"]:
                tf = codepoint << 2
                pkts.append(
                    IP(dst=target["ip"], tos=tf, ttl=tl) / TCP(
                        sport=sp, dport=48020))
    send(pkts, iface=ifname)

def get_interfaces(ip):
    logger = logging.getLogger("trace-wr")

    # Creates a set of the available interface names
    s = set([interface.ifname for interface in ip.interfaces.values()])

    # Removes the metadata and lo interfaces from the set
    try:
        s.remove('lo')
        s.remove('metadata')
    except:
        logger.error("Metadata or lo not found!\n")

    # Debug printing list of interfaces
    for a in s:
        logger.debug("Interface seen: " + str(ip.interfaces[a].ifname) + "\n")
        conf.route.ifdel(str(ip.interfaces[a].ifname))

    return s

def main():
    # Sets up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("trace-wr")
  
    # list of codepoints for forger
    list_cp = [2, 8, 10, 18, 26, 34, 46]
    # Set up IPDB
    ip = IPDB()
    with open('/monroe/config') as configfile:
        config = json.load(configfile)
    nodeid = config['nodeid']
    try:
        switch = config['switch']
    except:
        switch = False
    # Create temporary directory for results
    subprocess.call(['mkdir', '/tmp/res/'])

    interfaces_present = get_interfaces(ip)
    #edgetrace block
    for item in ["op0", "op1", "op2"]:
        if item in interfaces_present:
            addrset = ip.interfaces[item].ipaddr
            addr_list = [x for x in addrset if '.' in x[0]]
            for i in addr_list:
                if_addr = i[0]
                if_netmask = i[1]
            ifname = item
            print("\nRunning edgetrace on interface: " + str(ifname)
                + "\n")
            print("\nConfiguring Scapy route with address: " + str(if_addr) )         
            conf.route.ifadd(str(ifname),str(if_addr) + "/" + str(if_netmask))
            for table in ip.routes.tables.keys():
                if table in [0, 254, 255]:
                    continue
                dr = ip.routes.tables[table]['default']
                if dr['prefsrc'] == str(if_addr):
                    conf.route.add(net="0.0.0.0/0", gw=dr['gateway'], dev=str(ifname))
            wr_str = "mnr-" + str(ifname) + "-" + nodeid
            subprocess.Popen(['/opt/monroe/edgetrace-linux-amd64', '-description', wr_str])
            time.sleep(70)
            print("\n Removing route. Routes are now: ")
            conf.route.ifdel(str(ifname))
            print("\n " + str(conf.route))
            print("\nRoutes are:\n" + str(conf.route))
    if switch != False:
        for item in ["op0", "op1", "op2"]:
            if item in interfaces_present:
                addrset = ip.interfaces[item].ipaddr
                addr_list = [x for x in addrset if '.' in x[0]]
                for i in addr_list:
                    if_addr = i[0]
                    if_netmask = i[1]
                ifname = item
                print("\nRunning script on interface: " + str(ifname)
                    + "\n")
                print("\nConfiguring Scapy route with address: " + str(if_addr) )         
                conf.route.ifadd(str(ifname),str(if_addr) + "/" + str(if_netmask))
                for table in ip.routes.tables.keys():
                    if table in [0, 254, 255]:
                        continue
                    dr = ip.routes.tables[table]['default']
                    if dr['prefsrc'] == str(if_addr):
                        conf.route.add(net="0.0.0.0/0", gw=dr['gateway'], dev=str(ifname))
                print("\nRoutes are:\n" + str(conf.route))
                print("\nCalling tcpdump...")
                #call wireshark on ifname for a wile in tmp
                wr_str = "/tmp/res/" + str(ifname) + "-" + nodeid +".pcap"
                tcpdump = subprocess.Popen(['/usr/sbin/tcpdump', '-w', wr_str,'-i', str(ifname), 'icmp or icmp6 or tcp[13]=18'])
                for cp in list_cp:
                    for tl in range(1, 3):
                        emit_slow(str(if_addr), cp, "/opt/monroe/hosts.jsonnd", str(ifname), tl)
    
                for cp in list_cp:
                    for tl in range(3, 31):
                        emit(str(if_addr), cp, "/opt/monroe/hosts.jsonnd", str(ifname), tl)
                        time.sleep(2)
    
                #wait and stop wireshark
                time.sleep(15)
                print("\n Killing tcpdump")
                tcpdump.kill()
                #Deletes the route before moving on to the next
                print("\n Removing route. Routes are now: ")
                conf.route.ifdel(str(ifname))
                print("\n " + str(conf.route))
        
# Clean up IPDB before exit
    savestr = '/monroe/results/all.tgz'
    args = ['tar', 'cvfz', savestr, '/tmp/res']
    subprocess.call(args)
    ip.release()


if __name__ == "__main__":
    sys.exit(main())
