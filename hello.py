#-*- coding:utf-8 -*-

import os
from flask import Flask, render_template_string, render_template, url_for, redirect
import json
import urllib2
import numpy as np
import folium

app = Flask(__name__)

@app.route('/')
@app.route('/#')
def index():
  return render_template('index.html')

@app.route('/Raph')
def raph():
  return 'café ?'

@app.route('/ipgp')
def ipgp():
  # clé pour API JCDecaux 
  api_key='d6177aa449272d6c0bdde000927553cf45ac7c50'

  # stations around IPGP:
  stations_ipgp = ['05031 - LACEPEDE','05021 - JUSSIEU','05023 - PLACE JUSSIEU']
  s = '{%extends "layout.html"%}\n{%block body%}'
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
  s += '{% endblock %}'
  #s += 'random numpy generated number '+str(np.random.rand())
  return render_template_string(s)

@app.route('/paris')
def paris():
  url = 'https://api.jcdecaux.com/vls/v1/stations?contract=Paris&apiKey=d6177aa449272d6c0bdde000927553cf45ac7c50'
  response = urllib2.urlopen(url).read()
  stations = json.loads(response)
  
  map_paris = folium.Map([48.85329,2.34902], zoom_start=12)
  # fetching and plotting info on map
  for station in stations:
    #create the marker corresponding to the station and it's status
    status = station['status']
    name = station['name'].encode('ascii','replace')
    available_bikes = station['available_bikes']
    available_bike_stands = station['available_bike_stands']
    lon = station['position']['lng']
    lat = station['position']['lat']
    s = '{0} status: {1}, bikes: {2} ,free spots: {3}'.format(name,\
           status, available_bikes, available_bike_stands)
    s = s.encode('ascii', 'replace')
    if available_bikes==0:
      col = 'red'
    elif float(available_bikes)/(available_bike_stands+available_bikes) <=0.15:
      col= 'orange'
    else:
      col = 'green'
    map_paris.circle_marker([lat, lon], popup=s, radius=50,line_color=col,fill_color=col)

  map_paris.create_map('paris.html')
  with open('paris.html') as f:
    s = '{%extends "layout.html"%}\n{%block body%}\n'+f.read()+'\n{% endblock %}'
  with open('templates/paris.html', 'w') as g:
    g.write(s)
  #return render_template('paris.html')
  return render_template_string(s)
