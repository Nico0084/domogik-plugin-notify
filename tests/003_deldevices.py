#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.tests.common.testdevice import TestDevice
from domogik.common.utils import get_sanitized_hostname
import traceback
import sys

if __name__ == "__main__":

    # set up the plugin name
    name = "notify"

    # load the test devices class
    td = TestDevice()

    # delete existing devices for this plugin on this host
    client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
    try:
        td.del_devices_by_client(client_id)
    except:
        print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
        sys.exit(1)
