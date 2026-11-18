const fs = require('fs');
const BASE = 'd:/yuege/xhs-interview-bank/batches/2026-11-18-niuke-agent-mianjing/';
const query = '__QUERY__';
const from = __FROM__, to = __TO__;
const cardsPath = BASE + 'cards_frozen.json';
let all = fs.existsSync(cardsPath) ? JSON.parse(fs.readFileSync(cardsPath, 'utf8')) : {};
for (let p = from; p <= to; p++) {
  const url = 'https://www.nowcoder.com/search/all?query=' + encodeURIComponent(query) + '&type=all&page=' + p;
  try {
    await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 20000});
    await page.waitForTimeout(2200);
    const batch = await page.evaluate(() => {
      const out = {};
      document.querySelectorAll('a[href*="/feed/main/detail/"], a[href*="/discuss/"]').forEach(a => {
        const href = a.getAttribute('href') || '';
        if (href.includes('sourceSSR') === false && href.includes('/discuss/')) { /* keep */ }
        const m = href.match(/\/(?:feed\/main\/detail\/|discuss\/)([\w-]{10,})/);
        if (!m) return;
        const card = a.closest('[class*="feed-item"], [class*="result"], li, article, [class*="search-result"]');
        const title = (card?.querySelector('[class*="title"], a')?.textContent || a.textContent || '').trim().slice(0, 80);
        const meta = (card?.innerText || '').split('\n').slice(0, 3).join(' ').slice(0, 100);
        if (!out[m[1]]) out[m[1]] = {post_id: m[1], href: href.startsWith('http') ? href : 'https://www.nowcoder.com' + href, title, meta};
      });
      return out;
    });
    Object.assign(all, batch);
  } catch (e) { /* 记录页码，继续 */ }
  fs.writeFileSync(cardsPath, JSON.stringify(all, null, 1), 'utf8');
}
return {pages: [from, to], cards: Object.keys(all).length};
