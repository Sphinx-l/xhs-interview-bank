const targets = [
["6ae1ad31", "%E6%90%BA%E7%A8%8BAgent%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E9%9D%A2%E7%BB%8F"],
["6af5686e", "%E6%9D%AD%E5%B7%9E%E5%B0%8F%E5%8E%82Agent%E5%BC%80%E5%8F%91%E5%B2%97"],
["6aeb2f0f", "%E9%98%BF%E9%87%8C%E5%8D%83%E9%97%AE%E4%BA%8B%E4%B8%9A%E9%83%A8agent%E5%BC%80%E5%8F%91%E4%BA%8C%E9%9D%A2"],
["6afc1c66", "%E9%95%BF%E9%91%AB%E5%AD%98%E5%82%A8-agent%E5%BC%80%E5%8F%91%E4%BA%8C%E9%9D%A2"],
["6ae990ce", "%E8%85%BE%E8%AE%AFAgent%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E4%B8%89%E9%9D%A2"],
["6ae2e7be", "%E5%BF%AB%E6%89%8B%E5%8E%8B%E5%8A%9B%E9%9D%A2%20Agent%E5%BC%80%E5%8F%91"],
["6aeb4d5e", "%E5%B9%BF%E5%B7%9E%E9%92%9B%E5%8A%A8%E7%A7%91%E6%8A%80agent%E5%BC%80%E5%8F%91%E5%B2%97"]
];
const out = {};
for (const [key, kwEnc] of targets) {
  try {
    await page.goto("https://www.xiaohongshu.com/search_result?keyword=" + kwEnc + "&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 40000});
    await page.waitForTimeout(3500);
    const clicked = await page.evaluate((k) => {
      const links = [...document.querySelectorAll("a[href*='" + k + "']")];
      const a = links.find(e => e.href.includes("/search_result/") || e.href.includes("/explore/"));
      if (!a) return false;
      a.scrollIntoView(); a.click(); return true;
    }, key);
    if (!clicked) { out[key] = { error: "card not found in results" }; continue; }
    await page.waitForSelector("#detail-desc, .note-text, .detail", {timeout: 8000}).catch(() => {});
    await page.waitForTimeout(2000);
    out[key] = await page.evaluate(() => {
      const q = s => document.querySelector(s);
      const title = q(".title, #detail-title") ? q(".title, #detail-title").innerText.trim() : document.title;
      const desc = q("#detail-desc, .note-text, .desc") ? q("#detail-desc, .note-text, .desc").innerText.trim() : "";
      const date = q(".date, .bottom-container") ? q(".date, .bottom-container").innerText.trim().slice(0, 30) : "";
      const imgs = document.querySelectorAll(".note-image, .swiper-slide img, .carousel img").length;
      return { title, date, imgCount: imgs, url: location.href.slice(0, 130), desc: desc.slice(0, 9000) };
    });
  } catch (e) {
    out[key] = { error: String(e).slice(0, 120) };
  }
}
return out;