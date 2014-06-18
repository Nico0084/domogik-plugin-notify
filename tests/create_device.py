#!/usr/bin/python
#-*- coding: utf-8 -*-create_device.py

### configuration ######################################
DEVICE_NAME= 'Test-SMS'
OPERATOR=  '' # <'SFR_sms-web'or 'Orange_sms-web'or 'Bouygues_sms-web' or 'Freemobile_sms-web'>
PHONE_TEL = '' # <your phone number> 
OP_LOGIN= '' # <Your user of operator service>
OP_PWD = '' # <Your password of operator service>
##################################################
DEVICE_NAME_NOTIFRY = "Test-newtifry"
SOURCE_KEY = '' # <Your source key give by Newtifry>
TO = 'newtifry-test'

from domogik.tests.common.testdevice import TestDevice
from domogik.common.utils import get_sanitized_hostname

plugin = 'notify'

def create_device():
    ### create the device, and if ok, get its id in device_id
    print("Creating the SMS  device...")
    td = TestDevice()
    print 'host :',  get_sanitized_hostname()
    device_id = td.create_device("plugin-{0}.{1}".format(plugin, get_sanitized_hostname()), DEVICE_NAME, "smsweb.instance")
    print "Device sms created"
    td.configure_global_parameters({"operator": OPERATOR, "to" : PHONE_TEL,  "login" : OP_LOGIN,  "pwd": OP_PWD})
    print "Device SMS {0} configured".format(DEVICE_NAME)
    
    print("Creating the Newtifry  device...")
    td = TestDevice()
    print 'host :',  get_sanitized_hostname()
    device_id = td.create_device("plugin-{0}.{1}".format(plugin, get_sanitized_hostname()), DEVICE_NAME_NOTIFRY, "newtifry.instance")
    print "Device Newtifry created"
    td.configure_global_parameters({"to" : TO,  "sourcekey" : SOURCE_KEY,  "defaulttitle":  'Test message'})
    print "Device Newtifry {0} configured".format(DEVICE_NAME) 
    
if __name__ == "__main__":
    create_device()



