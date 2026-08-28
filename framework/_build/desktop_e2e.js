/* Full-course desktop learning-runtime acceptance matrix and visual audit. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const BROWSER_OPTIONS = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
  ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {};
const auditArg = process.argv.indexOf('--audit-dir');
const AUDIT = auditArg >= 0 ? path.resolve(process.argv[auditArg + 1]) : null;
const VIEWPORTS = [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
  { width: 2560, height: 1440 },
];

function discoverLessons() {
  const lessons = [];
  for (const entry of fs.readdirSync(ROOT, { withFileTypes: true })) {
    const match = /^(\d\d)-/.exec(entry.name);
    if (!entry.isDirectory() || !match) continue;
    const number = Number(match[1]);
    if (number < 1 || number > 14) continue;
    const presentation = path.join(ROOT, entry.name, 'presentation');
    const docs = fs.existsSync(presentation)
      ? fs.readdirSync(presentation).filter(name => name.endsWith('-doc.html')) : [];
    if (docs.length !== 1) throw new Error(`L${number}: expected one interactive document, found ${docs.length}`);
    lessons.push({ lesson: `L${number}`, number,
      relative: path.join(entry.name, 'presentation', docs[0]) });
  }
  lessons.sort((a, b) => a.number - b.number);
  if (lessons.length !== 14 || lessons.some((item, index) => item.number !== index + 1)) {
    throw new Error(`expected L1-L14 documents, found ${lessons.map(item => item.lesson).join(', ')}`);
  }
  return lessons;
}

const LESSONS = discoverLessons();
const fileUrl = (relative, suffix = '') => `file://${path.join(ROOT, relative)}${suffix}`;
const slug = value => String(value).replace(/[^a-z0-9-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
const viewportName = viewport => `${viewport.width}x${viewport.height}`;

function contractFor(number) {
  return JSON.parse(fs.readFileSync(
    path.join(ROOT, 'pedagogy', 'lessons', `${String(number).padStart(2, '0')}.yml`), 'utf8'));
}

async function expectedStates(page, allowedRoutes) {
  return page.evaluate(routes => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    return contract.scenes.filter(scene => routes.includes(scene.route)).flatMap(scene => {
      const declared = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
      return declared.filter(stage => routes.includes(stage.route || scene.route)).map(stage => ({
        scene: scene.id, stage: stage.id, sceneRoute: scene.route,
        stageRoute: stage.route || scene.route, type: scene.type,
        layout: scene.layout || 'focus', domId: scene.dom_id,
      }));
    });
  }, allowedRoutes);
}

async function inspectState(page, expected, position, total) {
  return page.evaluate(({ expectedState, index, count }) => {
    const active = document.querySelector('body > .lr-scene-active');
    const activeScenes = [...document.querySelectorAll('body > .lr-scene')]
      .filter(node => getComputedStyle(node).display !== 'none');
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
    const activeStep = active?.querySelector('.step.lr-stage-active:not([hidden])');
    const activeFigure = active?.querySelector('.fig-stage.on:not([hidden])');
    const candidates = [
      active?.querySelector('h1,h2,h3'),
      activeStep,
      activeFigure,
      ...Array.from(active?.querySelectorAll('[data-lr-essential]') || []),
    ].filter((node, itemIndex, items) => node && items.indexOf(node) === itemIndex
      && getComputedStyle(node).display !== 'none' && node.getClientRects().length);
    const essentialFailures = candidates.map(node => ({
      label: node.dataset.lrEssential || node.id || String(node.className) || node.tagName,
      box: rect(node),
    })).filter(item => !inside(item.box, bounds));
    const stageOverflow = Boolean(activeStep)
      && (activeStep.scrollWidth > activeStep.clientWidth + tolerance
        || activeStep.scrollHeight > activeStep.clientHeight + tolerance);
    const current = {
      scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
      sceneRoute: active?.dataset.route,
      stageRoute: document.body.dataset.currentStageRoute,
      scope: document.body.dataset.routeScope,
      layout: active?.dataset.sceneLayout,
      type: active?.dataset.sceneType,
    };
    const stateMatches = current.scene === expectedState.scene
      && current.stage === expectedState.stage
      && current.sceneRoute === expectedState.sceneRoute
      && current.stageRoute === expectedState.stageRoute;
    const controlState = Boolean(prev && next)
      && prev.disabled === (index === 0) && next.disabled === (index === count - 1);
    const bodyOverflow = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
      > innerHeight + tolerance;
    const horizontalOverflow = document.documentElement.scrollWidth
      > document.documentElement.clientWidth + tolerance;
    const scrolly = active?.querySelector(':scope > .scrolly');
    const stepsRect = rect(scrolly?.querySelector(':scope > .steps'));
    const figureRect = rect(scrolly?.querySelector(':scope > .figwrap'));
    const split = /split-(\d+)-(\d+)/.exec(current.layout || '');
    const expectedLeft = split ? Number(split[1]) : null;
    const cssLeft = active ? parseFloat(getComputedStyle(active).getPropertyValue('--lr-left')) : NaN;
    const actualLeft = stepsRect && figureRect
      ? 100 * stepsRect.width / Math.max(1, stepsRect.width + figureRect.width) : null;
    const layoutMatches = active?.dataset.layoutApplied === 'true'
      && current.layout === expectedState.layout
      && (expectedLeft === null || (Math.abs(cssLeft - expectedLeft) < .1
        && (actualLeft === null || Math.abs(actualLeft - expectedLeft) <= 4)));
    const scrollContainer = active?.matches('.wrap') ? active : active?.querySelector(':scope > .wrap');
    const progress = window.LEARNING_RUNTIME?.getState().progress;
    const enabledRoutes = current.scope === 'ALL' ? ['LIVE', 'REQUIRED', 'OPTIONAL']
      : (current.scope === 'LIVE+REQUIRED' ? ['LIVE', 'REQUIRED'] : ['LIVE']);
    const expectedProgress = Math.round(100 * enabledRoutes.reduce((sum, routeName) =>
      sum + (progress?.[routeName]?.visited || 0), 0) / Math.max(1, enabledRoutes.reduce((sum, routeName) =>
      sum + (progress?.[routeName]?.total || 0), 0)));
    const displayedProgress = parseInt(controls?.querySelector('.lr-route-progress')?.textContent || '', 10);
    const routeProgressMatches = displayedProgress === expectedProgress;
    const geometry = {
      bodyOverflow,
      bodyScrollPosition: { x: scrollX, y: scrollY },
      horizontalOverflow,
      oneSceneActive: activeScenes.length === 1,
      sceneInsideViewport: inside(sceneRect, bounds),
      controlsInsideViewport: inside(controlsRect,
        { left: bounds.left, top: 0, right: innerWidth, bottom: innerHeight }),
      navInsideViewport: inside(navRect, { left: 0, top: 0, right: innerWidth, bottom: innerHeight }),
      essentialInsideViewport: essentialFailures.length === 0,
      stageOverflow,
      layoutMatches,
      routeProgressMatches,
      layoutGeometry: { expectedLeft, cssLeft, actualLeft, steps: stepsRect, figure: figureRect },
      contentViewport: bounds,
      sceneBox: sceneRect,
      essentialFailures,
      internalVerticalScroll: Boolean(scrollContainer)
        && scrollContainer.scrollHeight > scrollContainer.clientHeight + tolerance,
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
        && scrollX === 0 && scrollY === 0 && geometry.oneSceneActive
        && geometry.sceneInsideViewport && geometry.controlsInsideViewport
        && geometry.navInsideViewport && geometry.essentialInsideViewport
        && !stageOverflow && layoutMatches && routeProgressMatches,
    };
  }, { expectedState: expected, index: position, count: total });
}

async function saveFailure(page, lesson, viewport, scope, state) {
  if (!AUDIT) return null;
  const file = `failure-${slug(lesson)}-${viewportName(viewport)}-${slug(scope)}`
    + `-${slug(state.scene || 'unknown')}-${slug(state.stage || 'unknown')}.png`;
  await page.screenshot({ path: path.join(AUDIT, file) });
  return file;
}

async function prepare(page, relative, query = '?mode=aula', clear = true) {
  const target = fileUrl(relative, query);
  await page.goto(target);
  await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  if (clear) {
    await page.evaluate(() => localStorage.clear());
    // The runtime writes the current state into the hash during first paint.  A
    // reload would therefore restore that stale deep link even after storage is
    // cleared; navigate to the canonical hash-free URL to get a deterministic
    // first state for every route traversal.
    await page.goto(target);
    await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  }
  await page.evaluate(() => document.fonts?.ready);
}

async function traverse(page, lesson, viewport, scope, allowedRoutes, errors) {
  const expected = await expectedStates(page, allowedRoutes);
  const states = [];
  for (let index = 0; index < expected.length; index++) {
    const state = await inspectState(page, expected[index], index, expected.length);
    if (!state.passed) state.failureScreenshot = await saveFailure(page, lesson, viewport, scope, state);
    states.push(state);
    if (index < expected.length - 1) {
      await page.keyboard.press('ArrowRight');
      const next = expected[index + 1];
      await page.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
        && document.body.dataset.currentStageId === target.stage, next);
    }
  }
  return {
    scope,
    expected: expected.length,
    visited: new Set(states.map(state => `${state.scene}/${state.stage}`)).size,
    states,
    errors: [...errors],
    geometry: {
      layouts: [...new Set(states.map(state => state.layout))],
      internalScrollStates: states.filter(state => state.internalVerticalScroll).length,
      allStatesInsideViewport: states.every(state => state.sceneInsideViewport
        && state.essentialInsideViewport && state.layoutMatches),
    },
    passed: states.length === expected.length && expected.length > 0
      && states.every(state => state.passed) && !errors.length,
  };
}

async function testNavigationAndPersistence(page, expectTeacher = false) {
  const endState = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.keyboard.press('PageUp');
  const afterBack = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.keyboard.press('PageDown');
  const afterForward = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  let drawer = true;
  if (expectTeacher) {
    await page.locator('#lr-teacher-toggle').click();
    const open = await page.locator('#lr-teacher-drawer').evaluate(node =>
      node.classList.contains('open') && node.getAttribute('aria-hidden') === 'false'
      && node.querySelector('.lr-teacher-body').textContent.includes(document.body.dataset.currentStageId));
    await page.keyboard.press('Escape');
    const closed = await page.locator('#lr-teacher-drawer').evaluate(node =>
      !node.classList.contains('open') && node.getAttribute('aria-hidden') === 'true');
    drawer = open && closed;
  }
  const focusVisible = await page.locator('#lr-controls .lr-prev').evaluate(node => {
    node.focus();
    const style = getComputedStyle(node);
    return style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2;
  });
  await page.keyboard.press('ArrowLeft');
  const persisted = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  const hash = await page.evaluate(() => location.hash);
  const progress = await page.evaluate(() => {
    const saved = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime;
    return Boolean(saved?.version >= 2 && saved.progress?.LIVE && Array.isArray(saved.visited));
  });
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  const restored = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  const home = await page.locator('#lr-nav .lr-course-home').getAttribute('href');
  return {
    backward: afterBack !== endState,
    forward: afterForward === endState,
    drawer,
    focusVisible,
    persistence: persisted === restored,
    deepLink: hash.includes('/') && persisted === restored,
    progress,
    courseHome: home === '../../index.html',
  };
}

async function overflowFixture(browser) {
  const lesson = LESSONS.find(item => item.number === 8) || LESSONS[0];
  const viewport = { width: 1280, height: 720 };
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  await prepare(page, lesson.relative);
  const expected = await expectedStates(page, ['LIVE']);
  const targetIndex = Math.max(0, Math.min(3, expected.length - 2));
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
    lesson: lesson.lesson, viewport: viewportName(viewport), mode: 'negative-fixture',
    scene: after.scene, stage: after.stage,
    baselinePassed: before.passed,
    detectorRejectedOverflow: !after.passed && (!after.essentialInsideViewport || after.horizontalOverflow),
    passed: before.passed && !after.passed && (!after.essentialInsideViewport || after.horizontalOverflow),
  };
}

function visibleStateAudit() {
  const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
  const available = state => {
    const scene = document.getElementById(state.scene.dom_id);
    if (!scene || scene.hidden || getComputedStyle(scene).display === 'none') return false;
    if (state.stage.dom_stage === undefined) return !scene.hidden;
    const wanted = String(state.stage.dom_stage);
    const step = [...scene.querySelectorAll('.step')].find(node => node.dataset.stage === wanted);
    return Boolean(step && !step.hidden);
  };
  const states = contract.scenes.flatMap(scene => {
    const stages = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
    return stages.map(stage => ({ scene, stage, route: stage.route || scene.route }));
  });
  return {
    officialAvailable: states.filter(state => state.route !== 'OPTIONAL').every(available),
    optionalCount: states.filter(state => state.route === 'OPTIONAL').length,
    optionalAvailable: states.filter(state => state.route === 'OPTIONAL').filter(available).length,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    vertical: document.documentElement.scrollHeight > innerHeight,
    routeScope: document.body.dataset.routeScope,
    progressReady: Boolean(window.LEARNING_RUNTIME?.getState().progress?.LIVE),
  };
}

async function studyAudit(browser, item) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(fileUrl(item.relative, '?mode=estudio'));
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const initial = await page.evaluate(visibleStateAudit);
  const toggle = page.locator('#lr-nav .lr-study-optional');
  const toggleVisible = initial.optionalCount === 0 ? await toggle.isHidden() : await toggle.isVisible();
  let optedIn = { optionalAvailable: 0, routeScope: initial.routeScope };
  let optedOut = initial;
  let explicitOptIn = true;
  if (initial.optionalCount) {
    await toggle.click();
    optedIn = await page.evaluate(visibleStateAudit);
    await toggle.click();
    optedOut = await page.evaluate(visibleStateAudit);
    await page.goto(fileUrl(item.relative, '?mode=estudio&optional=1'));
    await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
    const explicit = await page.evaluate(visibleStateAudit);
    explicitOptIn = explicit.routeScope === 'ALL'
      && explicit.optionalAvailable === explicit.optionalCount;
  }
  const motion = await page.evaluate(() => {
    const probe = document.querySelector('.lr-scene .step-inner') || document.querySelector('.lr-scene *');
    return { reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
      transition: probe ? getComputedStyle(probe).transitionDuration : '0s' };
  });
  const passed = initial.officialAvailable && initial.optionalAvailable === 0
    && initial.routeScope === 'LIVE+REQUIRED' && initial.vertical && !initial.horizontalOverflow
    && initial.progressReady && toggleVisible && motion.reduced
    && motion.transition.split(',').every(value => parseFloat(value) === 0)
    && (!initial.optionalCount || (optedIn.optionalAvailable === initial.optionalCount
      && optedIn.routeScope === 'ALL' && optedOut.optionalAvailable === 0
      && optedOut.routeScope === 'LIVE+REQUIRED' && explicitOptIn)) && !errors.length;
  await context.close();
  return { lesson: item.lesson, viewport: '1440x900', mode: 'estudio', initial,
    optedIn, optedOut, explicitOptIn, toggleVisible, motion, errors, passed };
}

async function mobileAudit(browser, item) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(fileUrl(item.relative, '?mode=aula'));
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const availability = await page.evaluate(visibleStateAudit);
  const mobileState = await page.evaluate(() => ({
    requested: document.body.dataset.requestedMode,
    mode: document.body.dataset.learningMode,
    marked: document.body.classList.contains('lr-mobile-fallback'),
    navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
    toolbarVisible: getComputedStyle(document.querySelector('#lr-mobile-toolbar')).display !== 'none',
    toolbarHeight: document.querySelector('#lr-mobile-toolbar').getBoundingClientRect().height,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  }));
  const initial = { ...availability, ...mobileState };
  const toggle = page.locator('#lr-mobile-toolbar .lr-study-optional');
  const toggleCorrect = initial.optionalCount === 0 ? await toggle.isHidden() : await toggle.isVisible();
  let optionalOptIn = true;
  if (initial.optionalCount) {
    await toggle.click();
    const enabled = await page.evaluate(visibleStateAudit);
    optionalOptIn = enabled.optionalAvailable === enabled.optionalCount && enabled.routeScope === 'ALL';
  }
  const passed = initial.requested === 'aula' && initial.mode === 'estudio' && initial.marked
    && initial.navHidden && initial.toolbarVisible && initial.toolbarHeight >= 44
    && initial.vertical && !initial.horizontalOverflow && initial.reducedMotion
    && initial.officialAvailable && initial.optionalAvailable === 0
    && toggleCorrect && optionalOptIn && !errors.length;
  await context.close();
  return { lesson: item.lesson, viewport: '390x844', mode: 'mobile-fallback',
    ...initial, toggleCorrect, optionalOptIn, errors, passed };
}

function chooseVisualSamples() {
  const scenes = LESSONS.flatMap(item => contractFor(item.number).scenes.map(scene => ({ item, scene })));
  const choose = (name, predicate, preferred) => {
    const candidates = scenes.filter(predicate);
    const selected = candidates.find(candidate => candidate.item.number === preferred) || candidates[0];
    return { name, selected };
  };
  return [
    choose('hero', candidate => candidate.scene.type === 'hero-challenge', 1),
    choose('recall', candidate => candidate.scene.type === 'recall', 6),
    choose('code-state', candidate => candidate.scene.type === 'code-state', 7),
    choose('simulator', candidate => candidate.scene.type === 'concept-simulator', 8),
    choose('architecture', candidate => candidate.scene.type === 'architecture-map', 10),
    choose('mathematical', candidate => candidate.item.number === 14
      && candidate.scene.type === 'mathematical-state', 14),
    choose('bridge', candidate => candidate.scene.type === 'bridge', 13),
    choose('quiz', candidate => candidate.scene.type === 'diagnostic-quiz', 11),
  ];
}

async function visualAudit(browser) {
  const viewport = { width: 1440, height: 900 };
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const records = [];
  for (const sample of chooseVisualSamples()) {
    if (!sample.selected) {
      records.push({ sample: sample.name, passed: false, reason: 'no matching declared scene' });
      continue;
    }
    const { item, scene } = sample.selected;
    const stage = (scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }])[0];
    const effectiveRoute = stage.route || scene.route;
    await prepare(page, item.relative, '?mode=aula&profe=1');
    if (scene.route !== 'LIVE' || effectiveRoute !== 'LIVE') {
      await page.locator('#lr-controls .lr-route-scope').click();
      if (scene.route === 'OPTIONAL' || effectiveRoute === 'OPTIONAL') {
        await page.locator('#lr-controls .lr-route-scope').click();
      }
    }
    await page.evaluate(({ sceneId, stageId }) => window.LEARNING_RUNTIME.goTo(sceneId, stageId),
      { sceneId: scene.id, stageId: stage.id });
    const expected = await expectedStates(page,
      effectiveRoute === 'OPTIONAL' || scene.route === 'OPTIONAL'
        ? ['LIVE', 'REQUIRED', 'OPTIONAL']
        : (effectiveRoute === 'REQUIRED' || scene.route === 'REQUIRED' ? ['LIVE', 'REQUIRED'] : ['LIVE']));
    const index = expected.findIndex(state => state.scene === scene.id && state.stage === stage.id);
    const state = index >= 0 ? await inspectState(page, expected[index], index, expected.length) : null;
    let screenshot = null;
    if (AUDIT && state) {
      screenshot = `visual-${sample.name}-${item.lesson.toLowerCase()}-${slug(scene.id)}.png`;
      await page.screenshot({ path: path.join(AUDIT, screenshot) });
    }
    records.push({ sample: sample.name, lesson: item.lesson, scene: scene.id,
      stage: stage.id, screenshot, geometry: state, passed: Boolean(state?.passed) });
  }
  await context.close();
  return records;
}

async function indexAudit(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(fileUrl('index.html'));
  await page.evaluate(() => {
    localStorage.setItem('algoTrading.01', JSON.stringify({ runtime: { version: 2,
      progress: { LIVE: { percent: 50 }, REQUIRED: { percent: 25 } } } }));
  });
  await page.reload();
  const result = await page.evaluate(() => {
    const card = document.querySelector('.lcard[data-lesson="01"]');
    const outputs = [...card.querySelectorAll('.lc-route-row output')].map(node => node.value);
    return {
      blocks: document.querySelectorAll('.course-block').length,
      actions: document.querySelectorAll('.lc-actions a').length,
      source: card.dataset.progressSource,
      outputs,
      assessmentLinearLabel: document.querySelector('#block-assessment')?.textContent === 'ASSESSMENT',
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    };
  });
  result.passed = result.blocks === 4 && result.actions === 42 && result.source === 'runtime'
    && result.outputs[0] === '50%' && result.outputs[1] === '25%'
    && result.assessmentLinearLabel && !result.horizontalOverflow;
  await page.close();
  return { lesson: 'course-map', viewport: '1440x900', mode: 'index', ...result };
}

async function examAudit(browser) {
  const viewports = [...VIEWPORTS, { width: 390, height: 844 }];
  const records = [];
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(fileUrl('15-final-exam/examen.html', '?mode=aula'));
    const result = await page.evaluate(() => ({
      linear: document.body.dataset.delivery === 'assessment-linear',
      noSceneRuntime: !document.querySelector('#lr-nav') && !window.LEARNING_RUNTIME,
      questions: document.querySelectorAll('.q').length,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    }));
    result.passed = result.linear && result.noSceneRuntime && result.questions === 40
      && !result.horizontalOverflow && !errors.length;
    records.push({ lesson: 'L15', viewport: viewportName(viewport), mode: 'assessment-linear',
      ...result, errors });
    await page.close();
  }
  return records;
}

(async () => {
  if (AUDIT) fs.mkdirSync(AUDIT, { recursive: true });
  const browser = await chromium.launch(BROWSER_OPTIONS);
  const results = [];

  const fixture = await overflowFixture(browser);
  results.push(fixture);
  console.log(`${fixture.passed ? '✓' : '✗'} intermediate-stage overflow fixture`);

  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    for (const item of LESSONS) {
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      await prepare(page, item.relative, '?mode=aula');
      const live = await traverse(page, item.lesson, viewport, 'LIVE', ['LIVE'], errors);
      const studentRouteSafety = await page.evaluate(() => ({
        scopeControlHidden: document.querySelector('#lr-controls .lr-route-scope').hidden,
        scope: document.body.dataset.routeScope,
        nonLiveNavVisible: [...document.querySelectorAll('#lr-nav .lr-scene-links button')]
          .filter(button => !button.hidden && !button.classList.contains('lr-route-live')).length,
      }));
      const navigation = await testNavigationAndPersistence(page, false);
      live.passed = live.passed && Object.values(navigation).every(Boolean)
        && studentRouteSafety.scopeControlHidden && studentRouteSafety.scope === 'LIVE'
        && studentRouteSafety.nonLiveNavVisible === 0;
      const record = { lesson: item.lesson, viewport: viewportName(viewport), mode: 'aula',
        ...live, navigation, studentRouteSafety };
      results.push(record);
      console.log(`${record.passed ? '✓' : '✗'} ${item.lesson} ${record.viewport} LIVE `
        + `states=${record.visited}/${record.expected}`);

      if (viewport.width === 1440) {
        await prepare(page, item.relative, '?mode=aula&profe=1');
        await page.locator('#lr-controls .lr-route-scope').click();
        const scopeText = (await page.locator('#lr-controls .lr-route-scope').textContent()).trim();
        const combined = await traverse(page, item.lesson, viewport,
          'LIVE+REQUIRED', ['LIVE', 'REQUIRED'], errors);
        const professor = await testNavigationAndPersistence(page, true);
        combined.scopeControl = scopeText === 'LIVE+REQUIRED';
        combined.professor = professor;
        combined.passed = combined.passed && combined.scopeControl
          && Object.values(professor).every(Boolean);
        const combinedRecord = { lesson: item.lesson, viewport: '1440x900',
          mode: 'aula-profesor', ...combined };
        results.push(combinedRecord);
        console.log(`${combinedRecord.passed ? '✓' : '✗'} ${item.lesson} 1440x900 LIVE+REQUIRED `
          + `states=${combinedRecord.visited}/${combinedRecord.expected}`);

        const declaredScenes = contractFor(item.number).scenes;
        const hasOptional = declaredScenes.some(scene => scene.route === 'OPTIONAL'
          || scene.stages?.some(stage => (stage.route || scene.route) === 'OPTIONAL'));
        if (hasOptional) {
          await prepare(page, item.relative, '?mode=aula&profe=1');
          await page.locator('#lr-controls .lr-route-scope').click();
          await page.locator('#lr-controls .lr-route-scope').click();
          const all = await traverse(page, item.lesson, viewport, 'ALL',
            ['LIVE', 'REQUIRED', 'OPTIONAL'], errors);
          all.scopeControl = (await page.locator('#lr-controls .lr-route-scope').textContent()).trim() === 'ALL';
          all.passed = all.passed && all.scopeControl
            && all.states.every(state => state.routeProgressMatches);
          const allRecord = { lesson: item.lesson, viewport: '1440x900',
            mode: 'aula-profesor', ...all };
          results.push(allRecord);
          console.log(`${allRecord.passed ? '✓' : '✗'} ${item.lesson} 1440x900 ALL `
            + `states=${allRecord.visited}/${allRecord.expected}`);
        }
      }
      await page.close();
    }
    await context.close();
  }

  for (const item of LESSONS) {
    const study = await studyAudit(browser, item);
    results.push(study);
    console.log(`${study.passed ? '✓' : '✗'} ${item.lesson} study + OPTIONAL opt-in`);
    const mobile = await mobileAudit(browser, item);
    results.push(mobile);
    console.log(`${mobile.passed ? '✓' : '✗'} ${item.lesson} mobile aula fallback`);
  }

  const visuals = await visualAudit(browser);
  results.push(...visuals.map(record => ({ mode: 'visual-sample', viewport: '1440x900', ...record })));
  visuals.forEach(record => console.log(`${record.passed ? '✓' : '✗'} visual ${record.sample}`
    + `${record.lesson ? ` · ${record.lesson}/${record.scene}` : ''}`));

  const index = await indexAudit(browser);
  results.push(index);
  console.log(`${index.passed ? '✓' : '✗'} course map runtime progress`);
  const exams = await examAudit(browser);
  results.push(...exams);
  exams.forEach(record => console.log(`${record.passed ? '✓' : '✗'} L15 linear ${record.viewport}`));

  const failures = results.filter(result => !result.passed);
  const summary = {
    generated_at: new Date().toISOString(),
    lessons: LESSONS.map(item => item.lesson),
    viewports: VIEWPORTS.map(viewportName),
    checks: results.length,
    failures: failures.length,
    results,
  };
  if (AUDIT) fs.writeFileSync(path.join(AUDIT, 'desktop-audit.json'),
    JSON.stringify(summary, null, 2) + '\n');
  await browser.close();
  process.exit(failures.length ? 1 : 0);
})().catch(error => { console.error(error); process.exit(1); });
