# -*- coding: utf-8 -*-
"""批次 2026-11-16-agent-mianjing：从 notes/ 快照生成 mianjing/ 主产物"""
import json, glob, os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))

def channel_of(title, desc, role):
    probe = (title or '') + ' ' + (desc or '')[:200] + ' ' + (role or '')
    if re.search(r'社招|工作\s*\d+\s*年|\d+\s*年经验', probe): return '社招'
    if re.search(r'秋招|春招|提前批|校招|届', probe): return '校招'
    if re.search(r'实习|日常实习', probe): return '实习'
    return '未标注'

def clean_desc(desc):
    lines = []
    for l in (desc or '').splitlines():
        l = l.strip()
        if not l: continue
        if re.fullmatch(r'(#\S*?#)+', l.replace(' ', '')): continue  # 纯话题标签行
        if re.match(r'^#[^#]+[话题]＃?#?$', l): continue
        lines.append(l)
    return lines

def extract_image_qs(path):
    """从 image-extract.md 取题面行（编号行），带图号标注"""
    out = []
    img = ''
    for l in open(path, encoding='utf-8').read().splitlines():
        l = l.rstrip()
        m = re.match(r'^>\s*来自\s*(\S+)', l)
        if m: img = m.group(1); continue
        if not l.strip() or l.startswith('#'): continue
        s = l.strip()
        if re.match(r'^\d+[、\.\)]|^[\(（]\d+[\)）]|^[①②③④⑤⑥⑦⑧⑨⑩]', s):
            out.append((img, s))
    return out

m = json.load(open(os.path.join(BASE, 'manifest.json'), encoding='utf-8'))
stats = []
for x in m['notes']:
    if x['status'] != 'retained': continue
    nid = x['note_id']
    nj_path = os.path.join(BASE, 'notes', nid, 'note.json')
    if not os.path.exists(nj_path): continue
    nj = json.load(open(nj_path, encoding='utf-8'))
    desc_lines = clean_desc(nj.get('desc', ''))
    ie_path = os.path.join(BASE, 'notes', nid, 'image-extract.md')
    img_qs = extract_image_qs(ie_path) if os.path.exists(ie_path) else []

    ch = channel_of(x.get('title'), nj.get('desc'), x.get('role', ''))
    company = x.get('company') or 'unspecified'
    role = x.get('role') or 'unspecified'
    rnd = x.get('round') or 'unspecified'
    url = nj.get('url') or x.get('url')

    body = [f"# {nj.get('title') or x.get('title') or nid}", '']
    body.append(f"- 来源：[{nj.get('title') or '笔记'}]({url})（小红书笔记快照，公司/岗位/轮次为发帖人自述，未核实；直链可能触发风控 404，可站内搜标题定位）")
    body.append(f"- 公司：{company}（渠道：{ch}）｜ 岗位：{role} ｜ 轮次：{rnd}")
    n = len(desc_lines) + len(img_qs)
    body.append(f"- 题目 {n} 条（题目顺序为原帖顺序）")
    body.append('')
    if desc_lines:
        body.append('## 正文题面')
        body.append('')
        body += [f'- {l}' for l in desc_lines]
        body.append('')
    if img_qs:
        body.append('## 图片题面（画面提取）' if desc_lines else '## 题面（画面提取）')
        body.append('')
        body += [f'- {q}（画面提取，{img}）' for img, q in img_qs]
        body.append('')
    if not desc_lines and not img_qs:
        body.append('（正文仅话题标签，题面在图片中，**待画面提取**）')
        body.append('')

    fname = f"{company}__{nid[:8]}.md"
    open(os.path.join(BASE, 'mianjing', fname), 'w', encoding='utf-8').write('\n'.join(body))
    stats.append((nid[:8], company, ch, n, bool(desc_lines), bool(img_qs), x.get('title', '')[:30]))

print('generated:', len(stats))
pending_img = [s for s in stats if not s[4] and not s[5]]
print('待画面提取（正文无题面且无画面提取）:', len(pending_img), [s[0] for s in pending_img])
from collections import Counter
print('渠道分布:', dict(Counter(s[2] for s in stats)))
print('题目总数:', sum(s[3] for s in stats))
json.dump([{'id': s[0], 'company': s[1], 'channel': s[2], 'n': s[3], 'title': s[6]} for s in stats],
          open(os.path.join(BASE, '_tabbit_stats.json') if False else os.path.join(BASE, '_mianjing_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
