#!/usr/bin/python
import json
import subprocess
import logging
from pyroute2 import IPDB
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("runme")

def add_dns(interface):
    str = ""
    try:
        with open('/dns') as dnsfile:

            dnsdata = dnsfile.readlines()
            dnslist = [ x.strip() for x in dnsdata ]
            for item in dnslist:
                if interface in item:
                    str += item.split('@')[0].replace("server=", "nameserver ")
                    str += "\n"
        str += "nameserver 8.8.8.8\n"
        with open("/etc/resolv.conf", "w") as f:
            f.write(str)
    except:
       str = "Could not find DNS file"
    return str


def main():
    ip = IPDB()
    s = set([interface.ifname for interface in ip.interfaces.values()])
    logger.debug("Interfaces encountered: ")
    logger.debug(s)
    
    try:
         s.remove('lo')
         s.remove('metadata')
    except:
         logger.debug("Metadata or lo not found!\n")
    
    try:
        with open('/monroe/config') as configfile:
            config  = json.load(configfile)
            nodeid = config['nodeid']
    except:
        nodeid = 'could-not-get-id'
    try:
        with open('/monroe/config') as configfile:
            config  = json.load(configfile)
            operator = config['operator']
    except:
       operator = 'N/A'


    subprocess.call(['mkdir', '/tmp/res/'])
    result_files=[]
    
    for item in s:
        if item in ['op0', 'op1']:
            logger.debug("Running on interface: " + item)   

            try:
               subprocess.call(['route', 'del','default'])
               logger.debug("Default route deleted.")   
            except Exception as e:
               logger.debug(e)


            try:
               subprocess.call(['route', 'add','default','dev', item])
               logger.debug("Default route for interface " + item + " was added.")   
            except Exception as e:
               logger.debug(e)


            try:
               a = add_dns(item)
               logger.debug("DNS added\n")
               logger.debug(a)
               logger.debug("Testing connectivity...\n")
               process = subprocess.Popen(['ping' , '-c', '3', '8.8.8.8'], stdout=subprocess.PIPE)
               result_ping = process.communicate()[0]
               logger.debug(result_ping)

            except Exception as e:
               logger.debug(e)


            try:   
               logger.debug("Running netalyzr...\n")
               process = subprocess.Popen(['java', '-jar', '/opt/monroe/NetalyzrCLI.jar'])
               process.wait()
               result = "See container.log"
               logger.debug("Finished running netalyzr...\n")
            except Exception as e:
               logger.debug(e)
           
            wr_str = "/tmp/res/mnr-" +str(nodeid) + "_" + item
            result_files.append(wr_str)
             
            try:
               logger.debug("Verifying resolv.conf...\n")
               dnsproc = subprocess.Popen(['cat','/etc/resolv.conf'], stdout=subprocess.PIPE)
               result_dns = dnsproc.communicate()[0]
            except Exception as e:
               result_dns = e
            
            try:
               logger.debug("Writing results to file...\n")
               with open(wr_str, 'w') as wr_file:
                   wr_file.write("ID: " + str(nodeid) + "\n")
                   wr_file.write("Interface: " + item +"\n")
                   wr_file.write("Operator: " + str(operator) +"\n")
                   wr_file.write("Resolv.conf:\n" + str(result_dns)+ "\n")
                   wr_file.write("Ping Results:\n" + str(result_ping)+ "\n")

               with open(wr_str, 'a') as wr_file:
                   wr_file.write(result)

               logger.debug("Acquiring global IP address...\n")
               process = subprocess.Popen(['curl', 'https://stat.ripe.net/data/whats-my-ip/data.json'], stdout=subprocess.PIPE)
               result_ripe = process.communicate()[0]        

               with open(wr_str, 'a') as wr_file:
                   wr_file.write(result_ripe)

            except Exception as e:
                logger.debug(e)   
        
    for result_file in result_files:
        try:
            subprocess.call(['/usr/bin/mv', result_file, '/monroe/results/'])
        except Exception as e:
            logger.debug(e)
    ip.release()

if __name__ == "__main__":
    sys.exit(main())

