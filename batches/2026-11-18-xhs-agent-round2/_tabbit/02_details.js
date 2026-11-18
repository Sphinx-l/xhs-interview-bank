const targets = [
["6ae1ad31", "6ae1ad31000000001f0150df"],
["6af5686e", "6af5686e000000002b02866a"],
["6aeb2f0f", "6aeb2f0f0000000019000a47"],
["6afc1c66", "6afc1c6600000000250089bd"],
["6ae990ce", "6ae990ce000000000303867c"],
["6ae2e7be", "6ae2e7be000000001d00fc08"],
["6aeb4d5e", "6aeb4d5e00000000030148b4"],
["6ad6b3b2", "6ad6b3b20000000031007a0e"],
["6ae5608a", "6ae5608a00000000180249fc"],
["6adff2d4", "6adff2d4000000002802d464"],
["6adf6d34", "6adf6d34000000001201820c"],
["6adc0286", "6adc0286000000003101c4df"],
["6a6027de", "6a6027de000000000903594a"],
["6ae700ff", "6ae700ff000000001a022f02"]
];
const out = {};
for (const [key, url] of targets) {
  try {
    await page.goto(url, {waitUntil: "domcontentloaded", timeout: 40000});
    await page.waitForTimeout(2500);
    out[key] = await page.evaluate(() => {
      const q = s => document.querySelector(s);
      const title = q(".title, #detail-title") ? q(".title, #detail-title").innerText.trim() : document.title;
      const desc = q("#detail-desc, .note-text, .desc") ? q("#detail-desc, .note-text, .desc").innerText.trim() : "";
      const date = q(".date, .bottom-container") ? q(".date, .bottom-container").innerText.trim().slice(0, 30) : "";
      const imgs = document.querySelectorAll(".note-image, .swiper-slide img, .carousel img").length;
      return { title, date, imgCount: imgs, desc: desc.slice(0, 9000) };
    });
  } catch (e) {
    out[key] = { error: String(e).slice(0, 150) };
  }
}
return out;