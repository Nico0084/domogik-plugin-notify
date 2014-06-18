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

This is an upgrade based on sms plugin for domogik 0.3
@author: Gizmo - Guillaume MORLET <contact@gizmo-network.fr>

Implements
========

- Class Freemobile_sms

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import urllib,urllib2
from domogik_packages.plugin_notify.lib.client_devices import BaseClientService
#from client_devices import BaseClientService

url_sms = "https://smsapi.free-mobile.fr/sendmsg?"

class Freemobile_sms(BaseClientService):
    """ Sms Control for Freemobile operator
    """
    
    def send_sms(self,to,body):
        print("sms_send : entrée")
        data = urllib.urlencode({'user' : self.login})
        data += "&"+ urllib.urlencode({'pass': self.password})
        data += "&"+ urllib.urlencode({'msg' : "{0}".format(body)})
        request = url_sms + data
        print "send_sms : \n" , request
        try:
            response = urllib2.urlopen(request)    # This request is sent in HTTP POST
        except IOError, e:
            print "failed : {0}".format(e)
            codeResult = e.code
            if codeResult == 400 : error = 'A mandatory parameter is missing'   #Un des paramètres obligatoires est manquant.
            elif codeResult == 402 : error = 'Too many SMS were sent in too little time.'      # Trop de SMS ont été envoyés en trop peu de temps.
            elif codeResult == 403 : error = 'The service is not enabled on the subscriber area, or login / incorrect key.'      # Le service n’est pas activé sur l’espace abonné, ou login / clé incorrect.
            elif codeResult == 500 : error = 'Server side error. Please try again later.'      # Erreur côté serveur. Veuillez réessayez ultérieurement.
            else : error = format(e)
            return {'status': 'SMS not sended', 'error': error}
        else :
            codeResult = response.getcode()
            response.close()
            if codeResult == 200 : error = ''     # Le SMS a été envoyé sur votre mobile.
            elif codeResult == 400 : error = 'A mandatory parameter is missing'   #Un des paramètres obligatoires est manquant.
            elif codeResult == 402 : error = 'Too many SMS were sent in too little time.'      # Trop de SMS ont été envoyés en trop peu de temps.
            elif codeResult == 403 : error = 'The service is not enabled on the subscriber area, or login / incorrect key.'      # Le service n’est pas activé sur l’espace abonné, ou login / clé incorrect.
            elif codeResult == 500 : error = 'Server side error. Please try again later.'      # Erreur côté serveur. Veuillez réessayez ultérieurement.
            else : error = 'Unknown error.'
        if error != '' :  return {'status': 'SMS not sended', 'error': error}
        else : return {'status': 'SMS sended', 'error': ''}

    def send(self, message):
        """ Send Sms
            @param message : message dict data contain at least keys:
                - 'to' : recipient of the message
                - 'header' : header for message
                - 'body" : message
                - extra key defined in 'command' json declaration like 'title', priority', ....
            @return : dict = {'status' : <Status info>, 'error' : <Error Message>}
        """
        msg = message['header'] + ': ' if message['header'] else ''
        if 'title' in message : msg = msg + ' ** ' + message['title'] + ' ** '
        msg = msg + message['body']
        result = self.send_sms(message['to'], msg)
        print result
        return result
