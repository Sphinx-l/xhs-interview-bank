const st = await page.evaluate(() => ({
  url: location.href.slice(0, 120),
  links: document.querySelectorAll("a[href*='/search_result/'], a[href*='/explore/']").length,
  head: document.body.innerText.replace(/\s+/g, " ").slice(0, 120)
}));
return st;
