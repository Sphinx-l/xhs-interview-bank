# -*- coding: utf-8 -*-
"""标题初筛：从 cards_frozen.json 生成 screening_log.md 与 manifest.json 初稿"""
import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'c:/Users/ljq/Desktop/xhs-interview-bank/batches/2026-11-18-juejin-agent-mianjing'

# 人工判定进入内容复核的候选（含边界复核）
REVIEW = {
    '7663419501435191336': 'Agent面经（Rinta，RAG 项目追问题面）',
    '7686441082470711330': 'RAG 面经（查询改写/Bad Case 追问链，2月前）',
    '7675566936094785571': '米哈游 Agent 一面凉经（自述转自牛客，跨源待判）',
    '7571258854900842539': '大模型应用开发面经 5年经验（社招重点，多家公司）',
    '7682634449857544219': '拼多多 AI Agent 面经（纯干货标题有营销味，复核定性）',
    '7546495958554755098': '阿里云多模态大模型岗三面面经',
    '7595232643464134690': '字节豆包大模型岗三轮技术面',
    '7526268411145404416': '大模型面经（1）（疑似题面合集，复核定性）',
    '7639868628453425187': '字节前端一面（含 Agent/Skill/MCP 题，岗位边界复核）',
    '7485296558465826835': '金三银四真实面经（AI 号连载，疑似转载合集，快速定性）',
    '7691126299994898472': '美团 AI 测试社招面试题（霍格沃兹系列抽检定性，Agent 评测向）',
}

# 标题/摘要排除规则（按优先级）
EXCLUDE_RULES = [
    (r'(内推|招聘|急缺|岗位更新|招人|HC|职级薪资|薪资结构|年薪|offer报价)', 'excluded_recruitment', '招聘/内推/薪资资讯，非面经'),
    (r'(前端|JavaScript|CSS|vue|Vue|react|React|webpack|Webpack|盒模型|浏览器渲染|鸿蒙)', 'excluded_non_target', '前端岗面经，非 Agent/大模型开发方向'),
    (r'(Java|java|Spring|spring|JVM|jvm|MySQL|mysql|后端八股|服务端社招|Android|android|客户端)', 'excluded_non_target', 'Java/后端/客户端岗面经，非本方向'),
    (r'(上岸|零基础|转行.*路线|学习路线|面试题宝典|面试手册|宝藏|训练营|星球|公众号|关注点|开源.*求职网站|校招社招的区别|不迷茫|简历模版|ATS|Paper Reading|智能分诊.*工具|自动采集器)', 'excluded_marketing', '营销卖课/引流/工具介绍/方法论，无真实面试来源'),
    (r'(凉经|面经|面试)', 'needs_review_fallback', '含面经关键词，规则未覆盖，保守进复核'),
]

cards = json.load(open(BASE + r'/_tabbit/cards_frozen.json', encoding='utf-8'))
manifest = []
log_lines = ['# 标题初筛 screening_log（2026-11-18）', '',
             '关键词：Agent面经 / 大模型面经 / 大模型 社招 / Agent 社招 面经（type=2 文章）。以下按标题+摘要初筛，「按标题排除，未读正文」。', '']
counts = {'review': 0, 'excluded': 0}
for c in cards:
    pid, text = c['post_id'], c['text']
    title = text.split(' ')[2] if text.count(' ') >= 2 else text[:40]
    # 卡片 text 格式：作者 时间 标签 标题 摘要…，取前 100 字做规则匹配即可
    probe = text[:200]
    if pid in REVIEW:
        status, reason = 'pending_review', '人工候选：' + REVIEW[pid]
    else:
        status, reason = None, None
        for pat, st, rs in EXCLUDE_RULES:
            if re.search(pat, probe):
                if st == 'needs_review_fallback':
                    status, reason = 'pending_review', '规则未覆盖的含面经帖，保守进复核：' + probe[:80]
                else:
                    status, reason = st, rs + '（按标题排除，未读正文）'
                break
        if status is None:
            status, reason = 'pending_review', '无规则命中，保守进复核：' + probe[:80]
    counts['review' if status == 'pending_review' else 'excluded'] += 1
    log_lines.append(f"- {pid} | {status} | {reason}")
    manifest.append({
        'post_id': pid, 'url': 'https://juejin.cn/post/' + pid, 'title': text[:60],
        'status': status, 'reason': reason,
        'company': 'unspecified', 'role': 'unspecified', 'round': 'unspecified',
        'channel': '未标注', 'question_ids': [],
        'keywords': c['keywords'],
    })
log_lines.insert(3, f"可见文章 {len(cards)} 篇（去重后）；初筛进内容复核 {counts['review']} 篇；按标题排除 {counts['excluded']} 篇。")
json.dump(manifest, open(BASE + '/manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(BASE + '/screening_log.md', 'w', encoding='utf-8').write('\n'.join(log_lines) + '\n')
print(f"cards={len(cards)} review={counts['review']} excluded={counts['excluded']}")
