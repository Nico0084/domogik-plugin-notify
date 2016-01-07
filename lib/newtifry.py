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
#from domogik_packages.plugin_notify.lib.client_devices import BaseClientService
from client_devices import BaseClientService

BACKEND_NEWTIFRY = "https://newtifry.appspot.com/newtifry"

class Newtifry(BaseClientService):
    """ Notification Control for Newtifry web service
    """
    def update(self,  params):
        """ Create or update internal data, must be overwrited.
            @param params :  domogik type.
                type : dict
            @param get_parameter : XplPlugin.get_parameter method.
                type : methode (device, key)
        """
        self.to = params['to']
        self.sourcekey = params['sourcekey']
        self.backend = params['backend'] if 'backend' in params else None
        self.defaulttitle = params['defaulttitle'] if 'defaulttitle' in params else None

    def send_msg(self, message):
        backend = BACKEND_NEWTIFRY if self.backend == None else self.backend
        request =  urllib.urlencode(message)
        print (u"send_msg : {0}".format(request))
        try:
            response = urllib2.urlopen(backend,  request)    # This request is sent in HTTP POST
            # Read the body.
            body = response.read()
            # It's JSON - parse it.
            contents = json.loads(body)
            print (contents)
            if contents.has_key('error'):
                return {'status': u'Message not sended', 'error': "Server did not accept our message: {0}".format(contents['error'])}
            else:
                return {'status': u'Message sended. Size: {0}.'.format( contents['size']), 'error': u''}
        except urllib2.URLError, e:
            print (u"failed : {0}".format(e))
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
        msg = {'format' : 'json',  'source': self.sourcekey, 'title': u'Notification', 'message': message['body']}
        if 'title' in message : msg['title'] = message['title']
        elif self.defaulttitle : msg['title'] = self.defaulttitle
        if 'priority' in message : msg['priority'] = message['priority']
        if 'url' in message : msg['url'] = message['url']
        if 'image' in message : msg['image'] = message['image']
        result = self.send_msg(msg)
        print(result)
        return result
