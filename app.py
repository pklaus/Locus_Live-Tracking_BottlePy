#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, post, get, request, response, redirect, error, abort
import filedict
import json
import time
import pprint
from random import choice
import string
import re

events = filedict.FileDict(filename="data/events.dict.sqlite")

def unixtime():
    return int(time.time())

def create_id(size=8):
    return ''.join([choice(string.ascii_letters + string.digits) for i in range(size)])

@get('/')
def home():
    return 'Locus Live-Tracking via Bottle for Python'

@post('/event')
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

@get('/events')
def dump_events():
    response.headers['Content-Type'] = 'text/plain; charset=UTF8'
    evs = [events[key] for key in events]
    return pprint.pformat(evs)

run(host='0.0.0.0', port=8080, debug=True, reloader=True)
#run(host='0.0.0.0', port=8080)
#run(host='0.0.0.0', server=PasteServer, port=8080)

