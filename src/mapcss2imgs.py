#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi
import hashlib
import os
import urllib
import json

STYLES_PATH = "/srv/www/mapcss.osmosnimki.ru/htdocs/styles/"

def html():
  print "Content-Type: text/html"     # HTML is following
  print ""                            # blank line, end of headers
def urlencode(x):
  return urllib.quote(x,"")
def ScxFormattedJSON(x):
  return '<script>window.name="'+urlencode(json.dumps(x))+'"</script>'

#  print "<html><head><title>MapCSS preview</title></head><body>"
form = cgi.FieldStorage()
if "action" not in form:
  html()  
  print """<form method="post"><input type=hidden name=action value=save><input type="text" name="file" value="ttt"><textarea name=mapcss></textarea><input type=submit></form>"""
  print "</body></html>"
  exit()

elif form["action"].value == "save":
  html()
  if "file" not in form or "mapcss" not in form:
    print ScxFormattedJSON({Status:'invalid params',Result:False})
    exit()
  dirname = hashlib.md5(form["file"].value).hexdigest()
#  print dirname
  print ScxFormattedJSON({"Status":"ok","Result":True})
  try: 
    os.makedirs(STYLES_PATH + dirname)
  except OSError:
    pass
  f = open(STYLES_PATH + dirname+ "/style.mapcss","w")
  #print form["mapcss"].value
  f.write(form["mapcss"].value)

  f.close()
  os.system("python /home/gis/kothic/src/komap.py -s %s -l en -o %s >/dev/null"%(STYLES_PATH+ dirname+ "/style.mapcss", STYLES_PATH+ dirname+ "/mapnik-en.xml"))
  os.system("python /home/gis/kothic/src/komap.py -s %s -l ru -o %s 2>/dev/null"%(STYLES_PATH+ dirname+ "/style.mapcss", STYLES_PATH+ dirname+ "/mapnik-ru.xml"))
  os.system("python /home/gis/kothic/src/komap.py -s %s -l be -o %s 2>/dev/null"%(STYLES_PATH+ dirname+ "/style.mapcss", STYLES_PATH+ dirname+ "/mapnik-be.xml"))
  os.system("python /home/gis/mapnik/upgrade_map_xml.py %s --in-place 2>/dev/null >/dev/null"%( STYLES_PATH+ dirname+ "/mapnik-en.xml"))
  os.system("python /home/gis/mapnik/upgrade_map_xml.py %s --in-place 2>/dev/null >/dev/null"%( STYLES_PATH+ dirname+ "/mapnik-ru.xml"))
  os.system("python /home/gis/mapnik/upgrade_map_xml.py %s --in-place 2>/dev/null >/dev/null"%( STYLES_PATH+ dirname+ "/mapnik-be.xml"))



elif form["action"].value == "render":
#  html()
  if "bbox" not in form or "file" not in form or "height" not in form or "width" not in form:
      html()
      print "<h1>Bad arguments!</h1>"
      exit()
  import mapnik2 as mapnik
  print "Content-Type: text/html"     # HTML is following
  print                               # blank line, end of headers

  dirname = hashlib.md5(form["file"].value).hexdigest()
#  mapfile =  STYLES_PATH+ dirname+ "/mapnik-ru.xml"
  map_uri = STYLES_PATH+ dirname+"/ru"+form["bbox"].value+".png"
  imgx = int(form["height"].value)
  imgy = int(form["width"].value)
  ll = tuple([float(i) for i in  form["bbox"].value.split(",")])
  cbox = "%s,%s,%s,%s"%ll
  langs = ("ru","en","be")
  for lang in langs: 
    mapfile =  STYLES_PATH+ dirname+ "/mapnik-%s.xml"%lang
 
    map_uri = STYLES_PATH+ dirname+"/"+lang+cbox+".png"
    m = mapnik.Map(imgx,imgy)
    mapnik.load_map(m,mapfile)
    prj = mapnik.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over")
    c0 = prj.forward(mapnik.Coord(ll[0],ll[1]))
    c1 = prj.forward(mapnik.Coord(ll[2],ll[3]))
    if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
        bbox = mapnik.Box2d(c0.x,c0.y,c1.x,c1.y)
    else:
        bbox = mapnik.Envelope(c0.x,c0.y,c1.x,c1.y)
    m.zoom_to_box(bbox)
    im = mapnik.Image(imgx,imgy)
    mapnik.render(m, im)
    view = im.view(0,0,imgx,imgy) # x,y,width,height
    view.save(map_uri,'png')
    print "<img src=/mapcss/styles/"+dirname+"/"+lang+cbox+".png"+">"
  print "</body></html>"

  

  
elif form["action"].value == "GetMap":
  if "bbox" not in form or "file" not in form or "height" not in form or "width" not in form:
      html()
      print "<h1>Bad arguments!</h1>"
      exit()
  import mapnik2 as mapnik
  if "lang" in form:
    lang = form["lang"].value
  else:
    lang = "ru"
  dirname = hashlib.md5(form["file"].value).hexdigest()
  imgx = int(form["height"].value) 
  imgy = int(form["width"].value)
  ll = tuple([float(i) for i in  form["bbox"].value.split(",")])
  cbox = "%s,%s,%s,%s"%ll

#  langs = ("ru","en","be")
#  for lang in langs: 
  mapfile =  STYLES_PATH+ dirname+ "/mapnik-%s.xml"%lang
    
  map_uri = STYLES_PATH+ dirname+"/"+lang+cbox+"."+str(imgx)+"."+str(imgy)+".png"
  m = mapnik.Map(imgx,imgy)
  mapnik.load_map(m,mapfile)
  prj = mapnik.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over")
  c0 = prj.forward(mapnik.Coord(ll[0],ll[1]))
  c1 = prj.forward(mapnik.Coord(ll[2],ll[3]))
  if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
        bbox = mapnik.Box2d(c0.x,c0.y,c1.x,c1.y)
  else:
        bbox = mapnik.Envelope(c0.x,c0.y,c1.x,c1.y)
  m.zoom_to_box(bbox)
  im = mapnik.Image(imgx,imgy)
  mapnik.render(m, im)
  view = im.view(0,0,imgx,imgy) # x,y,width,height
  view.save(map_uri,'png')
  print "Location: /styles/"+dirname+"/"+lang+cbox+"."+str(imgx)+"."+str(imgy)+".png"
  print ""
#  print "</body></html>"

