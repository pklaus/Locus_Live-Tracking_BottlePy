#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle, route, run, post, get, request, response, redirect, error, abort, static_file, TEMPLATE_PATH
from bottle import jinja2_template as template, jinja2_view
import filedict
import json
import time
import os
import pprint
from functools import partial
from datetime import datetime, date, time as dtime
from random import choice
import string
import re
import argparse

TEMPLATE_PATH.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],'views'))
DEFAULT_DB_FILE = os.path.join(os.path.split(os.path.realpath(__file__))[0],"data/events.dict.sqlite")
LATEST = dict()
EVENTS = dict()
NONAME = '_-_noname_-_'

filter_dict = {}
view = partial(jinja2_view,
          template_settings={'filters': filter_dict})

def filter(func):
	"""Decorator to add the function to filter_dict"""
	filter_dict[func.__name__] = func
	return func

@filter
def unixtime_to_iso8601(ut):
    return datetime.fromtimestamp(int(ut)).isoformat()

def unixtime():
    return int(time.time())

def create_id(size=8):
    return ''.join([choice(string.ascii_letters + string.digits) for i in range(size)])

api = Bottle()

@api.get('/')
def home():
    return 'Locus Live-Tracking via Bottle for Python'

def update_latest(event):
    try:
        name = event['name']
    except:
        name = NONAME
    try:
        LATEST[name]
    except:
        LATEST[name] = dict(id=None, server_time=0)
    if LATEST[name]['server_time'] < event['server_time']:
        LATEST[name] = dict(id=event['id'], server_time = event['server_time'])

@api.post('/event')
def store_event():
    event = dict() # we store the event's details in a dictionary
    try:
        event['lat'] = float(request.forms.getunicode('lat'))
        event['lon'] = float(request.forms.getunicode('lon'))
    except:
        abort('Please provide at least lat and lon parameters.')
    # All values that should be converted to float:
    keys = ['alt', 'speed', 'acc', 'bearing']
    for key in keys:
        try:
            event[key] = float(request.forms.getunicode(key))
        except:
            pass
    # All values that should be converted to int:
    keys = ['time', 'battery', 'gsm_signal']
    for key in keys:
        try:
            event[key] = request.forms.getunicode(key).strip()
        except:
            pass
    # All values that should be left as string:
    keys = ['name', 'track']
    for key in keys:
        try:
            event[key] = request.forms.getunicode(key).strip()
        except:
            pass
    event['id'] = create_id()
    event['server_time'] = unixtime()
    event['ip'] = request.remote_addr
    # store the event in the SQlite based dictionary
    EVENTS[event['id']] = event
    update_latest(event)
    return 'Success!'

@api.get('/events')
def dump_events():
    response.headers['Content-Type'] = 'text/plain; charset=UTF8'
    evs = [EVENTS[key] for key in EVENTS]
    return pprint.pformat(evs)

interface = Bottle()
interface.mount('/api', api)

@interface.route('/static/<path:path>')
def static(path):
    return static_file(path, root='./static')

@interface.route('/')
@view('home.jinja2')
def home():
    return dict()

@interface.route('/entire-history')
@view('events.jinja2')
def entire_history():
    return dict(events=[EVENTS[key] for key in EVENTS])

@interface.route('/latest')
@interface.route('/latest/')
@interface.route('/latest/<name:path>')
@view('latest.jinja2')
def show_latest(name=NONAME):
    if not LATEST or name not in LATEST:
        return dict(event=None)
    return dict(event=EVENTS[LATEST[name]['id']])

@interface.route('/latest_day')
def latest_day(name=NONAME):
    latest = EVENTS[LATEST[name]['id']]
    d = datetime.utcfromtimestamp(latest['server_time']).date()
    redirect('day/'+d.isoformat())

@interface.route('/day/<year:int>-<month:int>-<day:int>')
@view('day.jinja2')
def show_day(year, month, day):
    d = date(year, month, day)
    unix_lower = int(datetime.combine(d, dtime( 0,  0,  0)).strftime('%s'))
    unix_upper = int(datetime.combine(d, dtime(23, 59, 59)).strftime('%s'))
    events = []
    min_lat, min_lon = 400., 400.
    max_lat, max_lon = 0., 0.
    for key in EVENTS:
        event = EVENTS[key]
        if event['server_time'] >= unix_lower and event['server_time'] <= unix_upper:
            events.append(event)
            min_lat = min(min_lat, event['lat'])
            min_lon = min(min_lon, event['lon'])
            max_lat = max(max_lat, event['lat'])
            max_lon = max(max_lon, event['lon'])
    if len(events):
        center_lat = (max_lat + min_lat)/2
        center_lon = (max_lon + min_lon)/2
    else:
        center_lat = 50.1
        center_lon = 8.6
    return {'date': d, 'events': events, 'lat': center_lat, 'lon': center_lon}

if __name__ == '__main__':
    parser = argparse.ArgumentParser( 
      description='Start a server to store location information.' )
    parser.add_argument('-p', '--port', type=int, default=8080,
      help='The port to run the web server on.')
    parser.add_argument('-6', '--ipv6', action='store_true',
      help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('-d', '--debug', action='store_true',
      help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('-l', '--log-file',
      help='The file to store the server log in.')
    parser.add_argument('-b', '--db-file', default=DEFAULT_DB_FILE,
      help='The db to store the location information in.')
    args = parser.parse_args()
    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')
    EVENTS = filedict.FileDict(filename=args.db_file)
    for key in EVENTS:
        update_latest(EVENTS[key])
    if args.log_file:
        try:
            from requestlogger import WSGILogger, ApacheFormatter
            from logging.handlers import TimedRotatingFileHandler
            handlers = [ TimedRotatingFileHandler(args.log_file, 'd', 7) , ]
            interface = WSGILogger(interface, handlers, ApacheFormatter())
        except ImportError:
            print('Missing module wsgi-request-logger. Cannot enable logging.')
    if args.debug:
        run(interface, host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            # CherryPy is Python3 ready and has IPv6 support:
            run(interface, host='::', server='cherrypy', port=args.port)
        else:
            run(interface, host='0.0.0.0', server='cherrypy', port=args.port)

