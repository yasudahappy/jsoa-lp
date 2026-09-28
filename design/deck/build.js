// JSOA 加盟店ご案内資料 → PDF
// deck.html を等倍で印刷する。A4横・余白ゼロ・背景ありで、文字はベクターのまま出る。
//   node design/deck/build.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.goto('file:///home/user/jsoa-lp/design/deck/deck.html', { waitUntil: 'load' });
  await p.waitForTimeout(1200);
  await p.pdf({
    path: '/home/user/jsoa-lp/design/deck/JSOA-加盟店ご案内資料.pdf',
    printBackground: true,
    preferCSSPageSize: true,
  });
  await b.close();
  console.log('done');
})();
