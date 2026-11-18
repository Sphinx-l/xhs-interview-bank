const ids = ["7595232643464134690", "7526268411145404416", "7639868628453425187", "7485296558465826835", "7691126299994898472"];
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
      const text = body.innerText.replace(/ /g, " ");
      return { title, author, time, length: text.length, text: text.slice(0, 12000) };
    });
  } catch (e) {
    out[id] = { error: String(e).slice(0, 200) };
  }
}
return out;
