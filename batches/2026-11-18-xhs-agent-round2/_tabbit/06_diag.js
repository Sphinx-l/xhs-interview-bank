await page.goto("https://www.xiaohongshu.com/search_result?keyword=%E6%90%BA%E7%A8%8BAgent%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E9%9D%A2%E7%BB%8F&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 40000});
await page.waitForTimeout(4000);
const info = await page.evaluate(() => {
  const links = [...document.querySelectorAll("a")].filter(a => a.href.includes("search_result") || a.href.includes("explore"));
  return {
    total: links.length,
    hrefs: links.slice(0, 6).map(a => a.href.slice(0, 110)),
    hasTarget: links.some(a => a.href.includes("6ae1ad31")),
    bodyHas: document.body.innerText.includes("携程"),
    snippet: [...new Set(links.map(a => (a.innerText || "").replace(/\s+/g, " ").trim().slice(0, 40)))].slice(0, 8)
  };
});
return info;
