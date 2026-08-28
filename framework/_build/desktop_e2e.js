/* Desktop learning runtime acceptance matrix and screenshot audit. */
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
const slug = value => String(value).replace(/[^a-z0-9-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();

async function expectedStates(page, allowedRoutes) {
  return page.evaluate(routes => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    return contract.scenes.filter(scene => routes.includes(scene.route)).flatMap(scene => {
      const declared = scene.stages || [{ id: 'stage', route: scene.route }];
      const allowed = declared.filter(stage => routes.includes(stage.route || scene.route));
      return (allowed.length ? allowed : declared.slice(0, 1)).map(stage => ({
        scene: scene.id, stage: stage.id, route: scene.route,
      }));
    });
  }, allowedRoutes);
}

async function inspectState(page, expected, position, total) {
  return page.evaluate(({ expectedState, index, count }) => {
    const active = document.querySelector('body > .lr-scene-active');
    const nav = document.querySelector('#lr-nav');
    const controls = document.querySelector('#lr-controls');
    const prev = controls?.querySelector('.lr-prev');
    const next = controls?.querySelector('.lr-next');
    const tolerance = 2;
    const rect = node => node ? node.getBoundingClientRect() : null;
    const inside = (box, bounds) => Boolean(box)
      && box.left >= bounds.left - tolerance && box.top >= bounds.top - tolerance
      && box.right <= bounds.right + tolerance && box.bottom <= bounds.bottom + tolerance;
    const navRect = rect(nav), controlsRect = rect(controls), sceneRect = rect(active);
    const bounds = {
      left: navRect?.right || 0, top: 0, right: innerWidth,
      bottom: controlsRect?.top || innerHeight,
    };
    const activeStep = active?.querySelector('.step.lr-stage-active');
    const activeFigure = active?.querySelector('.fig-stage.on');
    const candidates = [
      active?.querySelector('h1,h2,h3'),
      activeStep?.querySelector('.step-inner') || activeStep,
      activeFigure,
      ...Array.from(active?.querySelectorAll('[data-lr-essential]') || []),
    ].filter((node, idx, items) => node && items.indexOf(node) === idx
      && getComputedStyle(node).display !== 'none' && node.getClientRects().length);
    const essentialFailures = candidates.map(node => ({
      label: node.dataset.lrEssential || node.id || node.className || node.tagName,
      box: rect(node),
    })).filter(item => !inside(item.box, bounds));
    const stageOverflow = Boolean(activeStep)
      && (activeStep.scrollWidth > activeStep.clientWidth + tolerance
        || activeStep.scrollHeight > activeStep.clientHeight + tolerance);
    const current = {
      scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
      route: active?.dataset.route,
      scope: document.body.dataset.routeScope,
    };
    const stateMatches = current.scene === expectedState.scene
      && current.stage === expectedState.stage && current.route === expectedState.route;
    const controlState = Boolean(prev && next)
      && prev.disabled === (index === 0) && next.disabled === (index === count - 1);
    const bodyOverflow = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
      > innerHeight + tolerance;
    const horizontalOverflow = document.documentElement.scrollWidth
      > document.documentElement.clientWidth + tolerance;
    const geometry = {
      bodyOverflow,
      horizontalOverflow,
      sceneInsideViewport: inside(sceneRect, bounds),
      controlsInsideViewport: inside(controlsRect, { left: bounds.left, top: 0, right: innerWidth, bottom: innerHeight }),
      navInsideViewport: inside(navRect, { left: 0, top: 0, right: innerWidth, bottom: innerHeight }),
      essentialInsideViewport: essentialFailures.length === 0,
      stageOverflow,
      essentialFailures,
    };
    return {
      ...current,
      expected: expectedState,
      position: index + 1,
      total: count,
      stateMatches,
      controlState,
      ...geometry,
      passed: stateMatches && controlState && !bodyOverflow && !horizontalOverflow
        && geometry.sceneInsideViewport && geometry.controlsInsideViewport
        && geometry.navInsideViewport && geometry.essentialInsideViewport && !stageOverflow,
    };
  }, { expectedState: expected, index: position, count: total });
}

async function saveFailure(page, lesson, viewport, scope, state) {
  if (!AUDIT) return null;
  const file = `failure-${slug(lesson)}-${viewport.width}x${viewport.height}-${slug(scope)}`
    + `-${slug(state.scene || 'unknown')}-${slug(state.stage || 'unknown')}.png`;
  await page.screenshot({ path: path.join(AUDIT, file) });
  return file;
}

async function prepare(page, relative, query = '?mode=aula&profe=1') {
  await page.goto(fileUrl(relative, query));
  await page.waitForFunction(() => document.body.classList.contains('mode-aula'));
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForFunction(() => document.body.classList.contains('mode-aula'));
  await page.evaluate(() => document.fonts?.ready);
}

async function traverse(page, lesson, viewport, scope, allowedRoutes, errors) {
  const expected = await expectedStates(page, allowedRoutes);
  const states = [];
  for (let index = 0; index < expected.length; index++) {
    const state = await inspectState(page, expected[index], index, expected.length);
    if (!state.passed) state.failureScreenshot = await saveFailure(
      page, lesson, viewport, scope, state);
    states.push(state);
    if (index < expected.length - 1) {
      await page.keyboard.press('ArrowRight');
      await page.waitForTimeout(20);
    }
  }
  return {
    scope,
    expected: expected.length,
    visited: new Set(states.map(state => `${state.scene}/${state.stage}`)).size,
    states,
    errors: [...errors],
    passed: states.length === expected.length && states.every(state => state.passed)
      && !errors.length,
  };
}

async function testNavigationAndPersistence(page) {
  const endState = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.keyboard.press('PageUp');
  const afterBack = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.keyboard.press('PageDown');
  const afterForward = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.locator('#lr-teacher-toggle').click();
  const drawerOpened = await page.locator('#lr-teacher-drawer').evaluate(node => node.classList.contains('open'));
  await page.keyboard.press('Escape');
  const drawerClosed = await page.locator('#lr-teacher-drawer').evaluate(node => !node.classList.contains('open'));
  const focusVisible = await page.locator('#lr-controls .lr-prev').evaluate(node => {
    node.focus();
    const style = getComputedStyle(node);
    return style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2;
  });
  await page.keyboard.press('ArrowLeft');
  const persisted = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.reload();
  await page.waitForFunction(() => document.body.classList.contains('mode-aula'));
  const restored = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  return {
    backward: afterBack !== endState,
    forward: afterForward === endState,
    drawer: drawerOpened && drawerClosed,
    focusVisible,
    persistence: persisted === restored,
  };
}

async function overflowFixture(browser) {
  const viewport = { width: 1280, height: 720 };
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  await prepare(page, PILOTS[1][1]);
  const expected = await expectedStates(page, ['LIVE']);
  const targetIndex = Math.min(3, expected.length - 2);
  for (let index = 0; index < targetIndex; index++) await page.keyboard.press('ArrowRight');
  const before = await inspectState(page, expected[targetIndex], targetIndex, expected.length);
  await page.evaluate(() => {
    const fixture = document.createElement('div');
    fixture.dataset.lrEssential = 'intermediate-overflow-fixture';
    fixture.textContent = 'overflow fixture';
    fixture.style.cssText = 'position:fixed;left:calc(100vw + 40px);top:120px;width:240px;height:80px';
    document.querySelector('body > .lr-scene-active').appendChild(fixture);
  });
  const after = await inspectState(page, expected[targetIndex], targetIndex, expected.length);
  if (AUDIT) await page.screenshot({ path: path.join(AUDIT, 'fixture-intermediate-overflow-detected.png') });
  await context.close();
  return {
    lesson: 'L8', viewport: '1280x720', mode: 'negative-fixture',
    scene: after.scene, stage: after.stage,
    baselinePassed: before.passed,
    detectorRejectedOverflow: !after.passed && (!after.essentialInsideViewport || after.horizontalOverflow),
    passed: before.passed && !after.passed && (!after.essentialInsideViewport || after.horizontalOverflow),
  };
}

(async () => {
  if (AUDIT) fs.mkdirSync(AUDIT, { recursive: true });
  const browser = await chromium.launch();
  const results = [];
  let failures = 0;

  const fixture = await overflowFixture(browser);
  results.push(fixture);
  if (!fixture.passed) failures++;
  console.log(`${fixture.passed ? '✓' : '✗'} intermediate-stage overflow fixture`);

  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    for (const [lesson, relative] of PILOTS) {
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await prepare(page, relative);
      const live = await traverse(page, lesson, viewport, 'LIVE', ['LIVE'], errors);
      const navigation = await testNavigationAndPersistence(page);
      live.passed = live.passed && Object.values(navigation).every(Boolean);
      const record = { lesson, viewport: `${viewport.width}x${viewport.height}`, mode: 'aula', ...live, navigation };
      if (!record.passed) failures++;
      results.push(record);
      console.log(`${record.passed ? '✓' : '✗'} ${lesson} ${record.viewport} LIVE `
        + `states=${record.visited}/${record.expected}`);

      if (viewport.width === 1440) {
        await prepare(page, relative);
        await page.locator('#lr-controls .lr-route-scope').click();
        const scopeText = (await page.locator('#lr-controls .lr-route-scope').textContent()).trim();
        const combined = await traverse(
          page, lesson, viewport, 'LIVE+REQUIRED', ['LIVE', 'REQUIRED'], errors);
        combined.scopeControl = scopeText === 'LIVE+REQUIRED';
        combined.passed = combined.passed && combined.scopeControl;
        const combinedRecord = { lesson, viewport: '1440x900', mode: 'aula', ...combined };
        if (!combinedRecord.passed) failures++;
        results.push(combinedRecord);
        console.log(`${combinedRecord.passed ? '✓' : '✗'} ${lesson} 1440x900 LIVE+REQUIRED `
          + `states=${combinedRecord.visited}/${combinedRecord.expected}`);

        if (AUDIT) {
          await prepare(page, relative);
          const middle = Math.floor(live.expected / 2);
          for (let i = 0; i < middle; i++) await page.keyboard.press('ArrowRight');
          await page.screenshot({ path: path.join(AUDIT, `${lesson.toLowerCase()}-aula-1440x900.png`) });
        }
      }
      await page.close();
    }
    await context.close();
  }

  for (const [lesson, relative] of PILOTS) {
    const study = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const studyPage = await study.newPage();
    const studyErrors = [];
    studyPage.on('pageerror', error => studyErrors.push(error.message));
    await studyPage.goto(fileUrl(relative, '?mode=estudio'));
    const studyResult = await studyPage.evaluate(() => {
      const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
      const scenes = contract.scenes.map(scene => document.getElementById(scene.dom_id));
      return {
        mode: document.body.dataset.learningMode,
        declaredRequired: contract.scenes.filter(scene => scene.route === 'REQUIRED').length,
        required: document.querySelectorAll('body > .lr-scene[data-route="REQUIRED"]').length,
        declaredOptional: contract.scenes.filter(scene => scene.route === 'OPTIONAL').length,
        optional: document.querySelectorAll('body > .lr-scene[data-route="OPTIONAL"]').length,
        allScenesVisible: scenes.every(scene => scene && scene.getAttribute('aria-hidden') === 'false'
          && getComputedStyle(scene).display !== 'none'),
        vertical: document.documentElement.scrollHeight > innerHeight,
        horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
      };
    });
    studyResult.passed = studyResult.mode === 'estudio'
      && studyResult.required === studyResult.declaredRequired
      && studyResult.optional === studyResult.declaredOptional
      && studyResult.allScenesVisible && studyResult.vertical && !studyResult.horizontalOverflow
      && !studyErrors.length;
    if (!studyResult.passed) failures++;
    results.push({ lesson, viewport: '1440x900', mode: 'estudio',
      ...studyResult, errors: studyErrors });
    await study.close();

    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 },
      isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const mobilePage = await mobile.newPage();
    const mobileErrors = [];
    mobilePage.on('pageerror', error => mobileErrors.push(error.message));
    await mobilePage.goto(fileUrl(relative, '?mode=aula'));
    const mobileResult = await mobilePage.evaluate(() => ({
      runtimeMode: document.body.dataset.learningMode,
      fallback: document.body.classList.contains('lr-mobile-fallback'),
      navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
      vertical: document.documentElement.scrollHeight > innerHeight,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
      reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    }));
    mobileResult.passed = mobileResult.runtimeMode === 'estudio' && mobileResult.fallback
      && mobileResult.navHidden && mobileResult.vertical && !mobileResult.horizontalOverflow
      && mobileResult.reducedMotion && !mobileErrors.length;
    if (!mobileResult.passed) failures++;
    results.push({ lesson, viewport: '390x844', mode: 'mobile-fallback',
      ...mobileResult, errors: mobileErrors });
    await mobile.close();
  }

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
