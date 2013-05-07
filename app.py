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

TEMPLATE_PATH.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],'views'))

events = filedict.FileDict(filename="data/events.dict.sqlite")

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

run(interface, host='0.0.0.0', port=8080, debug=True, reloader=True)
# CherryPy is Python3 ready and has IPv6 support:
#run(host='::', server='cherrypy', port=8080)

