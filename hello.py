#-*- coding:utf-8 -*-

import os
import re
from flask import Flask, render_template_string, render_template, url_for, redirect, request
import json
import urllib2
import numpy as np
import folium
#import psycopg2
#import urlparse
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
try:
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#  app.config['DEBUG'] = True
except:
  app.config['SQLAlchemny_DATABASE_URI'] = "postgresql://thomasbelahi@localhost/mylocaldb"
db = SQLAlchemy(app)


@app.route('/')
@app.route('/#')
def index():
  return render_template('index.html')

class Debt(db.Model):
  __tablename__ = 'creances'
  id = db.Column('debt_id', db.Integer, primary_key=True)
  pub_date = db.Column(db.DateTime)
  creancier = db.Column(db.String) # TODO: connect to User dataB when created
  debiteur = db.Column(db.String) # TODO: connect to User dataB when created
  drink = db.Column(db.String)
  debt_value = db.Column(db.Float)
  paid = db.Column(db.Boolean)

  def __init__(self, creancier, debiteur, drink, debt_value):
    self.pub_date = datetime.utcnow()
    self.creancier = creancier
    self.debiteur = debiteur
    self.drink = drink
    self.debt_value = debt_value
    self.paid = False


@app.route('/coffeemachine')
def coffeemachine():
  # TODO: display database and add new entry button, require login
  return render_template('coffeemachine.html', creances=Debt.query.order_by(Debt.pub_date.desc()).all())

@app.route('/new_debt', methods=['GET', 'POST'])
def new():
  if request.method == 'POST':
    print db
    print request.form['creancier'], request.form['debiteur'], request.form['drink'], request.form['debt_value']
    a = float(request.form['debt_value'])
    creance = Debt(request.form['creancier'], request.form['debiteur'], request.form['drink'], float(request.form['debt_value']))
    db.session.add(creance)
    db.session.commit()
    return redirect(url_for('coffeemachine'))
  return render_template('new_debt.html')


@app.route('/ipgp', methods=['GET','POST'])
def ipgp():
  if request.method == 'POST':
   if request.form['submit'] == 'prendre':
     ss = getStationsIPGP_prendre()
   elif request.form['submit'] == 'poser':
     ss = getStationsIPGP_poser()
  elif request.method == 'GET':
   ss = getStationsIPGP_prendre()
  return render_template_string(ss)

def getStationsIPGP_prendre():
  # clé pour API JCDecaux
  api_key='d6177aa449272d6c0bdde000927553cf45ac7c50'

  carte_ipgp = folium.Map([48.84555,2.35506], zoom_start=16)
  # stations around IPGP:
  stations_ipgp = ['05031 - LACEPEDE','05021 - JUSSIEU','05023 - PLACE JUSSIEU']
  # fetching and plotting info on map
  s = ''
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
    s = '{0} status: {1}, available bikes: {2}, free parking spots: {3}'.format(name,\
        status, available_bikes, available_bike_stands)
    s = s.encode('ascii', 'replace')
    if available_bikes==0:
      col = 'red'
    elif float(available_bikes)/(available_bike_stands+available_bikes) <=0.15:
      col= 'orange'
    else:
      col = 'green'
    carte_ipgp.circle_marker([lat, lon], popup=s, radius=50,line_color=col,fill_color=col)

  carte_ipgp.create_map('ipgp.html')
  with open('ipgp.html') as f:
    s = f.read()
  ss = '{%extends "layout.html"%}\n{%block body%}\n'+re.search('<!DOCTYPE html>.*</head>(.*)',s,re.DOTALL|re.MULTILINE).group(1)+'\n{% endblock %}'
  return ss

def getStationsIPGP_poser():
  # clé pour API JCDecaux
  api_key='d6177aa449272d6c0bdde000927553cf45ac7c50'

  carte_ipgp = folium.Map([48.84555,2.35506], zoom_start=16)
  # stations around IPGP:
  stations_ipgp = ['05031 - LACEPEDE','05021 - JUSSIEU','05023 - PLACE JUSSIEU']
  # fetching and plotting info on map
  s = ''
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
    s = '{0} status: {1}, available bikes: {2}, free parking spots: {3}'.format(name,\
        status, available_bikes, available_bike_stands)
    s = s.encode('ascii', 'replace')
    if available_bikes==available_bike_stands:
      col = 'red'
    elif float(available_bike_stands)/(available_bike_stands+available_bikes) <=0.15:
      col= 'orange'
    else:
      col = 'green'
    carte_ipgp.circle_marker([lat, lon], popup=s, radius=50,line_color=col,fill_color=col)

  carte_ipgp.create_map('ipgp.html')
  with open('ipgp.html') as f:
    s = f.read()
  ss = '{%extends "layout.html"%}\n{%block body%}\n'+re.search('<!DOCTYPE html>.*</head>(.*)',s,re.DOTALL|re.MULTILINE).group(1)+'\n{% endblock %}'
  return ss

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
    s = '{0} status: {1}, bikes: {2}, free parking spots: {3}'.format(name,\
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
    s = f.read()
  ss = '{%extends "layout.html"%}\n{%block body%}\n'+re.search('<!DOCTYPE html>.*</head>(.*)',s,re.DOTALL|re.MULTILINE).group(1)+'\n{% endblock %}'
  #return render_template('paris.html')
  return render_template_string(ss)
