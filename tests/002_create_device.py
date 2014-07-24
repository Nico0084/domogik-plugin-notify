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
BACKEND = 'https://newtifry.appspot.com/newtifry'

from domogik.tests.common.testdevice import TestDevice
from domogik.common.utils import get_sanitized_hostname

plugin = 'notify'

def create_device():
    ### create the device, and if ok, get its id in device_id
    client_id  = "plugin-{0}.{1}".format(plugin, get_sanitized_hostname())
    print "Creating the SMS  device..."
    td = TestDevice()
    params = td.get_params(client_id, "notify.smsweb")
        # fill in the params
    params["device_type"] = "notify.smsweb"
    params["name"] = DEVICE_NAME
    params["reference"] = "reference"
    params["description"] = "description"
    for idx, val in enumerate(params['global']):
        if params['global'][idx]['key'] == 'operator' :  params['global'][idx]['value'] = OPERATOR
        if params['global'][idx]['key'] == 'login' :  params['global'][idx]['value'] = OP_LOGIN
        if params['global'][idx]['key'] == 'pwd' :  params['global'][idx]['value'] = OP_PWD

    for idx, val in enumerate(params['xpl']):
        params['xpl'][idx]['value'] = PHONE_TEL

    # go and create
    td.create_device(params)
    print "Device SMS {0} configured".format(DEVICE_NAME_NOTIFRY)

    print("Creating the Newtifry  device...")
    td = TestDevice()
    params = td.get_params(client_id, "notify.newtifry")
        # fill in the params
    params["device_type"] = "notify.newtifry"
    params["name"] = DEVICE_NAME_NOTIFRY
    params["reference"] = "reference"
    params["description"] = "description"
    for idx, val in enumerate(params['global']):
        if params['global'][idx]['key'] == 'sourcekey' :  params['global'][idx]['value'] = SOURCE_KEY
        if params['global'][idx]['key'] == 'defaulttitle' :  params['global'][idx]['value'] = 'Test message'
        if params['global'][idx]['key'] == 'backend' :  params['global'][idx]['value'] = BACKEND

    for idx, val in enumerate(params['xpl']):
        params['xpl'][idx]['value'] = TO

    # go and create
    td.create_device(params)

    print "Device Newtifry {0} configured".format(DEVICE_NAME_NOTIFRY)
    
if __name__ == "__main__":
    create_device()



