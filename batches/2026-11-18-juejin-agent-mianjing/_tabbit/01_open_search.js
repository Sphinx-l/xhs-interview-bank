await page.goto("https://juejin.cn/search?query=Agent%E9%9D%A2%E7%BB%8F", {waitUntil: "domcontentloaded", timeout: 45000});
await page.waitForLoadState("networkidle", {timeout: 20000}).catch(() => {});
return await tabbit.observe({frames: "none", maxChars: 6000});
