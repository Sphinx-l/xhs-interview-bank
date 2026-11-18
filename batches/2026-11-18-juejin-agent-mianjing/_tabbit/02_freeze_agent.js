await page.goto("https://juejin.cn/search?query=Agent%E9%9D%A2%E7%BB%8F&type=2", {waitUntil: "domcontentloaded", timeout: 45000});
await page.waitForLoadState("networkidle", {timeout: 15000}).catch(() => {});
// 滚动加载，直到无新增或达 10 轮
let prev = 0;
for (let i = 0; i < 10; i++) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1200);
  const n = await page.evaluate(() => document.querySelectorAll("main a[href*='/post/']").length);
  if (n === prev) break;
  prev = n;
}
// 探测分页/加载更多控件
const pager = await page.evaluate(() => {
  const btns = [...document.querySelectorAll("main button, main a")].map(e => e.innerText && e.innerText.trim()).filter(t => t && t.length < 12);
  return btns.slice(-10);
});
const cards = await page.evaluate(() => {
  const out = []; const seen = new Set();
  document.querySelectorAll("main a[href*='/post/']").forEach(a => {
    const href = a.href;
    const m = href.match(/\/post\/(\d+)/);
    if (!m || seen.has(m[1])) return;
    seen.add(m[1]);
    const li = a.closest("li");
    const text = li ? li.innerText.replace(/\s+/g, " ").trim() : a.innerText.replace(/\s+/g, " ").trim();
    out.push({ post_id: m[1], href, text: text.slice(0, 400) });
  });
  return out;
});
return { count: cards.length, pager, cards };
