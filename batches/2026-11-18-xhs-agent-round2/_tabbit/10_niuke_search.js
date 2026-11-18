await page.goto("https://www.nowcoder.com/search/all?query=Agent%20%E7%A7%8B%E6%8B%9B%20%E9%9D%A2%E7%BB%8F", {waitUntil: "domcontentloaded", timeout: 45000});
await page.waitForTimeout(3000);
let prev = 0;
for (let i = 0; i < 4; i++) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1500);
  const n = await page.evaluate(() => document.querySelectorAll("a[href*='/discuss/'], a[href*='/feed/main/detail/']").length);
  if (n === prev) break;
  prev = n;
}
const cards = await page.evaluate(() => {
  const out = []; const seen = new Set();
  document.querySelectorAll("a[href*='/discuss/'], a[href*='/feed/main/detail/']").forEach(a => {
    const m = a.href.match(/\/(?:discuss|feed\/main\/detail)\/([0-9a-f]{12,24})/);
    if (!m || seen.has(m[1])) return;
    seen.add(m[1]);
    const text = (a.closest("div, li") ? a.closest("div, li").innerText : a.innerText).replace(/\s+/g, " ").trim();
    out.push({ post_id: m[1], href: a.href.slice(0, 200), text: text.slice(0, 180) });
  });
  return out;
});
return { url: page.url(), count: cards.length, cards };
