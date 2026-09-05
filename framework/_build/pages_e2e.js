/* Student acceptance on the published, presentation-only artifact. */
const {webkit} = require('playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || '_site');
const prefix = '/algo_trading_intro/';

(async () => {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const relative = decodeURIComponent(url.pathname).replace(prefix, '') || 'index.html';
    const target = path.resolve(root, relative);
    if (!target.startsWith(root + path.sep) || !fs.existsSync(target) || fs.statSync(target).isDirectory()) {
      res.writeHead(404); res.end(); return;
    }
    const mime = {'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css'};
    res.setHeader('Content-Type', mime[path.extname(target)] || 'application/octet-stream');
    fs.createReadStream(target).pipe(res);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}${prefix}`;
  const browser = await webkit.launch();
  try {
    for (const viewport of [{width:390,height:844}, {width:1366,height:900}]) {
      const page = await browser.newPage({viewport});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(base);
      const links = await page.locator('.lcard[data-lesson] a[href*="/presentation/"]').evaluateAll(nodes => nodes.map(n => n.getAttribute('href')));
      // A release before L1 is also valid: no published lessons yet.
      for (const href of links) {
        const response = await page.goto(new URL(href, base).href);
        assert.equal(response.status(), 200);
        assert(await page.title());
        assert.equal(await page.locator('#guion-src').count(), 0);
        assert.equal(await page.locator('.course-lab').count(), 0);
        assert(await page.locator('a[href="../../index.html"]').count());
      }
      assert.deepEqual(errors, []);
      await page.close();
      console.log(`Pages ${viewport.width}px: ${links.length} presentations OK`);
    }
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
