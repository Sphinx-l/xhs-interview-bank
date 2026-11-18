#!/bin/sh
CLI="$LOCALAPPDATA/Tabbit/LocalAgent/bin/tabbit-cli.exe"
T="xhs-h5"
R=$(D:/MSYS2/ucrt64/bin/python3 -c "
import json,os
try: d=json.load(open('_refetch_result.json',encoding='utf-8'))
except FileNotFoundError: d=[]
l=json.load(open('_refetch_list.json',encoding='utf-8'))
done=set(x['note_id'] for x in d if x.get('status')=='fetched')
print(len(l)-len(done))")
while [ "$R" -gt 0 ]; do
  OUT=$("$CLI" nodejs --task "$T" --request-id "rf-$(date +%s)" --tab 2105692499 --timeout-ms 165000 < _refetch.js.tpl 2>&1 | grep -oE '"value":\{[^}]*\}|"errorCode":"[A-Z_]+"')
  echo "remaining was $R: $OUT"
  R=$(D:/MSYS2/ucrt64/bin/python3 -c "
import json
try: d=json.load(open('_refetch_result.json',encoding='utf-8'))
except FileNotFoundError: d=[]
l=json.load(open('_refetch_list.json',encoding='utf-8'))
done=set(x['note_id'] for x in d if x.get('status')=='fetched')
print(len(l)-len(done))")
done
