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

Send SMS on web service for french telephony providers : Orange_sms-web, SFR_sms-web, Bouygues_sms-web, Freemobile_sms-web.

This is an upgrade based on sms plugin for domogik 0.3
@author: Gizmo - Guillaume MORLET <contact@gizmo-network.fr>

Implements
========

- class BaseClientService to handle Operators

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""
OPERATORS_SERVICE =  ['SFR_sms-web', 'Orange_sms-web', 'Bouygues_sms-web', 'Freemobile_sms-web', 'Newtifry']

def createDevice(params, log = None):
    """ Create a device depending of operator, use instance for get parameters.
        - Developer : add your python class derived from DeviceBase class."""
    newOperator = None
    if params['operator'] == 'SFR_sms-web' :
        from domogik_packages.plugin_notify.lib.smsweb_sfr import SFR_sms
        newOperator = SFR_sms(params, log)
    elif params['operator'] == 'Orange_sms-web' :
        from domogik_packages.plugin_notify.lib.smsweb_orange import Orange_sms
        newOperator = Orange_sms(params, log)
    elif params['operator'] == 'Bouygues_sms-web' :
        from domogik_packages.plugin_notify.lib.smsweb_bouygues import Bouygues_sms
        newOperator = Bouygues_sms(params, log)
    elif params['operator'] == 'Freemobile_sms-web' :
        from domogik_packages.plugin_notify.lib.smsweb_freemobile import Freemobile_sms
        newOperator = Freemobile_sms(params,  log)
    elif params['operator'] == 'Newtifry' :
        from domogik_packages.plugin_notify.lib.newtifry import Newtifry
        newOperator = Newtifry(params,  log)
    return newOperator

def GetDeviceParams(xplPlugin, device):
    """ Return all internal parameters depending of instance_type.
        - Developer : add your instance_type proper parameters
            @param xplPlugin : XplPlugin base class reference for "get_parameter" and "get_parameter_for_feature"" methods access.
                type : object class XplPlugin
            @param device :  domogik device data.
                type : dict
            @return : parameters for creating or update ClientService object.
                    Value must contain at least keys :
                        - 'operator' = Selected from OPERATORS_SERVICE
                        - 'to' = Client reference, the same as xPL key 'to'
                type : dict
    """
    print (u"Extract parameters from device : \n{0}".format(device))
    if device['device_type_id'] == 'notify.smsweb':
        operator = xplPlugin.get_parameter(device, 'operator')
        id = xplPlugin.get_parameter_for_feature(device, 'xpl_stats',  'xPL_ack-msg',  'to')
        login = xplPlugin.get_parameter(device, 'login')
        pwd = xplPlugin.get_parameter(device, 'pwd')
        if operator and device["name"] and id and login and pwd :
            params = {'name': device["name"], 'operator' : operator,  'to' : id,  'login' : login,  'pwd': pwd}
            return params
    if device['device_type_id'] == 'notify.newtifry':
        operator = 'Newtifry'
        id = xplPlugin.get_parameter_for_feature(device, 'xpl_stats',  'xPL_ack-msg',  'to')
        sourcekey = xplPlugin.get_parameter(device, 'sourcekey')
        backend = xplPlugin.get_parameter(device, 'backend')
        defaulttitle = xplPlugin.get_parameter(device, 'defaulttitle')
        if operator and device["name"] and id and sourcekey :
            params = {'name': device["name"] , 'operator' : operator, 'to' : id, 'sourcekey' : sourcekey, 'backend': backend,'defaulttitle' : defaulttitle}
            return params
    return None

class BaseClientService():
    """ Basic Class for operator functionnalities.
        - Developper : Use on inherite class to impllement new operator class
                Overwrite  methods to handle xpl event."""

    def __init__(self, params, log):
        """ Must be called and overwrited with operator parameters.
        """
        self._log = log
        self.update(params)
        if self._log : self._log.info(u"Client {0} created , with parameters : {1}".format(self.__class__.__name__,  params))

    def update(self,  params):
        """ Create or update internal data, must be overwrited if others params needed.
            @param params :  Values come from 'GetDeviceParams'.
                type : dict
            @param get_parameter : XplPlugin.get_parameter method.
                type : methode (device, key)
        """
        if 'to' in params : self.to = params['to']
        else :
            if self._log : self._log.warning(u"Updating Client {0}, parameters 'to' missing : {1}".format(self.__class__.__name__,  params))
        if 'login' in params : self.login = params['login']
        if 'pwd' in params : self.password = params['pwd']

    def send(self, message):
        """ Must be overwrited:
            @param message : message dict data contain at least keys:
                - 'to' : recipient of the message
                - 'header' : header for message
                - 'body" : message
                - extra key defined in 'command' json declaration like 'title', priority', ....
            @return : dict = {'status' : <Status info>, 'error' : <Error Message>}
        """
        return {'status': u'SMS not sended', 'error': u'Send function not defined.'}

