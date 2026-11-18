await page.goto("https://www.xiaohongshu.com/search_result?keyword=Agent%20%E7%A4%BE%E6%8B%9B%20%E9%9D%A2%E7%BB%8F&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 45000});
await page.waitForTimeout(3000);
// 滚动加载 3 轮
let prev = 0;
for (let i = 0; i < 6; i++) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1500);
  const n = await page.evaluate(() => document.querySelectorAll("a[href*='/search_result/'], a[href*='/explore/']").length);
  if (n === prev) break;
  prev = n;
}
// 提取卡片：href 含 token、标题、作者、点赞
const cards = await page.evaluate(() => {
  const out = []; const seen = new Set();
  document.querySelectorAll("a[href*='/search_result/'], a[href*='/explore/']").forEach(a => {
    const href = a.href;
    const m = href.match(/\/(?:search_result|explore)\/([0-9a-f]{24})/);
    if (!m || seen.has(m[1])) return;
    const sec = a.closest("section");
    const title = (sec ? sec.innerText : a.innerText).replace(/\s+/g, " ").trim();
    if (title.length < 5) return;
    seen.add(m[1]);
    out.push({ note_id: m[1], href, text: title.slice(0, 200) });
  });
  return out;
});
return { url: page.url(), count: cards.length, cards };
