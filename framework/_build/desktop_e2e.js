/* Desktop learning runtime acceptance matrix and optional screenshot audit. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const auditArg = process.argv.indexOf('--audit-dir');
const AUDIT = auditArg >= 0 ? path.resolve(process.argv[auditArg + 1]) : null;
const VIEWPORTS = [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
  { width: 2560, height: 1440 },
];
const PILOTS = [
  ['L1', '01-python-i-data-model/presentation/python-i-data-model-doc.html'],
  ['L8', '08-order-types-matching/presentation/order-types-matching-doc.html'],
  ['L10', '10-strategy-framework/presentation/strategy-framework-doc.html'],
  ['L14', '14-avellaneda-stoikov/presentation/avellaneda-stoikov-doc.html'],
];

const fileUrl = (relative, query = '') => `file://${path.join(ROOT, relative)}${query}`;

(async () => {
  if (AUDIT) fs.mkdirSync(AUDIT, { recursive: true });
  const browser = await chromium.launch();
  const results = [];
  let failures = 0;

  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    for (const [lesson, relative] of PILOTS) {
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(fileUrl(relative, '?mode=aula&profe=1'));
      await page.waitForFunction(() => document.body.classList.contains('mode-aula'));
      await page.evaluate(() => localStorage.clear());
      await page.reload();
      await page.waitForFunction(() => document.body.classList.contains('mode-aula'));

      const initial = await page.evaluate(() => {
        const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
        const expected = contract.scenes
          .filter(scene => scene.route === 'LIVE')
          .reduce((total, scene) => total + Math.max(1,
            (scene.stages || []).filter(stage => (stage.route || scene.route) === 'LIVE').length), 0);
        const active = document.querySelector('body > .lr-scene-active');
        const rect = active.getBoundingClientRect();
        const nav = document.querySelector('#lr-nav').getBoundingClientRect();
        const controls = document.querySelector('#lr-controls').getBoundingClientRect();
        const focused = document.querySelector('#lr-controls .lr-next');
        focused.focus();
        const focusStyle = getComputedStyle(focused);
        return {
          expected,
          bodyOverflow: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            > innerHeight + 2,
          horizontalOverflow: document.documentElement.scrollWidth
            > document.documentElement.clientWidth + 2,
          sceneInsideViewport: rect.left >= nav.right - 2 && rect.top >= -2
            && rect.right <= innerWidth + 2 && rect.bottom <= controls.top + 2,
          route: active.dataset.route,
          focusVisible: focusStyle.outlineStyle !== 'none'
            && parseFloat(focusStyle.outlineWidth) >= 2,
          state: `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`,
        };
      });

      const visited = new Set([initial.state]);
      for (let guard = 0; guard < initial.expected + 3; guard++) {
        const done = await page.locator('#lr-controls .lr-next').isDisabled();
        if (done) break;
        await page.keyboard.press('ArrowRight');
        visited.add(await page.evaluate(() =>
          `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`));
      }
      const endState = await page.evaluate(() =>
        `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`);
      await page.keyboard.press('PageUp');
      const afterBack = await page.evaluate(() =>
        `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`);
      await page.keyboard.press('PageDown');
      const afterForward = await page.evaluate(() =>
        `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`);

      await page.locator('#lr-teacher-toggle').click();
      const drawerOpened = await page.locator('#lr-teacher-drawer').evaluate(node => node.classList.contains('open'));
      await page.keyboard.press('Escape');
      const drawerClosed = await page.locator('#lr-teacher-drawer').evaluate(node => !node.classList.contains('open'));

      await page.keyboard.press('ArrowLeft');
      const persistedState = await page.evaluate(() =>
        `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`);
      await page.reload();
      await page.waitForFunction(() => document.body.classList.contains('mode-aula'));
      const restoredState = await page.evaluate(() =>
        `${document.querySelector('.lr-scene-progress').textContent}|${document.querySelector('.lr-stage-progress').textContent}`);

      const record = {
        lesson, viewport: `${viewport.width}x${viewport.height}`,
        ...initial, visited: visited.size, errors,
        backward: afterBack !== endState,
        forward: afterForward === endState,
        drawer: drawerOpened && drawerClosed,
        persistence: persistedState === restoredState,
      };
      const passed = !record.bodyOverflow && !record.horizontalOverflow
        && record.sceneInsideViewport && record.route === 'LIVE' && record.focusVisible
        && record.visited === record.expected && !record.errors.length
        && record.backward && record.forward && record.drawer && record.persistence;
      record.passed = passed;
      if (!passed) failures++;
      results.push(record);
      console.log(`${passed ? '✓' : '✗'} ${lesson} ${record.viewport} `
        + `states=${record.visited}/${record.expected} bodyScroll=${record.bodyOverflow} hscroll=${record.horizontalOverflow}`);

      if (AUDIT && viewport.width === 1440) {
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        for (let i = 0; i < Math.floor(initial.expected / 2); i++) {
          if (await page.locator('#lr-controls .lr-next').isDisabled()) break;
          await page.keyboard.press('ArrowRight');
        }
        await page.screenshot({ path: path.join(AUDIT, `${lesson.toLowerCase()}-aula-1440x900.png`) });
      }
      await page.close();
    }
    await context.close();
  }

  const study = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const studyPage = await study.newPage();
  await studyPage.goto(fileUrl(PILOTS[0][1], '?mode=estudio'));
  const studyResult = await studyPage.evaluate(() => ({
    mode: document.body.dataset.learningMode,
    required: document.querySelectorAll('[data-route="REQUIRED"]').length,
    optional: document.querySelectorAll('[data-route="OPTIONAL"]').length,
    vertical: document.documentElement.scrollHeight > innerHeight,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
  }));
  studyResult.passed = studyResult.mode === 'estudio' && studyResult.required > 0
    && studyResult.optional > 0 && studyResult.vertical && !studyResult.horizontalOverflow;
  if (!studyResult.passed) failures++;
  results.push({ lesson: 'L1', viewport: '1440x900', mode: 'estudio', ...studyResult });
  await study.close();

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 },
    isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const mobilePage = await mobile.newPage();
  await mobilePage.goto(fileUrl(PILOTS[1][1], '?mode=aula'));
  const mobileResult = await mobilePage.evaluate(() => ({
    mode: document.body.dataset.learningMode,
    fallback: document.body.classList.contains('lr-mobile-fallback'),
    navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
    vertical: document.documentElement.scrollHeight > innerHeight,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  }));
  mobileResult.passed = mobileResult.mode === 'estudio' && mobileResult.fallback
    && mobileResult.navHidden && mobileResult.vertical && !mobileResult.horizontalOverflow
    && mobileResult.reducedMotion;
  if (!mobileResult.passed) failures++;
  results.push({ lesson: 'L8', viewport: '390x844', mode: 'mobile-fallback', ...mobileResult });
  await mobile.close();

  const exam = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await exam.goto(fileUrl('15-final-exam/examen.html', '?mode=aula'));
  const examResult = await exam.evaluate(() => ({
    linear: document.body.dataset.delivery === 'assessment-linear',
    noSceneRuntime: !document.querySelector('#lr-nav'),
    questions: document.querySelectorAll('.q').length,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
  }));
  examResult.passed = examResult.linear && examResult.noSceneRuntime
    && examResult.questions === 40 && !examResult.horizontalOverflow;
  if (!examResult.passed) failures++;
  results.push({ lesson: 'L15', viewport: '1440x900', mode: 'assessment-linear', ...examResult });
  await exam.close();

  if (AUDIT) fs.writeFileSync(path.join(AUDIT, 'desktop-audit.json'),
    JSON.stringify({ generated_at: new Date().toISOString(), results }, null, 2) + '\n');
  await browser.close();
  process.exit(failures ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });
