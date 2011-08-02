#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi
import hashlib
import os
import urllib
import json

STYLES_PATH = "/srv/www/mapcss.osmosnimki.ru/htdocs/styles/styles/"

def html():
  print "Content-Type: text/html"     # HTML is following
  print                               # blank line, end of headers
def urlencode(x):
  return urllib.quote(x,"")
form = cgi.FieldStorage()
if "action" not in form:
  html()
  print """<form method="post"><input type=hidden name=action value=save><input type="text" name="file" value="ttt"><textarea name=mapcss></textarea><input type=submit></form>"""
  print "</body></html>"
  exit()

elif form["action"].value == "js":
  html()
  if "mapcss" not in form:
    print ["error!"]
    exit()
  dirname = hashlib.md5(form["mapcss"].value).hexdigest()
  try:
    os.makedirs(STYLES_PATH + dirname)
  except OSError:
    pass
  f = open(STYLES_PATH + dirname+ "/style.mapcss","w")
  f.write(form["mapcss"].value)

  f.close()
  os.system("python /var/www/kothic/kothic-js/scripts/mapcss_converter.py --mapcss %s -o %s"%(STYLES_PATH+ dirname+ "/style.mapcss", STYLES_PATH+ dirname+ "/style.js -p /leaf/icons"))
  print open(STYLES_PATH+ dirname+ "/style.js", "r").read()
