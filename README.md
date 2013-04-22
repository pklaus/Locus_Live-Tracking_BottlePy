## Locus Pro Maps  Live-Tracking  Web Server

This is a web api based on bottle.py to store location
information generated using Locus Map Pro Live-Tracking.

Up to now this is not much more that a proof of concept.

**What works:** You can run the `./app.py` file in this project
and set up Locus on your Android phone to POST to the URL
<http://example.com:8080/event> where example.com is the
server you're running this on.
A list of all data collected so far is available at
the URL `/events`.

More is to be included in the [ToDo list](TODO.md).

### Locus' Live-Tracking Feature

More information on the Live-Tracking feature of Locus Map Pro can be found on
[its documentation web page](http://docs.locusmap.eu/doku.php/manual:live_tracking).

### Alternatives

* Easy via Google Docs: <http://docs.locusmap.eu/doku.php/manual:live_tracking_google_docs>
* More interfaces and ideas on <http://forum.locusmap.eu/viewtopic.php?f=44&t=2061>
* Another Service using Django, Bing and Leaflet: <http://vapiti.lnet.fi/LocusTracker/>
* A commercial service livetrack24 with Locus: <http://forum.locusmap.eu/viewtopic.php?f=26&t=2628>

### Requirements

This web app runs on Python 3.3, [Bottle][] and [CherryPy][].
Also it includes a version of [FileDict][].

[Bottle]: http://bottlepy.org
[CherryPy]: http://www.cherrypy.org/
[FileDict]: https://github.com/pklaus/filedict/tree/threadsafe

