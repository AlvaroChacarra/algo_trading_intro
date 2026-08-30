/* Full-course desktop learning-runtime acceptance matrix and visual audit. */
const fs = require('fs');
const path = require('path');
const evidenceContract = require('./desktop_evidence_contract');

const ROOT = path.resolve(__dirname, '..', '..');
let chromium = null;
let AUDIT = null;
let auditReady = false;
let LESSONS = [];
const VIEWPORTS = [
  { width: 1280, height: 720 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
  { width: 2560, height: 1440 },
];

function parseAuditDirectory(argv) {
  const auditArg = argv.indexOf('--audit-dir');
  if (auditArg < 0) return null;
  if (!argv[auditArg + 1]) throw new Error('--audit-dir requires a path');
  return path.resolve(argv[auditArg + 1]);
}

const fileUrl = (relative, suffix = '') => `file://${path.join(ROOT, relative)}${suffix}`;
const slug = value => String(value).replace(/[^a-z0-9-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
const viewportName = viewport => `${viewport.width}x${viewport.height}`;

function resetAuditDirectory() {
  if (!AUDIT) return;
  AUDIT = evidenceContract.prepareAuditDirectory(ROOT, AUDIT);
  auditReady = true;
}

function screenshotList() {
  if (!AUDIT || !fs.existsSync(AUDIT)) return [];
  return fs.readdirSync(AUDIT).filter(name => name.toLowerCase().endsWith('.png')).sort();
}

function writeJsonAtomic(filename, value) {
  const temporary = `${filename}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n');
  fs.renameSync(temporary, filename);
}

function contractFor(number) {
  return JSON.parse(fs.readFileSync(
    path.join(ROOT, 'pedagogy', 'lessons', `${String(number).padStart(2, '0')}.yml`), 'utf8'));
}

async function expectedStates(page, allowedRoutes) {
  return page.evaluate(routes => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    const escape = value => CSS.escape(String(value));
    const selectorFor = (node, scene) => {
      if (!node || !scene?.id) return null;
      if (node.id) return `#${escape(node.id)}`;
      const parts = [];
      let current = node;
      while (current && current !== scene) {
        const tag = current.tagName.toLowerCase();
        const siblings = current.parentElement
          ? [...current.parentElement.children].filter(item => item.tagName === current.tagName) : [];
        parts.unshift(`${tag}:nth-of-type(${Math.max(1, siblings.indexOf(current) + 1)})`);
        current = current.parentElement;
      }
      return current === scene ? `#${escape(scene.id)} > ${parts.join(' > ')}` : null;
    };
    const autoEssential = (node, scene, roots = []) => {
      if (!node) return false;
      for (let current = node; current && current !== scene; current = current.parentElement) {
        if (roots.includes(current)) continue;
        if (current.hidden || current.inert || current.classList.contains('hidden')) return false;
        if (current.matches('details:not([open])') && current !== node) return false;
        if (document.body.classList.contains('mode-aula')
          && current.classList.contains('full-code')) return false;
      }
      return true;
    };
    const meaningfulChildren = (node, scene, roots = []) => [...(node?.children || [])].filter(child =>
      !['SCRIPT', 'STYLE', 'TEMPLATE'].includes(child.tagName)
      && !child.classList.contains('lr-scene-badge') && autoEssential(child, scene, roots));
    const essentialsFor = (sceneContract, stageContract) => {
      const scene = document.getElementById(sceneContract.dom_id);
      if (!scene) return [];
      const wanted = stageContract.dom_stage === undefined
        ? null : String(stageContract.dom_stage);
      const step = wanted === null ? null
        : [...scene.querySelectorAll('.step')].find(node => node.dataset.stage === wanted);
      const figure = wanted === null ? null
        : [...scene.querySelectorAll('.fig-stage')].find(node => node.dataset.stage === wanted);
      const candidates = [];
      const add = nodes => nodes.filter(Boolean).forEach(node => candidates.push(node));
      add([...scene.querySelectorAll('[data-lr-essential]')].filter(node => {
        const owner = node.closest('.step,.fig-stage');
        return !owner || owner === step || owner === figure;
      }));
      for (const root of [step, figure].filter(Boolean)) {
        const content = root.matches('.step')
          ? (root.querySelector(':scope > .step-inner') || root) : root;
        add(meaningfulChildren(content, scene, [root]));
        add([...content.querySelectorAll('canvas,svg,img,video,pre,table,[role="img"],'
          + 'button,input,select,textarea')].filter(node => autoEssential(node, scene, [root])));
      }
      const sharedHeading = [...scene.querySelectorAll('h1,h2')]
        .find(node => !node.closest('.step,.fig-stage') && autoEssential(node, scene));
      if (sharedHeading) candidates.unshift(sharedHeading);
      if (!step && !figure) {
        const wrap = scene.matches('.wrap') ? scene
          : scene.querySelector(':scope > .wrap') || scene;
        add(meaningfulChildren(wrap, scene));
        add([...scene.querySelectorAll('canvas,svg,img,video,pre,table,[role="img"],'
          + 'button,input,select,textarea')].filter(node => autoEssential(node, scene)));
      }
      return [...new Set(candidates)].map(node => selectorFor(node, scene))
        .filter(Boolean).filter((selector, index, items) => items.indexOf(selector) === index);
    };
    return contract.scenes.flatMap(scene => {
      const declared = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
      const allowed = declared.map(stage => ({ ...stage,
        effectiveRoute: String(stage.route || scene.route || 'LIVE').toUpperCase() }))
        .filter(stage => routes.includes(stage.effectiveRoute));
      return allowed.map((stage, stageIndex) => ({
        scene: scene.id, stage: stage.id, sceneRoute: scene.route,
        stageRoute: stage.effectiveRoute, type: scene.type,
        durationMinutes: stage.duration_minutes ?? scene.duration_minutes,
        stagePosition: stageIndex + 1, stageTotal: allowed.length,
        layout: scene.layout || 'focus', domId: scene.dom_id,
        essentialSelectors: essentialsFor(scene, stage),
      }));
    });
  }, allowedRoutes);
}

