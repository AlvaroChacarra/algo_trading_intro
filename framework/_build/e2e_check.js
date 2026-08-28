/* General browser smoke: every lesson in study, aula and mobile fallback. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const BROWSER_OPTIONS = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
  ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {};

function lessonDocs() {
  const out = [];
  for (const directory of fs.readdirSync(ROOT)) {
    const match = /^(\d\d)-/.exec(directory);
    const number = match ? Number(match[1]) : 0;
    const presentation = path.join(ROOT, directory, 'presentation');
    if (number < 1 || number > 14 || !fs.existsSync(presentation)) continue;
    const docs = fs.readdirSync(presentation).filter(file => file.endsWith('-doc.html'));
    if (docs.length !== 1) throw new Error(`${directory}: expected one -doc.html, found ${docs.length}`);
    out.push({ number, path: path.join(presentation, docs[0]) });
  }
  out.sort((a, b) => a.number - b.number);
  if (out.length !== 14 || out.some((item, index) => item.number !== index + 1)) {
    throw new Error(`expected L1-L14, found ${out.map(item => item.number).join(',')}`);
  }
  return out;
}

const docs = lessonDocs();
const url = (file, query = '') => `file://${file}${query}`;

function listen(page) {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  return errors;
}

async function quizSmoke(page) {
  const quizzes = page.locator('.quiz[data-quiz]');
  let questions = 0;
  for (let quizIndex = 0; quizIndex < await quizzes.count(); quizIndex++) {
    const quiz = quizzes.nth(quizIndex), items = quiz.locator('.q');
    for (let questionIndex = 0; questionIndex < await items.count(); questionIndex++) {
      const options = items.nth(questionIndex).locator('.opt');
      if (await options.count()) {
        await options.first().click();
        questions++;
      }
    }
  }
  const state = await page.evaluate(() => {
    const quizzes = [...document.querySelectorAll('.quiz[data-quiz]')];
    return {
      quizzes: quizzes.length,
      disabled: quizzes.every(quiz => [...quiz.querySelectorAll('.q')].every(question =>
        [...question.querySelectorAll('.opt')].every(option => option.disabled))),
      explanations: quizzes.every(quiz => [...quiz.querySelectorAll('.q .why')]
        .every(note => note.classList.contains('show'))),
      scores: quizzes.map(quiz => quiz.querySelector('.score')?.textContent.trim() || ''),
      persisted: Boolean(JSON.parse(localStorage.getItem(DOC.key()) || '{}').quiz),
    };
  });
  return { ...state, questions, passed: state.quizzes > 0 && questions > 0
    && state.disabled && state.explanations && state.scores.every(Boolean) && state.persisted };
}

async function simulatorSmoke(page, lesson) {
  if (lesson === 1) {
    await page.locator('#lang-cpp').click();
    await page.locator('#lang-run').click();
    await page.waitForFunction(() =>
      [...document.querySelectorAll('#lang-trace .trace-step')].every(node => node.classList.contains('ok')));
    return page.evaluate(() => ({
      action: '#lang-cpp + #lang-run',
      mode: document.querySelector('#lang-cpp').classList.contains('on'),
      trace: document.querySelectorAll('#lang-trace .trace-step.ok').length,
      log: document.querySelector('#lang-log').textContent,
      passed: document.querySelector('#lang-cpp').classList.contains('on')
        && document.querySelectorAll('#lang-trace .trace-step.ok').length === 5
        && document.querySelector('#lang-log').textContent.includes('99975.0'),
    }));
  }
  if (lesson === 2) {
    await page.locator('#cancel-next').click();
    await page.locator('#cancel-next').click();
    await page.locator('#cancel-comp').click();
    await page.locator('#sort-lambda').click();
    for (let index = 0; index < 3; index++) await page.locator('#sort-next').click();
    return page.evaluate(() => ({
      action: 'cancel tracer + lambda sort tracer',
      count: document.querySelector('#cancel-count').textContent,
      cancelLog: document.querySelector('#cancel-log').textContent,
      sortLog: document.querySelector('#sort-log').textContent,
      passed: document.querySelector('#cancel-count').textContent === '1 orden'
        && document.querySelector('#cancel-result').textContent.includes('id=2')
        && document.querySelector('#cancel-log').textContent.includes('new_book → 1')
        && document.querySelector('#cancel-comp').classList.contains('on')
        && document.querySelector('#cancel-code').textContent.includes('[o for o in book')
        && document.querySelector('#sort-lambda').classList.contains('on')
        && document.querySelectorAll('#sort-trace .trace-step.ok').length === 3
        && document.querySelector('#sort-log').textContent.includes('B · A · C'),
    }));
  }
  if (lesson === 3) {
    await page.locator('#main-fixed').click();
    await page.locator('#main-import').click();
    await page.locator('#main-run').click();
    const cleanImport = await page.evaluate(() =>
      document.querySelector('#main-log').textContent.includes('import limpio')
      && document.querySelectorAll('#main-trace .fail').length === 0);
    await page.locator('#main-direct').click();
    await page.locator('#main-run').click();
    return page.evaluate(clean => ({
      action: 'guarded import + direct execution',
      cleanImport: clean,
      directLog: document.querySelector('#main-log').textContent,
      passed: clean && document.querySelector('#main-fixed').classList.contains('on')
        && document.querySelector('#main-direct').classList.contains('on')
        && document.querySelector('#main-log').textContent.includes('programa arranca')
        && document.querySelector('#main-trace').textContent.includes('main() → ARRANCANDO BACKTEST'),
    }), cleanImport);
  }
  if (lesson === 4) {
    await page.locator('#ow-sell').click();
    await page.locator('#ow-price').fill('101250');
    await page.locator('#ow-size').fill('0.4');
    return page.evaluate(() => ({
      action: 'order workshop sell 0.4 @ 101250',
      repr: document.querySelector('#ow-repr').textContent,
      notional: document.querySelector('#ow-not').textContent,
      cashFlow: document.querySelector('#ow-cf').textContent,
      passed: document.querySelector('#ow-sell').classList.contains('on')
        && document.querySelector('#ow-repr').textContent === 'OrderMini(sell 0.4 BTCUSDT @ 101250)'
        && document.querySelector('#ow-not').textContent === '40500.0'
        && document.querySelector('#ow-cf').textContent === '+40500.0',
    }));
  }
  if (lesson === 5) {
    await page.locator('#inv-fill').click();
    const throughApi = await page.evaluate(() => ({
      cash: document.querySelector('#inv-cash').textContent,
      position: document.querySelector('#inv-pos').textContent,
      consistent: document.querySelector('#inv-status').textContent.includes('✓'),
    }));
    await page.locator('#inv-break').click();
    return page.evaluate(before => ({
      action: '#inv-fill + #inv-break', before,
      afterCash: document.querySelector('#inv-cash').textContent,
      afterStatus: document.querySelector('#inv-status').textContent,
      passed: before.cash === '-50,000' && before.position === '0.5' && before.consistent
        && document.querySelector('#inv-cash').textContent === '1,000,000'
        && document.querySelector('#inv-status').textContent.includes('✗')
        && document.querySelector('#inv-state').classList.contains('bad'),
    }), throughApi);
  }
  if (lesson === 6) {
    await page.locator('#sup-b').click();
    const missingSuper = await page.evaluate(() =>
      document.querySelector('#sup-status').textContent.includes('falta name')
      && Boolean(document.querySelector('#sup-trace .fail')));
    await page.locator('#sup-c').click();
    const cooperative = await page.evaluate(() =>
      document.querySelector('#sup-status').textContent.includes('completo')
      && document.querySelector('#sup-state').textContent.includes('threshold'));
    await page.locator('#abc-abstract').click();
    const abstractGuard = await page.evaluate(() =>
      document.querySelector('#abc-log').textContent.includes('obliga a implementar')
      && document.querySelectorAll('#abc-trace .fail').length === 2);
    await page.locator('#abc-return').click();
    return page.evaluate(state => ({
      action: 'super() + ABC contract variants', ...state,
      finalLog: document.querySelector('#abc-log').textContent,
      passed: state.missingSuper && state.cooperative && state.abstractGuard
        && document.querySelector('#abc-log').textContent.includes('mantiene el contrato'),
    }), { missingSuper: Boolean(missingSuper), cooperative, abstractGuard });
  }
  if (lesson === 7) {
    await page.locator('#sc-t').evaluate(node => {
      node.value = '123'; node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    return page.evaluate(() => ({
      action: '#sc-t → snapshot 123',
      snapshot: document.querySelector('#sc-tv').textContent,
      stats: document.querySelector('#sc-stats').textContent,
      rows: document.querySelectorAll('#sc-book .row').length,
      passed: document.querySelector('#sc-tv').textContent === '123'
        && document.querySelector('#sc-stats').textContent.includes('microprice')
        && document.querySelector('#sc-stats').textContent.includes('imbalance(1)')
        && document.querySelectorAll('#sc-book .row').length >= 2,
    }));
  }
  if (lesson === 8) {
    await page.locator('#cross-side [data-side="sell"]').click();
    await page.locator('#policy-modes [data-mode="fok"]').click();
    await page.locator('#sim-type [data-type="fok"]').click();
    await page.locator('#sim-size').evaluate(node => {
      node.value = '2'; node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await page.locator('#sim-price').evaluate(node => {
      node.value = '2'; node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    for (let index = 0; index < 3; index++) await page.locator('#sim-next').click();
    return page.evaluate(() => ({
      action: 'SELL crosses + FOK atomic failure',
      detail: document.querySelector('#sim-detail').textContent,
      policy: document.querySelector('#policy-note').textContent,
      passed: document.querySelector('#cross-side [data-side="sell"]').classList.contains('on')
        && document.querySelector('#cross-code').textContent.includes('order.price <= level_price')
        && document.querySelector('#policy-modes [data-mode="fok"]').classList.contains('on')
        && document.querySelector('#policy-note').textContent.includes('return []')
        && document.querySelector('#sim-book-label').textContent === 'after'
        && document.querySelector('#sim-detail').textContent.includes('fills[]')
        && document.querySelector('#sim-detail').textContent.includes('idéntico'),
    }));
  }
  if (lesson === 9) {
    await page.locator('#mk-i').evaluate(node => {
      node.value = '2'; node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await page.locator('#pl-play').click();
    await page.waitForFunction(() => document.querySelector('#pl-log').textContent.startsWith('paso '));
    const progressed = await page.evaluate(() => ({
      log: document.querySelector('#pl-log').textContent,
      owner: document.querySelector('#pl-owner').textContent,
    }));
    await page.locator('#pl-reset').click();
    return page.evaluate(progress => ({
      action: 'Market cursor + replay play/reset', progress,
      snapshot: document.querySelector('#mk-i-v').textContent,
      state: document.querySelector('#mk-state').textContent,
      passed: document.querySelector('#mk-i-v').textContent === '2'
        && document.querySelector('#mk-state').textContent.includes('OrderBook(')
        && progress.log.startsWith('paso ')
        && progress.owner.includes('Market.step()')
        && document.querySelector('#pl-log').textContent === 'pulsa play'
        && !document.querySelector('#pl-play').disabled,
    }), progressed);
  }
  if (lesson === 10) {
    await page.locator('#st-b').click();
    return page.locator('#st-b').evaluate(node => ({ action: '#st-b', passed: node.classList.contains('on') }));
  }
  if (lesson === 11) {
    await page.locator('#mn-toggle').click();
    return page.locator('#mn-toggle').evaluate(node => ({ action: '#mn-toggle',
      passed: node.textContent.includes('Quitar') }));
  }
  if (lesson === 12) {
    await page.locator('#pw-vwap').click();
    await page.locator('#lr-nav .lr-study-optional').evaluate(node => node.click());
    await page.locator('#pv-roll').click();
    const state = await page.evaluate(() => ({ action: '#pw-vwap + #pv-roll',
      primary: document.querySelector('#pw-vwap').classList.contains('on'),
      optional: document.querySelector('#pv-roll').classList.contains('on') }));
    await page.locator('#lr-nav .lr-study-optional').evaluate(node => node.click());
    return { ...state, passed: state.primary && state.optional };
  }
  if (lesson === 13) {
    await page.locator('#mm-on').click();
    return page.locator('#mm-on').evaluate(node => ({ action: '#mm-on', passed: node.classList.contains('on') }));
  }
  if (lesson === 14) {
    await page.locator('#lb-g').evaluate(node => {
      node.value = '100';node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await page.locator('#lb-q').evaluate(node => {
      node.value = '-10';node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await page.locator('#lb-t').evaluate(node => {
      node.value = '50';node.dispatchEvent(new Event('input', { bubbles: true }));
    });
    return page.evaluate(() => ({ action: '#lb-g + #lb-q + #lb-t',
      values: [document.querySelector('#lb-gv').textContent,
        document.querySelector('#lb-qv').textContent, document.querySelector('#lb-tv').textContent],
      passed: document.querySelector('#lb-gv').textContent === '1.00'
        && document.querySelector('#lb-qv').textContent === '-1.0'
        && document.querySelector('#lb-tv').textContent === '0.50'
        && Boolean(document.querySelector('#lb-r').textContent),
    }));
  }
  return { action: 'missing lesson-specific simulator smoke', passed: false };
}

async function studySmoke(page, item, errors) {
  await page.goto(url(item.path, '?mode=estudio'));
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const steps = page.locator('.scrolly .step:not([hidden])');
  for (let index = 0; index < await steps.count(); index++) {
    const step = steps.nth(index);
    if (await step.isVisible()) await step.scrollIntoViewIfNeeded();
  }
  await page.waitForTimeout(25);
  const simulator = await simulatorSmoke(page, item.number);
  const quiz = await quizSmoke(page);
  const result = await page.evaluate(() => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    const cumulativeChecks = [
      ['#l7-build-code', ['from_snapshot', 'microprice']],
      ['#l8-build-code', ['add_limit', 'return fills']],
      ['#l9-build-code', ['def reset', 'self.book = None']],
    ];
    const cumulative = cumulativeChecks.every(([selector, needles]) => {
      const element = document.querySelector(selector);
      return !element || needles.every(needle => element.textContent.includes(needle));
    });
    const optionalScenes = contract.scenes.filter(scene => scene.route === 'OPTIONAL');
    return {
      runtime: document.body.dataset.runtimeVersion === '2',
      contractError: document.body.dataset.runtimeContractError || null,
      scenes: contract.scenes.length,
      officialScope: document.body.dataset.routeScope === 'LIVE+REQUIRED',
      optionalHidden: optionalScenes.every(scene => document.getElementById(scene.dom_id)?.hidden),
      cumulative,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    };
  });
  return { ...result, simulator, quiz, errors: [...errors],
    passed: result.runtime && !result.contractError && result.scenes > 0 && result.officialScope
      && result.optionalHidden && result.cumulative && !result.horizontalOverflow
      && simulator.passed && quiz.passed && !errors.length };
}

async function aulaSmoke(page, item, errors) {
  await page.goto(url(item.path, '?mode=aula'));
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'aula');
  const count = await page.evaluate(() => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    return contract.scenes.filter(scene => scene.route === 'LIVE').reduce((total, scene) =>
      total + (scene.stages?.filter(stage => (stage.route || scene.route) === 'LIVE').length || 1), 0);
  });
  for (let index = 1; index < count; index++) await page.keyboard.press('ArrowRight');
  const result = await page.evaluate(expected => ({
    expected,
    activeScenes: [...document.querySelectorAll('body > .lr-scene')]
      .filter(node => getComputedStyle(node).display !== 'none').length,
    noBodyScroll: scrollY === 0 && document.documentElement.scrollHeight <= innerHeight + 2,
    noHorizontalScroll: document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2,
    scope: document.body.dataset.routeScope,
    progress: window.LEARNING_RUNTIME.getState().progress.LIVE,
  }), count);
  result.passed = result.expected > 0 && result.activeScenes === 1 && result.noBodyScroll
    && result.noHorizontalScroll && result.scope === 'LIVE'
    && result.progress.visited === result.progress.total && !errors.length;
  return { ...result, errors: [...errors] };
}

async function mobileSmoke(browser, item) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = listen(page);
  await page.goto(url(item.path, '?mode=aula'));
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const simulator = await simulatorSmoke(page, item.number);
  let orderWorkshop = { applicable: false, passed: true };
  if (item.number === 4) {
    const workshop = page.locator('[data-scene-id="l04-order-workshop"]');
    await workshop.locator('#ow-price').fill('101250');
    await workshop.locator('#ow-size').fill('0.4');
    orderWorkshop = await workshop.evaluate(scene => {
      const visible = node => {
        const style = getComputedStyle(node), box = node.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden'
          && box.width > 0 && box.height > 0;
      };
      const repr = scene.querySelector('#ow-repr');
      const notional = scene.querySelector('#ow-not');
      const cashFlow = scene.querySelector('#ow-cf');
      const log = scene.querySelector('#ow-log');
      const state = {
        applicable: true,
        side: scene.querySelector('#ow-sell').classList.contains('on'),
        price: scene.querySelector('#ow-price').value,
        size: scene.querySelector('#ow-size').value,
        repr: repr.textContent.trim(),
        notional: notional.textContent.trim(),
        cashFlow: cashFlow.textContent.trim(),
        outputsVisible: [repr, notional, cashFlow, log].every(visible),
        log: log.textContent.trim(),
      };
      state.passed = state.side && state.price === '101250' && state.size === '0.4'
        && state.repr === 'OrderMini(sell 0.4 BTCUSDT @ 101250)'
        && state.notional === '40500.0' && state.cashFlow === '+40500.0'
        && state.outputsVisible && state.log.includes('order.notional() = 40500.0')
        && state.log.includes("cash_flow() = 40500.0");
      return state;
    });
  }
  await page.waitForTimeout(25);
  const result = await page.evaluate(() => ({
    requested: document.body.dataset.requestedMode,
    mode: document.body.dataset.learningMode,
    fallback: document.body.classList.contains('lr-mobile-fallback'),
    navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
    toolbar: getComputedStyle(document.querySelector('#lr-mobile-toolbar')).display !== 'none',
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
  }));
  result.passed = result.requested === 'aula' && result.mode === 'estudio' && result.fallback
    && result.navHidden && result.toolbar && result.reducedMotion && !result.horizontalOverflow
    && simulator.passed && orderWorkshop.passed && !errors.length;
  await context.close();
  return { ...result, simulator, orderWorkshop, errors };
}

(async () => {
  const browser = await chromium.launch(BROWSER_OPTIONS);
  const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  let failures = 0;

  for (const item of docs) {
    const studyPage = await desktop.newPage();
    const studyErrors = listen(studyPage);
    const study = await studySmoke(studyPage, item, studyErrors);
    console.log(`${study.passed ? '✓' : '✗'} L${item.number} estudio`);
    if (!study.passed) {
      failures++;
      console.error(`   ${JSON.stringify(study)}`);
    }
    await studyPage.close();

    const aulaPage = await desktop.newPage();
    const aulaErrors = listen(aulaPage);
    const aula = await aulaSmoke(aulaPage, item, aulaErrors);
    console.log(`${aula.passed ? '✓' : '✗'} L${item.number} aula LIVE states=${aula.expected}`);
    if (!aula.passed) {
      failures++;
      console.error(`   ${JSON.stringify(aula)}`);
    }
    await aulaPage.close();

    const mobile = await mobileSmoke(browser, item);
    console.log(`${mobile.passed ? '✓' : '✗'} L${item.number} mobile fallback`);
    if (!mobile.passed) {
      failures++;
      console.error(`   ${JSON.stringify(mobile)}`);
    }
  }

  const indexPage = await desktop.newPage();
  const indexErrors = listen(indexPage);
  await indexPage.goto(url(path.join(ROOT, 'index.html')));
  const index = await indexPage.evaluate(() => ({
    actions: document.querySelectorAll('.lc-actions a').length,
    blocks: document.querySelectorAll('.course-block').length,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
  }));
  index.passed = index.actions === 42 && index.blocks === 4
    && !index.horizontalOverflow && !indexErrors.length;
  console.log(`${index.passed ? '✓' : '✗'} course map`);
  if (!index.passed) failures++;
  await indexPage.close();

  const examPage = await desktop.newPage();
  const examErrors = listen(examPage);
  await examPage.goto(url(path.join(ROOT, '15-final-exam', 'examen.html'), '?mode=aula'));
  const exam = await examPage.evaluate(() => ({
    linear: document.body.dataset.delivery === 'assessment-linear',
    noRuntime: !window.LEARNING_RUNTIME && !document.querySelector('#lr-nav'),
    questions: document.querySelectorAll('.q').length,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
  }));
  exam.passed = exam.linear && exam.noRuntime && exam.questions === 40
    && !exam.horizontalOverflow && !examErrors.length;
  console.log(`${exam.passed ? '✓' : '✗'} L15 linear assessment`);
  if (!exam.passed) failures++;
  await examPage.close();

  await desktop.close();
  await browser.close();
  process.exit(failures ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });
