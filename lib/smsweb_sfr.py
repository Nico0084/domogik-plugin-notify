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

- Class SFR_sms

@author: Nico <nico84dev@gmail.com>
@copyright: (C) 2007-2014 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import mechanize
import cookielib
import re
import traceback

from domogik_packages.plugin_notify.lib.client_devices import BaseClientService

url_sms = "http://www.sfr.fr/xmscomposer/index.html?todo=compose"
url_confirm = 'http://www.sfr.fr/xmscomposer/mc/envoyer-texto-mms/confirm.html'
service_url = 'http://www.sfr.fr/xmscomposer/j_spring_cas_security_check'
url_verif_auth = 'https://www.sfr.fr/cas/login?service=http%3A%2F%2Fwww.sfr.fr%2Fxmscomposer%2Fj_spring_cas_security_check'

class SFR_sms(BaseClientService):
    """ Sms Control for SFR operator
    """
    phone_regex = re.compile('^(\+33|0033|0)(6|7)(\d{8})$')

    def portail_login(self, browser):
        browser.open(url_sms)
        self._log.debug("SFR_sms-web: {0}".format(browser.geturl()))
        for x in browser.forms():
        	self._log.debug("    SFR_sms-web: {0}".format(x))
        browser.select_form(nr=0)
        browser['username'] = self.params['login']
        browser['password'] = self.params['pwd']
        browser['remember-me'] = ['on']
        browser.submit()
        return 1

    def send_sms(self, to, body, browser):
        if self.phone_regex.match(to) is None:
            return {'status': u'SMS not sended', 'error': 'Sms format phone {0} is bad.'.format(to)}

        browser.open(url_sms)
        for x in browser.forms():
        	self._log.debug("    SFR_sms-web: {0}".format(x))
        browser.select_form(nr=0)
        try:
            browser['msisdns'] = to
            browser['textMessage'] = body.encode('utf-8')
            browser.submit()
            for x in browser.forms():
                self._log.debug("    SFR_sms-web: {0}".format(x))
            browser.select_form(nr=0)
            browser.submit()
            return {'status': u'SMS sended', 'error': ''}
        except :
            error = traceback.format_exc()
            if self._log : self._log.error(u"Orange_sms-web sms send failed : {0}".format(error))
            return {'status': u'SMS not sended', 'error': u"SMS send failed : {0}".format(error)}


    def send(self, message):
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
        self._log.debug(u"SFR_sms-web, function Sms Send : before portail_login : {0}".formate(message))
        if self.portail_login(br):
            msg = message['header'] + u': ' if message['header'] else u''
            if 'title' in message : msg = msg + u' ** ' + message['title'] + u' ** '
            msg = msg + message['body']
            result = self.send_sms(message['to'], msg , br)
            self._log.debug("SFR_sms-web, function Sms Send : after send_sms. {0}".format(result))
        else:
            self._log.debug("SFR_sms-web, function portail_login : error")
            result = {'status': u'SMS not sended', 'error': u'Portail login error.'}
        return result
