### ToDo

The next steps to work on could be the following:

* Display the current location:
  * A box on the home page: "Philipp is currently here: "
* Display a Track
  * Using [a Polyline with Leaflet](http://leafletjs.com/reference.html#polyline)
  * [Using OpenLayers](http://wiki.openstreetmap.org/wiki/Openlayers_Track_example)
  * Problem: The location updates are not 'a track'. What can you do about it?  
    Simply connect the dots of the last day / 48h / week / month.  
    Restrict to a maximum of x dots by default.  
    If there is no dot for a longer period of time (more than x minutes / hours),
    don't connect them but start a new track segment.
* Make tracks downloadable as GPX  
  This could be implemented in an API call /api/gpx?name=<name>&period=<weeks>
* Extend the information stored in events:
  The API call to POST an /event could store more parameters:
  * user name
  * current mission / track
  * The new fields in Locus: battery, gsm_sign

