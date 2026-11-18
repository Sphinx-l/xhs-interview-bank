const fs = require('fs');
const BASE = 'd:/yuege/xhs-interview-bank/batches/2026-11-17-llm-mianjing/';
const N = '__CHUNK__';
const chunk = JSON.parse(fs.readFileSync(BASE + '_chunk_' + N + '.json', 'utf8'));
const resPath = BASE + '_chunk_' + N + '_result.json';
let collected = fs.existsSync(resPath) ? JSON.parse(fs.readFileSync(resPath, 'utf8')) : [];
const done = new Set(collected.map(r => r.note_id));
const out = [...collected];
for (const item of chunk) {
  if (done.has(item.note_id)) continue;
  try {
    await page.goto(item.href, {waitUntil: 'domcontentloaded', timeout: 15000});
    await page.waitForTimeout(1100);
    const data = await page.evaluate(() => {
      const q = s => document.querySelector(s)?.textContent?.trim() || '';
      const title = q('#detail-title') || q('.title') || document.title;
      const desc = q('#detail-desc') || q('.note-text') || q('.desc') || '';
      const author = q('.author-wrapper .name') || q('.username') || '';
      const date = q('.date') || q('.bottom-container .date') || '';
      const imgs = [...document.querySelectorAll('.swiper-slide:not(.swiper-slide-duplicate) img, .note-image img, [class*="carousel"] img')].map(i => i.src).filter(s => /^http/.test(s) && !/avatar|icon|logo/.test(s));
      const video = !!document.querySelector('video, [class*="video-player"]');
      const comments = [...document.querySelectorAll('.comment-item .content, [class*="comment-item"] .content')].map(e => e.textContent.trim()).slice(0, 20);
      return {title, desc, author, date, imgs: [...new Set(imgs)], video, comments};
    });
    out.push({note_id: item.note_id, status: 'fetched', ...data, img_count: data.imgs.length});
  } catch (e) {
    out.push({note_id: item.note_id, status: 'error', error: String(e).slice(0, 150)});
  }
  fs.writeFileSync(resPath, JSON.stringify(out, null, 1), 'utf8');
}
return {chunk: N, fetched: out.filter(r => r.status === 'fetched').length, errors: out.filter(r => r.status === 'error').length, total: out.length};
