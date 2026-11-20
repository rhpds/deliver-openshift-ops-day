#!/bin/sh
# Re-apply the console-reload watchdog script tag and marker after every
# container start; the content entrypoint regenerates the served site, so
# keep checking for two minutes until it has settled.
for i in $(seq 1 60); do
  if [ -f /showroom/www/index.html ] && ! grep -q console-reload-watchdog /showroom/www/index.html; then
    sed -i 's|</head>|<script src="./console-reload-watchdog.js"></script></head>|' /showroom/www/index.html
    date +%s > /showroom/www/console-reload.marker
  fi
  sleep 2
done