async function inspectState(page, expected, position, total, progressOracle = null) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() =>
    requestAnimationFrame(resolve))));
  return page.evaluate(({ expectedState, index, count, oracle }) => {
    const active = document.querySelector('body > .lr-scene-active');
    const activeScenes = [...document.querySelectorAll('body > .lr-scene')]
      .filter(node => getComputedStyle(node).display !== 'none');
    const nav = document.querySelector('#lr-nav');
    const controls = document.querySelector('#lr-controls');
    const prev = controls?.querySelector('.lr-prev');
    const next = controls?.querySelector('.lr-next');
    const tolerance = 2;
    const rect = node => node ? node.getBoundingClientRect().toJSON() : null;
    const inside = (box, bounds) => Boolean(box)
      && box.left >= bounds.left - tolerance && box.top >= bounds.top - tolerance
      && box.right <= bounds.right + tolerance && box.bottom <= bounds.bottom + tolerance;
    const visibilityEvidence = node => {
      if (!node) return { rendered: false, positiveArea: false, effectiveOpacity: 0,
        unoccluded: false };
      let effectiveOpacity = 1;
      let structurallyVisible = !node.hidden && !node.closest('[hidden],[inert]');
      for (let currentNode = node; currentNode && currentNode.nodeType === 1;
        currentNode = currentNode.parentElement) {
        const style = getComputedStyle(currentNode);
        effectiveOpacity *= Number.parseFloat(style.opacity || '1');
        if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
            || style.contentVisibility === 'hidden') structurallyVisible = false;
      }
      const box = node.getBoundingClientRect();
      const positiveArea = box.width > 0.5 && box.height > 0.5;
      const points = positiveArea ? [
        [box.left + box.width / 2, box.top + box.height / 2],
        [box.left + Math.min(2, box.width / 2), box.top + Math.min(2, box.height / 2)],
        [box.right - Math.min(2, box.width / 2), box.bottom - Math.min(2, box.height / 2)],
      ].filter(([x, y]) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight) : [];
      const unoccluded = points.some(([x, y]) => {
        const hit = document.elementFromPoint(x, y);
        return Boolean(hit && (hit === node || node.contains(hit)));
      });
      return { rendered: Boolean(structurallyVisible && effectiveOpacity > 0.01
          && node.getClientRects().length), positiveArea, effectiveOpacity, unoccluded };
    };
    const isRendered = node => {
      const evidence = visibilityEvidence(node);
      return evidence.rendered && evidence.positiveArea;
    };
    const diagnosticSelector = node => {
      if (!node) return null;
      if (node.id) return `#${CSS.escape(node.id)}`;
      const name = String(node.className || '').trim().split(/\s+/).filter(Boolean).slice(0, 2)
        .map(value => `.${CSS.escape(value)}`).join('');
      return `${node.tagName.toLowerCase()}${name}`;
    };
    const scrollerEvidence = (scroller, targetBox = null) => {
      const style = getComputedStyle(scroller);
      const overflowX = ['auto', 'scroll'].includes(style.overflowX)
        && scroller.scrollWidth > scroller.clientWidth + tolerance;
      const overflowY = ['auto', 'scroll'].includes(style.overflowY)
        && scroller.scrollHeight > scroller.clientHeight + tolerance;
      const declaredAxis = scroller.dataset.lrScrollerAxis || '';
      const actualAxis = overflowX && overflowY ? 'both'
        : (overflowX ? 'horizontal' : (overflowY ? 'vertical' : ''));
      const before = { left: scroller.scrollLeft, top: scroller.scrollTop };
      if (overflowX) scroller.scrollLeft = scroller.scrollWidth;
      if (overflowY) scroller.scrollTop = scroller.scrollHeight;
      const reachedEnd = (!overflowX
        || scroller.scrollLeft >= scroller.scrollWidth - scroller.clientWidth - tolerance)
        && (!overflowY
          || scroller.scrollTop >= scroller.scrollHeight - scroller.clientHeight - tolerance);
      scroller.scrollLeft = before.left; scroller.scrollTop = before.top;
      const scrollerBox = scroller.getBoundingClientRect();
      return { selector: diagnosticSelector(scroller), declared: scroller.dataset.lrScroller === 'true',
        declaredAxis, overflowX, overflowY, real: overflowX || overflowY,
        focusable: scroller.tabIndex >= 0, axisMatches: declaredAxis === actualAxis, reachedEnd,
        clipsTargetX: Boolean(targetBox && overflowX
          && (targetBox.left < scrollerBox.left - tolerance
            || targetBox.right > scrollerBox.right + tolerance)),
        clipsTargetY: Boolean(targetBox && overflowY
          && (targetBox.top < scrollerBox.top - tolerance
            || targetBox.bottom > scrollerBox.bottom + tolerance)) };
    };
    const validScroller = evidence => evidence.declared && evidence.real && evidence.focusable
      && evidence.axisMatches && evidence.reachedEnd;
    const scrollReachabilityFor = (node, box) => {
      const entries = [];
      for (let ancestor = node; ancestor && ancestor !== document.body;
        ancestor = ancestor.parentElement) {
        if (ancestor.dataset.lrScroller === 'true') entries.push(scrollerEvidence(ancestor, box));
      }
      return entries;
    };
    const navRect = rect(nav), controlsRect = rect(controls), sceneRect = rect(active);
    const bounds = {
      left: navRect?.right || 0, top: 0, right: innerWidth,
      bottom: controlsRect?.top || innerHeight,
    };
    const activeStep = active?.querySelector('.step.lr-stage-active:not([hidden])');
    const activeFigure = active?.querySelector('.fig-stage.on:not([hidden])');
    const selectorEntries = [...new Set(expectedState.essentialSelectors || [])]
      .map(selector => {
        try { return { selector, nodes: [...document.querySelectorAll(selector)].filter(isRendered) }; }
        catch (error) { return { selector, nodes: [], selectorError: error.message }; }
      });
    const declaredEssentials = [...(active?.querySelectorAll('[data-lr-essential]') || [])]
      .filter(isRendered).map(node => ({
        selector: `[data-lr-essential="${CSS.escape(node.dataset.lrEssential || '')}"]`,
        nodes: [node],
      }));
    const essentialEntries = [...selectorEntries, ...declaredEssentials];
    const unresolvedEssentialSelectors = essentialEntries.filter(entry => !entry.nodes.length)
      .map(entry => ({ selector: entry.selector, error: entry.selectorError || null }));
    const essentialNodes = essentialEntries.flatMap(entry => entry.nodes.map(node => ({
      selector: entry.selector, node,
    }))).filter((entry, itemIndex, items) => items.findIndex(item => item.node === entry.node) === itemIndex);
    const essentialFailures = [];
    const essentialChecks = essentialNodes.map(entry => {
      const box = rect(entry.node);
      const visibility = visibilityEvidence(entry.node);
      const diagnosticFailures = [];
      if (!visibility.rendered) diagnosticFailures.push({ kind: 'not-effectively-visible' });
      if (!visibility.positiveArea) diagnosticFailures.push({ kind: 'zero-area' });
      if (!visibility.unoccluded) diagnosticFailures.push({ kind: 'occluded' });
      if (!inside(box, bounds)) diagnosticFailures.push({ kind: 'content-viewport', bounds });
      for (let ancestor = entry.node.parentElement; ancestor && ancestor !== document.body;
        ancestor = ancestor.parentElement) {
        const style = getComputedStyle(ancestor);
        const clipsX = ['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowX);
        const clipsY = ['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowY);
        if (!clipsX && !clipsY) continue;
        const ancestorRect = ancestor.getBoundingClientRect();
        const clippingBox = {
          left: ancestorRect.left + ancestor.clientLeft,
          top: ancestorRect.top + ancestor.clientTop,
          right: ancestorRect.left + ancestor.clientLeft + ancestor.clientWidth,
          bottom: ancestorRect.top + ancestor.clientTop + ancestor.clientHeight,
        };
        const clippedX = clipsX && (box.left < clippingBox.left - tolerance
          || box.right > clippingBox.right + tolerance);
        const clippedY = clipsY && (box.top < clippingBox.top - tolerance
          || box.bottom > clippingBox.bottom + tolerance);
        if (clippedX || clippedY) diagnosticFailures.push({
          kind: 'clipping-ancestor', ancestor: diagnosticSelector(ancestor),
          axes: `${clippedX ? 'x' : ''}${clippedY ? 'y' : ''}`, bounds: clippingBox,
        });
      }
      const scrollReachability = scrollReachabilityFor(entry.node, box);
      const canExposeX = scrollReachability.some(item => validScroller(item)
        && item.overflowX && item.clipsTargetX);
      const canExposeY = scrollReachability.some(item => validScroller(item)
        && item.overflowY && item.clipsTargetY);
      const scrollReachable = canExposeX || canExposeY;
      const outsideX = box && (box.left < bounds.left - tolerance
        || box.right > bounds.right + tolerance);
      const outsideY = box && (box.top < bounds.top - tolerance
        || box.bottom > bounds.bottom + tolerance);
      const failures = diagnosticFailures.filter(failure => {
        if (failure.kind === 'occluded') return !scrollReachable;
        if (failure.kind === 'content-viewport') {
          return (outsideX && !canExposeX) || (outsideY && !canExposeY);
        }
        if (failure.kind === 'clipping-ancestor') {
          return (failure.axes.includes('x') && !canExposeX)
            || (failure.axes.includes('y') && !canExposeY);
        }
        return true;
      });
      const accessible = visibility.rendered && visibility.positiveArea
        && visibility.effectiveOpacity > 0.01 && (visibility.unoccluded || scrollReachable)
        && failures.length === 0;
      const result = { selector: entry.selector,
        label: entry.node.dataset.lrEssential || diagnosticSelector(entry.node), box,
        effectiveVisible: visibility.rendered, positiveArea: visibility.positiveArea,
        effectiveOpacity: visibility.effectiveOpacity, unoccluded: visibility.unoccluded,
        accessible, scrollReachable, scrollReachability,
        diagnosticFailures, failures };
      if (failures.length) essentialFailures.push(result);
      return result;
    });
    const stageOverflowChecks = [activeStep, activeFigure].filter(Boolean).map(node => ({
      node, kind: node.classList.contains('fig-stage') ? 'figure' : 'step',
      scrollWidth: node.scrollWidth, clientWidth: node.clientWidth,
      scrollHeight: node.scrollHeight, clientHeight: node.clientHeight,
      overflowX: node.scrollWidth > node.clientWidth + tolerance,
      overflowY: node.scrollHeight > node.clientHeight + tolerance,
    })).map(item => {
      const scrollReachability = [item.node,
        ...item.node.querySelectorAll('[data-lr-scroller="true"]')]
        .filter(isRendered).map(node => scrollerEvidence(node));
      const accessible = (!item.overflowX || scrollReachability.some(evidence =>
        validScroller(evidence) && evidence.overflowX))
        && (!item.overflowY || scrollReachability.some(evidence =>
          validScroller(evidence) && evidence.overflowY));
      return { kind: item.kind, scrollWidth: item.scrollWidth, clientWidth: item.clientWidth,
        scrollHeight: item.scrollHeight, clientHeight: item.clientHeight,
        overflowX: item.overflowX, overflowY: item.overflowY,
        overflow: item.overflowX || item.overflowY, accessible, scrollReachability };
    });
    const stageOverflow = stageOverflowChecks.some(item => item.overflow);
    const stageOverflowAccessible = stageOverflowChecks.every(item => item.accessible);
    const current = {
      scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
      sceneRoute: active?.dataset.sceneRoute,
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
    const displayedProgress = parseInt(controls?.querySelector('.lr-route-progress')?.textContent || '', 10);
    let savedProgress = null;
    try { savedProgress = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime?.progress || null; }
    catch (_error) { savedProgress = null; }
    const savedProgressMatches = !oracle || ['LIVE', 'REQUIRED', 'OPTIONAL'].every(routeName =>
      savedProgress?.[routeName]?.visited === oracle.routes[routeName].visited
      && savedProgress?.[routeName]?.total === oracle.routes[routeName].total
      && savedProgress?.[routeName]?.percent === (oracle.routes[routeName].total
        ? Math.round(100 * oracle.routes[routeName].visited / oracle.routes[routeName].total) : 100)
      && savedProgress?.[routeName]?.complete === (oracle.routes[routeName].total === 0
        || oracle.routes[routeName].visited === oracle.routes[routeName].total));
    const routeProgressMatches = !oracle || (displayedProgress === oracle.percent && savedProgressMatches);
    const allVisibleNodes = active ? [active, ...active.querySelectorAll('*')].filter(isRendered) : [];
    const actualScrollers = allVisibleNodes.filter(node => {
      const style = getComputedStyle(node);
      return ((['auto', 'scroll'].includes(style.overflowX)
          && node.scrollWidth > node.clientWidth + tolerance)
        || (['auto', 'scroll'].includes(style.overflowY)
          && node.scrollHeight > node.clientHeight + tolerance));
    });
    const declaredScrollers = allVisibleNodes.filter(node => node.dataset.lrScroller === 'true');
    const scrollerChecks = declaredScrollers.map(node => {
      const style = getComputedStyle(node);
      const overflowX = ['auto', 'scroll'].includes(style.overflowX)
        && node.scrollWidth > node.clientWidth + tolerance;
      const overflowY = ['auto', 'scroll'].includes(style.overflowY)
        && node.scrollHeight > node.clientHeight + tolerance;
      const declaredAxis = node.dataset.lrScrollerAxis || '';
      const axisMatches = declaredAxis === (overflowX && overflowY ? 'both'
        : (overflowX ? 'horizontal' : (overflowY ? 'vertical' : '')));
      const before = { left: node.scrollLeft, top: node.scrollTop };
      if (overflowX) node.scrollLeft = node.scrollWidth;
      if (overflowY) node.scrollTop = node.scrollHeight;
      const reachedEnd = (!overflowX || node.scrollLeft >= node.scrollWidth - node.clientWidth - tolerance)
        && (!overflowY || node.scrollTop >= node.scrollHeight - node.clientHeight - tolerance);
      node.scrollLeft = before.left; node.scrollTop = before.top;
      return { selector: diagnosticSelector(node), declaredAxis, overflowX, overflowY,
        real: overflowX || overflowY, focusable: node.tabIndex >= 0, axisMatches, reachedEnd };
    });
    const undeclaredScrollers = actualScrollers.filter(node => node.dataset.lrScroller !== 'true')
      .map(diagnosticSelector);
    const scrollAuditPassed = undeclaredScrollers.length === 0 && scrollerChecks.every(item =>
      item.real && item.focusable && item.axisMatches && item.reachedEnd);
    const hiddenFocusable = [...document.querySelectorAll('a[href],button,input,select,textarea,'
      + '[tabindex]:not([tabindex="-1"])')].filter(node => node.closest('[aria-hidden="true"]')
        && !node.closest('[hidden],[inert]') && node.tabIndex >= 0).map(diagnosticSelector);
    const badgeRoute = active?.querySelector('.lr-scene-badge .lr-route-label')?.textContent.trim() || null;
    const badgeDuration = active?.querySelector('.lr-scene-badge .lr-duration')?.textContent.trim() || null;
    const navRoute = nav?.querySelector('.lr-scene-links button.on .lr-route-label')?.textContent.trim() || null;
    const teacherKicker = document.querySelector('#lr-teacher-drawer .lr-teacher-kicker')
      ?.textContent.trim() || null;
    const teacherRoute = teacherKicker?.split(/\s+·\s+/)[0] || null;
    const mobileText = document.querySelector('#lr-mobile-toolbar > span')?.textContent.trim() || null;
    const expectedMobileText = `Ruta · ${expectedState.stageRoute} · `
      + `${expectedState.durationMinutes} min · Estudio · ${expectedState.scene}`;
    const mobileRouteVisible = mobileText?.includes(`· ${expectedState.stageRoute} ·`) ?? null;
    const mobileDurationVisible = mobileText
      ?.includes(`· ${expectedState.durationMinutes} min ·`) ?? null;
    const liveText = document.querySelector('body > .lr-sr-only[aria-live="polite"]')
      ?.textContent.trim() || null;
    const expectedLiveText = `${expectedState.scene}, ruta ${expectedState.stageRoute}, `
      + `${expectedState.durationMinutes} minutos, etapa ${expectedState.stagePosition} `
      + `de ${expectedState.stageTotal}`;
    const routePresentationMatches = badgeRoute === expectedState.stageRoute
      && navRoute === expectedState.stageRoute
      && (!teacherKicker || teacherKicker === `${expectedState.stageRoute} · `
        + `${expectedState.type} · ${expectedState.durationMinutes} min`)
      && mobileText === expectedMobileText
      && badgeDuration === `${expectedState.durationMinutes} min`
      && mobileRouteVisible && mobileDurationVisible;
    const liveRegionMatches = liveText === expectedLiveText;
    const runtimeState = window.LEARNING_RUNTIME?.getState?.();
    const getStateConsistent = Boolean(runtimeState)
      && runtimeState.mode === document.body.dataset.learningMode
      && runtimeState.requestedMode === document.body.dataset.requestedMode
      && runtimeState.routeScope === current.scope && runtimeState.scene === current.scene
      && runtimeState.stage === current.stage && runtimeState.route === current.stageRoute
      && runtimeState.sceneRoute === current.sceneRoute;
    const geometry = {
      evidenceSchema: 'desktop-state/v3',
      viewport: { width: innerWidth, height: innerHeight },
      activeVisibility: visibilityEvidence(active),
      activeSceneCount: activeScenes.length,
      bodyOverflow,
      bodyScrollPosition: { x: scrollX, y: scrollY },
      horizontalOverflow,
      oneSceneActive: activeScenes.length === 1,
      sceneInsideViewport: inside(sceneRect, bounds),
      controlsInsideViewport: inside(controlsRect,
        { left: bounds.left, top: 0, right: innerWidth, bottom: innerHeight }),
      navInsideViewport: inside(navRect, { left: 0, top: 0, right: innerWidth, bottom: innerHeight }),
      essentialInsideViewport: essentialNodes.length > 0
        && essentialChecks.every(item => item.diagnosticFailures.length === 0)
        && unresolvedEssentialSelectors.length === 0,
      essentialAccessible: essentialNodes.length > 0 && essentialFailures.length === 0
        && unresolvedEssentialSelectors.length === 0,
      essentialCount: essentialNodes.length,
      essentialSelectors: expectedState.essentialSelectors || [],
      unresolvedEssentialSelectors,
      essentialChecks,
      stageOverflow,
      stageOverflowAccessible,
      stageOverflowChecks,
      layoutMatches,
      layoutApplied: active?.dataset.layoutApplied === 'true',
      routeProgressMatches,
      savedProgressMatches,
      savedProgress,
      progressOracle: oracle,
      displayedProgress,
      scrollAuditPassed,
      scrollerChecks,
      undeclaredScrollers,
      hiddenFocusable,
      routePresentation: { badgeRoute, badgeDuration, navRoute, teacherRoute, teacherKicker,
        mobileText, expectedMobileText, mobileRouteVisible, mobileDurationVisible },
      routePresentationMatches,
      liveRegion: { text: liveText, expected: expectedLiveText },
      liveRegionMatches,
      getStateConsistent,
      runtimeState,
      layoutGeometry: { expectedLeft, cssLeft, actualLeft, steps: stepsRect, figure: figureRect },
      contentViewport: bounds,
      sceneBox: sceneRect,
      controlsBox: controlsRect,
      navBox: navRect,
      controlEvidence: { previousDisabled: prev?.disabled ?? null, nextDisabled: next?.disabled ?? null },
      essentialFailures,
      internalVerticalScroll: actualScrollers.some(node =>
        node.scrollHeight > node.clientHeight + tolerance),
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
        && geometry.navInsideViewport && geometry.essentialAccessible
        && stageOverflowAccessible && layoutMatches && routeProgressMatches && scrollAuditPassed
        && hiddenFocusable.length === 0 && routePresentationMatches && liveRegionMatches
        && getStateConsistent,
    };
  }, { expectedState: expected, index: position, count: total, oracle: progressOracle });
}

async function saveFailure(page, lesson, viewport, scope, state) {
  if (!AUDIT) return null;
  const file = `failure-${slug(lesson)}-${viewportName(viewport)}-${slug(scope)}`
    + `-${slug(state.scene || 'unknown')}-${slug(state.stage || 'unknown')}.png`;
  await page.screenshot({ path: path.join(AUDIT, file) });
  return file;
}

function collectPageFailures(page) {
  const errors = [];
  page.on('pageerror', error => errors.push(`pageerror: ${error?.message || String(error)}`));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(`console.error: ${message.text()}`);
  });
  return {
    reset() { errors.length = 0; },
    snapshot() { return [...errors]; },
  };
}

async function finalizePageRecord(record, identity, pageEntries) {
  const entries = Array.isArray(pageEntries) ? pageEntries : [pageEntries];
  const captured = entries.flatMap(entry => entry.failures.snapshot().map(error =>
    entry.label ? `${entry.label}: ${error}` : error));
  record.errors = [...new Set([...(Array.isArray(record.errors) ? record.errors : []), ...captured])];
  record.passed = Boolean(record.passed) && record.errors.length === 0;
  if (record.passed) return record;

  const screenshots = record.screenshot ? [record.screenshot] : [];
  if (!screenshots.length && auditReady) {
    const parts = (Array.isArray(identity) ? identity : [identity]).map(slug).filter(Boolean);
    for (const entry of entries) {
      if (!entry.page || entry.page.isClosed()) continue;
      const suffix = entry.label ? `-${slug(entry.label)}` : '';
      const file = `failure-record-${parts.join('-')}${suffix}.png`;
      await entry.page.screenshot({ path: path.join(AUDIT, file) });
      screenshots.push(file);
    }
  }
  record.failureScreenshot = screenshots[0] || null;
  if (screenshots.length > 1) record.failureScreenshots = screenshots;
  return record;
}

async function prepare(page, relative, query = '?mode=aula', clear = true) {
  const target = fileUrl(relative, query);
  await page.goto(target);
  await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  if (clear) {
    await page.evaluate(() => {
      localStorage.clear();
      history.replaceState(null, '', location.pathname + location.search);
    });
    // A hash-only navigation keeps the existing document and its runtime alive.
    // Reload the canonical URL so each traversal starts in a new document.
    await page.reload();
    await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  }
  await page.evaluate(() => document.fonts?.ready);
}

async function traverse(page, lesson, viewport, scope, allowedRoutes, pageFailures) {
  const expected = await expectedStates(page, allowedRoutes);
  const inventory = await expectedStates(page, ['LIVE', 'REQUIRED', 'OPTIONAL']);
  const visitedOracle = new Set();
  const routeTotals = Object.fromEntries(['LIVE', 'REQUIRED', 'OPTIONAL'].map(routeName =>
    [routeName, inventory.filter(state => state.stageRoute === routeName).length]));
  const states = [];
  for (let index = 0; index < expected.length; index++) {
    visitedOracle.add(`${expected[index].scene}::${expected[index].stage}`);
    const routes = Object.fromEntries(['LIVE', 'REQUIRED', 'OPTIONAL'].map(routeName => [routeName, {
      visited: inventory.filter(state => state.stageRoute === routeName
        && visitedOracle.has(`${state.scene}::${state.stage}`)).length,
      total: routeTotals[routeName],
    }]));
    const enabledVisited = allowedRoutes.reduce((sum, routeName) => sum + routes[routeName].visited, 0);
    const enabledTotal = allowedRoutes.reduce((sum, routeName) => sum + routes[routeName].total, 0);
    const oracle = { routes, percent: Math.round(100 * enabledVisited / Math.max(1, enabledTotal)) };
    const state = await inspectState(page, expected[index], index, expected.length, oracle);
    if (!state.passed) state.failureScreenshot = await saveFailure(page, lesson, viewport, scope, state);
    states.push(state);
    if (index < expected.length - 1) {
      const next = expected[index + 1];
      // Geometry traversal must be deterministic. Keyboard ownership is audited
      // independently below (navigation, drawers and declared scrollers).
      const moved = await page.evaluate(target =>
        window.LEARNING_RUNTIME?.goTo(target.scene, target.stage) === true, next);
      if (!moved) throw new Error(`runtime refused ${next.scene}/${next.stage}`);
      await page.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
        && document.body.dataset.currentStageId === target.stage, next);
    }
  }
  const errors = pageFailures.snapshot();
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

async function drawerKeyboardAudit(page, triggerSelector, drawerSelector, openMethod = 'click') {
  const trigger = page.locator(triggerSelector);
  const drawer = page.locator(drawerSelector);
  if (!await trigger.count() || !await drawer.count() || !await trigger.isVisible()) {
    return { present: false, passed: false };
  }
  const backgroundBefore = await drawer.evaluate(node => [...document.body.children]
    .filter(item => item !== node).map(item => ({ inert: item.inert, attribute: item.hasAttribute('inert') })));
  const stageBefore = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await trigger.focus();
  if (openMethod === 'guide-api') {
    await page.evaluate(selector => {
      const opener = document.querySelector(selector);
      window.GUIDE_DRAWER?.open(opener);
    }, triggerSelector);
  } else {
    await trigger.click();
  }
  await drawer.waitFor({ state: 'visible' });
  const opened = await drawer.evaluate(node => node.classList.contains('open')
    && !node.hidden && !node.inert && node.getAttribute('aria-hidden') === 'false'
    && node.contains(document.activeElement));
  const backgroundInert = await drawer.evaluate(node => [...document.body.children]
    .filter(item => item !== node).every(item => item.inert && item.hasAttribute('inert'))
      && document.body.classList.contains('lr-modal-open'));
  const outsideFocusBlocked = await drawer.evaluate((node, selector) => {
    document.querySelector(selector)?.focus();
    return node.contains(document.activeElement);
  }, triggerSelector);
  const backgroundProbe = await page.evaluate(() => {
    const button = [...document.querySelectorAll('#lr-controls button,#lr-mobile-toolbar button')]
      .find(item => !item.disabled && item.getClientRects().length);
    if (!button) return null;
    window.__lrBackgroundClickCount = 0;
    button.addEventListener('click', () => { window.__lrBackgroundClickCount += 1; });
    const rect = button.getBoundingClientRect();
    return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
  });
  if (backgroundProbe) await page.mouse.click(backgroundProbe.x, backgroundProbe.y);
  const backgroundClickBlocked = await drawer.evaluate((node, initial) => ({
    clicks: window.__lrBackgroundClickCount || 0,
    stateUnchanged: `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}` === initial,
    focusInside: node.contains(document.activeElement),
  }), stageBefore);
  backgroundClickBlocked.passed = Boolean(backgroundProbe) && backgroundClickBlocked.clicks === 0
    && backgroundClickBlocked.stateUnchanged && backgroundClickBlocked.focusInside;
  const focusableSelector = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),'
    + 'textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
  const focusableCount = await drawer.locator(focusableSelector).count();
  let reverseLoop = false;
  let forwardLoop = false;
  if (focusableCount) {
    await drawer.evaluate((node, selector) => {
      const items = [...node.querySelectorAll(selector)].filter(item => !item.hidden
        && !item.closest('[hidden],[inert]') && item.getClientRects().length);
      items[0]?.focus();
    }, focusableSelector);
    await page.keyboard.press('Shift+Tab');
    reverseLoop = await drawer.evaluate((node, selector) => {
      const items = [...node.querySelectorAll(selector)].filter(item => !item.hidden
        && !item.closest('[hidden],[inert]') && item.getClientRects().length);
      return items.length > 0 && document.activeElement === items[items.length - 1];
    }, focusableSelector);
    await page.keyboard.press('Tab');
    forwardLoop = await drawer.evaluate((node, selector) => {
      const items = [...node.querySelectorAll(selector)].filter(item => !item.hidden
        && !item.closest('[hidden],[inert]') && item.getClientRects().length);
      return items.length > 0 && document.activeElement === items[0];
    }, focusableSelector);
  }
  const modalNavigation = [];
  const drawerScroller = drawer.locator('[data-lr-scroller="true"]').first();
  await drawerScroller.evaluate(node => {
    const spacer = document.createElement('div');
    spacer.dataset.lrAuditScrollSpacer = 'true';
    spacer.style.height = '1800px';
    node.appendChild(spacer);
    node.scrollTop = 0;
  });
  await drawerScroller.focus();
  await page.keyboard.press('PageDown');
  await page.waitForFunction(selector => document.querySelector(selector)?.scrollTop > 0,
    `${drawerSelector} [data-lr-scroller="true"]`);
  const nativeScroll = await drawerScroller.evaluate(node => {
    const result = { scrollable: node.scrollHeight > node.clientHeight, offset: node.scrollTop };
    node.querySelector('[data-lr-audit-scroll-spacer]')?.remove();
    return { ...result, passed: result.scrollable && result.offset > 0 };
  });
  for (const key of ['ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp', 'Space']) {
    await page.keyboard.press(key);
    const keyState = await drawer.evaluate((node, initial) => ({
      state: `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`,
      focusInside: node.contains(document.activeElement),
      unchanged: `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}` === initial,
    }), stageBefore);
    modalNavigation.push({ key, ...keyState });
  }
  const modalKeysBlocked = modalNavigation.every(item => item.unchanged && item.focusInside);
  await page.keyboard.press('Escape');
  const closed = await drawer.evaluate((node, selector) => ({
    hidden: node.hidden && node.inert && node.getAttribute('aria-hidden') === 'true'
      && !node.classList.contains('open'),
    noExposedFocusable: [...node.querySelectorAll(selector)].every(item =>
      Boolean(item.closest('[hidden],[inert]'))),
  }), focusableSelector);
  const focusRestored = await trigger.evaluate(node => document.activeElement === node);
  const backgroundRestored = await drawer.evaluate((node, before) => {
    const after = [...document.body.children].filter(item => item !== node)
      .map(item => ({ inert: item.inert, attribute: item.hasAttribute('inert') }));
    return JSON.stringify(after) === JSON.stringify(before)
      && !document.body.classList.contains('lr-modal-open');
  }, backgroundBefore);
  return { present: true, opened, backgroundInert, outsideFocusBlocked, backgroundClickBlocked,
    focusableCount, reverseLoop, forwardLoop,
    nativeScroll, modalNavigation, modalKeysBlocked, closed: closed.hidden,
    noExposedFocusable: closed.noExposedFocusable, focusRestored, backgroundRestored,
    passed: opened && backgroundInert && outsideFocusBlocked && backgroundClickBlocked.passed
      && focusableCount > 0 && reverseLoop && forwardLoop && nativeScroll.passed
      && modalKeysBlocked && closed.hidden && closed.noExposedFocusable && focusRestored
      && backgroundRestored };
}

async function modalCoordinationAudit(page) {
  const teacher = page.locator('#lr-teacher-drawer');
  const guide = page.locator('#guion-drawer');
  if (!await teacher.count() || !await guide.count()) {
    return { applicable: false, passed: true };
  }
  await page.locator('#lr-teacher-toggle').click();
  await teacher.waitFor({ state: 'visible' });
  const handoff = teacher.locator('.lr-full-guide');
  if (!await handoff.count()) {
    await page.keyboard.press('Escape');
    return { applicable: false, passed: true };
  }
  await handoff.click();
  await guide.waitFor({ state: 'visible' });
  const afterHandoff = await page.evaluate(() => {
    const teacherDrawer = document.getElementById('lr-teacher-drawer');
    const guideDrawer = document.getElementById('guion-drawer');
    return {
      teacherClosed: teacherDrawer.hidden && !teacherDrawer.classList.contains('open'),
      guideOpen: !guideDrawer.hidden && guideDrawer.classList.contains('open'),
      exactlyOneOpen: [teacherDrawer, guideDrawer]
        .filter(node => node.classList.contains('open')).length === 1,
      focusInsideGuide: guideDrawer.contains(document.activeElement),
      modalClass: document.body.classList.contains('lr-modal-open'),
    };
  });
  const focusBeforeIdempotentClose = await page.evaluate(() => document.activeElement?.id || '');
  await page.evaluate(() => window.LEARNING_TEACHER_DRAWER?.close());
  const idempotentClose = await page.evaluate(before => ({
    focusUnchanged: (document.activeElement?.id || '') === before,
    guideStillOpen: window.GUIDE_DRAWER?.isOpen() === true,
  }), focusBeforeIdempotentClose);
  await page.keyboard.press('Escape');
  const closed = await page.evaluate(() => !window.GUIDE_DRAWER?.isOpen()
    && !window.LEARNING_TEACHER_DRAWER?.isOpen()
    && !document.body.classList.contains('lr-modal-open'));
  await page.evaluate(() => window.GUIDE_DRAWER
    ?.open(document.querySelector('#lr-teacher-toggle')));
  await guide.waitFor({ state: 'visible' });
  await page.evaluate(() => window.LEARNING_TEACHER_DRAWER
    ?.open(document.querySelector('#lr-teacher-toggle')));
  await teacher.waitFor({ state: 'visible' });
  const reverseHandoff = await page.evaluate(() => {
    const teacherDrawer = document.getElementById('lr-teacher-drawer');
    const guideDrawer = document.getElementById('guion-drawer');
    return {
      guideClosed: guideDrawer.hidden && !guideDrawer.classList.contains('open'),
      teacherOpen: !teacherDrawer.hidden && teacherDrawer.classList.contains('open'),
      exactlyOneOpen: [teacherDrawer, guideDrawer]
        .filter(node => node.classList.contains('open')).length === 1,
      focusInsideTeacher: teacherDrawer.contains(document.activeElement),
      modalClass: document.body.classList.contains('lr-modal-open'),
    };
  });
  await page.keyboard.press('Escape');
  const reverseClosed = await page.evaluate(() => !window.GUIDE_DRAWER?.isOpen()
    && !window.LEARNING_TEACHER_DRAWER?.isOpen()
    && !document.body.classList.contains('lr-modal-open'));
  return { applicable: true, afterHandoff, idempotentClose, closed,
    reverseHandoff, reverseClosed,
    passed: Object.values(afterHandoff).every(Boolean)
      && Object.values(idempotentClose).every(Boolean) && closed
      && Object.values(reverseHandoff).every(Boolean) && reverseClosed };
}

async function documentTabAudit(page) {
  const setup = await page.evaluate(() => {
    const selector = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),'
      + 'textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
    const exposed = node => !node.hidden && !node.closest('[hidden],[inert],[aria-hidden="true"]')
      && getComputedStyle(node).display !== 'none' && getComputedStyle(node).visibility !== 'hidden'
      && node.getClientRects().length && node.tabIndex >= 0;
    const items = [...document.querySelectorAll(selector)].filter(exposed);
    document.querySelectorAll('[data-lr-audit-tab-start]').forEach(node =>
      node.removeAttribute('data-lr-audit-tab-start'));
    if (items[0]) {
      items[0].dataset.lrAuditTabStart = 'true';
      items[0].focus();
    }
    return { count: items.length };
  });
  if (!setup.count) return { count: 0, wrapped: false, hiddenFocus: [], passed: false };
  const hiddenFocus = [];
  let wrapped = false;
  for (let index = 0; index < setup.count + 2; index++) {
    await page.keyboard.press('Tab');
    const state = await page.evaluate(() => {
      const active = document.activeElement;
      const outsideDocumentTabOrder = !active || active === document.body;
      const hidden = !outsideDocumentTabOrder && (active.hidden
        || Boolean(active.closest('[hidden],[inert],[aria-hidden="true"]'))
        || getComputedStyle(active).display === 'none'
        || getComputedStyle(active).visibility === 'hidden');
      return { hidden, label: active?.id || String(active?.className || active?.tagName || ''),
        start: active?.dataset.lrAuditTabStart === 'true', outsideDocumentTabOrder };
    });
    if (state.hidden) hiddenFocus.push(state.label);
    if (state.start) { wrapped = true; break; }
  }
  await page.evaluate(() => document.querySelector('[data-lr-audit-tab-start]')
    ?.removeAttribute('data-lr-audit-tab-start'));
  return { count: setup.count, wrapped, hiddenFocus,
    passed: wrapped && hiddenFocus.length === 0 };
}

async function testNavigationAndPersistence(page, expectTeacher = false) {
  const endState = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  // Exercise global classroom navigation from neutral controls. A focused simulator or
  // declared scroller owns its axis keys and is audited independently by overflowFixture().
  await page.locator('#lr-controls .lr-prev').focus();
  await page.keyboard.press('PageUp');
  const afterBack = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  await page.locator('#lr-controls .lr-next').focus();
  await page.keyboard.press('PageDown');
  const afterForward = await page.evaluate(() =>
    `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`);
  const drawers = {};
  let drawersPassed = true;
  if (expectTeacher) {
    drawers.teacher = await drawerKeyboardAudit(page, '#lr-teacher-toggle', '#lr-teacher-drawer');
    drawers.guide = await page.locator('#guion-drawer').count()
      ? await drawerKeyboardAudit(page, '#lr-teacher-toggle', '#guion-drawer', 'guide-api')
      : { present: false, applicable: false, passed: false };
    drawersPassed = drawers.teacher.present && drawers.teacher.passed
      && drawers.guide.present && drawers.guide.passed;
    drawers.coordination = await modalCoordinationAudit(page);
    drawersPassed = drawersPassed && drawers.coordination.passed;
  }
  const tabOrder = await documentTabAudit(page);
  const focusVisible = await page.locator('#lr-controls .lr-prev').evaluate(node => {
    node.focus();
    const style = getComputedStyle(node);
    return style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2;
  });
  await page.keyboard.press('ArrowLeft');
  const persistence = await page.evaluate(() => {
    const target = {
      scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
    };
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime || null; }
    catch (_error) { saved = null; }
    let hashTarget = null;
    try { hashTarget = decodeURIComponent(location.hash.slice(1)); }
    catch (_error) { hashTarget = null; }
    return {
      target,
      hash: location.hash,
      hashTarget,
      storageTarget: saved ? { scene: saved.scene, stage: saved.stage } : null,
      storageVersion: saved?.version ?? null,
      progressValid: Boolean(saved?.version >= 2 && saved.progress?.LIVE
        && Array.isArray(saved.visited)),
    };
  });
  const targetPath = `${persistence.target.scene}/${persistence.target.stage}`;
  // Fresh-context hash precedence is sealed separately by persistenceIsolationAudit(). Here
  // we prove the same page can clear storage and restore the exact hash deterministically.
  const storageClearedForHashRestore = await page.evaluate(() => {
    localStorage.clear();
    return localStorage.length === 0;
  });
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME && document.body.classList.contains('mode-aula'));
  const restored = await page.evaluate(() => ({
    scene: document.body.dataset.currentSceneId,
    stage: document.body.dataset.currentStageId,
  }));
  const home = await page.locator('#lr-nav .lr-course-home').getAttribute('href');
  const restoredPath = `${restored.scene}/${restored.stage}`;
  return {
    backward: afterBack !== endState,
    forward: afterForward === endState,
    drawers,
    drawersPassed,
    tabOrder,
    tabOrderPassed: tabOrder.passed,
    focusVisible,
    reloadPersistence: targetPath === restoredPath,
    hashWritten: persistence.hashTarget === targetPath,
    hashTargetMatches: persistence.hashTarget === targetPath,
    storageTargetMatches: persistence.storageTarget?.scene === persistence.target.scene
      && persistence.storageTarget?.stage === persistence.target.stage,
    storageClearedForHashRestore,
    persistence: { ...persistence, restored: { scene: restored.scene, stage: restored.stage } },
    progress: persistence.progressValid,
    courseHome: home === '../../index.html',
  };
}

async function breakpointSeamAudit(browser, item) {
  const target = declaredStates(item).find(state => state.scene === 'l08-plan-validate-commit')
    || declaredStates(item).find(state => state.stageRoute === 'LIVE');
  const records = [];
  for (const width of [900, 901, 920, 960, 961]) {
    const context = await browser.newContext({ viewport: { width, height: 720 } });
    const page = await context.newPage();
    const pageFailures = collectPageFailures(page);
    const suffix = `?mode=aula#${encodeURIComponent(target.scene)}/${encodeURIComponent(target.stage)}`;
    await page.goto(fileUrl(item.relative, suffix));
    await page.waitForFunction(expected => window.LEARNING_RUNTIME
      && document.body.dataset.currentSceneId === expected.scene
      && document.body.dataset.currentStageId === expected.stage, target);
    const state = await page.evaluate(expected => {
      const scene = document.querySelector(`[data-scene-id="${CSS.escape(expected.scene)}"]`);
      const scrolly = scene?.querySelector('.scrolly');
      const steps = scrolly?.querySelector('.steps')?.getBoundingClientRect();
      const figure = scrolly?.querySelector('.figwrap')?.getBoundingClientRect();
      const effectiveMode = document.body.dataset.learningMode;
      const display = scrolly ? getComputedStyle(scrolly).display : null;
      const toolbar = document.getElementById('lr-mobile-toolbar');
      return {
        effectiveMode,
        display,
        toolbarVisible: Boolean(toolbar && getComputedStyle(toolbar).display !== 'none'),
        oneScene: [...document.querySelectorAll('body > .lr-scene')]
          .filter(node => getComputedStyle(node).display !== 'none').length === 1,
        panelsDoNotOverlap: !steps || !figure || steps.right <= figure.left + 2,
        bodyOverflowHidden: getComputedStyle(document.body).overflow === 'hidden',
        horizontalOverflow: document.documentElement.scrollWidth
          > document.documentElement.clientWidth + 2,
      };
    }, target);
    const mobile = width === 900;
    state.passed = mobile
      ? state.effectiveMode === 'estudio' && state.display === 'flex' && state.toolbarVisible
        && !state.horizontalOverflow
      : state.effectiveMode === 'aula' && state.display === 'grid' && state.oneScene
        && state.panelsDoNotOverlap && state.bodyOverflowHidden && !state.horizontalOverflow;
    const record = { width, ...state };
    await finalizePageRecord(record, ['negative-fixture', 'breakpoint', width],
      { page, failures: pageFailures });
    records.push(record);
    await context.close();
  }
  return { records, passed: records.every(record => record.passed) };
}

async function overflowFixture(browser) {
  const lesson = LESSONS.find(item => item.number === 8) || LESSONS[0];
  const viewport = { width: 1280, height: 720 };
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const pageFailures = collectPageFailures(page);
  await prepare(page, lesson.relative);
  const expected = await expectedStates(page, ['LIVE']);
  const targetIndex = Math.max(0, Math.min(3, expected.length - 2));
  for (let index = 0; index < targetIndex; index++) await page.keyboard.press('ArrowRight');
  const before = await inspectState(page, expected[targetIndex], targetIndex, expected.length);
  await page.evaluate(() => {
    const clip = document.createElement('div');
    clip.id = 'lr-nested-clip-fixture';
    clip.style.cssText = 'position:fixed;left:320px;top:120px;width:120px;height:80px;overflow:hidden';
    const fixture = document.createElement('div');
    fixture.dataset.lrEssential = 'nested-overflow-fixture';
    fixture.textContent = 'nested overflow fixture';
    fixture.style.cssText = 'margin-left:160px;width:240px;height:60px';
    clip.appendChild(fixture);
    const active = document.querySelector('body > .lr-scene-active');
    active.appendChild(clip);
    const horizontal = document.createElement('div');
    horizontal.id = 'lr-horizontal-keyboard-fixture';
    horizontal.tabIndex = 0;horizontal.dataset.lrScroller = 'true';
    horizontal.dataset.lrScrollerAxis = 'horizontal';
    horizontal.style.cssText = 'position:fixed;left:470px;top:120px;width:120px;height:40px;overflow:auto';
    horizontal.innerHTML = '<div style="width:480px;height:20px">horizontal keyboard fixture</div>';
    const vertical = document.createElement('div');
    vertical.id = 'lr-vertical-keyboard-fixture';
    vertical.tabIndex = 0;vertical.dataset.lrScroller = 'true';
    vertical.dataset.lrScrollerAxis = 'vertical';
    vertical.style.cssText = 'position:fixed;left:610px;top:120px;width:120px;height:60px;overflow:auto';
    vertical.innerHTML = '<div style="width:90px;height:360px">vertical keyboard fixture</div>';
    active.append(horizontal, vertical);
  });
  const scrollerKeyboard = [];
  for (const fixture of [
    { selector: '#lr-horizontal-keyboard-fixture', key: 'ArrowRight', property: 'scrollLeft' },
    { selector: '#lr-vertical-keyboard-fixture', key: 'PageDown', property: 'scrollTop' },
  ]) {
    const beforeState = await page.evaluate(() =>
      `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}/${location.hash}`);
    await page.locator(fixture.selector).focus();
    await page.keyboard.press(fixture.key);
    await page.waitForFunction(({ selector, property }) =>
      document.querySelector(selector)?.[property] > 0, fixture);
    const check = await page.locator(fixture.selector).evaluate((node, args) => ({
      offset: node[args.property],
      state: `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}/${location.hash}`,
    }), fixture);
    scrollerKeyboard.push({ ...fixture, beforeState, ...check,
      passed: check.offset > 0 && check.state === beforeState });
  }
  const fixtureState = { ...expected[targetIndex], essentialSelectors:
    [...expected[targetIndex].essentialSelectors, '[data-lr-essential="nested-overflow-fixture"]'] };
  const after = await inspectState(page, fixtureState, targetIndex, expected.length);
  if (AUDIT) await page.screenshot({ path: path.join(AUDIT, 'fixture-intermediate-overflow-detected.png') });
  const clippingDetected = after.essentialFailures.some(item => item.failures
    .some(failure => failure.kind === 'clipping-ancestor'));
  const breakpointSeams = await breakpointSeamAudit(browser, lesson);
  const record = {
    lesson: lesson.lesson, viewport: viewportName(viewport), mode: 'negative-fixture',
    scene: after.scene, stage: after.stage,
    before,
    after,
    baselinePassed: before.passed,
    detectorRejectedNestedClipping: !after.passed && clippingDetected,
    scrollerKeyboard,
    breakpointSeams,
    passed: before.passed && !after.passed && clippingDetected
      && scrollerKeyboard.every(item => item.passed) && breakpointSeams.passed,
  };
  await finalizePageRecord(record, [lesson.lesson, viewportName(viewport), 'negative-fixture'],
    { page, failures: pageFailures });
  await context.close();
  return record;
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
  const runtimeState = window.LEARNING_RUNTIME?.getState?.();
  const currentScene = contract.scenes.find(scene => scene.id === document.body.dataset.currentSceneId);
  const currentStage = currentScene?.stages?.find(stage =>
    stage.id === document.body.dataset.currentStageId)
    || (currentScene && { id: 'stage', route: currentScene.route });
  const currentRoute = currentStage?.route || currentScene?.route;
  const routeTotals = Object.fromEntries(['LIVE', 'REQUIRED', 'OPTIONAL'].map(routeName =>
    [routeName, states.filter(state => state.route === routeName).length]));
  const progressTotalsMatch = ['LIVE', 'REQUIRED', 'OPTIONAL'].every(routeName =>
    runtimeState?.progress?.[routeName]?.total === routeTotals[routeName]);
  const getStateConsistent = Boolean(runtimeState && currentScene && currentStage)
    && runtimeState.mode === document.body.dataset.learningMode
    && runtimeState.requestedMode === document.body.dataset.requestedMode
    && runtimeState.routeScope === document.body.dataset.routeScope
    && runtimeState.scene === currentScene.id && runtimeState.stage === currentStage.id
    && runtimeState.route === currentRoute && runtimeState.sceneRoute === currentScene.route;
  return {
    officialAvailable: states.filter(state => state.route !== 'OPTIONAL').every(available),
    optionalCount: states.filter(state => state.route === 'OPTIONAL').length,
    optionalAvailable: states.filter(state => state.route === 'OPTIONAL').filter(available).length,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    vertical: document.documentElement.scrollHeight > innerHeight,
    routeScope: document.body.dataset.routeScope,
    progressReady: Boolean(window.LEARNING_RUNTIME?.getState().progress?.LIVE),
    progressTotalsMatch,
    getStateConsistent,
    runtimeState,
  };
}

async function inspectFlowState(page, expected, position, total) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() =>
    requestAnimationFrame(resolve))));
  return page.evaluate(({ target, index, count }) => {
    const tolerance = 2;
    const visibilityEvidence = node => {
      if (!node) return { rendered: false, positiveArea: false, effectiveOpacity: 0,
        unoccluded: false };
      let effectiveOpacity = 1;
      let structurallyVisible = !node.hidden && !node.closest('[hidden],[inert]');
      for (let currentNode = node; currentNode && currentNode.nodeType === 1;
        currentNode = currentNode.parentElement) {
        const style = getComputedStyle(currentNode);
        effectiveOpacity *= Number.parseFloat(style.opacity || '1');
        if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
            || style.contentVisibility === 'hidden') structurallyVisible = false;
      }
      const box = node.getBoundingClientRect();
      const positiveArea = box.width > 0.5 && box.height > 0.5;
      const visibleBox = { left: Math.max(0, box.left), top: Math.max(0, box.top),
        right: Math.min(innerWidth, box.right), bottom: Math.min(innerHeight, box.bottom) };
      const occlusionApplicable = positiveArea && visibleBox.right > visibleBox.left
        && visibleBox.bottom > visibleBox.top;
      const points = occlusionApplicable ? [
        [(visibleBox.left + visibleBox.right) / 2, (visibleBox.top + visibleBox.bottom) / 2],
        [visibleBox.left + Math.min(2, (visibleBox.right - visibleBox.left) / 2),
          visibleBox.top + Math.min(2, (visibleBox.bottom - visibleBox.top) / 2)],
        [visibleBox.right - Math.min(2, (visibleBox.right - visibleBox.left) / 2),
          visibleBox.bottom - Math.min(2, (visibleBox.bottom - visibleBox.top) / 2)],
      ] : [];
      const unoccluded = !occlusionApplicable || points.some(([x, y]) => {
        const hit = document.elementFromPoint(x, y);
        return Boolean(hit && (hit === node || node.contains(hit)));
      });
      return { rendered: Boolean(structurallyVisible && effectiveOpacity > 0.01
          && node.getClientRects().length), positiveArea, effectiveOpacity, unoccluded,
        occlusionApplicable };
    };
    const rendered = node => {
      const evidence = visibilityEvidence(node);
      return evidence.rendered && evidence.positiveArea;
    };
    const diagnostic = node => node?.id ? `#${CSS.escape(node.id)}`
      : `${node?.tagName?.toLowerCase() || 'unknown'}.${String(node?.className || '')
        .trim().split(/\s+/).filter(Boolean).slice(0, 2).map(CSS.escape).join('.')}`;
    const documentScrollerEvidence = (node, targetBox) => {
      const scrolling = document.scrollingElement || document.documentElement;
      const overflowY = scrolling.scrollHeight > scrolling.clientHeight + tolerance;
      const toolbar = document.getElementById('lr-mobile-toolbar');
      const toolbarBox = toolbar && rendered(toolbar) ? toolbar.getBoundingClientRect() : null;
      const stickyBottoms = [...document.querySelectorAll('.figwrap')].filter(item => {
        if (item.contains(node) || !rendered(item) || !targetBox) return false;
        const style = getComputedStyle(item);
        const box = item.getBoundingClientRect();
        return ['sticky', 'fixed'].includes(style.position) && Number(style.zIndex || 0) > 0
          && box.bottom > 0 && box.top < innerHeight
          && box.right > targetBox.left + tolerance && box.left < targetBox.right - tolerance
          && box.bottom > targetBox.top + tolerance && box.top < targetBox.bottom - tolerance;
      }).map(item => item.getBoundingClientRect().bottom);
      const safeTop = Math.max(0, toolbarBox?.bottom || 0, ...stickyBottoms);
      const originallyClipped = Boolean(targetBox
        && (targetBox.top < safeTop - tolerance || targetBox.bottom > innerHeight + tolerance));
      const absoluteTop = targetBox ? targetBox.top + scrollY : 0;
      const absoluteBottom = targetBox ? targetBox.bottom + scrollY : 0;
      const maxY = Math.max(0, scrolling.scrollHeight - scrolling.clientHeight);
      const targetY = Math.max(0, Math.min(maxY, absoluteTop - safeTop));
      const exposedTop = absoluteTop - targetY;
      const exposedBottom = absoluteBottom - targetY;
      const targetReachable = overflowY && originallyClipped
        && exposedBottom > safeTop + tolerance && exposedTop < innerHeight - tolerance;
      return { selector: 'document.scrollingElement', documentScroller: true,
        targetReachable, declared: true, declaredAxis: 'vertical', overflowX: false, overflowY,
        real: overflowY, focusable: true, axisMatches: true, reachedEnd: true,
        targetScrollTop: targetY, maximumScrollTop: maxY,
        clipsTargetX: false, clipsTargetY: originallyClipped && targetReachable };
    };
    const scrollerEvidence = (scroller, targetBox = null) => {
      const style = getComputedStyle(scroller);
      const overflowX = ['auto', 'scroll'].includes(style.overflowX)
        && scroller.scrollWidth > scroller.clientWidth + tolerance;
      const overflowY = ['auto', 'scroll'].includes(style.overflowY)
        && scroller.scrollHeight > scroller.clientHeight + tolerance;
      const declaredAxis = scroller.dataset.lrScrollerAxis || '';
      const actualAxis = overflowX && overflowY ? 'both'
        : (overflowX ? 'horizontal' : (overflowY ? 'vertical' : ''));
      const before = { left: scroller.scrollLeft, top: scroller.scrollTop };
      if (overflowX) scroller.scrollLeft = scroller.scrollWidth;
      if (overflowY) scroller.scrollTop = scroller.scrollHeight;
      const reachedEnd = (!overflowX
        || scroller.scrollLeft >= scroller.scrollWidth - scroller.clientWidth - tolerance)
        && (!overflowY
          || scroller.scrollTop >= scroller.scrollHeight - scroller.clientHeight - tolerance);
      scroller.scrollLeft = before.left; scroller.scrollTop = before.top;
      const scrollerBox = scroller.getBoundingClientRect();
      return { selector: diagnostic(scroller), declared: scroller.dataset.lrScroller === 'true',
        declaredAxis, overflowX, overflowY, real: overflowX || overflowY,
        focusable: scroller.tabIndex >= 0, axisMatches: declaredAxis === actualAxis, reachedEnd,
        clipsTargetX: Boolean(targetBox && overflowX
          && (targetBox.left < scrollerBox.left - tolerance
            || targetBox.right > scrollerBox.right + tolerance)),
        clipsTargetY: Boolean(targetBox && overflowY
          && (targetBox.top < scrollerBox.top - tolerance
            || targetBox.bottom > scrollerBox.bottom + tolerance)) };
    };
    const validScroller = evidence => evidence.declared && evidence.real && evidence.focusable
      && evidence.axisMatches && evidence.reachedEnd;
    const scrollReachabilityFor = (node, box) => {
      const entries = [];
      for (let ancestor = node; ancestor && ancestor !== document.body;
        ancestor = ancestor.parentElement) {
        if (ancestor.dataset.lrScroller === 'true') entries.push(scrollerEvidence(ancestor, box));
      }
      const documentEvidence = documentScrollerEvidence(node, box);
      if (documentEvidence.real) entries.push(documentEvidence);
      return entries;
    };
    const scene = document.getElementById(target.domId);
    const selectorEntries = [...new Set(target.essentialSelectors || [])].map(selector => {
      try { return { selector, nodes: [...document.querySelectorAll(selector)].filter(rendered) }; }
      catch (error) { return { selector, nodes: [], error: error.message }; }
    });
    const unresolvedEssentialSelectors = selectorEntries.filter(entry => !entry.nodes.length)
      .map(entry => ({ selector: entry.selector, error: entry.error || null }));
    const essentialNodes = selectorEntries.flatMap(entry => entry.nodes.map(node =>
      ({ selector: entry.selector, node }))).filter((entry, itemIndex, items) =>
      items.findIndex(item => item.node === entry.node) === itemIndex);
    const essentialFailures = [];
    const essentialChecks = essentialNodes.map(entry => {
      const box = entry.node.getBoundingClientRect().toJSON();
      const visibility = visibilityEvidence(entry.node);
      const diagnosticFailures = [];
      if (!visibility.rendered) diagnosticFailures.push({ kind: 'not-effectively-visible' });
      if (!visibility.positiveArea) diagnosticFailures.push({ kind: 'zero-area' });
      if (!visibility.unoccluded) diagnosticFailures.push({ kind: 'occluded' });
      if (box.left < -tolerance || box.right > innerWidth + tolerance) {
        diagnosticFailures.push({ kind: 'horizontal-viewport', bounds: { left: 0, right: innerWidth } });
      }
      for (let ancestor = entry.node.parentElement; ancestor && ancestor !== document.body;
        ancestor = ancestor.parentElement) {
        const style = getComputedStyle(ancestor);
        const clipsX = ['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowX);
        const clipsY = ['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowY);
        if (!clipsX && !clipsY) continue;
        const ancestorRect = ancestor.getBoundingClientRect();
        const bounds = { left: ancestorRect.left + ancestor.clientLeft,
          top: ancestorRect.top + ancestor.clientTop,
          right: ancestorRect.left + ancestor.clientLeft + ancestor.clientWidth,
          bottom: ancestorRect.top + ancestor.clientTop + ancestor.clientHeight };
        const clippedX = clipsX && (box.left < bounds.left - tolerance
          || box.right > bounds.right + tolerance);
        const clippedY = clipsY && (box.top < bounds.top - tolerance
          || box.bottom > bounds.bottom + tolerance);
        if (clippedX || clippedY) diagnosticFailures.push({ kind: 'clipping-ancestor',
          ancestor: diagnostic(ancestor), axes: `${clippedX ? 'x' : ''}${clippedY ? 'y' : ''}`,
          bounds });
      }
      const scrollReachability = scrollReachabilityFor(entry.node, box);
      const canExposeX = scrollReachability.some(item => validScroller(item)
        && !item.documentScroller && item.overflowX && item.clipsTargetX);
      const canExposeNestedY = scrollReachability.some(item => validScroller(item)
        && !item.documentScroller && item.overflowY && item.clipsTargetY);
      const canExposeDocumentY = scrollReachability.some(item => validScroller(item)
        && item.documentScroller && item.targetReachable && item.clipsTargetY);
      const canExposeY = canExposeNestedY || canExposeDocumentY;
      const scrollReachable = canExposeX || canExposeY;
      const failures = diagnosticFailures.filter(failure => {
        if (failure.kind === 'occluded') return !scrollReachable;
        if (failure.kind === 'horizontal-viewport') return !canExposeX;
        if (failure.kind === 'clipping-ancestor') {
          return (failure.axes.includes('x') && !canExposeX)
            || (failure.axes.includes('y') && !canExposeNestedY);
        }
        return true;
      });
      const accessible = visibility.rendered && visibility.positiveArea
        && visibility.effectiveOpacity > 0.01 && (visibility.unoccluded || scrollReachable)
        && failures.length === 0;
      const result = { selector: entry.selector, label: diagnostic(entry.node), box,
        effectiveVisible: visibility.rendered, positiveArea: visibility.positiveArea,
        effectiveOpacity: visibility.effectiveOpacity, unoccluded: visibility.unoccluded,
        accessible, scrollReachable, scrollReachability,
        diagnosticFailures, failures };
      if (failures.length) essentialFailures.push(result);
      return result;
    });
    const activeStep = scene?.querySelector('.step.lr-stage-active:not([hidden])');
    const activeFigure = scene?.querySelector('.fig-stage.on:not([hidden])');
    const stageOverflowChecks = [activeStep, activeFigure].filter(Boolean).map(node => ({
      node, kind: node.classList.contains('fig-stage') ? 'figure' : 'step',
      scrollWidth: node.scrollWidth, clientWidth: node.clientWidth,
      scrollHeight: node.scrollHeight, clientHeight: node.clientHeight,
      overflowX: node.scrollWidth > node.clientWidth + tolerance,
      overflowY: node.scrollHeight > node.clientHeight + tolerance,
    })).map(item => {
      const scrollReachability = [item.node,
        ...item.node.querySelectorAll('[data-lr-scroller="true"]')]
        .filter(rendered).map(node => scrollerEvidence(node));
      const accessible = (!item.overflowX || scrollReachability.some(evidence =>
        validScroller(evidence) && evidence.overflowX))
        && (!item.overflowY || scrollReachability.some(evidence =>
          validScroller(evidence) && evidence.overflowY));
      return { kind: item.kind, scrollWidth: item.scrollWidth, clientWidth: item.clientWidth,
        scrollHeight: item.scrollHeight, clientHeight: item.clientHeight,
        overflowX: item.overflowX, overflowY: item.overflowY,
        overflow: item.overflowX || item.overflowY, accessible, scrollReachability };
    });
    const stageOverflow = stageOverflowChecks.some(item => item.overflow);
    const stageOverflowAccessible = stageOverflowChecks.every(item => item.accessible);
    const visibleNodes = scene ? [scene, ...scene.querySelectorAll('*')].filter(rendered) : [];
    const actualScrollers = visibleNodes.filter(node => {
      const style = getComputedStyle(node);
      return (['auto', 'scroll'].includes(style.overflowX)
          && node.scrollWidth > node.clientWidth + tolerance)
        || (['auto', 'scroll'].includes(style.overflowY)
          && node.scrollHeight > node.clientHeight + tolerance);
    });
    const scrollerChecks = visibleNodes.filter(node => node.dataset.lrScroller === 'true').map(node => {
      const style = getComputedStyle(node);
      const overflowX = ['auto', 'scroll'].includes(style.overflowX)
        && node.scrollWidth > node.clientWidth + tolerance;
      const overflowY = ['auto', 'scroll'].includes(style.overflowY)
        && node.scrollHeight > node.clientHeight + tolerance;
      const axis = overflowX && overflowY ? 'both' : (overflowX ? 'horizontal' : (overflowY ? 'vertical' : ''));
      const before = { left: node.scrollLeft, top: node.scrollTop };
      if (overflowX) node.scrollLeft = node.scrollWidth;
      if (overflowY) node.scrollTop = node.scrollHeight;
      const reachedEnd = (!overflowX || node.scrollLeft >= node.scrollWidth - node.clientWidth - tolerance)
        && (!overflowY || node.scrollTop >= node.scrollHeight - node.clientHeight - tolerance);
      node.scrollLeft = before.left; node.scrollTop = before.top;
      return { selector: diagnostic(node), declaredAxis: node.dataset.lrScrollerAxis || '',
        overflowX, overflowY, real: overflowX || overflowY, focusable: node.tabIndex >= 0,
        axisMatches: node.dataset.lrScrollerAxis === axis, reachedEnd };
    });
    const undeclaredScrollers = actualScrollers.filter(node => node.dataset.lrScroller !== 'true')
      .map(diagnostic);
    const hiddenFocusable = [...document.querySelectorAll('a[href],button,input,select,textarea,'
      + '[tabindex]:not([tabindex="-1"])')].filter(node => node.closest('[aria-hidden="true"]')
        && !node.closest('[hidden],[inert]') && node.tabIndex >= 0).map(diagnostic);
    const badgeRoute = scene?.querySelector('.lr-scene-badge .lr-route-label')?.textContent.trim() || null;
    const badgeDuration = scene?.querySelector('.lr-scene-badge .lr-duration')?.textContent.trim() || null;
    const mobileText = document.querySelector('#lr-mobile-toolbar > span')?.textContent.trim() || null;
    const mobileVisible = rendered(document.querySelector('#lr-mobile-toolbar'));
    const liveText = document.querySelector('body > .lr-sr-only[aria-live="polite"]')
      ?.textContent.trim() || null;
    const expectedLive = `${target.scene}, ruta ${target.stageRoute}, ${target.durationMinutes} minutos, `
      + `etapa ${target.stagePosition} de ${target.stageTotal}`;
    const runtimeState = window.LEARNING_RUNTIME?.getState?.();
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime; }
    catch (_error) { saved = null; }
    const progressConsistent = Boolean(runtimeState?.progress && saved?.progress)
      && ['LIVE', 'REQUIRED', 'OPTIONAL'].every(route => {
        const current = runtimeState.progress[route], stored = saved.progress[route];
        return current && stored && current.total === stored.total && current.visited === stored.visited
          && current.percent === stored.percent && current.complete === stored.complete;
      });
    const sceneBox = scene?.getBoundingClientRect().toJSON() || null;
    const sceneVisibility = visibilityEvidence(scene);
    const targetMatches = runtimeState?.scene === target.scene && runtimeState?.stage === target.stage
      && runtimeState?.route === target.stageRoute && runtimeState?.sceneRoute === target.sceneRoute
      && document.body.dataset.currentSceneId === target.scene
      && document.body.dataset.currentStageId === target.stage;
    const essentialInside = essentialNodes.length > 0
      && essentialChecks.every(item => item.diagnosticFailures.length === 0)
      && unresolvedEssentialSelectors.length === 0;
    const essentialAccessible = essentialNodes.length > 0 && essentialFailures.length === 0
      && unresolvedEssentialSelectors.length === 0;
    const scrollAuditPassed = undeclaredScrollers.length === 0 && scrollerChecks.every(item =>
      item.real && item.focusable && item.axisMatches && item.reachedEnd);
    const routePresentationMatches = badgeRoute === target.stageRoute
      && badgeDuration === `${target.durationMinutes} min`
      && (!mobileVisible || (mobileText.includes(`· ${target.stageRoute} ·`)
        && mobileText.includes(`· ${target.durationMinutes} min ·`)));
    return { scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
      sceneRoute: runtimeState?.sceneRoute || null,
      stageRoute: document.body.dataset.currentStageRoute,
      scope: document.body.dataset.routeScope,
      expected: target, position: index + 1, total: count,
      evidenceSchema: 'desktop-flow-state/v3',
      viewport: { width: innerWidth, height: innerHeight },
      activeSceneCount: document.querySelectorAll('body > .lr-scene-active').length,
      targetMatches, rendered: rendered(scene),
      sceneVisibility, sceneBox,
      sceneHorizontalInside: Boolean(sceneBox && sceneBox.left >= -tolerance
        && sceneBox.right <= innerWidth + tolerance),
      horizontalOverflow: document.documentElement.scrollWidth
        > document.documentElement.clientWidth + tolerance,
      essentialCount: essentialNodes.length, essentialInside, essentialAccessible, essentialChecks,
      essentialFailures, unresolvedEssentialSelectors, stageOverflow, stageOverflowAccessible,
      stageOverflowChecks,
      scrollAuditPassed, scrollerChecks, undeclaredScrollers, hiddenFocusable,
      routePresentation: { badgeRoute, badgeDuration, mobileText, mobileVisible },
      routePresentationMatches, liveRegion: { text: liveText, expected: expectedLive },
      liveRegionMatches: liveText === expectedLive, progressConsistent, runtimeState,
      savedRuntimeState: saved,
      passed: targetMatches && rendered(scene) && sceneVisibility.unoccluded && Boolean(sceneBox)
        && sceneBox.left >= -tolerance && sceneBox.right <= innerWidth + tolerance
        && document.documentElement.scrollWidth <= document.documentElement.clientWidth + tolerance
        && essentialAccessible && stageOverflowAccessible && scrollAuditPassed
        && hiddenFocusable.length === 0
        && routePresentationMatches && liveText === expectedLive && progressConsistent };
  }, { target: expected, index: position, count: total });
}

