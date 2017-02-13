#!/usr/bin/python
#-*- coding: utf-8 -*-

### configuration ###########################################
plugin = "notify"
########################################################

from domogik.common.packagejson import PackageJson

print(u"Package validation ...")
p = PackageJson(name=plugin, pkg_type = "plugin")
print(p.json)
print(u"****************************************************")
if p.validate() == False :
    print(u"*** Error json validation for plugin : {0}".format(plugin))
else :
    print(u"Json is validate for plugin : {0}".format(plugin))
