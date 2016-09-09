# -*- coding: utf-8 -*-

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
Send Notification message with newtifry service.

Implements
========

- Class Newtifry

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import urllib,urllib2
import json
import traceback

#from domogik_packages.plugin_notify.lib.client_devices import BaseClientService
from client_devices import BaseClientService

BACKEND_NEWTIFRY = "https://newtifry.appspot.com/newtifry"

class Newtifry(BaseClientService):
    """ Notification Control for Newtifry web service
    """
    def update(self, params):
        """ Overwrited of BaseClientService class for extra parameters.
            @param params :  parameters from GetDeviceParams() of domogik device.
                type : dict
        """
        BaseClientService.update(self, params)
        self.sourcekey = params['sourcekey']
        self.backend = params['backend'] if 'backend' in params else None
        self.defaulttitle = params['defaulttitle'] if 'defaulttitle' in params else None

    def send_msg(self, message):
        backend = BACKEND_NEWTIFRY if self.backend == None else self.backend
        try:
            request =  urllib.urlencode(message)
        except :
            error = traceback.format_exc()
            if self._log : self._log.error(u"Newtifry message send failed : {0}".format(error))
            return {'status': u'Message not sended', 'error': u"Message send failed : {0}".format(error)}
        self._log.debug("Newtifry, send_msg : {0}".format(request))
        try:
            response = urllib2.urlopen(backend, request)    # This request is sent in HTTP POST
            # Read the body.
            body = response.read()
            # It's JSON - parse it.
            contents = json.loads(body)
            if contents.has_key('error'):
                return {'status': u'Message not sended', 'error': "Server did not accept our message: {0}".format(contents['error'])}
            else:
                return {'status': u'Message sended. Size: {0}.'.format( contents['size']), 'error': u''}
        except urllib2.URLError, e:
            return {'status': u'Message not sended', 'error':  format(e)}

    def send(self, message):
        """ Send message
            @param message : message dict data contain at least keys:
                - 'to' : recipient of the message
                - 'header' : header for message
                - 'body" : message
                - extra key defined in 'command' json declaration like 'title', priority', ....
            @return : dict = {'status' : <Status info>, 'error' : <Error Message>}
        """
        try :
            msg = {'format' : 'json',  'source': self.sourcekey, 'title': u'Notification', 'message': message['body'].encode('utf-8')}
            if 'title' in message : msg['title'] = message['title'].encode('utf-8')
            elif self.defaulttitle : msg['title'] = self.defaulttitle.encode('utf-8')
            # optional parameters
            if 'priority' in message : msg['priority'] = int(float(message['priority']))
            if 'url' in message : msg['url'] = message['url'].encode('utf-8')
            if 'image' in message : msg['image'] = message['image'].encode('utf-8')
            result = self.send_msg(msg)
        except :
            result = {'status': u"Message not sended", 'error':  u"Bad message format : {0}".format(message)}
            self._log.warning(u"Newtifry : {0} Message <{1}> not sended. {2}".format(self.to, message, traceback.format_exc()))
        return result