async function flowStatesAudit(page, scopeRoutes, targetRoutes = scopeRoutes) {
  const declared = await expectedStates(page, scopeRoutes);
  const expected = declared.filter(state => targetRoutes.includes(state.stageRoute));
  const states = [];
  for (let index = 0; index < expected.length; index++) {
    const target = expected[index];
    const navigated = await page.evaluate(state =>
      window.LEARNING_RUNTIME?.goTo(state.scene, state.stage) === true, target);
    await page.waitForFunction(state => document.body.dataset.currentSceneId === state.scene
      && document.body.dataset.currentStageId === state.stage, target);
    const state = await inspectFlowState(page, target, index, expected.length);
    states.push({ ...state, navigated });
  }
  return { scopeRoutes, targetRoutes, expected: expected.length, visited: states.length, states,
    passed: expected.length > 0 && states.length === expected.length
      && states.every(state => state.navigated && state.passed) };
}

async function observerStateAudit(page) {
  const target = await page.evaluate(() => {
    const contract = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
    const candidates = contract.scenes.flatMap(scene => {
      const stages = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
      return stages.map(stage => ({ scene, stage, route: stage.route || scene.route }));
    }).filter(item => item.route !== 'OPTIONAL' && item.stage.dom_stage !== undefined)
      .map(item => {
        const sceneNode = document.getElementById(item.scene.dom_id);
        const step = [...(sceneNode?.querySelectorAll('.step') || [])]
          .find(node => node.dataset.stage === String(item.stage.dom_stage));
        return { ...item, step };
      }).filter(item => item.step && !item.step.hidden && item.step.getClientRects().length);
    const currentScene = document.body.dataset.currentSceneId;
    const currentStage = document.body.dataset.currentStageId;
    const selected = [...candidates].reverse().find(item =>
      item.scene.id !== currentScene || item.stage.id !== currentStage) || candidates[0];
    if (!selected) return null;
    selected.step.scrollIntoView({ block: 'center', behavior: 'auto' });
    return { scene: selected.scene.id, stage: selected.stage.id, route: selected.route };
  });
  if (!target) return { target: null, passed: false, reason: 'no visible official step target' };
  await page.waitForFunction(expected => document.body.dataset.currentSceneId === expected.scene
    && document.body.dataset.currentStageId === expected.stage, target);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));
  const state = await page.evaluate(visibleStateAudit);
  const persisted = await page.evaluate(expected => {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime; }
    catch (_error) { saved = null; }
    const [rawScene, rawStage] = location.hash.slice(1).split('/');
    let hashScene = rawScene, hashStage = rawStage;
    try { hashScene = decodeURIComponent(rawScene || ''); hashStage = decodeURIComponent(rawStage || ''); }
    catch (_error) { /* malformed hashes fail by comparison below */ }
    return { hashMatches: hashScene === expected.scene && hashStage === expected.stage,
      storageMatches: saved?.scene === expected.scene && saved?.stage === expected.stage
        && saved?.routeScope === document.body.dataset.routeScope };
  }, target);
  return { target, state, ...persisted,
    passed: state.getStateConsistent && state.runtimeState?.scene === target.scene
      && state.runtimeState?.stage === target.stage && state.runtimeState?.route === target.route
      && persisted.hashMatches && persisted.storageMatches };
}

async function studyAudit(browser, item) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const pageFailures = collectPageFailures(page);
  await page.goto(fileUrl(item.relative, '?mode=estudio'));
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const initial = await page.evaluate(visibleStateAudit);
  const observerSync = await observerStateAudit(page);
  const officialFlow = await flowStatesAudit(page, ['LIVE', 'REQUIRED']);
  const toggle = page.locator('#lr-nav .lr-study-optional');
  const toggleVisible = initial.optionalCount === 0 ? await toggle.isHidden() : await toggle.isVisible();
  let optedIn = { optionalAvailable: 0, routeScope: initial.routeScope };
  let optedOut = initial;
  let explicitOptIn = { applicable: false, state: null };
  let optionalFlow = { scopeRoutes: ['LIVE', 'REQUIRED', 'OPTIONAL'],
    targetRoutes: ['OPTIONAL'], expected: 0, visited: 0, states: [], passed: true };
  if (initial.optionalCount) {
    await toggle.click();
    optedIn = await page.evaluate(visibleStateAudit);
    optionalFlow = await flowStatesAudit(page, ['LIVE', 'REQUIRED', 'OPTIONAL'], ['OPTIONAL']);
    await toggle.click();
    optedOut = await page.evaluate(visibleStateAudit);
    await page.goto(fileUrl(item.relative, '?mode=estudio&optional=1'));
    await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
    const explicit = await page.evaluate(visibleStateAudit);
    explicitOptIn = { applicable: true, state: explicit };
  }
  const motion = await page.evaluate(() => {
    const probe = document.querySelector('.lr-scene .step-inner') || document.querySelector('.lr-scene *');
    return { reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
      transition: probe ? getComputedStyle(probe).transitionDuration : '0s' };
  });
  const passed = initial.officialAvailable && initial.optionalAvailable === 0
    && initial.routeScope === 'LIVE+REQUIRED' && initial.vertical && !initial.horizontalOverflow
    && initial.progressReady && initial.progressTotalsMatch && initial.getStateConsistent
    && observerSync.passed && officialFlow.passed && optionalFlow.passed
    && toggleVisible && motion.reduced
    && motion.transition.split(',').every(value => parseFloat(value) === 0)
    && (!initial.optionalCount || (optedIn.optionalAvailable === initial.optionalCount
      && optedIn.routeScope === 'ALL' && optedOut.optionalAvailable === 0
      && optedOut.routeScope === 'LIVE+REQUIRED' && optedIn.getStateConsistent
      && optedOut.getStateConsistent && explicitOptIn.state.routeScope === 'ALL'
      && explicitOptIn.state.optionalAvailable === explicitOptIn.state.optionalCount
      && explicitOptIn.state.getStateConsistent));
  const record = { lesson: item.lesson, viewport: '1440x900', mode: 'estudio', initial, observerSync,
    officialFlow, optionalFlow, optedIn, optedOut, explicitOptIn, toggleVisible, motion, passed };
  await finalizePageRecord(record, [item.lesson, '1440x900', 'estudio'],
    { page, failures: pageFailures });
  await context.close();
  return record;
}

async function mobileAudit(browser, item) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const pageFailures = collectPageFailures(page);
  await page.goto(fileUrl(item.relative, '?mode=aula&profe=1'));
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'estudio');
  const availability = await page.evaluate(visibleStateAudit);
  const observerSync = await observerStateAudit(page);
  const officialFlow = await flowStatesAudit(page, ['LIVE', 'REQUIRED']);
  const mobileState = await page.evaluate(() => ({
    requestedMode: document.body.dataset.requestedMode,
    effectiveMode: document.body.dataset.learningMode,
    marked: document.body.classList.contains('lr-mobile-fallback'),
    navHidden: getComputedStyle(document.querySelector('#lr-nav')).display === 'none',
    toolbarVisible: getComputedStyle(document.querySelector('#lr-mobile-toolbar')).display !== 'none',
    toolbarHeight: document.querySelector('#lr-mobile-toolbar').getBoundingClientRect().height,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  }));
  const initial = { ...availability, ...mobileState };
  const toggle = page.locator('#lr-mobile-toolbar .lr-study-optional');
  const toggleCorrect = initial.optionalCount === 0 ? await toggle.isHidden() : await toggle.isVisible();
  let optionalOptIn = { applicable: false, state: null };
  let optionalFlow = { scopeRoutes: ['LIVE', 'REQUIRED', 'OPTIONAL'],
    targetRoutes: ['OPTIONAL'], expected: 0, visited: 0, states: [], passed: true };
  if (initial.optionalCount) {
    await toggle.click();
    const enabled = await page.evaluate(visibleStateAudit);
    optionalOptIn = { applicable: true, state: enabled };
    optionalFlow = await flowStatesAudit(page, ['LIVE', 'REQUIRED', 'OPTIONAL'], ['OPTIONAL']);
  }
  const mobileDrawer = await drawerKeyboardAudit(
    page, '#lr-mobile-toolbar .lr-mobile-teacher', '#lr-teacher-drawer');
  const passed = initial.requestedMode === 'aula' && initial.effectiveMode === 'estudio' && initial.marked
    && initial.navHidden && initial.toolbarVisible && initial.toolbarHeight >= 44
    && initial.vertical && !initial.horizontalOverflow && initial.reducedMotion
    && initial.officialAvailable && initial.optionalAvailable === 0
    && initial.getStateConsistent && initial.progressTotalsMatch
    && observerSync.passed && officialFlow.passed && optionalFlow.passed && toggleCorrect
    && (!initial.optionalCount || (optionalOptIn.state.optionalAvailable === initial.optionalCount
      && optionalOptIn.state.routeScope === 'ALL' && optionalOptIn.state.getStateConsistent))
    && mobileDrawer.passed;
  const record = { lesson: item.lesson, viewport: '390x844',
    ...initial, mode: 'mobile-fallback', runtimeMode: initial.effectiveMode,
    observerSync, officialFlow, optionalFlow, toggleCorrect, optionalOptIn, mobileDrawer, passed };
  await finalizePageRecord(record, [item.lesson, '390x844', 'mobile-fallback'],
    { page, failures: pageFailures });
  await context.close();
  return record;
}

function declaredStates(item) {
  return contractFor(item.number).scenes.flatMap(scene => {
    const stages = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
    return stages.map(stage => ({ lesson: item.lesson, scene: scene.id, stage: stage.id,
      sceneRoute: scene.route, stageRoute: stage.route || scene.route,
      durationMinutes: stage.duration_minutes ?? scene.duration_minutes,
      override: Boolean(stage.route && stage.route !== scene.route) }));
  });
}

