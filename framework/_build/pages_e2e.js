/* Mobile/WebKit acceptance test for the built Pages artifact and project base path. */
const { webkit } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const SITE = path.resolve(process.argv[2] || '_site');
const BASE = '/algo_trading_intro/';
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.wasm': 'application/wasm', '.woff2': 'font/woff2' };

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
  const returnedPath = new URL(page.url()).pathname;
  if (![BASE, BASE + 'index.html'].includes(returnedPath)) {
    failures++; console.error(`✗ course return resolved to ${page.url()}`);
  }

  // The static notebook remains the fast reading view and exposes the editable lab.
  await page.goto(origin + '01-python-i-data-model/exercises/01_build_exercises.html');
  const labLink = page.locator('.course-lab');
  if (await labLink.count() !== 1 ||
      await labLink.evaluate(element => element.getBoundingClientRect().height) < 44) {
    failures++; console.error('✗ rendered notebook has no touch-friendly lab link');
  } else {
    const labUrl = new URL(await labLink.getAttribute('href'), page.url()).href;
    const labErrors = [];
    const onLabError = error => labErrors.push(error.message);
    page.on('pageerror', onLabError);
    const response = await page.goto(labUrl, { waitUntil: 'domcontentloaded' });
    try {
      await page.locator('.jp-Notebook').waitFor({ state: 'visible', timeout: 45000 });
    } catch (_error) {
      failures++; console.error('✗ JupyterLite did not open the requested notebook');
    }
    const codeCells = await page.locator('.jp-Notebook .jp-CodeCell').count();
    const labHome = await page.locator('.course-home').count();
    const labPath = new URL(page.url()).pathname;
    let executed = false;
    if (codeCells) {
      try {
        const firstCodeCell = page.locator('.jp-Notebook .jp-CodeCell').first();
        await firstCodeCell.locator('.cm-content').click();
        await page.keyboard.press('Shift+Enter');
        await page.waitForFunction(() => {
          const prompt = document.querySelector('.jp-Notebook .jp-CodeCell .jp-InputArea-prompt');
          return /\[\d+\]/.test(prompt?.textContent || '');
        }, undefined, { timeout: 90000 });
        executed = true;
      } catch (_error) {
        console.error('✗ JupyterLite Python kernel did not execute a code cell');
      }
    }
    if (!response || !response.ok() || !labPath.startsWith(BASE + 'jupyter/lab/') ||
        !codeCells || !executed || labHome !== 1 || labErrors.length) {
      failures++;
      console.error(`✗ JupyterLite status=${response && response.status()} cells=${codeCells} ` +
        `executed=${executed} home=${labHome} errors=${labErrors.length}`);
      labErrors.slice(0, 3).forEach(error => console.error('  ', error));
    } else {
      console.log(`✓ JupyterLite editable notebook (${codeCells} code cells; Python executed)`);
    }
    page.off('pageerror', onLabError);
  }

  await browser.close();
  await new Promise(resolve => app.close(resolve));
  process.exit(failures ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });
