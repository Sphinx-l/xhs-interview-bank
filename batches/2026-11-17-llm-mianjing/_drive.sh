#!/bin/sh
CLI="$LOCALAPPDATA/Tabbit/LocalAgent/bin/tabbit-cli.exe"
cd "$(dirname "$0")"
for N in 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16; do
  TAB=$("$CLI" create --task "xhs-harvest-2" 2>/dev/null | D:/MSYS2/ucrt64/bin/python3 -c "import sys,json
try:
    d=json.load(sys.stdin); print(d['tabs'][0]['tabId'])
except Exception: print('')" )
  [ -z "$TAB" ] && TAB=2105691830
  sed "s/__CHUNK__/$N/" _crawler.js.tpl > _crawler_run.js
  echo "=== chunk $N tab $TAB start $(date +%H:%M:%S) ==="
  "$CLI" nodejs --task "xhs-harvest-2" --tab "$TAB" --request-id "crawl-$N" --timeout-ms 170000 < _crawler_run.js 2>&1 | grep -o '"value":{[^}]*}' | tail -1
done
echo "ALL DONE $(date +%H:%M:%S)"
