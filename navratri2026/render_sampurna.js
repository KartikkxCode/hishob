const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + __dirname + '/sampurna.html');
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: __dirname + '/Navratra_Hishob_20-10-2026.pdf', format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">पान <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: { top: '12mm', bottom: '14mm', left: '11mm', right: '11mm' } });
  await b.close();
})();
