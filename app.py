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
from datetime import datetime
from random import choice
import string
import re
import argparse

TEMPLATE_PATH.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],'views'))
DEFAULT_DB_FILE = os.path.join(os.path.split(os.path.realpath(__file__))[0],"data/events.dict.sqlite")

events = dict()

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

latest = dict()
def update_latest(event):
    try:
        name = event['name']
    except:
        name = 'noname'
    try:
        latest[name]
    except:
        latest[name] = dict(id=None, server_time=0)
    if latest[name]['server_time'] < events[key]['server_time']:
        latest[name]['id'] = events[key]['id']
        latest[name]['server_time'] = events[key]['server_time']

@api.post('/event')
def store_event():
    event = dict() # we store the event's details in a dictionary
    try:
        event['lat'] = float(request.forms.getunicode('lat').strip())
        event['lon'] = float(request.forms.getunicode('lon').strip())
    except:
        abort('Please provide at least lat and lon parameters.')
    keys = ['alt', 'speed', 'acc', 'bearing', 'time']
    for key in keys:
        try:
            event[key] = request.forms.getunicode(key).strip()
        except:
            pass
    event['id'] = create_id()
    event['server_time'] = unixtime()
    event['ip'] = request.remote_addr
    # store the event in the SQlite based dictionary
    events[event['id']] = event
    update_latest(event)
    return 'Success!'

@api.get('/events')
def dump_events():
    response.headers['Content-Type'] = 'text/plain; charset=UTF8'
    evs = [events[key] for key in events]
    return pprint.pformat(evs)

interface = Bottle()
interface.mount(api, '/api')

@interface.route('/static/<path:path>')
def static(path):
    return static_file(path, root='./static')

@interface.route('/')
@view('events.jinja2')
def index():
    return dict(events=[events[key] for key in events])

@interface.route('/latest')
@interface.route('/latest/')
@interface.route('/latest/<name:path>')
@view('latest.jinja2')
def show_latest(name='noname'):
    if name not in latest:
        abort(404, 'Name not found.')
    return dict(event=events[latest[name]['id']])

if __name__ == '__main__':
    parser = argparse.ArgumentParser( 
      description='Start a server to store location information.' )
    parser.add_argument('-p', '--port', type=int, default=8080,
      help='The port to run the web server on.')
    parser.add_argument('-6', '--ipv6', action='store_true',
      help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('-d', '--debug', action='store_true',
      help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('-b', '--db-file', default=DEFAULT_DB_FILE,
      help='The db to store the location information in.')
    args = parser.parse_args()
    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')
    events = filedict.FileDict(filename=args.db_file)
    for key in events:
        update_latest(events[key])
    if args.debug:
        run(interface, host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            # CherryPy is Python3 ready and has IPv6 support:
            run(interface, host='::', server='cherrypy', port=args.port)
        else:
            run(interface, host='0.0.0.0', server='cherrypy', port=args.port)

