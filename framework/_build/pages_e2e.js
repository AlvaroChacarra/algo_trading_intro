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

function releasedLessonNumbers() {
  const publication = path.join(SITE, '_publication.json');
  if (!fs.existsSync(publication)) return null;
  const metadata = JSON.parse(fs.readFileSync(publication, 'utf8'));
  if (!Array.isArray(metadata.released_classes)) {
    throw new Error('_publication.json has no released_classes array');
  }
  return metadata.released_classes.map(item => Number(item.id));
}

function lessonSamples() {
  const lessons = [];
  for (const directory of fs.readdirSync(SITE)) {
    const match = /^(\d\d)-/.exec(directory);
    const number = match ? Number(match[1]) : 0;
    const presentation = path.join(SITE, directory, 'presentation');
    if (number < 1 || number > 14 || !fs.existsSync(presentation)) continue;
    const docs = fs.readdirSync(presentation).filter(file => file.endsWith('-doc.html'));
    if (docs.length !== 1) throw new Error(`${directory}: expected one interactive document`);
    lessons.push({ number, directory, relative: `${directory}/presentation/${docs[0]}` });
  }
  lessons.sort((a, b) => a.number - b.number);
  if (!lessons.length) throw new Error('Pages artifact contains no released lessons');

  const expected = releasedLessonNumbers();
  const observed = lessons.map(item => item.number);
  if (expected && (expected.length !== observed.length || expected.some((item, index) => item !== observed[index]))) {
    throw new Error(`Pages lessons ${observed} do not match publication metadata ${expected}`);
  }
  return lessons;
}

