## Locus Pro Maps  Live-Tracking  Web Server

This is a web api based on bottle.py to store location
information generated using Locus Map Pro Live-Tracking.

Up to now this project is not quite finished or polished
but it does work already.

You can run the `./app.py` file in this project and
set up Locus on your Android phone to POST to the URL
<http://example.com:8080/api/event> where example.com
is the server you're running this on.
A JSON interface to the data collected is available at
the URL `/api/events`.

### Locus' Live-Tracking Feature

More information on the Live-Tracking feature of Locus Map Pro can be found on
[its documentation web page](http://docs.locusmap.eu/doku.php/manual:live_tracking).

### Alternatives

* Easy via Google Docs: <http://docs.locusmap.eu/doku.php/manual:live_tracking_google_docs>
* More interfaces and ideas on <http://forum.locusmap.eu/viewtopic.php?f=44&t=2061>
* Another Service using Django, Bing and Leaflet: <http://vapiti.lnet.fi/LocusTracker/>
* The commercial service *livetrack24* with Locus: <http://forum.locusmap.eu/viewtopic.php?f=26&t=2628>

### Requirements

This web app runs on Python 3.3, [Bottle][] with [Jinja2][] and [CherryPy][].
Also it includes a version of [FileDict][].

[Bottle]: http://bottlepy.org
[CherryPy]: http://www.cherrypy.org/
[Jinja2]: http://jinja.pocoo.org/
[FileDict]: https://github.com/pklaus/filedict/tree/threadsafe

