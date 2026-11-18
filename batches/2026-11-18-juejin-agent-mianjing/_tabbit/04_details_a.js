const ids = ["7663419501435191336", "7686441082470711330", "7675566936094785571", "7571258854900842539", "7682634449857544219", "7546495958554755098"];
const out = {};
for (const id of ids) {
  try {
    await page.goto("https://juejin.cn/post/" + id, {waitUntil: "domcontentloaded", timeout: 45000});
    await page.waitForLoadState("networkidle", {timeout: 12000}).catch(() => {});
    await page.waitForTimeout(800);
    out[id] = await page.evaluate(() => {
      const q = s => document.querySelector(s);
      const title = q("h1") ? q("h1").innerText.trim() : document.title;
      const author = q(".author-name, .username, a[href*='/user/']") ? q(".author-name, .username, a[href*='/user/']").innerText.trim() : "";
      const time = q("time") ? (q("time").getAttribute("datetime") || q("time").innerText) : "";
      const body = q(".article-content") || q("article") || q(".markdown-body") || document.body;
      const text = body.innerText.replace(/ /g, " ");
      return { title, author, time, length: text.length, text: text.slice(0, 12000) };
    });
  } catch (e) {
    out[id] = { error: String(e).slice(0, 200) };
  }
}
return out;
