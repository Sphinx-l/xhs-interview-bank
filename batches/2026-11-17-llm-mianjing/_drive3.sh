#!/bin/sh
CLI="$LOCALAPPDATA/Tabbit/LocalAgent/bin/tabbit-cli.exe"
T="xhs-h5"
clean() {
  D:/MSYS2/ucrt64/bin/python3 - "$N" <<PY
import json, sys
p = '_chunk_%s_result.json' % sys.argv[1]
try:
    r = json.load(open(p, encoding='utf-8'))
    keep = [x for x in r if x.get('status') == 'fetched']
    json.dump(keep, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
except FileNotFoundError:
    pass
PY
}
run() {
  N=$1; RID=$2
  sed "s/__CHUNK__/$N/" _crawler2.js.tpl > _crawler2_run.js
  "$CLI" nodejs --task "$T" --request-id "$RID" --tab 2105692499 --timeout-ms 165000 < _crawler2_run.js 2>&1 | grep -oE '"remaining":[0-9]+|"errorCode":"[A-Z_]+"'
}
for N in $@; do
  for P in a b c; do
    clean $N
    R=$(run $N "d-$N-$P")
    echo "chunk $N pass$P: $R"
    case "$R" in *remaining\":0*) break;; esac
  done
done
