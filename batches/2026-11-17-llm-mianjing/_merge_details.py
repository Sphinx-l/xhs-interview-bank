import json, glob, re
out = {}
for p in sorted(glob.glob('_chunk_*_result.json')):
    for r in json.load(open(p, encoding='utf-8')):
        out[r['note_id']] = r
# refetch 结果覆盖补充
try:
    for r in json.load(open('_refetch_result.json', encoding='utf-8')):
        if r.get('status') == 'fetched':
            old = out.get(r['note_id'], {})
            old.update({k: v for k, v in r.items() if k not in ('status',)})
            old['refetched'] = True
            out[r['note_id']] = old
except FileNotFoundError:
    pass
json.dump(list(out.values()), open('details_collected.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
rich = [r for r in out.values() if len(re.sub(r'#[^#\s]+#?', '', r.get('desc') or '').strip()) > 60]
print('total', len(out), '| rich-text', len(rich), '| with-imgs', sum(1 for r in out.values() if r.get('img_count')))
