# !/usr/bin/python
#-*- coding: utf-8 -*-

import traceback

from domogik_packages.plugin_notify.lib.notify_client import NotifyClient, getClientId
from domogik_packages.plugin_notify.lib.client_devices import GetDeviceParams, OPERATORS_SERVICE

class NotifyClientsManagerException(Exception):
    """
    Notify Manager exception
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = u"NotifyClientsManager exception" + value

    def __str__(self):
        return repr(self.value)

class NotifyClientsManager :
    """
    Manager Notify Web Clients.
    """
    def __init__ (self, plugin, cb_send_sensor) :
        """Init manager Notify Clients"""
        self.Plugin = plugin
        self._send_sensor = cb_send_sensor
        self.clients = {} # list of all Notify Clients
        self.Plugin.log.info(u"Manager Notify Clients is ready.")

    def _del__(self):
        """Delete all Notify CLients"""
        self.Plugin.log.info(u"try __del__ NotifyClients")
        for id in self.clients : self.clients[id].close()

    def stop(self):
        """Close all Notify CLients"""
        self.Plugin.log.info(u"Closing NotifyManager.")
        for id in self.clients : self.clients[id].close()

    def addClient(self, instance):
        """Add a Notify from domogik instance"""
        name = getClientId(instance)
        if self.clients.has_key(name) :
            self.Plugin.log.debug(u"Manager Client : Notify Client {0} already exist, not added.".format(name))
            return False
        else:
            params = GetDeviceParams(self.Plugin, instance)
            if params :
                if params['operator'] in OPERATORS_SERVICE :
                    self.clients[name] = NotifyClient(self, instance, params, self.Plugin.log)
                else :
                    self.Plugin.log.error(u"Manager Client : Notify Client type {0} not exist, not added.".format(name))
                    return False
                self.Plugin.log.info(u"Manager Client : created new client {0}.".format(name))
            else :
                self.Plugin.log.info(u"Manager Client : instance not configured can't add new client {0}.".format(name))
                return False
            return True

    def removeClient(self, name):
        """Remove a Notify client and close it"""
        client = self.getClient(name)
        if client :
            client.close()
            self.clients.pop(name)

    def getClient(self, id):
        """Get Notify client object by id."""
        if self.clients.has_key(id) :
            return self.clients[id]
        else :
            return None

    def getIdsClient(self, idToCheck):
        """Get Notify client key ids."""
        retval =[]
        findId = ""
        self.Plugin.log.debug (u"getIdsClient check for device : {0}".format(idToCheck))
        if isinstance(idToCheck, NotifyClient) : # from python instance class client
            for id in self.clients.keys() :
                if self.clients[id] == idToCheck :
                    retval = [id]
                    break
        else :
            self.Plugin.log.debug (u"getIdsClient, no NotifyClient instance...")
            if isinstance(idToCheck, str) :
                findId = idToCheck
                self.Plugin.log.debug (u"str instance...")
            else :
                if isinstance(idToCheck, dict) :
                    if idToCheck.has_key('to') : findId = idToCheck['to']
                    elif idToCheck.has_key('device_id'):  # from 0MQ Request
                        findId = idToCheck['device_id']
                    elif idToCheck.has_key('name') and idToCheck.has_key('id'): # from domogik device
                        findId = getClientId(idToCheck)
            if self.clients.has_key(findId) :
                retval = [findId]
                self.Plugin.log.debug (u"key id type find")
            else :
                self.Plugin.log.debug (u"No key id type, search {0} in devices {1}".format(findId, self.clients.keys()))
                for id in self.clients.keys() :
                    self.Plugin.log.debug(u"Search in list by device key : {0}".format(self.clients[id].to))
                    if self.clients[id].to == findId :
                        self.Plugin.log.debug(u'find Notify Client by to param :)')
                        retval.append(id)
                    elif self.clients[id].getDmgDeviceId() == findId :
                        self.Plugin.log.debug(u'find Notify Client by dmg device id :)')
                        retval.append(id)
        self.Plugin.log.debug(u"getIdsClient result : {0}".format(retval))
        return retval

    def checkClientsRegistered(self, dmgDevices):
        """Check if operator clients existing or not in domogiks devices and do creation, update or remove action."""
        for device in dmgDevices:
            cId = getClientId(device)
            if self.clients.has_key(cId) :  # Client exist with same ref, just do an update of parameters
                 self.clients[cId].updateDevice(device)
            else :
                exist_Id = self.getIdsClient(device)
                if exist_Id != [] :
                    if len(exist_Id) == 1 : # Client exist but without same ref, just do an update of parameters
                        self.clients[cId] = self.clients.pop(exist_Id[0]) # rename and change key client id
                        self.Plugin.log.info(u"Notify Client {0} renamed {1}".format(exist_Id[0], cId))
                        self.clients[cId].updateDevice(device)  # update client
                    else :
                        self.log.warning(u"Inconsistency clients for same domogik device. Clients: {0}, domogik device :{1}".format(exist_Id, device))
                else :  # client doesn't exist, create it:
                    try :
                        if self.managerClients.addClient(device) :
                            self.clients[cId].NotifyConnection()
                            self.log.info(u"Ready to work with device {0}".format(cId))
                        else : self.log.info(u"Device parameters not configured, can't create Notify Client : {0}".format(cId))
                    except:
                        self.log.error(traceback.format_exc())
        # check clients to remove
        delC = []
        for cId in self.clients:
            for device in dmgDevices:
                if getClientId(device) == cId :
                    find = True
                    break;
            if not find : delC.append(cId)
        for cId in delC : self.removeClient(cId)

    def NotifyClientsConnection(self):
        """ Send a Notification connection Notify to all Clients."""
        for id in self.clients :
            self.clients[id].NotifyConnection()

    def sendMQMsg(self, sensor_id, dt_type, value):
        """Publish message over 0MQ"""
        self._send_sensor(sensor_id, dt_type, value)
