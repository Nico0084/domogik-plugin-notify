#!/usr/bin/python
#-*- coding: utf-8 -*-

from domogik.tests.common.helpers import configure

configure("plugin", "notify", "vmdomogik0", "msg_header", "Domogik notification")
configure("plugin", "notify", "vmdomogik0", "send_at_start", True)
configure("plugin", "notify", "vmdomogik0", "configured", True)
