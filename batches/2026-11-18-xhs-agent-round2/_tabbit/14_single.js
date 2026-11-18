await page.goto("https://www.xiaohongshu.com/search_result?keyword=%E8%85%BE%E8%AE%AFAgent%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E4%B8%89%E9%9D%A2&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 40000});
await page.waitForTimeout(4000);
const clicked = await page.evaluate(() => {
  const links = [...document.querySelectorAll("a[href*='6ae990ce']")];
  const a = links.find(e => e.href.includes("/search_result/") || e.href.includes("/explore/"));
  if (!a) return false;
  a.scrollIntoView(); a.click(); return true;
});
if (!clicked) return { error: "card not found" };
await page.waitForTimeout(3000);
return await page.evaluate(() => {
  const q = s => document.querySelector(s);
  const title = q(".title, #detail-title") ? q(".title, #detail-title").innerText.trim() : document.title;
  const desc = q("#detail-desc, .note-text, .desc") ? q("#detail-desc, .note-text, .desc").innerText.trim() : "";
  return { title, desc: desc.slice(0, 300), bodyHead: document.body.innerText.replace(/\s+/g, " ").slice(0, 150) };
});
