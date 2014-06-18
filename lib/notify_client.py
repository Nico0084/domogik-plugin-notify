# !/usr/bin/python
#-*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
===========

Send SMS on web service for french telephony providers : Orange, SFR, Bouygues, Freemobile.

This is an upgrade based on sms plugin for domogik 0.3
@author: Gizmo - Guillaume MORLET <contact@gizmo-network.fr>

Implements
========

- class NotifyClient to handle SMS

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""


import json
import threading
import time
import sys
from domogik_packages.plugin_notify.lib.client_devices import createDevice, OPERATORS_SERVICE
    
class NotifyClientException(Exception):
    """
    NotifyClient exception
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = "NotifyClient exception, " + value

    def __str__(self):
        return repr(self.value)

def getClientId(device):
    """Return key Notify client id."""
    if device.has_key('name') and device.has_key('id'):
        return "{0}_{1}".format(device['name'], + device['id'])
    else : return None
    
class NotifyClient :
    "Objet client de base pour la liaison operateur de Notification."

    def __init__ (self,  manager,  params, log) :
        "Initialise le client"
        self._manager = manager
        self.operator = params['operator']
        self.name = params['name']
        self._log = log
        self._operator = None
        self._operator = createDevice(params, self._log)

    # On accède aux attributs uniquement depuis les property
    smsId = property(lambda self: getClientId(self._device)) 
    domogikDevice = property(lambda self: self._getDomogikDevice())

    def __del__(self):
        '''Send Xpl message and Close updater timers.'''
        print "Try __del__ client"
        self.close()
        
    def close(self):
        """Send Xpl message and Close updater timers."""
        self._log.info("Close SMS client {0}".format(self.name))
        
    def updateDevice(self,  params):
        """Update device data."""
        self._operator.update(params)
        self.operator = params['operator']
        self.name = params['name']

    def _getDomogikDevice(self):
        """Return device Id for xPL domogik device"""
        if self._operator :
            return self._operator.to
        else : return None

    def handle_xpl_cmd(self,  xPLmessage):
        '''Handle a xpl-cmnd message from hub.
        '''
        if xPLmessage.has_key('to') and xPLmessage.has_key('body') :
            xPLmessage['header'] = self._manager._xplPlugin.get_config("msg_header")
            data = self._operator.send(xPLmessage)
            if data['error'] == '' : del data['error']
            data['to'] = self.domogikDevice
            self._manager.sendXplAck(data)
        else : 
            self._log.debug(u"SMS Client {0}, recieved unknown command {1}".format(getClientId(self._device), xPLmessage))
            
