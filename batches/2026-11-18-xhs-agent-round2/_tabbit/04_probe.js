await page.goto("https://www.xiaohongshu.com/search_result?keyword=Agent%20%E7%A4%BE%E6%8B%9B%20%E9%9D%A2%E7%BB%8F&source=web_explore_feed", {waitUntil: "domcontentloaded", timeout: 40000});
await page.waitForTimeout(4000);
const info = await page.evaluate(() => {
  const links = [...document.querySelectorAll("a[href*='/search_result/'], a[href*='/explore/']")];
  return {
    url: location.href.slice(0, 100),
    title: document.title,
    total: links.length,
    ids: links.slice(0, 40).map(a => (a.href.match(/\/(?:search_result|explore)\/([0-9a-f]{8})/) || [])[1]).filter(Boolean),
    bodySnippet: document.body.innerText.slice(0, 200)
  };
});
return info;
