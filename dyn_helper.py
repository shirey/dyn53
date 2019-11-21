import socket
from requests import get
import boto3 #pip instsall boto3
from properties.p import Property #pip install property
import os
import re

IP_REGEXP_MATCH = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

class DYNHelper:
    
    logger = None
    props = None
    properties_file_name = None
    dyn_hostname = None
    access_key = None
    access_secret = None
    
    def __init__(self, prop_file_name):
        self.__init_properties(prop_file_name)

    #given the AWS access key and secret for an account with access
    #to the Route53 service, walk all hosted zones and and records
    #until an "A" record matching the hostname parameter is found.
    #When found update the record to the ip address specified in
    #the new_ip parameter.
    def updateDNSRecord(self, new_ip):
        #trim the hostname and create a version with a "." at the end
        #both will be used to check against the record hostnames.
        hn = self.dyn_hostname.strip().lower()
        dottedHostname = hn + "."
        
        #create a boto3/route53 client
        r53client =  boto3.client('route53', aws_access_key_id=self.access_key, aws_secret_access_key=self.access_secret)
        
        #get all the zones hosted in this account
        zones = r53client.list_hosted_zones_by_name()
        
        #iterate through all zones until a matching record is found
        found = False
        for zone in zones['HostedZones']:
            #if a matching record was found in the previous zone skip all remaining zones
            if found:
                break
            #iterate through all records in the zone
            records = r53client.list_resource_record_sets(HostedZoneId=zone['Id'])
            for record in records['ResourceRecordSets']:
                #look for an "A" record with a matching zone name, if found update the IP address
                if record['Type'] == 'A' and (record['Name'].lower() == hn or record['Name'].lower() == dottedHostname):
                    found = True
                    r53client.change_resource_record_sets(
                        HostedZoneId=zone['Id'],
                        ChangeBatch= {
                                      'Changes': [
                                        {
                                         'Action': 'UPSERT',
                                         'ResourceRecordSet': {
                                             'Name': record['Name'],
                                             'Type': 'A',
                                             'TTL': record['TTL'],
                                             'ResourceRecords': [{'Value': new_ip}]
                                         }
                                        }]
                                 })
                    break
        #if a matching record wasn't found say so and exit with an error code
        if not found:
            raise Exception("A matching record for " + self.dyn_hostname + " was not found.  Unable to update the IP address to " + new_ip)
    
    #checks the IP address of the given hostname against the
    #reported external IP address of the host
    #if the ip addresses are different the reported IP of the
    #host is returned otherwise None is returned
    def check_ip(self):
        dnsVal = socket.gethostbyname(self.dyn_hostname)
        ipmatch = re.fullmatch(IP_REGEXP_MATCH, dnsVal)
        if ipmatch is None:
            raise Exception("DNS reported IP address is not a valid IPv4 IP address: " + dnsVal)
        reportedIP = get('https://api.ipify.org').text
        ipmatch = re.fullmatch(IP_REGEXP_MATCH, reportedIP)
        if ipmatch is None:
            raise Exception("External reported IP address is not a valid IPv4 IP address: " + reportedIP)
        if reportedIP != dnsVal:
            return(reportedIP)
        else:
            return(None)
    
    #get the required properties from a property file
    def __init_properties(self, file_name):
        self.properties_file_name = file_name
        if not os.path.isfile(file_name):                                                                                          
            raise Exception("Property file " + file_name + " is required and was not found.")                                               
            
        propMgr = Property()                                                                                                          
        self.props = propMgr.load_property_files(file_name)
        self.dyn_hostname = self.__getProperty("hostname")
        self.access_key = self.__getProperty("aws.access.key")
        self.access_secret = self.__getProperty("aws.access.secret")
    
    #get a property from the props.  If it doesn't exist or is blank throw an exception
    def __getProperty(self, propName):                                                                         
        if not propName in self.props:                                                                                                
            raise Exception('Required property ' + propName + ' not found in ' + self.properties_file_name)                                                                                                                   
        else:                                                                                                                     
            val = self.props[propName]                                                                                                
            if val is None or val.strip == "":                                                                                      
                raise Exception('Required property ' + propName + ' is blank in ' + self.properties_file_name)                                                                                                                
            else:                                                                                                                 
                return val.strip()        
