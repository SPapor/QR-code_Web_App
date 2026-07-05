#!/bin/sh
set -e

# the db volume is created root-owned on first use; hand it to the app
# user (uid 1000 == the host user, so host-mounted backup dirs stay writable),
# then drop root for the actual process
if [ "$(id -u)" = "0" ]; then
    [ -d /data ] && chown -R app:app /data
    exec setpriv --reuid=app --regid=app --init-groups "$@"
fi
exec "$@"
