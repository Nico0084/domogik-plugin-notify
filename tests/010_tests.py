#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.xpl.common.plugin import XplPlugin
from domogik.xpl.common.xplmessage import XplMessage
from domogik.tests.common.plugintestcase import PluginTestCase
from domogik.tests.common.testplugin import TestPlugin
from domogik.tests.common.testdevice import TestDevice
from domogik.tests.common.testsensor import TestSensor
from domogik.tests.common.testcommand import TestCommand


from domogik.common.utils import get_sanitized_hostname
from datetime import datetime
import unittest
import sys
import os
import traceback
import threading
import time

### global variables
DEVICE_NAME="IRTrans_1"
DEVICE_PATH = "/usr/local/irtrans"
DEVICE_IP_SERVER = "localhost"
DEVICE_IP_IRTRANS = "162.168.0.175"
CODE_IR = "[T]0[D]2100010000101101111100100000011110000000000000000000000000100000032100010000101101111100100000000000000000010000010000101000000000011110101000000000000000000000000000000000000000000000000000000110000000000000000010101110"
TIMING = "[0][N]4[1]440 448[2]440 1288[3]3448 1720[4]408 29616[RC]1[RP]0[FREQ]38"

class IRTransTestCase(PluginTestCase):

    def test_0100_dummy(self):
        self.assertTrue(True)

    def test_0110_send_code_standard(self):
        """ check if the xpl messages about get_switch_state are OK
            Sample message : 
            xpl-trig
            {
            hop=1
            source=domogik-daikcode.domogik-vm1
            target=*
            }
            irtrans.basic
            {
            device=/home
            device=Daikin remote 1
            current=19465224
            }
        dmg_send xpl-cmnd irtrans.basic "device=IRTrans_1,command=send,datatype=IRTrans standard,code=a22222,timing=a45454"   
            
        """
        
        
        global device_id
        global xpl_plugin
        
        # do the test
        print(u"********** start testing xpl command send standard code IR.")
        command = TestCommand(self,  device_id,  'send_standard')
        print (u'try to send xpl_cmnd fake....')   # "command" : "send",  "datatype" : "IRTrans standard", 
        self.assertTrue(command.test_XplCmd({"code": CODE_IR,  "timing": TIMING}, {"result" :"ok"}))
        msg1_time = datetime.now()
        time.sleep(8)

    def assert_Xpl_Stat_Ack_Wait(self, xplMsg) :
        """Assert a xpltrig for waiting a switch state"""
        print(u"Check that a message about xpl stat ack is sent. The message must be received once time.")
        schema,  data = xplMsg
        print "schema" , schema
        print "data", data
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                  xplschema = schema,
                                  xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                  data = data,
                                  timeout = 60))
        print "listener ack running"

    def send_xplTrig(self, data):
        """ Send xPL fake message on network
        """
        global xpl_plugin
        
        msg = XplMessage()
        msg.set_type("xpl-trig")
        msg.set_header(source ="domogik-{0}.{1}".format(self.name, get_sanitized_hostname()))
        msg.set_schema("sensor.basic")
        msg.add_data(data)
        print (u"send fake xpl switch on : {0}".format(msg))
        xpl_plugin.myxpl.send(msg)

    def send_xpCmd(self, data):
        """ Send xPL fake message on network
        """
        global xpl_plugin
        
        msg = XplMessage()
        msg.set_type("xpl-cmnd")
     #   msg.set_header(source ="domogik-{0}.{1}".format(self.name, get_sanitized_hostname()))
        msg.set_schema("irtrans.basic")
        msg.add_data(data)
        print (u"send fake xpl cmd switch on : {0}".format(msg))
        xpl_plugin.myxpl.send(msg)

if __name__ == "__main__":

    ### configuration

    # set up the xpl features
    xpl_plugin = XplPlugin(name = 'testirtr', 
                           daemonize = False, 
                           parser = None, 
                           nohub = True,
                           test  = True)
    # set test plugin ready for manager
    th = threading.Thread(None, xpl_plugin.ready, "plugin_test_ready") 
    th.start()

    # set up the plugin name
    name = "irtrans"

    # set up the configuration of the plugin
    # configuration is done in test_0010_configure_the_plugin with the cfg content
    # notice that the old configuration is deleted before
    cfg = {'configured' : True }

    ### start tests

    # load the test devices class
    td = TestDevice()

    # delete existing devices for this plugin on this host
    client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
    try:
        td.del_devices_by_client(client_id)
    except:
        print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
        sys.exit(1)

    # create a test device
    try:
        device_id = td.create_device(client_id, "test_IRTrans_Lan", "irtrans_lan.device")
        params = {"device" : DEVICE_NAME, "server_path" : DEVICE_PATH, "ip_server": DEVICE_IP_SERVER, "irtrans_ip": DEVICE_IP_IRTRANS}
        print (u"configure_global_parameters : {0}".format(params))
        td.configure_global_parameters(params)
    except:
        print(u"Error while creating the test devices : {0}".format(traceback.format_exc()))
        sys.exit(1)

    ### prepare and run the test suite
    suite = unittest.TestSuite()
    # check domogik is running, configure the plugin
    suite.addTest(IRTransTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
    suite.addTest(IRTransTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))

    # start the plugin
    suite.addTest(IRTransTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

    # do the specific plugin tests
    suite.addTest(IRTransTestCase("test_0110_send_code_standard", xpl_plugin, name, cfg))

   # do some tests comon to all the plugins
    suite.addTest(IRTransTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(IRTransTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))
    unittest.TextTestRunner().run(suite)

    # quit
    xpl_plugin.force_leave()
