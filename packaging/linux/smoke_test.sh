#!/usr/bin/env bash
# Launch the app under a virtual X server and make sure it stays alive.
#
#   packaging/linux/smoke_test.sh <path-to-binary> [seconds]
#
# Needs xvfb-run. Exits non-zero if the app dies before the timeout.
set -uo pipefail

BIN=$1
SECONDS_ALIVE=${2:-10}
LOG=$(mktemp)
YTDL_CONFIG_DIR=$(mktemp -d)
export YTDL_CONFIG_DIR
export QT_QPA_PLATFORM=xcb

xvfb-run -a -s "-screen 0 1280x800x24" bash -c '
    "$1" >"$2" 2>&1 &
    pid=$!
    sleep "$3"
    if kill -0 "$pid" 2>/dev/null; then
        echo "App still running after $3 s (pid $pid), stopping it."
        kill "$pid"
        wait "$pid" 2>/dev/null
        exit 0
    fi
    wait "$pid"
    echo "App exited early with status $?"
    exit 1
' smoke "$BIN" "$LOG" "$SECONDS_ALIVE"
rc=$?

echo "----- app output -----"
cat "$LOG"
echo "----------------------"
rm -rf "$LOG" "$YTDL_CONFIG_DIR"
exit $rc
