# Author: Aravind Prabhakar 
# Version: V1.0
# Date: 2022-11-03
# Description: script to poll BW utilization for accounting purposes. This is further used to enable RPC calls
#              files are created for each month in name peak_<year>_<month>.json under /var/log
#
# -------- Example output ---------
#   more /var/log/peak_2022_nov.json
#   {
#       "time": "2022-11-03T18:45:54.732666",
#       "BPS": "85128"
#   }
#

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError,ConnectError, ConnectTimeoutError, RpcError, \
    CommitError
from lxml import etree

import argparse
import json
import datetime
import os

parser = argparse.ArgumentParser()
#parser.add_argument("-i", action='store', dest='INTF', nargs='+', help='interfaces to monitor. Separate interfaces with a whitespace')
parser.add_argument("-i", action='store', dest='INTF', help='interfaces to monitor. Separate interfaces with a whitespace')
args = parser.parse_args()

HOST = '192.167.1.3' 
USER = 'root'
PASSWD = 'juniper123'
STATS = {}

def Devopen(dev):
    try:
        dev.open(gather_facts=False)
        print ("device opened")
        cu = Config(dev)
    except ConnectAuthError:
        print("failed: authentication incorrect")
    except ConnectRefusedError:
        print("failed: connection refused")
    except ConnectTimeoutError:
        print("failed: connection timed out")
    except ConnectError:
        print("failed: connect error")

    return

def createMonthFiles():
    months = {
            "1": "jan",
            "2": "feb",
            "3": "mar",
            "4": "apr",
            "5": "may",
            "6": "jun",
            "7": "jul",
            "8": "aug",
            "9": "sep",
            "10": "oct",
            "11": "nov",
            "12": "dec"
            }
    cal = datetime.datetime.now().isoformat().split("-")
    year = cal[0]
    month = cal[1]
    FNAME = "/var/log/peak_{}_{}.json".format(year, months[month])
    if not os.path.isfile(FNAME):
        fopen = open(FNAME, 'w')
        fopen.close()
    
    FILE_PATH = "/var/log/peak_{}_{}.json".format(cal[0], months[cal[1]])

    return FILE_PATH

def main():
    FILE_PATH = createMonthFiles()

    # validate if file present or not
    if os.path.isfile(FILE_PATH) is not True:
        fopen = open(FILE_PATH, 'w')
        fopen.close()

    # open device
    dev = Device(host=HOST,user=USER,passwd=PASSWD)
    dopen = Devopen(dev)
    
    STATS["time"] = datetime.datetime.now().isoformat()
    BPS = 0
    ISTATS = {}
    INTF_STATS = []
    # gather bw stats
    IMON = args.INTF.split(" ")
    for numintf in IMON:
        opintf = dev.rpc.get_interface_information(interface_name=numintf, detail=True)
        for stats in opintf.xpath('.//input-bps'):
            ISTATS["BPS"] = stats.text.strip("\n")
            BPS = BPS + int(ISTATS["BPS"])
            ISTATS["INTF"] = numintf
            INTF_STATS.append(ISTATS)
            ISTATS = {}
    STATS["DETAIL"] = INTF_STATS
    STATS["BPS"] = BPS
    #print(STATS)

    fr = open(FILE_PATH, 'r')
    val = fr.read()
    fr.close()

    if val == "":
        cval = 0
    else:
        jload = json.loads(val)
        cval = int(jload["BPS"])

    if int(STATS["BPS"]) > cval:
        print("Value greater than previous peak at time {}.. saving..\n".format(STATS["time"]))
        with open(FILE_PATH, 'w') as fw:
            fw.write(json.dumps(STATS, indent=4))

if __name__ == "__main__":
    main()
