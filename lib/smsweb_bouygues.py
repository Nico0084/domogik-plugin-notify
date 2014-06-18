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

- Class Bouygues_sms

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import sys
import mechanize
import cookielib
import urllib
import re
from domogik_packages.plugin_notify.lib.client_devices import BaseClientService

url_sms = "http://www.espaceclient.bouyguestelecom.fr/ECF/jsf/client/envoiSMS/viewEnvoiSMS.jsf"
url_sms2 = 'http://www.mobile.service.bbox.bouyguestelecom.fr/services/SMSIHD/sendSMS.phtml'

class Bouygues_sms(BaseClientService):
    """ Sms Control
    """
    phone_regex = re.compile('^(\+33|0033|0)(6|7)(\d{8})$')

    def portail_login(self,browser):
        browser.open(url_sms)
        print(browser.geturl())
        for x in browser.forms():
        	print(x)	
        browser.select_form(name='code')
        browser['j_username'] = login
        browser['j_password'] = password
        browser.submit()
        return 1

    def send_sms(self,to,body,browser):
        print("sms_send : entrée")
        if self.phone_regex.match(to) is None:
            return {'status': 'SMS not sended', 'error': 'Sms format to is bad.'}
        if self.phone_regex.match(self.to) is None:
            return {'status': 'SMS not sended', 'error': 'Sms format phone is bad.'}

        browser.open(url_sms2)
        print("sms_send : formulaire sms")
        for x in browser.forms():
                print(x)	
        browser.select_form(nr=0)
        browser['fieldMsisdn'] = to
        browser['fieldMessage'] = body.encode('utf-8')
        browser.submit()
        return {'status': 'SMS sended', 'error': ''}

    def send(self, to, body):
        """ Send Sms
            @param message : message dict data contain at least keys:
                - 'to' : recipient of the message
                - 'header' : header for message
                - 'body" : message
                - extra key defined in 'command' json declaration like 'title', priority', ....
            @return : dict = {'status' : <Status info>, 'error' : <Error Message>}
        """
        br = mechanize.Browser()

        br.set_handle_equiv(True)
        br.set_handle_robots(False)
        br.set_handle_referer(True)
        br.set_handle_refresh(True)
        br.set_handle_redirect(True)

        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        #self._log.debug("call back5")
        print("function Sms Send : before portail_login")
        if self.portail_login(br):
            print("function Sms Send : between portail_login and send_sms")
            msg = message['header'] + ': ' if message['header'] else ''
            if 'title' in message : msg = msg + ' ** ' + message['title'] + ' ** '
            msg = msg + message['body']
            result = self.send_sms(message['to'], msg, br)
            print("function Sms Send : after send_sms")
        else:
            print("function portail_login : error")
            result = {'status': 'SMS not sended', 'error': 'Portail login error.'}
        return result

