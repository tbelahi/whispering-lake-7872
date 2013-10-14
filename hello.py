#-*- coding:utf-8 -*-

import os
from flask import Flask, render_template_string
import json
import urllib2
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello():
  return 'hello world!'

@app.route('/Raph')
def raph():
  return 'café ?'

@app.route('/velo')
def velo():
  # clé pour API JCDecaux 
  api_key='d6177aa449272d6c0bdde000927553cf45ac7c50'

  # stations around IPGP:
  stations_ipgp = ['05031 - LACEPEDE','05021 - JUSSIEU','05023 - PLACE JUSSIEU']
  #s = '{%extends "layout.html"%}\n{%block body%}'
  s = ''
  # fetching and plotting info on map
  for station in stations_ipgp:
    # requesting real-time info on the station from Vélib API
    url = 'https://api.jcdecaux.com/vls/v1/stations/{0}?contract=Paris&apiKey={1}'\
          .format(str(station[:5]), api_key)
    response = urllib2.urlopen(url).read()
    # put them in a dictionnary
    station_real_time = json.loads(response)
    
    #create the marker corresponding to the station and it's status
    status = station_real_time['status']
    name = station_real_time['name'].encode('ascii','replace')
    available_bikes = station_real_time['available_bikes']
    available_bike_stands = station_real_time['available_bike_stands']
    lon = station_real_time['position']['lng']
    lat = station_real_time['position']['lat']
    s += '<p>{0} status: {1}, bikes: {2} ,free spots: {3}</p>\n'.format(name,\
        status, available_bikes, available_bike_stands)

  #return 'en construction'
  #s += '{% endblock %}'
  s += 'random numpy generated number '+str(np.random.rand())
  return render_template_string(s)
