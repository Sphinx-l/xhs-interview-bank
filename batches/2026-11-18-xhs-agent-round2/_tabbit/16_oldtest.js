await page.goto("https://www.xiaohongshu.com/search_result?keyword=%E5%AD%97%E8%8A%82agent%E5%BC%80%E5%8F%91%28%E6%8A%96%E9%9F%B3%E5%BC%80%E5%8F%91%29%E4%B8%80%E9%9D%A2%E9%9D%A2%E7%BB%8F&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 40000});
await page.waitForTimeout(4000);
const clicked = await page.evaluate(() => {
  const links = [...document.querySelectorAll("a[href*='6a918ac7']")];
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
  const user = q(".username, .author .name") ? q(".username, .author .name").innerText.trim() : "";
  return { title, user, desc: desc.slice(0, 200) };
});
