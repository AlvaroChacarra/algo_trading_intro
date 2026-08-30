'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const contract = require('./desktop_evidence_contract');

const ROOT = path.resolve(__dirname, '..', '..');

function nestedErrors(value, location = 'results') {
  if (!value || typeof value !== 'object') return [];
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => nestedErrors(item, `${location}[${index}]`));
  }
  const found = [];
  for (const [key, item] of Object.entries(value)) {
    if (key === 'errors' && Array.isArray(item) && item.length) {
      found.push(`${location}.errors=${JSON.stringify(item)}`);
    } else {
      found.push(...nestedErrors(item, `${location}.${key}`));
    }
  }
  return found;
}

function validateScreenshots(summary, auditDirectory) {
  const declared = Array.isArray(summary?.screenshots) ? summary.screenshots : [];
  const safe = declared.every(name => typeof name === 'string' && path.basename(name) === name
    && name.toLowerCase().endsWith('.png'));
  const unique = declared.length === new Set(declared).size;
  let actual = [];
  try {
    actual = fs.readdirSync(auditDirectory)
      .filter(name => name.toLowerCase().endsWith('.png')).sort();
  } catch (_error) { /* reported through exactDirectory */ }
  const visualRecords = Array.isArray(summary?.results)
    ? summary.results.filter(record => record.mode === 'visual-sample') : [];
  const visualNames = visualRecords.map(record => record.screenshot);
  const visualValid = visualRecords.length === contract.VISUAL_SAMPLES.length
    && visualRecords.every((record, index) => record.sample === contract.VISUAL_SAMPLES[index]
      && typeof record.screenshot === 'string'
      && record.screenshot.startsWith(`visual-${record.sample}-`)
      && record.screenshot.endsWith('.png'))
    && new Set(visualNames).size === visualNames.length;
  const required = ['fixture-intermediate-overflow-detected.png', ...visualNames];
  const exactDeclared = JSON.stringify([...declared].sort()) === JSON.stringify([...required].sort());
  const exactDirectory = JSON.stringify([...declared].sort()) === JSON.stringify(actual);
  const noFailureImages = declared.every(name => !name.startsWith('failure-'));
  let evidence = [];
  let pngError = null;
  if (safe && unique && exactDirectory) {
    try { evidence = contract.screenshotEvidence(auditDirectory, declared); }
    catch (error) { pngError = error.message; }
  }
  const declaredEvidence = Array.isArray(summary?.screenshot_evidence)
    ? summary.screenshot_evidence : [];
  const manifestExact = !pngError
    && JSON.stringify(declaredEvidence) === JSON.stringify(evidence);
  const dimensionsValid = !pngError && evidence.every(item => {
    if (item.name === 'fixture-intermediate-overflow-detected.png') {
      return item.width === 1280 && item.height === 720;
    }
    return item.width === 1440 && item.height === 900;
  });
  return { expected: required.length, observed: declared.length, safe, unique, visualValid,
    exactDeclared, exactDirectory, noFailureImages, pngError, manifestExact, dimensionsValid,
    evidence, passed: safe && unique && visualValid && exactDeclared && exactDirectory
      && noFailureImages && !pngError && manifestExact && dimensionsValid };
}

function validateAuditDirectory(auditDirectory, root = ROOT) {
  const errors = [];
  const ownership = contract.validateAuditOwner(root, auditDirectory);
  if (!ownership.passed) {
    return { passed: false, errors: [`unsafe audit directory: ${ownership.error}`] };
  }
  const completePath = path.join(auditDirectory, 'desktop-audit.json');
  const incompletePath = path.join(auditDirectory, 'desktop-audit-incomplete.json');
  if (fs.existsSync(incompletePath)) errors.push('incomplete artifact exists');
  if (!fs.existsSync(completePath)) return { passed: false, errors: [...errors, 'complete artifact missing'] };
  let summary;
  try { summary = JSON.parse(fs.readFileSync(completePath, 'utf8')); }
  catch (error) { return { passed: false, errors: [...errors, `invalid JSON: ${error.message}`] }; }

  let head = null;
  let plan = null;
  try { head = contract.sourceHead(root); }
  catch (error) { errors.push(`cannot recompute source provenance: ${error.message}`); }
  try { plan = contract.buildExpectedAuditPlan(root); }
  catch (error) { errors.push(`cannot recompute audit plan: ${error.message}`); }
  if (summary.completed !== true) errors.push('completed is not true');
  if (summary.passed !== true) errors.push('passed is not true');
  if (summary.source_sha !== head) errors.push('source SHA does not match checked-out HEAD');
  let browserValidation = { passed: false };
  try {
    const { chromium } = require('playwright');
    const browserExecutable = fs.realpathSync.native(chromium.executablePath());
    browserValidation = contract.validateBrowserIdentity(
      summary.browser, contract.lockedBrowserIdentity(root, browserExecutable), summary.browser);
  } catch (error) {
    errors.push(`cannot read locked browser identity: ${error.message}`);
  }
  if (!browserValidation.passed) {
    errors.push(`browser identity does not match locked Chromium/Playwright: ${JSON.stringify(browserValidation)}`);
  }
  if (JSON.stringify(summary.browser_validation) !== JSON.stringify(browserValidation)) {
    errors.push('declared browser_validation differs from independent recomputation');
  }
  if (summary.hash_algorithm !== 'SHA-256') errors.push('unexpected hash algorithm');
  if (!Array.isArray(summary.results)) errors.push('results must be an array');

  let resultValidation = null;
  if (plan && Array.isArray(summary.results)) {
    const recordSet = contract.validateRecordSet(summary.results, plan);
    const coverage = contract.validateCoverage(summary.results, plan);
    resultValidation = contract.validateResultSemantics(summary.results, plan, root);
    if (!recordSet.passed) errors.push(`record set mismatch: ${JSON.stringify(recordSet)}`);
    if (!coverage.passed) errors.push(`coverage mismatch: ${JSON.stringify(coverage)}`);
    if (!resultValidation.passed) {
      const failed = resultValidation.checks.filter(check => !check.passed).map(check => check.id);
      errors.push(`substantive result mismatch: ${failed.join(', ')}`);
    }
    if (JSON.stringify(summary.record_set) !== JSON.stringify(recordSet)) {
      errors.push('declared record_set differs from independent recomputation');
    }
    if (JSON.stringify(summary.coverage) !== JSON.stringify(coverage)) {
      errors.push('declared coverage differs from independent recomputation');
    }
    if (JSON.stringify(summary.result_validation) !== JSON.stringify(resultValidation)) {
      errors.push('declared result_validation differs from independent recomputation');
    }
    if (summary.checks !== plan.ids.length || summary.results.length !== plan.ids.length) {
      errors.push('check count does not equal the closed-world plan');
    }
    const reportedOutcomeConsistent = summary.results.every((result, index) =>
      result.passed === resultValidation.checks[index].passed);
    if (!reportedOutcomeConsistent) errors.push('reported result outcomes differ from substantive recomputation');
    const recordedErrors = nestedErrors(summary.results);
    if (recordedErrors.length) errors.push(`recorded browser errors: ${recordedErrors.join('; ')}`);
  }

  const inputValidation = contract.validateInputEvidence(summary.hashes, root);
  if (!inputValidation.passed) errors.push(`input evidence mismatch: ${JSON.stringify(inputValidation)}`);
  if (JSON.stringify(summary.input_validation) !== JSON.stringify(inputValidation)) {
    errors.push('declared input_validation differs from independent recomputation');
  }
  if (summary.failures !== 0) errors.push('failure count is not zero');
  const screenshotValidation = validateScreenshots(summary, auditDirectory);
  if (!screenshotValidation.passed) {
    errors.push(`screenshot evidence mismatch: ${JSON.stringify(screenshotValidation)}`);
  }
  return { passed: errors.length === 0, errors, source_sha: head,
    expected_records: plan?.ids.length ?? null, input_validation: inputValidation,
    browser_validation: browserValidation, result_validation: resultValidation,
    screenshot_validation: screenshotValidation };
}

