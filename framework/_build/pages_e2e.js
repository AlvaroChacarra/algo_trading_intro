/* Mobile/WebKit acceptance test for the built Pages artifact and project base path. */
const { webkit } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const SITE = path.resolve(process.argv[2] || '_site');
const BASE = '/algo_trading_intro/';
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml' };

function server() {
  return http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (!pathname.startsWith(BASE)) { res.writeHead(404).end(); return; }
    let relative = pathname.slice(BASE.length);
    if (!relative || relative.endsWith('/')) relative += 'index.html';
    const target = path.resolve(SITE, relative);
    if (!target.startsWith(SITE + path.sep) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
      res.writeHead(404).end(); return;
    }
    res.setHeader('Content-Type', TYPES[path.extname(target)] || 'application/octet-stream');
    fs.createReadStream(target).pipe(res);
  });
}

const samples = [
  '',
  '01-python-i-data-model/presentation/python-i-data-model-doc.html',
  '08-order-types-matching/presentation/order-types-matching-doc.html',
  '14-avellaneda-stoikov/presentation/avellaneda-stoikov-doc.html',
  '06-oop-iii-inheritance/checkpoint.html',
  '15-final-exam/examen.html',
  '01-python-i-data-model/exercises/01_build_exercises.html',
  '08-order-types-matching/exercises/08_auxiliary.html',
  '14-avellaneda-stoikov/exercises/14_build_exercises.html',
];

(async () => {
  const app = server();
  await new Promise(resolve => app.listen(0, '127.0.0.1', resolve));
  const port = app.address().port;
  const origin = `http://127.0.0.1:${port}${BASE}`;
  const browser = await webkit.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  let failures = 0;

  for (const sample of samples) {
    const errors = [];
    const onError = error => errors.push(error.message);
    page.on('pageerror', onError);
    const response = await page.goto(origin + sample, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
    const hasHome = sample === '' || await page.locator('.course-home').count() === 1;
    const homeTallEnough = sample === '' || await page.locator('.course-home').evaluate(
      element => element.getBoundingClientRect().height >= 44);
    const notebookOk = !sample.includes('/exercises/') ||
      await page.locator('.jp-Notebook').count() === 1;
    page.off('pageerror', onError);
    if (!response || !response.ok() || errors.length || overflow || !hasHome ||
        !homeTallEnough || !notebookOk) {
      failures++;
      console.error(`✗ ${sample || 'index'} status=${response && response.status()} ` +
        `errors=${errors.length} overflow=${overflow} home=${hasHome && homeTallEnough} notebook=${notebookOk}`);
      errors.slice(0, 3).forEach(error => console.error('  ', error));
    } else {
      console.log(`✓ ${sample || 'index'}`);
    }
  }

  await page.goto(origin);
  const actions = await page.locator('.lc-actions a').count();
  if (actions !== 42) { failures++; console.error(`✗ index actions=${actions}, expected 42`); }
  await page.locator('.lc-actions a').first().click();
  await page.locator('.course-home').click();
  if (new URL(page.url()).pathname !== BASE) {
    failures++; console.error(`✗ course return resolved to ${page.url()}`);
  }

  await browser.close();
  await new Promise(resolve => app.close(resolve));
  process.exit(failures ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });
