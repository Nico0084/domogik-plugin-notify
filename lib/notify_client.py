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

from domogik_packages.plugin_notify.lib.client_devices import CreateOperator, GetDeviceParams

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
        return u"{0}_{1}".format(device['name'], device['id'])
    else : return None

class NotifyClient :
    """Basic client Class for link to operator notifycation."""

    def __init__ (self, manager, dmgDevice, params, log) :
        """Initialize client"""
        self._manager = manager
        self.operator = params['operator']
        self.name = params['name']
        self._log = log
        self._operator = None
        self._dmgDevice = dmgDevice
        self._operator = CreateOperator(params, self._log)

    # On accède aux attributs uniquement depuis les property
    clientId = property(lambda self: getClientId(self._device))
    to = property(lambda self: self._getTo())

    def __del__(self):
        """Close himself."""
        print "Try __del__ client"
        self.close()

    def close(self):
        """Close operator."""
        if self._manager.getStopConfig() :
            self.handle_cmd({"to": self.to, "title": "Disconnection" , "body": "Your Terminal is disconnect, it will no longer receive notifications."})
        self._operator.close()
        self._log.info(u"Close notification client {0} and his operator {1}".format(self.name, self.operator))

    def updateDevice(self, dmgDevice):
        """Update device data from a domogik device."""
        params = GetDeviceParams(self.Plugin, dmgDevice)
        self._dmgDevice = dmgDevice
        if self.operator != params['operator'] : # Operator change, remove odl and create a new
            del self._operator
            CreateOperator(params, self._log)
        else :                                   # Otherwise only update parameters
            self._operator.update(params)
        self.operator = params['operator']
        self.name = params['name']

    def _getTo(self):
        """Return to Id from client service"""
        if self._operator :
            return self._operator.to
        else : return None

    def getDmgDeviceId(self):
        """Return domogik device ID."""
        if self._dmgDevice :
            return self._dmgDevice['id']
        return None

    def getDmgCommands(self):
        """Return domogik commands for send message."""
        commands = {}
        if self._dmgDevice :
            for cmd in self._dmgDevice['commands']:
                commands[cmd] = {'parameters': self._dmgDevice['commands'][cmd]['parameters'],
                                 'id': self._dmgDevice['commands'][cmd]['id']}
        else :
            self._log.warning(u"Can't get domogik commands. Client {0} have not domogik device registered.".format(self.name))
        return commands

    def getDmgSensors(self):
        """Return domogik sensors status and error send."""
        sensors = {}
        if self._dmgDevice :
            for sensor in self._dmgDevice['sensors']:
                sensors[sensor] = {'data_type': self._dmgDevice['sensors'][sensor]['data_type'],
                                            'id': self._dmgDevice['sensors'][sensor]['id']}
        else :
            self._log.warning(u"Can't get domogik sensors. Client {0} have not domogik device registered.".format(self.name))
        return sensors

    def NotifyConnection(self):
        """ Send a Notification connection."""
        self.handle_cmd({'to': self.to, 'title': u"Connection", 'body': u"Your Terminal is registered to receive notification :)"})

    def handle_cmd(self, message):
        """Handle a cmd message from external (0MQ).
        """
        if self.to :
            if not message.has_key('to'):  message['to'] = self.to
            if message.has_key('body') :
                if not message.has_key('header'): message['header'] = self._manager.Plugin.get_config("msg_header")
                data = self._operator.send(message)
            else :
                self._log.debug(u"Notification Client {0}, recieved unknown command {1}".format(getClientId(self._device), message))
                data = {'status': u"Notification Not Sended",
                        'error': u"Notification Client {0}, recieved unknown command {1}".format(getClientId(self._device), message) }
        else :
            self._log.debug(u"Notification Client {0}, No operator registered, can't send notification :{1}".format(getClientId(self._device), message))
            data = {'status': u"Notification Not Sended",
                    'error': u"Notification Client {0}, No operator registered, can't send notification :{1}".format(getClientId(self._device), message)}
        sensors = self.getDmgSensors()
        if sensors :
            self._manager.sendMQMsg(sensors['msg_status']['id'], sensors['msg_status']['data_type'], data['status'])
            if data['error'] != u'' :
                self._manager.sendMQMsg(sensors['error_send']['id'], sensors['error_send']['data_type'], data['error'])
