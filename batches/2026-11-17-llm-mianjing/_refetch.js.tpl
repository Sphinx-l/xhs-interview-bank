const fs = require('fs');
const BASE = 'd:/yuege/xhs-interview-bank/batches/2026-11-17-llm-mianjing/';
const allList = JSON.parse(fs.readFileSync(BASE + '_refetch_list.json', 'utf8'));
var list = allList;
const resPath = BASE + '_refetch_result.json';
let collected = fs.existsSync(resPath) ? JSON.parse(fs.readFileSync(resPath, 'utf8')) : [];
const done = new Set(collected.map(r => r.note_id));
const out = [...collected];
list = list.filter(i => !done.has(i.note_id)).slice(0, 15);
for (const item of list) {
  if (done.has(item.note_id)) continue;
  try {
    await page.goto(item.href, {waitUntil: 'domcontentloaded', timeout: 20000});
    await page.waitForTimeout(2500);
    // 翻轮播收集全部图片
    const imgs = await page.evaluate(async () => {
      const seen = new Set();
      const grab = () => [...document.querySelectorAll('img')].forEach(i => {
        const s = i.src || i.currentSrc || '';
        if (/^http/.test(s) && !/avatar|icon|logo|qrcode|static\.xhscdn\.com\/formula/.test(s)) seen.add(s);
      });
      grab();
      for (let k = 0; k < 25; k++) {
        const btn = document.querySelector('.swiper-button-next, [class*="next-btn"], [class*="arrow"]');
        if (btn && getComputedStyle(btn).display !== 'none') { btn.click(); await new Promise(r => setTimeout(r, 450)); grab(); } else break;
      }
      return [...seen];
    });
    // 滚动加载评论
    const comments = await page.evaluate(async () => {
      const seen = [];
      for (let k = 0; k < 6; k++) {
        window.scrollBy(0, 1500);
        await new Promise(r => setTimeout(r, 600));
      }
      document.querySelectorAll('.comment-item, [class*="comment-item"]').forEach(e => {
        const c = e.querySelector('.content, [class*="content"]')?.textContent?.trim();
        if (c && c.length > 4) seen.push(c.slice(0, 800));
      });
      return seen.slice(0, 30);
    });
    const meta = await page.evaluate(() => {
      const q = s => document.querySelector(s)?.textContent?.trim() || '';
      return {title: q('#detail-title') || q('.title'), desc: q('#detail-desc') || q('.note-text'), author: q('.author-wrapper .name') || q('.username'), date: q('.date')};
    });
    out.push({note_id: item.note_id, status: 'fetched', imgs, img_count: imgs.length, comments, ...meta});
  } catch (e) {
    out.push({note_id: item.note_id, status: 'error', error: String(e).slice(0, 150)});
  }
  fs.writeFileSync(resPath, JSON.stringify(out, null, 1), 'utf8');
}
return {fetched: out.filter(r => r.status === 'fetched').length, errors: out.filter(r => r.status === 'error').length, total: out.length};
