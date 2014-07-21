#!/usr/bin/python
#-*- coding: utf-8 -*-

from domogik.tests.common.helpers import configure, delete_configuration
from domogik.common.utils import get_sanitized_hostname

host_id = get_sanitized_hostname()
delete_configuration("plugin", "notify", host_id)

configure("plugin", "notify", host_id, "msg_header", "Domogik notification")
configure("plugin", "notify", host_id, "send_at_start", True)
configure("plugin", "notify", host_id, "configured", True)
