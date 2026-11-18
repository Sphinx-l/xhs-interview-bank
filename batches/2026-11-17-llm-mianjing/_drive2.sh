#!/bin/sh
CLI="$LOCALAPPDATA/Tabbit/LocalAgent/bin/tabbit-cli.exe"
T="xhs-h4-$(date +%H%M)"
run() {
  N=$1; RID=$2
  sed "s/__CHUNK__/$N/" _crawler2.js.tpl > _crawler2_run.js
  "$CLI" nodejs --task "$T" --request-id "$RID" --timeout-ms 170000 < _crawler2_run.js 2>&1 | grep -oE '"remaining":[0-9]+|"errorCode":"[A-Z_]+"'
}
for N in 04 05 06 07 08 09 10 11 12 13 14 15 16; do
  R=$(run $N "r-$N-a"); echo "chunk $N pass1: $R"
  case "$R" in *remaining\":0*) : ;; *)
    R2=$(run $N "r-$N-b"); echo "chunk $N pass2: $R2"
    case "$R2" in *remaining\":0*) : ;; *) R3=$(run $N "r-$N-c"); echo "chunk $N pass3: $R3";; esac ;;
  esac
done
echo ALLDONE2
