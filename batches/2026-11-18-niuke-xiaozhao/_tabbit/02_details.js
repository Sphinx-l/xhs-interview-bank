const targets = [
["b4fb3bee", "https://www.nowcoder.com/feed/main/detail/b4fb3bee56134c3d9bcde6a3166a1711?sourceSSR=search"],
["7b1b40fd", "https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887?sourceSSR=search"],
["3b91f20a", "https://www.nowcoder.com/feed/main/detail/3b91f20a24c34faf84eb0a2b8e517ccf?sourceSSR=search"],
["9f7361c7", "https://www.nowcoder.com/feed/main/detail/9f7361c709f4413396988b4f334a0d6f?sourceSSR=search"],
["79fe3fc8", "https://www.nowcoder.com/feed/main/detail/79fe3fc8f8cb4c4d9beca478f4279e3a?sourceSSR=search"],
["9e1506be", "https://www.nowcoder.com/feed/main/detail/9e1506be1bd54e8fb83c764cf724a20b?sourceSSR=search"],
["6490526c", "https://www.nowcoder.com/feed/main/detail/6490526c86124f92b79a993e171f7222?sourceSSR=search"],
["f1ed02bf", "https://www.nowcoder.com/feed/main/detail/f1ed02bfdae04730837753b62e0d58b9?sourceSSR=search"]
];
const out = {};
for (const [key, url] of targets) {
  try {
    await page.goto(url, {waitUntil: "domcontentloaded", timeout: 40000});
    await page.waitForTimeout(2500);
    out[key] = await page.evaluate(() => {
      const q = s => document.querySelector(s);
      const title = q(".feed-title, h1, .title") ? q(".feed-title, h1, .title").innerText.trim() : document.title;
      const body = q(".feed-content, .feed-detail, .content, article") ? q(".feed-content, .feed-detail, .content, article").innerText : document.body.innerText;
      return { title, url: location.href.slice(0, 120), text: body.replace(/\s+/g, "
").slice(0, 11000) };
    });
    await page.waitForTimeout(1500);
  } catch (e) {
    out[key] = { error: String(e).slice(0, 120) };
  }
}
return out;