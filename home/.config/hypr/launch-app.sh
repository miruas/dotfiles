#!/bin/sh
set -eu
if uwsm check is-active compositor-only; then
    exec uwsm app -- "$@"
fi
# Give apps their own lifecycle even when launched by the desktop shell.
exec systemd-run --user --collect --quiet --service-type=exec --property=ExitType=cgroup --property=PartOf=graphical-session.target --slice=app.slice --working-directory="$HOME" -- "$@"
