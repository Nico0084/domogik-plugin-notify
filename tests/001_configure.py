#!/usr/bin/python
#-*- coding: utf-8 -*-

from domogik.tests.common.helpers import configure, delete_configuration
from domogik.common.utils import get_sanitized_hostname

plugin =  "notify"

host_id = get_sanitized_hostname()
delete_configuration("plugin", plugin, host_id)

configure("plugin", plugin, host_id, "msg_header", "Domogik notification")
configure("plugin", plugin, host_id, "send_at_start", True)
configure("plugin", plugin, host_id, "configured", True)