async function currentStateSnapshot(page, expected) {
  return page.evaluate(target => {
    const state = window.LEARNING_RUNTIME?.getState?.();
    const currentSceneId = document.body.dataset.currentSceneId;
    const active = document.querySelector('body > .lr-scene-active')
      || document.querySelector(`body > .lr-scene[data-scene-id="${CSS.escape(currentSceneId || '')}"]`);
    const badge = active?.querySelector('.lr-scene-badge .lr-route-label');
    const badgeDuration = active?.querySelector('.lr-scene-badge .lr-duration');
    const nav = document.querySelector('#lr-nav .lr-scene-links button.on .lr-route-label');
    const mobile = document.querySelector('#lr-mobile-toolbar > span');
    const visibilityEvidence = node => {
      if (!node) return { rendered: false, positiveArea: false, effectiveOpacity: 0,
        unoccluded: false };
      let effectiveOpacity = 1;
      let structurallyVisible = !node.hidden && !node.closest('[hidden],[inert]');
      for (let currentNode = node; currentNode && currentNode.nodeType === 1;
        currentNode = currentNode.parentElement) {
        const style = getComputedStyle(currentNode);
        effectiveOpacity *= Number.parseFloat(style.opacity || '1');
        if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
            || style.contentVisibility === 'hidden') structurallyVisible = false;
      }
      const box = node.getBoundingClientRect();
      const positiveArea = box.width > 0.5 && box.height > 0.5;
      const points = positiveArea ? [[box.left + box.width / 2, box.top + box.height / 2],
        [box.left + Math.min(2, box.width / 2), box.top + Math.min(2, box.height / 2)],
        [box.right - Math.min(2, box.width / 2), box.bottom - Math.min(2, box.height / 2)]]
        .filter(([x, y]) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight) : [];
      const unoccluded = points.some(([x, y]) => {
        const hit = document.elementFromPoint(x, y);
        return Boolean(hit && (hit === node || node.contains(hit)));
      });
      return { rendered: Boolean(structurallyVisible && effectiveOpacity > 0.01
          && node.getClientRects().length), positiveArea, effectiveOpacity, unoccluded };
    };
    const rendered = node => {
      const evidence = visibilityEvidence(node);
      return evidence.rendered && evidence.positiveArea && evidence.unoccluded;
    };
    return {
      scene: document.body.dataset.currentSceneId,
      stage: document.body.dataset.currentStageId,
      route: document.body.dataset.currentStageRoute,
      sceneRoute: active?.dataset.sceneRoute,
      scope: document.body.dataset.routeScope,
      runtimeState: state,
      getStateConsistent: Boolean(state)
        && state.mode === document.body.dataset.learningMode
        && state.requestedMode === document.body.dataset.requestedMode
        && state.routeScope === document.body.dataset.routeScope
        && state.scene === document.body.dataset.currentSceneId
        && state.stage === document.body.dataset.currentStageId
        && state.route === document.body.dataset.currentStageRoute
        && state.sceneRoute === active?.dataset.sceneRoute,
      targetMatches: document.body.dataset.currentSceneId === target.scene
        && document.body.dataset.currentStageId === target.stage
        && document.body.dataset.currentStageRoute === target.stageRoute,
      presentation: {
        badge: badge?.textContent.trim() || null,
        badgeDuration: badgeDuration?.textContent.trim() || null,
        badgeVisible: rendered(badge),
        badgeVisibility: visibilityEvidence(badge),
        nav: nav?.textContent.trim() || null,
        navVisible: rendered(nav),
        navVisibility: visibilityEvidence(nav),
        mobile: mobile?.textContent.trim() || null,
        mobileVisible: rendered(mobile),
        mobileVisibility: visibilityEvidence(mobile),
      },
    };
  }, expected);
}

async function persistenceIsolationAudit(browser, item) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const pageFailures = collectPageFailures(page);
  const states = declaredStates(item).filter(state => state.stageRoute === 'LIVE');
  const hashTarget = states[Math.min(1, states.length - 1)];
  const storageTarget = states[Math.max(0, states.length - 1)];
  const canonical = fileUrl(item.relative, '?mode=aula&profe=1');
  await page.goto(canonical);
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'aula');
  await page.evaluate(() => localStorage.clear());
  const storageInitiallyEmpty = await page.evaluate(() => localStorage.length === 0);
  const requestedHash = `#${encodeURIComponent(hashTarget.scene)}/${encodeURIComponent(hashTarget.stage)}`;
  const hashUrl = `${canonical}${requestedHash}`;
  await page.goto(hashUrl);
  await page.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
    && document.body.dataset.currentStageId === target.stage, hashTarget);
  const hashOnlyState = await currentStateSnapshot(page, hashTarget);
  const observedHash = await page.evaluate(() => location.hash);
  const hashOnly = { target: hashTarget, storageInitiallyEmpty, requestedHash, observedHash,
    state: hashOnlyState,
    passed: storageInitiallyEmpty && requestedHash === observedHash
      && hashOnlyState.targetMatches && hashOnlyState.getStateConsistent };

  await page.goto(canonical);
  await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'aula');
  const seededStorageTarget = await page.evaluate(target => {
    history.replaceState(null, '', location.pathname + location.search);
    localStorage.clear();
    localStorage.setItem(DOC.key(), JSON.stringify({ runtime: { version: 2, routeScope: 'LIVE',
      scene: target.scene, stage: target.stage, visited: [], progress: {} } }));
    const saved = JSON.parse(localStorage.getItem(DOC.key()) || '{}').runtime;
    return { scene: saved?.scene || null, stage: saved?.stage || null };
  }, storageTarget);
  const hashCleared = await page.evaluate(() => location.hash === '');
  await page.reload();
  await page.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
    && document.body.dataset.currentStageId === target.stage, storageTarget);
  const storageOnlyState = await currentStateSnapshot(page, storageTarget);
  const storageOnly = { target: storageTarget, requestedWithoutHash: !canonical.includes('#'),
    hashCleared, seededStorageTarget, state: storageOnlyState,
    passed: hashCleared && seededStorageTarget.scene === storageTarget.scene
      && seededStorageTarget.stage === storageTarget.stage
      && storageOnlyState.targetMatches && storageOnlyState.getStateConsistent };
  const record = { lesson: item.lesson, viewport: '1440x900', mode: 'persistence-isolation',
    hashOnly, storageOnly, passed: hashOnly.passed && storageOnly.passed };
  await finalizePageRecord(record, [item.lesson, '1440x900', 'persistence-isolation'],
    { page, failures: pageFailures });
  await context.close();
  return record;
}

async function freshProfessorDeepLinksAudit(browser) {
  const targets = {};
  for (const routeName of ['REQUIRED', 'OPTIONAL']) {
    for (const item of LESSONS) {
      const target = declaredStates(item).find(state => state.stageRoute === routeName);
      if (target) { targets[routeName] = { item, target }; break; }
    }
  }
  const records = [];
  for (const routeName of ['REQUIRED', 'OPTIONAL']) {
    const selected = targets[routeName];
    if (!selected) {
      records.push({ route: routeName, passed: false, reason: 'no declared target' });
      continue;
    }
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    await context.addInitScript(() => {
      try {
        sessionStorage.setItem('__lr_fresh_storage_state',
          localStorage.length === 0 ? 'empty' : 'nonempty');
      } catch (_error) { /* about:blank has an opaque origin */ }
    });
    const page = await context.newPage();
    const pageFailures = collectPageFailures(page);
    const { item, target } = selected;
    const requestedHash = `#${encodeURIComponent(target.scene)}/${encodeURIComponent(target.stage)}`;
    const url = fileUrl(item.relative, `?mode=aula&profe=1${requestedHash}`);
    await page.goto(url);
    await page.waitForFunction(expected => document.body.dataset.currentSceneId === expected.scene
      && document.body.dataset.currentStageId === expected.stage, target);
    const state = await currentStateSnapshot(page, target);
    const launchEvidence = await page.evaluate(() => ({
      storageInitiallyEmpty: sessionStorage.getItem('__lr_fresh_storage_state') === 'empty',
      observedHash: location.hash,
    }));
    const expectedScope = routeName === 'OPTIONAL' ? 'ALL' : 'LIVE+REQUIRED';
    const record = { route: routeName, lesson: item.lesson, target, expectedScope,
      requestedHash, ...launchEvidence, state,
      freshContext: true, passed: state.targetMatches && state.scope === expectedScope
        && state.getStateConsistent && launchEvidence.storageInitiallyEmpty
        && launchEvidence.observedHash === requestedHash };
    await finalizePageRecord(record,
      ['course', '1440x900', 'fresh-professor-deep-links', routeName],
      { page, failures: pageFailures });
    records.push(record);
    await context.close();
  }
  const result = { lesson: 'course', viewport: '1440x900', mode: 'fresh-professor-deep-links',
    records, passed: records.length === 2 && records.every(record => record.passed) };
  const failureScreenshots = records.filter(record => !record.passed)
    .map(record => record.failureScreenshot).filter(Boolean);
  if (failureScreenshots.length) {
    result.failureScreenshot = failureScreenshots[0];
    result.failureScreenshots = failureScreenshots;
  }
  return result;
}

async function routeOverrideAudit(browser) {
  const overrides = LESSONS.flatMap(item => declaredStates(item).filter(state => state.override)
    .map(state => ({ item, state })));
  const records = [];
  for (const item of LESSONS) {
    const lessonOverrides = overrides.filter(entry => entry.item === item);
    if (!lessonOverrides.length) continue;
    const desktopContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 },
      isMobile: true, hasTouch: true });
    const desktopPage = await desktopContext.newPage();
    const mobilePage = await mobileContext.newPage();
    const desktopFailures = collectPageFailures(desktopPage);
    const mobileFailures = collectPageFailures(mobilePage);
    for (const entry of lessonOverrides) {
      desktopFailures.reset();
      mobileFailures.reset();
      const { state } = entry;
      const suffix = `?mode=aula&profe=1#${encodeURIComponent(state.scene)}/${encodeURIComponent(state.stage)}`;
      await desktopPage.goto(fileUrl(item.relative, suffix));
      await desktopPage.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
        && document.body.dataset.currentStageId === target.stage, state);
      const desktop = await currentStateSnapshot(desktopPage, state);
      await desktopPage.locator('#lr-teacher-toggle').click();
      const teacher = await desktopPage.locator('#lr-teacher-drawer').evaluate((node, target) => {
        const kicker = node.querySelector('.lr-teacher-kicker')?.textContent.trim() || null;
        const override = node.querySelector('.lr-teacher-override')?.textContent.trim() || null;
        let effectiveOpacity = 1;
        let structurallyVisible = !node.hidden && node.getAttribute('aria-hidden') === 'false';
        for (let currentNode = node; currentNode && currentNode.nodeType === 1;
          currentNode = currentNode.parentElement) {
          const style = getComputedStyle(currentNode);
          effectiveOpacity *= Number.parseFloat(style.opacity || '1');
          if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)) {
            structurallyVisible = false;
          }
        }
        const box = node.getBoundingClientRect();
        const positiveArea = box.width > 0.5 && box.height > 0.5;
        const hit = positiveArea ? document.elementFromPoint(
          box.left + box.width / 2, box.top + box.height / 2) : null;
        const visibility = { effectiveOpacity, positiveArea,
          unoccluded: Boolean(hit && (hit === node || node.contains(hit))) };
        return {
          visible: structurallyVisible && effectiveOpacity > 0.01 && positiveArea
            && visibility.unoccluded,
          visibility,
          kicker,
          override,
          routeVisible: kicker?.startsWith(`${target.routeName} ·`) || false,
          overrideVisible: override?.includes(`Ruta efectiva ${target.routeName}`) || false,
          durationVisible: kicker?.includes(`· ${target.durationMinutes} min`) || false,
        };
      }, { routeName: state.stageRoute, durationMinutes: state.durationMinutes });
      await desktopPage.keyboard.press('Escape');

      await mobilePage.goto(fileUrl(item.relative, suffix));
      await mobilePage.waitForFunction(target => document.body.dataset.currentSceneId === target.scene
        && document.body.dataset.currentStageId === target.stage, state);
      const mobile = await currentStateSnapshot(mobilePage, state);
      const desktopVisible = desktop.presentation.badgeVisible && desktop.presentation.navVisible
        && desktop.presentation.badge === state.stageRoute && desktop.presentation.nav === state.stageRoute
        && desktop.presentation.badgeDuration === `${state.durationMinutes} min`;
      const mobileVisible = mobile.presentation.mobileVisible
        && mobile.presentation.mobile.includes(`· ${state.stageRoute} · ${state.durationMinutes} min ·`);
      const record = { lesson: item.lesson, scene: state.scene, stage: state.stage,
        sceneRoute: state.sceneRoute, effectiveRoute: state.stageRoute,
        durationMinutes: state.durationMinutes,
        desktop, teacher, mobile,
        passed: desktop.targetMatches && desktop.getStateConsistent && desktopVisible
          && teacher.visible && teacher.routeVisible && teacher.overrideVisible && teacher.durationVisible
          && mobile.targetMatches && mobile.getStateConsistent && mobileVisible };
      await finalizePageRecord(record,
        ['course', 'route-overrides', item.lesson, state.scene, state.stage], [
          { page: desktopPage, failures: desktopFailures, label: 'desktop' },
          { page: mobilePage, failures: mobileFailures, label: 'mobile' },
        ]);
      records.push(record);
    }
    await desktopContext.close();
    await mobileContext.close();
  }
  const result = { lesson: 'course', viewport: 'desktop+mobile', mode: 'route-overrides',
    expected: 14, declared: overrides.length, visible: records.filter(record => record.passed).length,
    records, passed: overrides.length === 14 && records.length === 14
      && records.every(record => record.passed) };
  const failureScreenshots = records.filter(record => !record.passed)
    .flatMap(record => record.failureScreenshots || [record.failureScreenshot]).filter(Boolean);
  if (failureScreenshots.length) {
    result.failureScreenshot = failureScreenshots[0];
    result.failureScreenshots = failureScreenshots;
  }
  return result;
}

