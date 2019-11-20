#dyn53 - when run checks the DNS reported IP address against the
#        externally reported IP address of the host
#        if the two addresses don't match, update the host record in in AWS Route53
#
#        Uses: dyn_helper.DYNHelper class to check the addresses and update the Route53 record

import logging
from dyn_helper import DYNHelper

LOG_FILE_NAME = "log/dyn53.log"
PROP_FILE_NAME = "dyn53.props"

helper = None

helper = None
logger = None
try:
    #initialize logger
    logger = logging.getLogger('dyn53')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%S")
    logFH = logging.FileHandler(LOG_FILE_NAME)
    logFH.setFormatter(formatter)
    logger.addHandler(logFH)

    #initialize helper class
    helper = DYNHelper(PROP_FILE_NAME)
    
    #check the externally reported ip address against the dns reported dns address
    ip = helper.check_ip()
    
    #if the reported addresses do not match update in Route53
    if not ip is None:
        helper.updateDNSRecord(ip)
        msg = "IP address switched for " + helper.dyn_hostname + " new address: " + ip
        logger.info(msg)
        print(msg)
    #otherwise log a "didn't change" message
    else:
        msg = "The IP address for " + helper.dyn_hostname + " did not change."
        logger.info(msg)
        print(msg)
    exit(0)
#handle and log any errors
except Exception as e:
    if logger is not None:
        logger.error("Error during execution.")
        logger.error(e, exc_info=True)
    print("An error occurred while checking a dynamic IP address.")
    print(str(e))
    exit(1)
