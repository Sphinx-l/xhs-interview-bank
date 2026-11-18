const info = await page.evaluate(() => ({
  url: location.href.slice(0, 110),
  links: document.querySelectorAll("a[href*='/search_result/'], a[href*='/explore/']").length,
  bodyHead: document.body.innerText.replace(/\s+/g, " ").slice(0, 150)
}));
return info;