function chooseVisualSamples() {
  return evidenceContract.visualSampleTargets(LESSONS).map(target => {
    const item = LESSONS.find(candidate => candidate.lesson === target.lesson);
    const scene = item?.contract.scenes.find(candidate => candidate.id === target.scene);
    return { name: target.name, selected: item && scene ? { item, scene } : null };
  });
}

async function visualAudit(browser) {
  const viewport = { width: 1440, height: 900 };
  const context = await browser.newContext({ viewport, reducedMotion: 'reduce' });
  await context.addInitScript(evidenceContract.VISUAL_AUDIT_INIT_SCRIPT);
  const page = await context.newPage();
  const pageFailures = collectPageFailures(page);
  const records = [];
  for (const sample of chooseVisualSamples()) {
    pageFailures.reset();
    if (!sample.selected) {
      const record = { sample: sample.name, passed: false, reason: 'no matching declared scene' };
      await finalizePageRecord(record, ['course', '1440x900', 'visual-sample', sample.name],
        { page, failures: pageFailures });
      records.push(record);
      continue;
    }
    const { item, scene } = sample.selected;
    const stage = (scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }])[0];
    const effectiveRoute = stage.route || scene.route;
    await prepare(page, item.relative, '?mode=aula&profe=1');
    if (effectiveRoute !== 'LIVE') {
      await page.locator('#lr-controls .lr-route-scope').click();
      if (effectiveRoute === 'OPTIONAL') {
        await page.locator('#lr-controls .lr-route-scope').click();
      }
    }
    await page.evaluate(({ sceneId, stageId }) => window.LEARNING_RUNTIME.goTo(sceneId, stageId),
      { sceneId: scene.id, stageId: stage.id });
    const expected = await expectedStates(page,
      effectiveRoute === 'OPTIONAL'
        ? ['LIVE', 'REQUIRED', 'OPTIONAL']
        : (effectiveRoute === 'REQUIRED' ? ['LIVE', 'REQUIRED'] : ['LIVE']));
    const index = expected.findIndex(state => state.scene === scene.id && state.stage === stage.id);
    const state = index >= 0 ? await inspectState(page, expected[index], index, expected.length) : null;
    const determinism = await page.evaluate(() => ({
      auditMode: window.__DESKTOP_VISUAL_AUDIT__ || null,
      reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
      randomProbe: [Math.random(), Math.random()],
    }));
    let screenshot = null;
    if (AUDIT && state) {
      screenshot = `visual-${sample.name}-${item.lesson.toLowerCase()}-${slug(scene.id)}.png`;
      await page.screenshot({ path: path.join(AUDIT, screenshot),
        animations: 'disabled', caret: 'hide' });
    }
    const record = { sample: sample.name, lesson: item.lesson, scene: scene.id,
      stage: stage.id, screenshot, geometry: state, determinism,
      passed: Boolean(state?.passed) && determinism.auditMode === 'visual-v1'
        && determinism.reducedMotion && determinism.randomProbe.every(value => value === 0.5) };
    await finalizePageRecord(record, [item.lesson, '1440x900', 'visual-sample', sample.name],
      { page, failures: pageFailures });
    records.push(record);
  }
  await context.close();
  return records;
}

async function indexAudit(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const pageFailures = collectPageFailures(page);
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
  const record = { lesson: 'course-map', viewport: '1440x900', mode: 'index', ...result };
  await finalizePageRecord(record, ['course-map', '1440x900', 'index'],
    { page, failures: pageFailures });
  await page.close();
  return record;
}

async function examAudit(browser) {
  const viewports = [...VIEWPORTS, { width: 390, height: 844 }];
  const records = [];
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport });
    const pageFailures = collectPageFailures(page);
    await page.goto(fileUrl('15-final-exam/examen.html', '?mode=aula'));
    const result = await page.evaluate(() => ({
      linear: document.body.dataset.delivery === 'assessment-linear',
      noSceneRuntime: !document.querySelector('#lr-nav') && !window.LEARNING_RUNTIME,
      questions: document.querySelectorAll('.q').length,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
    }));
    result.passed = result.linear && result.noSceneRuntime && result.questions === 40
      && !result.horizontalOverflow;
    const record = { lesson: 'L15', viewport: viewportName(viewport), mode: 'assessment-linear',
      ...result };
    await finalizePageRecord(record, ['L15', viewportName(viewport), 'assessment-linear'],
      { page, failures: pageFailures });
    records.push(record);
    await page.close();
  }
  return records;
}

(async () => {
  const startedAt = new Date().toISOString();
  let source_sha = null;
  let inputs = null;
  let plan = null;
  let phase = 'cli';
  let activeCheck = 'bootstrap';
  let browser = null;
  let browserEvidence = null;
  let browserValidation = null;
  const results = [];
  try {
  AUDIT = parseAuditDirectory(process.argv);
  phase = 'audit-directory';
  resetAuditDirectory();
  phase = 'source-sha';
  source_sha = evidenceContract.sourceHead(ROOT);
  phase = 'lesson-discovery';
  LESSONS = evidenceContract.discoverLessons(ROOT);
  plan = evidenceContract.buildExpectedAuditPlan(ROOT);
  phase = 'input-evidence';
  inputs = evidenceContract.inputEvidence(ROOT);
  phase = 'playwright-load';
  ({ chromium } = require('playwright'));
  phase = 'browser-launch';
  const browserExecutable = fs.realpathSync.native(chromium.executablePath());
  const lockedBrowser = evidenceContract.lockedBrowserIdentity(ROOT, browserExecutable);
  browser = await chromium.launch({ headless: true, executablePath: browserExecutable });
  browserEvidence = { ...lockedBrowser, name: browser.browserType().name(),
    version: browser.version(), playwright: require('playwright/package.json').version };
  browserValidation = evidenceContract.validateBrowserIdentity(
    browserEvidence, lockedBrowser, browserEvidence);
  if (!browserValidation.passed) {
    throw new Error(`launched browser does not match lock: ${JSON.stringify(browserValidation)}`);
  }

  phase = 'browser-matrix';
  activeCheck = 'negative-fixture';
  const fixture = await overflowFixture(browser);
  results.push(fixture);
  console.log(`${fixture.passed ? '✓' : '✗'} nested essential clipping fixture`);

  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    for (const item of LESSONS) {
      activeCheck = `${item.lesson}:${viewportName(viewport)}:aula`;
      const page = await context.newPage();
      const pageFailures = collectPageFailures(page);
      pageFailures.reset();
      await prepare(page, item.relative, '?mode=aula');
      const live = await traverse(page, item.lesson, viewport, 'LIVE', ['LIVE'], pageFailures);
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
      await finalizePageRecord(record,
        [item.lesson, viewportName(viewport), 'aula', live.scope],
        { page, failures: pageFailures });
      results.push(record);
      console.log(`${record.passed ? '✓' : '✗'} ${item.lesson} ${record.viewport} LIVE `
        + `states=${record.visited}/${record.expected}`);

      if (viewport.width === 1440) {
        pageFailures.reset();
        await prepare(page, item.relative, '?mode=aula&profe=1');
        await page.locator('#lr-controls .lr-route-scope').click();
        const scopeText = (await page.locator('#lr-controls .lr-route-scope').textContent()).trim();
        const combined = await traverse(page, item.lesson, viewport,
          'LIVE+REQUIRED', ['LIVE', 'REQUIRED'], pageFailures);
        const professor = await testNavigationAndPersistence(page, true);
        combined.scopeControl = scopeText === 'LIVE+REQUIRED';
        combined.professor = professor;
        combined.passed = combined.passed && combined.scopeControl
          && Object.values(professor).every(Boolean);
        const combinedRecord = { lesson: item.lesson, viewport: '1440x900',
          mode: 'aula-profesor', ...combined };
        await finalizePageRecord(combinedRecord,
          [item.lesson, '1440x900', 'aula-profesor', combined.scope],
          { page, failures: pageFailures });
        results.push(combinedRecord);
        console.log(`${combinedRecord.passed ? '✓' : '✗'} ${item.lesson} 1440x900 LIVE+REQUIRED `
          + `states=${combinedRecord.visited}/${combinedRecord.expected}`);

        const declaredScenes = contractFor(item.number).scenes;
        const hasOptional = declaredScenes.some(scene =>
          (scene.stages?.length ? scene.stages : [{ route: scene.route }])
            .some(stage => (stage.route || scene.route) === 'OPTIONAL'));
        if (hasOptional) {
          pageFailures.reset();
          await prepare(page, item.relative, '?mode=aula&profe=1');
          await page.locator('#lr-controls .lr-route-scope').click();
          await page.locator('#lr-controls .lr-route-scope').click();
          const all = await traverse(page, item.lesson, viewport, 'ALL',
            ['LIVE', 'REQUIRED', 'OPTIONAL'], pageFailures);
          all.scopeControl = (await page.locator('#lr-controls .lr-route-scope').textContent()).trim() === 'ALL';
          all.passed = all.passed && all.scopeControl
            && all.states.every(state => state.routeProgressMatches);
          const allRecord = { lesson: item.lesson, viewport: '1440x900',
            mode: 'aula-profesor', ...all };
          await finalizePageRecord(allRecord,
            [item.lesson, '1440x900', 'aula-profesor', all.scope],
            { page, failures: pageFailures });
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
    activeCheck = `${item.lesson}:study-mobile-persistence`;
    const study = await studyAudit(browser, item);
    results.push(study);
    console.log(`${study.passed ? '✓' : '✗'} ${item.lesson} study + OPTIONAL opt-in`);
    const mobile = await mobileAudit(browser, item);
    results.push(mobile);
    console.log(`${mobile.passed ? '✓' : '✗'} ${item.lesson} mobile aula fallback`);
    const persistence = await persistenceIsolationAudit(browser, item);
    results.push(persistence);
    console.log(`${persistence.passed ? '✓' : '✗'} ${item.lesson} hash-only + storage-only`);
  }

  const freshDeepLinks = await freshProfessorDeepLinksAudit(browser);
  results.push(freshDeepLinks);
  console.log(`${freshDeepLinks.passed ? '✓' : '✗'} fresh professor REQUIRED/OPTIONAL deep links`);

  const overrides = await routeOverrideAudit(browser);
  results.push(overrides);
  console.log(`${overrides.passed ? '✓' : '✗'} effective-route overrides visible `
    + `${overrides.visible}/${overrides.expected}`);

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

  phase = 'evidence-validation';
  activeCheck = 'input-integrity';
  const finalInputs = evidenceContract.inputEvidence(ROOT);
  const inputsStable = evidenceContract.sameInputEvidence(inputs, finalInputs);
  const inputValidation = evidenceContract.validateInputEvidence(inputs, ROOT);
  results.push({ lesson: 'course', viewport: 'n/a', mode: 'input-integrity',
    inputsStable, inputValidation, passed: inputsStable && inputValidation.passed });
  const identifiedResults = evidenceContract.attachRecordIds(results);
  const recordSet = evidenceContract.validateRecordSet(identifiedResults, plan);
  const coverage = evidenceContract.validateCoverage(identifiedResults, plan);
  const resultValidation = evidenceContract.validateResultSemantics(identifiedResults, plan, ROOT);
  const resultFailures = identifiedResults.filter(result => !result.passed);
  await browser.close();
  browser = null;
  const screenshots = screenshotList();
  const screenshotEvidence = AUDIT ? evidenceContract.screenshotEvidence(AUDIT, screenshots) : [];
  const passed = resultFailures.length === 0 && recordSet.passed && coverage.passed
    && resultValidation.passed && browserValidation.passed
    && inputsStable && inputValidation.passed;
  const summary = {
    completed: true,
    passed,
    started_at: startedAt,
    completed_at: new Date().toISOString(),
    source_sha,
    browser: browserEvidence,
    browser_validation: browserValidation,
    hash_algorithm: 'SHA-256',
    hashes: inputs,
    screenshots,
    screenshot_evidence: screenshotEvidence,
    lessons: coverage.documents,
    viewports: coverage.viewports,
    checks: identifiedResults.length,
    failures: resultFailures.length + (recordSet.passed ? 0 : 1)
      + (coverage.passed ? 0 : 1) + (resultValidation.passed ? 0 : 1)
      + (browserValidation.passed ? 0 : 1)
      + (inputValidation.passed && inputsStable ? 0 : 1),
    record_set: recordSet,
    coverage,
    result_validation: resultValidation,
    input_validation: inputValidation,
    results: identifiedResults,
  };
  if (auditReady) {
    fs.rmSync(path.join(AUDIT, 'desktop-audit-incomplete.json'), { force: true });
    writeJsonAtomic(path.join(AUDIT, 'desktop-audit.json'), summary);
  }
  phase = 'complete';
  process.exitCode = passed ? 0 : 1;
  } catch (error) {
    if (browser) {
      try { await browser.close(); } catch (_closeError) { /* preserve the original failure */ }
    }
    if (auditReady) {
      fs.rmSync(path.join(AUDIT, 'desktop-audit.json'), { force: true });
      fs.rmSync(path.join(AUDIT, 'desktop-audit-incomplete.json'), { force: true });
      const incomplete = {
        completed: false,
        passed: false,
        started_at: startedAt,
        failed_at: new Date().toISOString(),
        source_sha,
        browser: browserEvidence,
        browser_validation: browserValidation,
        hash_algorithm: 'SHA-256',
        hashes: inputs,
        screenshots: screenshotList(),
        checks_finished: results.length,
        phase,
        active_check: activeCheck,
        partial_results: evidenceContract.attachRecordIds(results),
        error: { name: error.name, message: error.message, stack: error.stack },
      };
      writeJsonAtomic(path.join(AUDIT, 'desktop-audit-incomplete.json'), incomplete);
    }
    console.error(error);
    process.exitCode = 1;
  }
})();