async function verifyBrowserEvidence(auditDirectory, root = ROOT) {
  const summary = JSON.parse(fs.readFileSync(path.join(auditDirectory, 'desktop-audit.json'), 'utf8'));
  const plan = contract.buildExpectedAuditPlan(root);
  const targets = contract.visualSampleTargets(plan.lessons);
  const records = new Map(summary.results.filter(record => record.mode === 'visual-sample')
    .map(record => [record.sample, record]));
  const manifest = new Map(summary.screenshot_evidence.map(item => [item.name, item]));
  const { chromium } = require('playwright');
  const playwrightVersion = require('playwright/package.json').version;
  let browser = null;
  const samples = [];
  try {
    const browserExecutable = fs.realpathSync.native(chromium.executablePath());
    const locked = contract.lockedBrowserIdentity(root, browserExecutable);
    browser = await chromium.launch({ headless: true, executablePath: browserExecutable });
    const observed = { ...locked, name: browser.browserType().name(), version: browser.version(),
      playwright: playwrightVersion };
    const identity = contract.validateBrowserIdentity(summary.browser,
      locked, observed);
    if (!identity.passed) return { identity, samples, passed: false };
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 },
      reducedMotion: 'reduce' });
    await context.addInitScript(contract.VISUAL_AUDIT_INIT_SCRIPT);
    const page = await context.newPage();
    const browserErrors = [];
    page.on('pageerror', error => browserErrors.push(`pageerror: ${error.message}`));
    page.on('console', message => {
      if (message.type() === 'error') browserErrors.push(`console.error: ${message.text()}`);
    });
    for (const target of targets) {
      browserErrors.length = 0;
      const record = records.get(target.name);
      const url = `file://${path.join(root, target.relative)}?mode=aula&profe=1`;
      await page.goto(url);
      await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'aula');
      await page.evaluate(() => {
        localStorage.clear();
        history.replaceState(null, '', location.pathname + location.search);
      });
      await page.reload();
      await page.waitForFunction(() => window.LEARNING_RUNTIME?.mode === 'aula');
      if (target.route !== 'LIVE') {
        await page.locator('#lr-controls .lr-route-scope').click();
        if (target.route === 'OPTIONAL') await page.locator('#lr-controls .lr-route-scope').click();
      }
      const navigated = await page.evaluate(state =>
        window.LEARNING_RUNTIME.goTo(state.scene, state.stage), target);
      await page.waitForFunction(state => document.body.dataset.currentSceneId === state.scene
        && document.body.dataset.currentStageId === state.stage, target);
      await page.evaluate(() => document.fonts?.ready);
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() =>
        requestAnimationFrame(resolve))));
      const state = await page.evaluate(expected => {
        const active = document.querySelector('body > .lr-scene-active');
        const controls = document.getElementById('lr-controls');
        const nav = document.getElementById('lr-nav');
        const inside = (node, bounds) => {
          if (!node) return false;
          const box = node.getBoundingClientRect();
          return box.left >= bounds.left - 2 && box.top >= bounds.top - 2
            && box.right <= bounds.right + 2 && box.bottom <= bounds.bottom + 2;
        };
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
        const runtime = window.LEARNING_RUNTIME?.getState?.();
        const scopeRoutes = document.body.dataset.routeScope === 'ALL'
          ? ['LIVE', 'REQUIRED', 'OPTIONAL']
          : (document.body.dataset.routeScope === 'LIVE+REQUIRED' ? ['LIVE', 'REQUIRED'] : ['LIVE']);
        const declared = JSON.parse(document.querySelector('#pedagogy-contract').textContent);
        const scene = declared.scenes.find(item => item.id === expected.scene);
        const stages = (scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route,
          duration_minutes: scene.duration_minutes }]).map(item => ({ ...item,
          route: item.route || scene.route, duration_minutes: item.duration_minutes ?? scene.duration_minutes }))
          .filter(item => scopeRoutes.includes(item.route));
        const stageIndex = stages.findIndex(item => item.id === expected.stage);
        const stageContract = stages[stageIndex];
        const expectedLive = `${expected.scene}, ruta ${expected.route}, ${expected.durationMinutes} minutos, `
          + `etapa ${stageIndex + 1} de ${stages.length}`;
        const badgeRoute = active?.querySelector('.lr-scene-badge .lr-route-label')?.textContent.trim();
        const badgeDuration = active?.querySelector('.lr-scene-badge .lr-duration')?.textContent.trim();
        const navRoute = nav?.querySelector('.lr-scene-links button.on .lr-route-label')?.textContent.trim();
        const live = document.querySelector('body > .lr-sr-only[aria-live="polite"]')?.textContent.trim();
        const progress = parseInt(controls?.querySelector('.lr-route-progress')?.textContent || '', 10);
        const enabled = scopeRoutes.reduce((acc, route) => ({ visited: acc.visited
          + runtime.progress[route].visited, total: acc.total + runtime.progress[route].total }),
        { visited: 0, total: 0 });
        const expectedProgress = Math.round(100 * enabled.visited / Math.max(1, enabled.total));
        const step = active?.querySelector('.step.lr-stage-active:not([hidden])');
        const figure = active?.querySelector('.fig-stage.on:not([hidden])');
        const stageNodes = [step, figure].filter(Boolean);
        const meaningfulChildren = node => [...(node?.children || [])].filter(child =>
          !['SCRIPT', 'STYLE', 'TEMPLATE'].includes(child.tagName)
          && !child.classList.contains('lr-scene-badge'));
        const essentialNodes = [];
        const add = nodes => nodes.filter(Boolean).forEach(node => essentialNodes.push(node));
        add([...(active?.querySelectorAll('[data-lr-essential]') || [])].filter(node => {
          const owner = node.closest('.step,.fig-stage');
          return !owner || owner === step || owner === figure;
        }));
        for (const rootNode of stageNodes) {
          const content = rootNode.matches('.step')
            ? (rootNode.querySelector(':scope > .step-inner') || rootNode) : rootNode;
          add(meaningfulChildren(content));
          add([...content.querySelectorAll('canvas,svg,img,video,pre,table,[role="img"],'
            + 'button,input,select,textarea')]);
        }
        const sharedHeading = [...(active?.querySelectorAll('h1,h2') || [])]
          .find(node => !node.closest('.step,.fig-stage'));
        add([sharedHeading]);
        if (!step && !figure) {
          const wrap = active?.matches('.wrap') ? active
            : active?.querySelector(':scope > .wrap') || active;
          add(meaningfulChildren(wrap));
          add([...(active?.querySelectorAll('canvas,svg,img,video,pre,table,[role="img"],'
            + 'button,input,select,textarea') || [])]);
        }
        const essentialVisibility = [...new Set(essentialNodes)].map(node => visibilityEvidence(node));
        const stageVisibility = stageNodes.map(node => ({
          kind: node.classList.contains('fig-stage') ? 'figure' : 'step',
          ...visibilityEvidence(node),
        }));
        return { requestedMode: document.body.dataset.requestedMode,
          effectiveMode: document.body.dataset.learningMode,
          auditMode: window.__DESKTOP_VISUAL_AUDIT__ || null,
          scene: runtime?.scene, stage: runtime?.stage, route: runtime?.route,
          sceneRoute: runtime?.sceneRoute, scope: runtime?.routeScope,
          oneActive: document.querySelectorAll('body > .lr-scene-active').length === 1,
          noBodyOverflow: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            <= innerHeight + 2,
          noHorizontalOverflow: document.documentElement.scrollWidth
            <= document.documentElement.clientWidth + 2,
          sceneInside: inside(active, { left: nav?.getBoundingClientRect().right || 0,
            top: 0, right: innerWidth, bottom: controls?.getBoundingClientRect().top || innerHeight }),
          controlsInside: inside(controls, { left: 0, top: 0, right: innerWidth, bottom: innerHeight }),
          navInside: inside(nav, { left: 0, top: 0, right: innerWidth, bottom: innerHeight }),
          activeVisibility: visibilityEvidence(active),
          stageVisibility,
          essentialVisibility,
          stageContractMatches: stageContract?.id === expected.stage
            && stageContract.route === expected.route
            && stageContract.duration_minutes === expected.durationMinutes,
          stageNoOverflow: stageNodes.every(node => node.scrollWidth <= node.clientWidth + 2
            && node.scrollHeight <= node.clientHeight + 2),
          badgeRoute, badgeDuration, navRoute, live, expectedLive, progress, expectedProgress };
      }, target);
      const screenshot = await page.screenshot({ animations: 'disabled', caret: 'hide' });
      const png = contract.parsePngBuffer(screenshot);
      const observedSha = crypto.createHash('sha256').update(screenshot).digest('hex');
      const stored = manifest.get(record?.screenshot);
      const requestedPath = `${target.scene}/${target.stage}`;
      const requestedHash = await page.evaluate(() => {
        try { return decodeURIComponent(location.hash.slice(1)); }
        catch (_error) { return null; }
      });
      await page.evaluate(() => sessionStorage.setItem('__lr_desktop_replay_hash', 'pending'));
      await page.addInitScript(() => {
        if (sessionStorage.getItem('__lr_desktop_replay_hash') !== 'pending') return;
        localStorage.clear();
        sessionStorage.setItem('__lr_desktop_replay_hash',
          localStorage.length === 0 ? 'cleared' : 'failed');
      });
      await page.reload();
      await page.waitForFunction(expected => window.LEARNING_RUNTIME?.mode === 'aula'
        && document.body.dataset.currentSceneId === expected.scene
        && document.body.dataset.currentStageId === expected.stage, target);
      const deepLink = await page.evaluate(() => {
        let observedHash = null;
        try { observedHash = decodeURIComponent(location.hash.slice(1)); }
        catch (_error) { observedHash = null; }
        const restoredPath = `${document.body.dataset.currentSceneId}/${document.body.dataset.currentStageId}`;
        const storageWasEmptyAtInit = sessionStorage.getItem('__lr_desktop_replay_hash') === 'cleared';
        sessionStorage.removeItem('__lr_desktop_replay_hash');
        return { observedHash, restoredPath, storageWasEmptyAtInit };
      });
      const semantic = navigated === true && state.requestedMode === 'aula'
        && state.effectiveMode === 'aula' && state.scene === target.scene && state.stage === target.stage
        && state.auditMode === 'visual-v1'
        && state.route === target.route && state.sceneRoute === target.sceneRoute
        && state.oneActive && state.noBodyOverflow && state.noHorizontalOverflow
        && state.sceneInside && state.controlsInside && state.navInside && state.stageNoOverflow
        && state.activeVisibility.rendered && state.activeVisibility.positiveArea
        && state.activeVisibility.effectiveOpacity > 0.01 && state.activeVisibility.unoccluded
        && state.stageVisibility.every(item => item.rendered
          && item.positiveArea && item.effectiveOpacity > 0.01 && item.unoccluded)
        && state.essentialVisibility.length > 0 && state.essentialVisibility.every(item => item.rendered
          && item.positiveArea && item.effectiveOpacity > 0.01 && item.unoccluded)
        && state.stageContractMatches
        && state.badgeRoute === target.route && state.navRoute === target.route
        && state.badgeDuration === `${target.durationMinutes} min`
        && state.live === state.expectedLive && state.progress === state.expectedProgress
        && requestedHash === requestedPath && deepLink.observedHash === requestedPath
        && deepLink.restoredPath === requestedPath && deepLink.storageWasEmptyAtInit;
      samples.push({ sample: target.name, target: `${target.lesson}:${target.scene}/${target.stage}`,
        screenshot: record?.screenshot || null, width: png.width, height: png.height,
        storedSha: stored?.sha256 || null, observedSha,
        deepLink: { requestedPath, requestedHash, ...deepLink },
        exactPixels: stored?.sha256 === observedSha,
        errors: [...browserErrors], semantic,
        passed: semantic && png.width === 1440 && png.height === 900
          && stored?.width === png.width && stored?.height === png.height
          && stored?.sha256 === observedSha && browserErrors.length === 0 });
    }
    await context.close();
    return { identity, samples, passed: samples.length === contract.VISUAL_SAMPLES.length
      && samples.every(sample => sample.passed) };
  } catch (error) {
    return { samples, error: error.message, passed: false };
  } finally {
    if (browser) await browser.close();
  }
}

async function main(argv = process.argv.slice(2)) {
  const verifyBrowser = argv[0] === '--verify-browser';
  const args = verifyBrowser ? argv.slice(1) : argv;
  if (args.length !== 1) {
    console.error('Usage: node validate_desktop_audit.js [--verify-browser] <audit-directory>');
    return 2;
  }
  const auditDirectory = path.resolve(args[0]);
  const result = validateAuditDirectory(auditDirectory);
  if (!result.passed) {
    result.errors.forEach(error => console.error(`desktop audit: ${error}`));
    return 1;
  }
  if (verifyBrowser) {
    const browserResult = await verifyBrowserEvidence(auditDirectory);
    if (!browserResult.passed) {
      console.error(`desktop audit: browser replay mismatch: ${JSON.stringify(browserResult)}`);
      return 1;
    }
  }
  console.log(`desktop audit valid: ${result.expected_records} exact records @ ${result.source_sha}`);
  return 0;
}

if (require.main === module) main().then(code => { process.exitCode = code; }, error => {
  console.error(error); process.exitCode = 1;
});

module.exports = { main, nestedErrors, validateAuditDirectory, validateScreenshots,
  verifyBrowserEvidence };
