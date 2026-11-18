const fs = require('fs');
const BASE = 'd:/yuege/xhs-interview-bank/batches/2026-11-18-niuke-agent-mianjing/';
const list = JSON.parse(fs.readFileSync(BASE + '_crawl_list.json', 'utf8'));
const resPath = BASE + '_details.json';
let collected = fs.existsSync(resPath) ? JSON.parse(fs.readFileSync(resPath, 'utf8')) : [];
const done = new Set(collected.map(r => r.post_id));
const todo = list.filter(i => !done.has(i.post_id)).slice(0, 12);
const out = [...collected];
for (const item of todo) {
  try {
    await page.goto(item.href, {waitUntil: 'domcontentloaded', timeout: 20000});
    await page.waitForTimeout(2000);
    const data = await page.evaluate(async () => {
      const q = s => document.querySelector(s)?.textContent?.trim() || '';
      const title = q('h1') || document.title;
      // 正文容器：feed 详情 / discuss 详情
      let body = '';
      for (const sel of ['[class*="feed-main"]', '.feed-detail', '[class*="post-content"]', '[class*="detail-content"]', 'article', '[class*="content-container"]']) {
        const el = document.querySelector(sel);
        if (el && el.innerText.length > body.length) body = el.innerText;
      }
      if (!body) body = document.body.innerText;
      // 滚动加载评论
      const comments = [];
      for (let k = 0; k < 3; k++) { window.scrollBy(0, 2000); await new Promise(r => setTimeout(r, 500)); }
      document.querySelectorAll('[class*="comment"] [class*="content"], .comment-item').forEach(e => {
        const c = e.textContent?.trim();
        if (c && c.length > 4) comments.push(c.slice(0, 500));
      });
      const author = q('[class*="author"] [class*="name"]') || '';
      const date = q('[class*="time"], [class*="date"]') || '';
      return {title: title.slice(0, 120), body: body.slice(0, 8000), comments: comments.slice(0, 30), author, date};
    });
    out.push({post_id: item.post_id, status: 'fetched', ...data});
  } catch (e) {
    out.push({post_id: item.post_id, status: 'error', error: String(e).slice(0, 120)});
  }
  fs.writeFileSync(resPath, JSON.stringify(out, null, 1), 'utf8');
}
return {fetched: out.filter(r => r.status === 'fetched').length, total: out.length};
