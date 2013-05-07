#!/bin/bash

LAT=$((RANDOM/3000)).$RANDOM
LON=$((RANDOM/3000)).$RANDOM
ALT=$((RANDOM/30))
SPEED=$((RANDOM/300+30))
ACC=$((RANDOM/3000+5))
BEARING=$((RANDOM/100))
TIME=$(date +%s)000

wget \
  -O - \
  --post-data \
  "lat=$LAT&lon=$LON&alt=$ALT&speed=$SPEED&acc=$ACC&bearing=$BEARING&time=$TIME" \
  http://localhost:8080/api/event
