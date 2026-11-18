const SEARCH = "https://www.xiaohongshu.com/search_result?keyword=Agent%20%E7%A4%BE%E6%8B%9B%20%E9%9D%A2%E7%BB%8F&source=web_explore_feed";
const out = {};
for (const key of ["6ae1ad31", "6af5686e"]) {
  try {
    await page.goto(SEARCH, {waitUntil: "domcontentloaded", timeout: 40000});
    await page.waitForTimeout(2500);
    const link = page.locator(`a[href*="${key}"]`).first();
    await link.waitFor({state: "visible", timeout: 10000});
    await link.click();
    await page.waitForTimeout(2500);
    out[key] = await page.evaluate(() => {
      const q = s => document.querySelector(s);
      const title = q(".title, #detail-title") ? q(".title, #detail-title").innerText.trim() : document.title;
      const desc = q("#detail-desc, .note-text, .desc") ? q("#detail-desc, .note-text, .desc").innerText.trim() : "";
      const imgs = document.querySelectorAll(".note-image, .swiper-slide img, .carousel img").length;
      return { title, url: location.href.slice(0, 120), imgCount: imgs, desc: desc.slice(0, 800) };
    });
  } catch (e) {
    out[key] = { error: String(e).slice(0, 150) };
  }
}
return out;
