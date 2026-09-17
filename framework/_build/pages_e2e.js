/* Student acceptance on the published, presentation-only artifact. */
const {webkit} = require('playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || '_site');
const sourceRoot = path.resolve(__dirname, '..', '..');
const option = name => {
  const index = process.argv.indexOf(name);
  return index < 0 ? null : process.argv[index + 1];
};
const liveUrl = option('--live-url');
const auditDir = option('--audit-dir');
const prefix = '/algo_trading_intro/';

async function inspectLayout(page, label) {
  const result = await page.evaluate(() => ({
    horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 2,
    mode: window.LEARNING_RUNTIME?.mode || null,
    scene: document.body.dataset.currentSceneId || null,
  }));
  assert.equal(result.horizontalOverflow, false, `${label}: horizontal overflow`);
  return result;
}

async function checkDownloads(page, live) {
  const links = await page.locator('a[href]').evaluateAll(nodes => nodes.map(n => n.href));
  const notebookLinks = [...new Set(links.filter(href => /\.ipynb(?:$|[?#])/.test(href)))];
  for (const href of notebookLinks) {
    const url = new URL(href);
    const relative = decodeURIComponent(url.pathname.split('/main/')[1] || '');
    assert(relative && !relative.split('/').some(part => ['..', 'solutions', 'soluciones'].includes(part)),
      `unexpected notebook download: ${href}`);
    let document;
    if (live) {
      const response = await page.request.get(href);
      assert.equal(response.status(), 200, `notebook download: ${href}`);
      document = await response.json();
    } else {
      document = JSON.parse(fs.readFileSync(path.join(sourceRoot, relative), 'utf8'));
    }
    assert.equal(document.nbformat, 4);
    for (const cell of document.cells) {
      assert(!['solution', 'validator', 'hidden_validator'].includes(cell.metadata?.course?.role),
        `private notebook role: ${href}`);
      if (cell.cell_type === 'code') {
        assert.equal(cell.execution_count, null);
        assert.deepEqual(cell.outputs, []);
      }
    }
  }
  return notebookLinks.length;
}

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
  if (!liveUrl) await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = liveUrl || `http://127.0.0.1:${server.address().port}${prefix}`;
  const browser = await webkit.launch();
  const records = [];
  if (auditDir) fs.mkdirSync(auditDir, {recursive:true});
  try {
    for (const viewport of [{width:390,height:844}, {width:1366,height:900}]) {
      const page = await browser.newPage({viewport});
      const errors = [];
      const badResponses = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {
        if (response.status() >= 400) badResponses.push(`${response.status()} ${response.url()}`);
      });
      const index = await page.goto(base);
      assert.equal(index.status(), 200);
      await inspectLayout(page, 'index');
      const downloads = await checkDownloads(page, Boolean(liveUrl));
      const links = await page.locator('.lcard[data-lesson] a[href*="/presentation/"]').evaluateAll(nodes => nodes.map(n => n.getAttribute('href')));
      // A release before L1 is also valid: no published lessons yet.
      for (const href of links) {
        const response = await page.goto(new URL(href, base).href);
        assert.equal(response.status(), 200);
        assert(await page.title());
        assert.equal(await page.locator('#guion-src').count(), 0);
        assert.equal(await page.locator('.course-lab').count(), 0);
        assert(await page.locator('a[href="../../index.html"]').count());
        await page.evaluate(() => document.fonts.ready);
        const layout = await inspectLayout(page, href);
        if (viewport.width < 768) assert.equal(layout.mode, 'estudio', 'mobile study fallback');
        if (layout.mode === 'aula') {
          const states = await page.evaluate(() => JSON.parse(document.querySelector('#pedagogy-contract').textContent)
            .scenes.filter(scene => scene.route === 'LIVE').flatMap(scene =>
              (scene.stages?.length ? scene.stages : [{id:'stage',route:scene.route}])
                .filter(stage => (stage.route || scene.route) === 'LIVE')
                .map(stage => ({scene:scene.id,stage:stage.id}))));
          for (const state of states) {
            await page.evaluate(s => window.LEARNING_RUNTIME.goTo(s.scene, s.stage), state);
            await inspectLayout(page, `${href}/${state.scene}/${state.stage}`);
            assert(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight + 2),
              `aula vertical overflow: ${href}/${state.scene}`);
          }
        }
        if (auditDir) {
          await page.screenshot({path:path.join(auditDir, `pages-${viewport.width}-${href.split('/')[0]}.png`)});
        }
        const home = page.locator('a[href="../../index.html"]:visible').first();
        await home.click();
        await page.waitForURL(new URL('index.html', base).href);
        records.push({viewport:viewport.width, href, passed:true});
      }
      assert.deepEqual(errors, []);
      assert.deepEqual(badResponses, []);
      await page.close();
      console.log(`Pages ${viewport.width}px: ${links.length} presentations, ${downloads} notebook downloads OK`);
    }
  } finally {
    await browser.close();
    if (!liveUrl) await new Promise(resolve => server.close(resolve));
    if (auditDir) fs.writeFileSync(path.join(auditDir, 'pages-audit.json'),
      JSON.stringify({base:liveUrl || 'local snapshot', source_sha:process.env.GITHUB_SHA || null, records}, null, 2));
  }
})().catch(error => { console.error(error); process.exit(1); });
