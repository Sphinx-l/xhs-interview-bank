await page.goto("https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887?sourceSSR=search", {waitUntil: "domcontentloaded", timeout: 40000});
await page.waitForTimeout(3000);
const probe = await page.evaluate(() => {
  const sels = [".feed-content", ".feed-detail", ".content", "article", ".feed-main", ".tw-common-font", ".feed-wrap", "[class*='content']", ".feed-detail-wrapper"];
  const out = {};
  for (const s of sels) {
    const e = document.querySelector(s);
    if (e) out[s] = e.innerText.length;
  }
  out["_bodyLen"] = document.body.innerText.length;
  out["_bodyHead"] = document.body.innerText.replace(/\s+/g, " ").slice(0, 260);
  return out;
});
return probe;
