const qs = [
  ["kw_llm_mianjing", "https://juejin.cn/search?query=%E5%A4%A7%E6%A8%A1%E5%9E%8B%E9%9D%A2%E7%BB%8F&type=2"],
  ["kw_llm_shezhao", "https://juejin.cn/search?query=%E5%A4%A7%E6%A8%A1%E5%9E%8B%20%E7%A4%BE%E6%8B%9B&type=2"],
  ["kw_agent_shezhao", "https://juejin.cn/search?query=Agent%20%E7%A4%BE%E6%8B%9B%20%E9%9D%A2%E7%BB%8F&type=2"]
];
const all = {};
for (const [key, url] of qs) {
  await page.goto(url, {waitUntil: "domcontentloaded", timeout: 45000});
  await page.waitForLoadState("networkidle", {timeout: 15000}).catch(() => {});
  let prev = 0;
  for (let i = 0; i < 8; i++) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1100);
    const n = await page.evaluate(() => document.querySelectorAll("main a[href*='/post/']").length);
    if (n === prev) break;
    prev = n;
  }
  all[key] = await page.evaluate(() => {
    const out = []; const seen = new Set();
    document.querySelectorAll("main a[href*='/post/']").forEach(a => {
      const href = a.href;
      const m = href.match(/\/post\/(\d+)/);
      if (!m || seen.has(m[1])) return;
      seen.add(m[1]);
      const li = a.closest("li");
      const text = li ? li.innerText.replace(/\s+/g, " ").trim() : "";
      out.push({ post_id: m[1], href, text: text.slice(0, 400) });
    });
    return out;
  });
}
return { counts: Object.fromEntries(Object.entries(all).map(([k, v]) => [k, v.length])), all };