const lessons = lessonSamples();
const lessonNotebookSamples = lessons.flatMap(item => {
  const nn = String(item.number).padStart(2, '0');
  return [
    `${item.directory}/exercises/${nn}_build_exercises.html`,
    `${item.directory}/exercises/${nn}_auxiliary.html`,
  ];
}).filter(relative => fs.existsSync(path.join(SITE, relative)));
const optionalSamples = [
  '06-oop-iii-inheritance/checkpoint.html',
  '15-final-exam/examen.html',
].filter(relative => fs.existsSync(path.join(SITE, relative)));
const samples = [
  '',
  ...lessons.map(item => item.relative),
  ...lessonNotebookSamples,
  ...optionalSamples,
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

  // Every released educational lesson uses the same vertical fallback and explicit OPTIONAL opt-in.
  for (const lesson of lessons) {
    await page.goto(origin + lesson.relative + '?mode=aula');
    await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
    const fallback = await page.evaluate(() => ({
      requested: document.body.dataset.requestedMode,
      mode: document.body.dataset.learningMode,
      marked: document.body.classList.contains('lr-mobile-fallback'),
      navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
      toolbar: getComputedStyle(document.querySelector('#lr-mobile-toolbar')).display !== 'none',
      scope: document.body.dataset.routeScope,
      horizontal: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    }));
    if (fallback.requested !== 'aula' || fallback.mode !== 'estudio' || !fallback.marked ||
        !fallback.navHidden || !fallback.toolbar || fallback.scope !== 'LIVE+REQUIRED' || fallback.horizontal) {
      failures++; console.error(`✗ L${lesson.number} mobile aula fallback ${JSON.stringify(fallback)}`);
    } else {
      console.log(`✓ L${lesson.number} mobile aula fallback → vertical study renderer`);
    }
  }

  await page.goto(origin);
  const actions = await page.locator('.lc-actions a').count();
  const expectedActions = lessons.length * 3;
  if (actions !== expectedActions) {
    failures++; console.error(`✗ index actions=${actions}, expected ${expectedActions}`);
  }
  const blocks = await page.locator('.course-block').count();
  if (blocks < 1 || blocks > 4) {
    failures++; console.error(`✗ index blocks=${blocks}, expected between 1 and 4`);
  }
  await page.locator('.lc-actions a').first().click();
  await page.locator('.course-home').click();
  const returnedPath = new URL(page.url()).pathname;
  if (![BASE, BASE + 'index.html'].includes(returnedPath)) {
    failures++; console.error(`✗ course return resolved to ${page.url()}`);
  }

  // Static notebooks expose a touch-friendly lab link; every released lesson must also
  // execute a meaningful, lesson-specific offline smoke in JupyterLite.
  const labSmokes = {
    1: `assert 2 + 2 == 4\nprint('WORK2_L1_OK')`,
    2: `book = [{'side':'buy','price':99},{'side':'sell','price':101}]\nassert len(book) == 2\nprint('WORK2_L2_OK')`,
    3: `import order_book\nassert callable(order_book.spread)\nprint('WORK2_L3_OK')`,
    4: `from exchange import Order\no = Order('BTC','buy',0.1,price=100)\nassert o.notional() == 10\nprint('WORK2_L4_OK')`,
    5: `from exchange import Level, OrderBook\nb = OrderBook('BTC',[Level(99,1)],[Level(101,1)])\nassert b.mid == 100\nprint('WORK2_L5_OK')`,
    6: `from strategies_toy import Momentum\nassert Momentum().decide(0.5) == 'buy'\nprint('WORK2_L6_OK')`,
    7: `from exchange import OrderBook\nassert hasattr(OrderBook, 'from_snapshot') and hasattr(OrderBook, 'microprice')\nprint('WORK2_L7_OK')`,
    8: `from exchange import MatchingEngine\nassert callable(MatchingEngine().process)\nprint('WORK2_L8_OK')`,
    9: `from exchange import Market\nm = Market.sample()\nassert len(m.snapshots) == 500\nprint('WORK2_L9_OK')`,
    10: `from exchange import Backtest, Market, Strategy\nassert callable(Backtest.run) and len(Market.sample().snapshots) == 500\nprint('WORK2_L10_OK')`,
    11: `from exchange import BacktestResult\nr = BacktestResult()\nassert r.n_fills == 0 and r.equity_curve == []\nprint('WORK2_L11_OK')`,
    12: `from exchange.strategies import VWAPStrategy\ns = VWAPStrategy('BTC','buy',1.0,5)\nassert s.horizon == 5\nprint('WORK2_L12_OK')`,
    13: `from exchange.strategies import MarketMaker\nfrom exchange.simulation import MMSimulation\nm = MarketMaker('BTC'); m.inventory = 1\nr = MMSimulation(m,steps=2).run()\nassert len(r.pnl) == 2\nprint('WORK2_L13_OK')`,
    14: `from exchange.strategies import AvellanedaStoikov\ns = AvellanedaStoikov('BTC',horizon=10); s.inventory=1; s.time=10\nassert s.reservation_price(100) == 100\nprint('WORK2_L14_OK')`,
  };
  const selectAll = process.platform === 'darwin' ? 'Meta+A' : 'Control+A';
  const requestedLabLesson = Number(process.env.WORK2_PAGES_LESSON || 0);
  const labLessons = requestedLabLesson
    ? lessons.filter(lesson => lesson.number === requestedLabLesson)
    : lessons;
  for (const lesson of labLessons) {
    const directory = lesson.relative.split('/')[0];
    const nn = String(lesson.number).padStart(2, '0');
    const staticPath = `${directory}/exercises/${nn}_build_exercises.html`;
    let lessonPassed = false;
    let lastFailure = null;

    // A fresh desktop context gives each notebook a clean JupyterLab workspace.
    // The mobile shell is validated above; code execution deliberately uses a
    // desktop editor so JupyterLab's windowed notebook renderer cannot leave
    // the active CodeMirror cell behind the mobile file-browser drawer.
    // Pyodide can very occasionally surface an asynchronous PyProxy/GIL error
    // after a successful cell. Retry the whole notebook in a new context, and
    // accept it only if that second run is completely clean.
    for (let labAttempt = 1; labAttempt <= 2 && !lessonPassed; labAttempt++) {
      const labContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const labPage = await labContext.newPage();
      await labPage.goto(origin + staticPath);
      const labLink = labPage.locator('.course-lab');
      const linkOk = await labLink.count() === 1 &&
        await labLink.evaluate(element => element.getBoundingClientRect().height) >= 44;
      if (!linkOk) {
        lastFailure = { reason: 'rendered notebook has no touch-friendly lab link', errors: [] };
        await labContext.close();
        continue;
      }

      const labUrl = new URL(await labLink.getAttribute('href'), labPage.url()).href;
      const labErrors = [];
      const onLabError = error => labErrors.push(error.message);
      labPage.on('pageerror', onLabError);
      const response = await labPage.goto(labUrl, { waitUntil: 'domcontentloaded' });
      let codeCells = 0;
      let executed = false;
      let stderr = false;
      let executionError = '';
      let cellText = 'cell unavailable';
      let firstCodeCell = null;
      try {
        const notebook = labPage.locator('.jp-Notebook').first();
        await notebook.waitFor({ state: 'visible', timeout: 45000 });
        codeCells = await notebook.locator('.jp-CodeCell').count();
        firstCodeCell = notebook.locator('.jp-CodeCell').first();
        const executeCell = async (outputTimeout) => {
          const editor = firstCodeCell.locator('.cm-content[data-language="python"]');
          await editor.waitFor({ state: 'visible', timeout: 90000 });
          // The status bar is the only stable readiness signal exposed by
          // JupyterLite. Waiting for its accessible Idle state prevents a cold
          // Pyodide kernel from receiving two overlapping Shift+Enter events.
          await labPage.getByRole('button', {
            name: /Python \(Pyodide\) \| Idle/,
          }).waitFor({ state: 'visible', timeout: 120000 });
          // CodeMirror only promotes the cell from command mode to edit mode on
          // pointer activation. `force` bypasses transient windowing overlays.
          await editor.click({ force: true });
          await labPage.keyboard.press(selectAll);
          await labPage.keyboard.insertText(labSmokes[lesson.number]);
          await labPage.keyboard.press('Shift+Enter');
          await firstCodeCell.locator('.jp-OutputArea-output').filter({
            hasText: `WORK2_L${lesson.number}_OK`,
          }).waitFor({ state: 'visible', timeout: outputTimeout });
        };
        try {
          await executeCell(30000);
        } catch (firstError) {
          console.warn(`↻ L${lesson.number} JupyterLite cell retry after: ${firstError.message}`);
          await executeCell(90000);
        }
        // Let kernel callbacks settle before inspecting page-level errors.
        await labPage.waitForTimeout(750);
        cellText = await firstCodeCell.innerText().catch(() => 'cell unavailable');
        stderr = await firstCodeCell.locator(
          '.jp-OutputArea-output[data-mime-type="application/vnd.jupyter.stderr"]'
        ).count() > 0 || cellText.includes('Traceback (most recent call last)');
        executed = !stderr;
      } catch (error) {
        executionError = error.message;
        cellText = firstCodeCell
          ? await firstCodeCell.innerText().catch(() => 'cell unavailable')
          : 'cell unavailable';
      }
      const labHome = await labPage.locator('.course-home').count();
      const labPath = new URL(labPage.url()).pathname;
      const clean = response && response.ok() && labPath.startsWith(BASE + 'jupyter/lab/') &&
        codeCells && executed && !stderr && labHome === 1 && !labErrors.length && !executionError;
      lastFailure = {
        reason: executionError,
        status: response && response.status(),
        codeCells,
        executed,
        stderr,
        labHome,
        errors: labErrors,
        cellText,
      };
      labPage.off('pageerror', onLabError);
      await labContext.close();

      if (clean) {
        lessonPassed = true;
        const recovered = labAttempt === 2 ? ' after clean-context retry' : '';
        console.log(`✓ L${lesson.number} JupyterLite offline smoke (${codeCells} code cells)${recovered}`);
      } else if (labAttempt === 1) {
        const why = executionError || labErrors[0] || `status ${lastFailure.status}`;
        console.warn(`↻ L${lesson.number} JupyterLite clean-context retry after: ${why}`);
      }
    }

    if (!lessonPassed) {
      failures++;
      console.error(`✗ L${lesson.number} JupyterLite status=${lastFailure && lastFailure.status} ` +
        `cells=${lastFailure && lastFailure.codeCells} executed=${lastFailure && lastFailure.executed} ` +
        `stderr=${lastFailure && lastFailure.stderr} home=${lastFailure && lastFailure.labHome} ` +
        `errors=${lastFailure && lastFailure.errors ? lastFailure.errors.length : 0}`);
      if (lastFailure && lastFailure.reason) console.error('  ', lastFailure.reason);
      if (lastFailure && lastFailure.errors) {
        lastFailure.errors.slice(0, 3).forEach(error => console.error('  ', error));
      }
      if (lastFailure && lastFailure.cellText) {
        console.error(`  first cell: ${lastFailure.cellText.slice(0, 1200)}`);
      }
    }
  }

  await browser.close();
  await new Promise(resolve => app.close(resolve));
  process.exit(failures ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });