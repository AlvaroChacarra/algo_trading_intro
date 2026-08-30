'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const { spawnSync } = require('child_process');
const test = require('node:test');
const contract = require('./desktop_evidence_contract');
const validator = require('./validate_desktop_audit');

const ROOT = path.resolve(__dirname, '..', '..');

function pngChunk(type, data) {
  const typeBuffer = Buffer.from(type, 'ascii');
  const chunk = Buffer.alloc(12 + data.length);
  chunk.writeUInt32BE(data.length, 0);
  typeBuffer.copy(chunk, 4);
  data.copy(chunk, 8);
  chunk.writeUInt32BE(contract.crc32(Buffer.concat([typeBuffer, data])), 8 + data.length);
  return chunk;
}

function solidPng(width, height) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 0;
  const raw = Buffer.alloc((width + 1) * height);
  const compressed = zlib.deflateSync(raw);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    pngChunk('IHDR', ihdr), pngChunk('IDAT', compressed), pngChunk('IEND', Buffer.alloc(0))]);
}

function declaredPng(width, height, raw) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    pngChunk('IHDR', ihdr), pngChunk('IDAT', zlib.deflateSync(raw)),
    pngChunk('IEND', Buffer.alloc(0))]);
}

const rawVisibility = () => ({ rendered: true, positiveArea: true,
  effectiveOpacity: 1, unoccluded: true });
const rawBox = () => ({ x: 0, y: 0, left: 0, top: 0,
  right: 100, bottom: 50, width: 100, height: 50 });
const rawProgress = () => Object.fromEntries(['LIVE', 'REQUIRED', 'OPTIONAL'].map(route =>
  [route, { total: 1, visited: 1, percent: 100, complete: true }]));

function desktopStateFixture() {
  const expected = { scene: 'scene-a', stage: 'stage-a', sceneRoute: 'LIVE',
    stageRoute: 'LIVE', durationMinutes: 2, layout: 'focus', type: 'hero',
    stagePosition: 1, stageTotal: 1 };
  const expectedLive = 'scene-a, ruta LIVE, 2 minutos, etapa 1 de 1';
  const expectedMobile = 'Ruta · LIVE · 2 min · Estudio · scene-a';
  return {
    evidenceSchema: 'desktop-state/v2', viewport: { width: 1280, height: 720 },
    activeVisibility: rawVisibility(), activeSceneCount: 1,
    sceneBox: rawBox(), controlsBox: rawBox(), navBox: rawBox(),
    expected, scene: expected.scene, stage: expected.stage, sceneRoute: expected.sceneRoute,
    stageRoute: expected.stageRoute, scope: 'LIVE', layout: expected.layout, type: expected.type,
    position: 1, total: 1, layoutApplied: true,
    controlEvidence: { previousDisabled: true, nextDisabled: true },
    runtimeState: { scene: expected.scene, stage: expected.stage, route: expected.stageRoute,
      sceneRoute: expected.sceneRoute, routeScope: 'LIVE' },
    stateMatches: true, controlState: true, oneSceneActive: true,
    sceneInsideViewport: true, controlsInsideViewport: true, navInsideViewport: true,
    essentialInsideViewport: true, layoutMatches: true, routeProgressMatches: true,
    savedProgressMatches: true, scrollAuditPassed: true, routePresentationMatches: true,
    liveRegionMatches: true, getStateConsistent: true,
    bodyOverflow: false, horizontalOverflow: false, stageOverflow: false,
    bodyScrollPosition: { x: 0, y: 0 },
    essentialCount: 1, essentialChecks: [{ selector: '#essential', label: '#essential',
      box: rawBox(), effectiveVisible: true, positiveArea: true, effectiveOpacity: 1,
      unoccluded: true, failures: [] }],
    unresolvedEssentialSelectors: [], essentialFailures: [],
    stageOverflowChecks: [{ kind: 'step', scrollWidth: 100, clientWidth: 100,
      scrollHeight: 50, clientHeight: 50, overflow: false }],
    undeclaredScrollers: [], hiddenFocusable: [], scrollerChecks: [],
    routePresentation: { badgeRoute: 'LIVE', badgeDuration: '2 min', navRoute: 'LIVE',
      teacherRoute: null, teacherKicker: null, mobileText: expectedMobile,
      expectedMobileText: expectedMobile, mobileRouteVisible: true, mobileDurationVisible: true },
    liveRegion: { text: expectedLive, expected: expectedLive },
  };
}

function flowStateFixture() {
  const expected = { scene: 'scene-a', stage: 'stage-a', sceneRoute: 'LIVE', route: 'LIVE',
    durationMinutes: 2, stagePosition: 1, stageTotal: 1 };
  const expectedLive = 'scene-a, ruta LIVE, 2 minutos, etapa 1 de 1';
  const progress = rawProgress();
  return { expected, state: { expected,
    evidenceSchema: 'desktop-flow-state/v2', viewport: { width: 1440, height: 900 },
    activeSceneCount: 1, sceneVisibility: rawVisibility(), sceneBox: rawBox(),
    scene: expected.scene, stage: expected.stage, sceneRoute: expected.sceneRoute,
    stageRoute: expected.route, scope: 'LIVE', position: 1, total: 1,
    targetMatches: true, rendered: true, sceneHorizontalInside: true, horizontalOverflow: false,
    essentialCount: 1, essentialInside: true,
    essentialChecks: [{ selector: '#essential', label: '#essential', box: rawBox(),
      effectiveVisible: true, positiveArea: true, effectiveOpacity: 1,
      unoccluded: true, failures: [] }],
    essentialFailures: [], unresolvedEssentialSelectors: [], stageOverflow: false,
    stageOverflowChecks: [{ kind: 'figure', scrollWidth: 100, clientWidth: 100,
      scrollHeight: 50, clientHeight: 50, overflow: false }],
    scrollAuditPassed: true, scrollerChecks: [], undeclaredScrollers: [], hiddenFocusable: [],
    routePresentation: { badgeRoute: 'LIVE', badgeDuration: '2 min',
      mobileText: null, mobileVisible: false }, routePresentationMatches: true,
    liveRegion: { text: expectedLive, expected: expectedLive }, liveRegionMatches: true,
    progressConsistent: true,
    runtimeState: { scene: expected.scene, stage: expected.stage, route: expected.route,
      sceneRoute: expected.sceneRoute, routeScope: 'LIVE', progress },
    savedRuntimeState: { scene: expected.scene, stage: expected.stage,
      routeScope: 'LIVE', progress: structuredClone(progress) },
    navigated: true,
  } };
}

function snapshotFixture(target, scope, surface) {
  const route = target.stageRoute || target.route;
  const presentation = {
    badge: route, badgeDuration: `${target.durationMinutes} min`, badgeVisible: true,
    badgeVisibility: rawVisibility(), nav: route, navVisible: true,
    navVisibility: rawVisibility(),
    mobile: `Ruta · ${route} · ${target.durationMinutes} min · Aula → estudio · ${target.scene}`,
    mobileVisible: true,
    mobileVisibility: rawVisibility(),
  };
  if (surface === 'desktop') {
    presentation.mobileVisible = false;
    presentation.mobileVisibility = { rendered: false, positiveArea: false,
      effectiveOpacity: 0, unoccluded: false };
  }
  return { scene: target.scene, stage: target.stage, route,
    sceneRoute: target.sceneRoute, scope, targetMatches: true, getStateConsistent: true,
    runtimeState: { scene: target.scene, stage: target.stage, route,
      sceneRoute: target.sceneRoute, routeScope: scope }, presentation };
}

function ownedAuditDirectory(root, name) {
  const audit = path.join(root, 'artifacts', name);
  if (fs.existsSync(audit)) fs.rmSync(audit, { recursive: true, force: true });
  return contract.prepareAuditDirectory(root, audit);
}

function identityRecord(checkId) {
  const parts = checkId.split(':');
  let record;
  switch (parts[0]) {
    case 'negative-fixture': record = { mode: 'negative-fixture' }; break;
    case 'aula': record = { mode: 'aula', lesson: parts[1], viewport: parts[2], scope: parts[3] }; break;
    case 'aula-profesor': record = { mode: 'aula-profesor', lesson: parts[1], viewport: parts[2], scope: parts[3] }; break;
    case 'estudio':
    case 'mobile-fallback':
    case 'persistence-isolation':
      record = { mode: parts[0], lesson: parts[1], viewport: parts[2] }; break;
    case 'fresh-professor-deep-links':
    case 'route-overrides':
    case 'input-integrity': record = { mode: parts[0] }; break;
    case 'visual-sample': record = { mode: 'visual-sample', sample: parts[1] }; break;
    case 'index': record = { mode: 'index', lesson: parts[1], viewport: parts[2] }; break;
    case 'assessment-linear':
      record = { mode: 'assessment-linear', lesson: parts[1], viewport: parts[2] }; break;
    default: record = { mode: 'invalid' };
  }
  return { ...record, check_id: checkId, passed: true };
}

function exactResults(plan) {
  return plan.ids.map(identityRecord);
}

function coverageResults(plan) {
  const results = [];
  for (const [checkId, expected] of Object.entries(plan.traversalStates)) {
    results.push({
      ...identityRecord(checkId),
      expected: expected.length,
      visited: expected.length,
      errors: [],
      states: expected.map(state => ({
        scene: state.scene, stage: state.stage, sceneRoute: state.sceneRoute,
        stageRoute: state.route, passed: true,
      })),
    });
  }
  results.push({ mode: 'route-overrides', expected: plan.overrideIds.length,
    declared: plan.overrideIds.length, visible: plan.overrideIds.length,
    records: plan.overrideIds.map(id => {
    const [lesson, state] = id.split(':');
    const [scene, stage] = state.split('/');
    const source = plan.lessons.flatMap(item => item.contract.scenes.flatMap(sceneItem => {
      const stages = sceneItem.stages?.length ? sceneItem.stages : [{ id: 'stage', route: sceneItem.route }];
      return stages.map(stageItem => ({ lesson: item.lesson, scene: sceneItem.id, stage: stageItem.id,
        sceneRoute: sceneItem.route, effectiveRoute: stageItem.route || sceneItem.route }));
    })).find(item => item.lesson === lesson && item.scene === scene && item.stage === stage);
    return { lesson, scene, stage, sceneRoute: source.sceneRoute,
      effectiveRoute: source.effectiveRoute, errors: [], passed: true };
  }) });
  results.push({ mode: 'fresh-professor-deep-links',
    records: plan.deepLinkIds.map(id => {
      const [route, lesson, state] = id.split(':');
      const [scene, stage] = state.split('/');
      return { route, lesson, target: { scene, stage }, freshContext: true,
        errors: [], passed: true };
    }) });
  return results;
}

test('closed-world plan is 132 unique records and 661 traversed states', () => {
  const plan = contract.buildExpectedAuditPlan(ROOT);
  assert.equal(plan.ids.length, 132);
  assert.equal(new Set(plan.ids).size, 132);
  assert.equal(plan.traversedStates, 661);
  assert.equal(plan.overrideIds.length, 14);
});

test('record-set validator rejects missing, duplicate, and unexpected records', () => {
  const plan = contract.buildExpectedAuditPlan(ROOT);
  assert.equal(contract.validateRecordSet(exactResults(plan), plan).passed, true);

  const missing = exactResults(plan).slice(1);
  assert.equal(contract.validateRecordSet(missing, plan).passed, false);
  assert.deepEqual(contract.validateRecordSet(missing, plan).missing, [plan.ids[0]]);

  const duplicate = exactResults(plan);
  duplicate[0] = { ...duplicate[1] };
  const duplicateResult = contract.validateRecordSet(duplicate, plan);
  assert.equal(duplicateResult.passed, false);
  assert.equal(duplicateResult.duplicates.length, 1);
  assert.equal(duplicateResult.missing.length, 1);

  const unexpected = exactResults(plan);
  unexpected.push({ mode: 'invented', check_id: 'invented-record', passed: true });
  assert.equal(contract.validateRecordSet(unexpected, plan).passed, false);

  const forgedId = exactResults(plan);
  forgedId[0].check_id = plan.ids[1];
  assert.equal(contract.validateRecordSet(forgedId, plan).idMismatches.length, 1);
});

test('coverage validator closes traversal, override, and deep-link identities', () => {
  const plan = contract.buildExpectedAuditPlan(ROOT);
  const results = coverageResults(plan);
  const valid = contract.validateCoverage(results, plan);
  assert.equal(valid.passed, true);
  assert.equal(valid.traversed_states, 661);

  const noStates = coverageResults(plan);
  noStates.find(record => record.mode === 'aula').states = [];
  assert.equal(contract.validateCoverage(noStates, plan).passed, false);

  results.find(record => record.mode === 'route-overrides').records.pop();
  assert.equal(contract.validateCoverage(results, plan).passed, false);

  const wrongDeepLink = coverageResults(plan);
  wrongDeepLink.find(record => record.mode === 'fresh-professor-deep-links')
    .records[0].target.stage = 'invented-stage';
  assert.equal(contract.validateCoverage(wrongDeepLink, plan).passed, false);
});

test('substantive validator rejects a structurally complete synthetic corpus', () => {
  const plan = contract.buildExpectedAuditPlan(ROOT);
  const synthetic = exactResults(plan);
  assert.equal(contract.validateRecordSet(synthetic, plan).passed, true);
  const result = contract.validateResultSemantics(synthetic, plan, ROOT);
  assert.equal(result.passed, false);
  assert.ok(result.checks.some(check => !check.passed));
});

test('desktop and flow semantics require complete raw visibility, opacity, and occlusion evidence', () => {
  const desktop = desktopStateFixture();
  assert.equal(contract.desktopStatePassed(desktop), true);
  const aggregateOnly = structuredClone(desktop);
  delete aggregateOnly.essentialChecks;
  assert.equal(contract.desktopStatePassed(aggregateOnly), false);
  const transparent = structuredClone(desktop);
  transparent.essentialChecks[0].effectiveOpacity = 0;
  assert.equal(contract.desktopStatePassed(transparent), false);
  const occluded = structuredClone(desktop);
  occluded.essentialChecks[0].unoccluded = false;
  assert.equal(contract.desktopStatePassed(occluded), false);
  const missingActiveRaw = structuredClone(desktop);
  delete missingActiveRaw.activeVisibility;
  assert.equal(contract.desktopStatePassed(missingActiveRaw), false);

  const flow = flowStateFixture();
  assert.equal(contract.flowStatePassed(flow.state, flow.expected, 0, 1), true);
  const forgedFlow = structuredClone(flow.state);
  forgedFlow.essentialChecks = [];
  assert.equal(contract.flowStatePassed(forgedFlow, flow.expected, 0, 1), false);
  const staleStoredFlow = structuredClone(flow.state);
  staleStoredFlow.savedRuntimeState.stage = 'stale';
  assert.equal(contract.flowStatePassed(staleStoredFlow, flow.expected, 0, 1), false);
  const hiddenSceneFlow = structuredClone(flow.state);
  hiddenSceneFlow.sceneVisibility.effectiveOpacity = 0;
  assert.equal(contract.flowStatePassed(hiddenSceneFlow, flow.expected, 0, 1), false);
});

test('navigation semantics reject aggregate booleans without exact hash and storage provenance', () => {
  const navigation = {
    backward: true, forward: true, tabOrderPassed: true, focusVisible: true,
    reloadPersistence: true, hashWritten: true, progress: true, courseHome: true,
    hashTargetMatches: true, storageTargetMatches: true, storageClearedForHashRestore: true,
    tabOrder: { count: 2, wrapped: true, hiddenFocus: [] },
    persistence: { target: { scene: 'scene-a', stage: 'stage-a' },
      hash: '#scene-a/stage-a', hashTarget: 'scene-a/stage-a',
      storageTarget: { scene: 'scene-a', stage: 'stage-a' }, storageVersion: 2,
      progressValid: true, restored: { scene: 'scene-a', stage: 'stage-a' } },
  };
  assert.equal(contract.navigationPassed(navigation, false), true);
  const wrongHash = structuredClone(navigation);
  wrongHash.persistence.hashTarget = 'scene-a/forged';
  assert.equal(contract.navigationPassed(wrongHash, false), false);
  const wrongStorage = structuredClone(navigation);
  wrongStorage.persistence.storageTarget.stage = 'forged';
  assert.equal(contract.navigationPassed(wrongStorage, false), false);
  const missingRaw = structuredClone(navigation);
  delete missingRaw.persistence;
  assert.equal(contract.navigationPassed(missingRaw, false), false);
});

test('visual init script fixes random values and neutralizes intervals while preserving timer ids', () => {
  let nextId = 40;
  const handlers = new Map();
  const cleared = [];
  const sandbox = {
    setInterval(handler) { const id = nextId++; handlers.set(id, handler); return id; },
    clearInterval(id) { cleared.push(id); handlers.delete(id); },
  };
  sandbox.window = sandbox;
  vm.runInNewContext(contract.VISUAL_AUDIT_INIT_SCRIPT, sandbox);
  assert.equal(sandbox.__DESKTOP_VISUAL_AUDIT__, 'visual-v1');
  assert.equal(vm.runInNewContext('Math.random()', sandbox), 0.5);
  let called = false;
  const id = sandbox.setInterval(() => { called = true; }, 0);
  assert.equal(id, 40);
  handlers.get(id)();
  assert.equal(called, false);
  sandbox.clearInterval(id);
  assert.deepEqual(cleared, [40]);
  assert.match(contract.VISUAL_AUDIT_INIT_SCRIPT, /__DESKTOP_VISUAL_AUDIT__/);
  assert.match(contract.VISUAL_AUDIT_INIT_SCRIPT, /2147483647/);
});

test('audit preparation refuses unsafe and unowned targets without deleting them', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-audit-safety-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-audit-outside-'));
  try {
    fs.mkdirSync(path.join(root, 'artifacts'));
    assert.throws(() => contract.prepareAuditDirectory(root, outside), /unsafe --audit-dir/);
    assert.throws(() => contract.prepareAuditDirectory(
      root, path.join(root, 'artifacts', 'nested', 'audit')), /unsafe --audit-dir/);

    const unowned = path.join(root, 'artifacts', 'unowned');
    fs.mkdirSync(unowned);
    const sentinel = path.join(unowned, 'keep.txt');
    fs.writeFileSync(sentinel, 'must survive\n');
    assert.throws(() => contract.prepareAuditDirectory(root, unowned), /refusing to clear unowned/);
    assert.equal(fs.readFileSync(sentinel, 'utf8'), 'must survive\n');

    const owned = path.join(root, 'artifacts', 'owned');
    contract.prepareAuditDirectory(root, owned);
    fs.writeFileSync(path.join(owned, 'stale.txt'), 'stale\n');
    contract.prepareAuditDirectory(root, owned);
    assert.deepEqual(fs.readdirSync(owned), [contract.AUDIT_OWNER_FILE]);

    const symlink = path.join(root, 'artifacts', 'linked');
    fs.symlinkSync(outside, symlink, 'dir');
    assert.throws(() => contract.prepareAuditDirectory(root, symlink), /symlinks/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  }
});

test('browser identity pins the exact Chromium launcher and complete registry payload', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-browser-identity-'));
  try {
    fs.mkdirSync(path.join(root, 'node_modules', 'playwright-core'), { recursive: true });
    fs.writeFileSync(path.join(root, 'package-lock.json'), JSON.stringify({ packages: {
      'node_modules/playwright': { version: '1.62.1' },
    } }));
    fs.writeFileSync(path.join(root, 'node_modules/playwright-core/browsers.json'), JSON.stringify({
      browsers: [
        { name: 'chromium', revision: '1234', browserVersion: '151.0.1' },
        { name: 'chromium-headless-shell', revision: '1234', browserVersion: '151.0.1' },
        { name: 'webkit', revision: '2336', browserVersion: '26.5' },
      ],
    }));
    const executable = path.join(root, 'cache', 'chromium-1234', 'chrome-linux64', 'chrome');
    fs.mkdirSync(path.dirname(executable), { recursive: true });
    fs.writeFileSync(executable, 'locked chromium executable\n');
    const locked = contract.lockedBrowserIdentity(root, executable);
    assert.deepEqual({
      schema: locked.schema,
      name: locked.name,
      product: locked.product,
      version: locked.version,
      playwright: locked.playwright,
      revision: locked.revision,
      executable_locator: locked.executable_locator,
      executable_sha256: locked.executable_sha256,
      executable_bytes: locked.executable_bytes,
    }, {
      schema: contract.BROWSER_IDENTITY_SCHEMA,
      name: 'chromium', product: 'chromium', version: '151.0.1', playwright: '1.62.1',
      revision: '1234', executable_locator: 'chromium@1234/chrome-linux64/chrome',
      executable_sha256: crypto.createHash('sha256').update('locked chromium executable\n').digest('hex'),
      executable_bytes: Buffer.byteLength('locked chromium executable\n'),
    });
    assert.match(locked.payload_sha256, /^[0-9a-f]{64}$/);
    assert.equal(locked.payload_bytes, locked.executable_bytes);
    assert.equal(locked.payload_files, 1);
    assert.equal(contract.validateBrowserIdentity(locked, locked, locked).passed, true);
    const legacyV1 = { ...locked, schema: 'playwright-browser/v1' };
    delete legacyV1.payload_sha256;
    delete legacyV1.payload_bytes;
    delete legacyV1.payload_files;
    assert.equal(contract.validateBrowserIdentity(legacyV1, locked, legacyV1).passed, false);
    for (const mutation of [
      { product: 'chromium-headless-shell' }, { revision: '9999' },
      { executable_locator: 'chromium@1234/elsewhere/chrome' },
      { executable_sha256: '0'.repeat(64) }, { executable_bytes: locked.executable_bytes + 1 },
      { payload_sha256: '0'.repeat(64) }, { payload_bytes: locked.payload_bytes + 1 },
      { payload_files: locked.payload_files + 1 },
    ]) {
      assert.equal(contract.validateBrowserIdentity({ ...locked, ...mutation }, locked).passed, false);
    }
    assert.equal(contract.validateBrowserIdentity({ ...locked, invented: true }, locked).passed, false);
    const partialObserved = { name: 'chromium', version: locked.version,
      playwright: locked.playwright };
    assert.equal(contract.validateBrowserIdentity(locked, locked, partialObserved).passed, false);

    const payloadOnly = path.join(root, 'cache', 'chromium-1234', 'payload.dat');
    fs.writeFileSync(payloadOnly, 'browser payload outside launcher\n');
    const changedPayload = contract.lockedBrowserIdentity(root, executable);
    assert.equal(changedPayload.executable_sha256, locked.executable_sha256);
    assert.notEqual(changedPayload.payload_sha256, locked.payload_sha256);
    assert.equal(changedPayload.payload_files, locked.payload_files + 1);
    fs.rmSync(payloadOnly);

    const shell = path.join(root, 'cache', 'chromium_headless_shell-1234',
      'chrome-headless-shell-linux64', 'chrome-headless-shell');
    fs.mkdirSync(path.dirname(shell), { recursive: true });
    fs.writeFileSync(shell, 'locked shell executable\n');
    const shellIdentity = contract.lockedBrowserIdentity(root, shell);
    assert.equal(shellIdentity.product, 'chromium-headless-shell');
    assert.equal(shellIdentity.executable_locator,
      'chromium-headless-shell@1234/chrome-headless-shell-linux64/chrome-headless-shell');
    const custom = path.join(root, 'custom-chrome');
    fs.writeFileSync(custom, 'custom\n');
    assert.throws(() => contract.lockedBrowserIdentity(root, custom), /one locked Chromium product/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('reusable WebKit identity hashes the launcher and the engine payload independently', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-webkit-identity-'));
  try {
    fs.mkdirSync(path.join(root, 'node_modules', 'playwright-core'), { recursive: true });
    fs.writeFileSync(path.join(root, 'package-lock.json'), JSON.stringify({ packages: {
      'node_modules/playwright': { version: '1.62.1' },
    } }));
    fs.writeFileSync(path.join(root, 'node_modules/playwright-core/browsers.json'), JSON.stringify({
      browsers: [{ name: 'webkit', revision: '2336', browserVersion: '26.5',
        revisionOverrides: { 'ubuntu20.04-x64': '2092' } }],
    }));
    const registry = path.join(root, 'cache', 'webkit-2336');
    const launcher = path.join(registry, 'pw_run.sh');
    const engine = path.join(registry, 'minibrowser-wpe', 'bin', 'MiniBrowser');
    fs.mkdirSync(path.dirname(engine), { recursive: true });
    fs.writeFileSync(launcher, '#!/bin/sh\nexec MiniBrowser "$@"\n');
    fs.writeFileSync(engine, 'locked WebKit engine\n');

    const locked = contract.lockedPlaywrightBrowserIdentity(root, 'webkit', launcher);
    assert.equal(locked.schema, contract.BROWSER_IDENTITY_SCHEMA);
    assert.equal(locked.name, 'webkit');
    assert.equal(locked.product, 'webkit');
    assert.equal(locked.version, '26.5');
    assert.equal(locked.playwright, '1.62.1');
    assert.equal(locked.revision, '2336');
    assert.equal(locked.executable_locator, 'webkit@2336/pw_run.sh');
    assert.equal(locked.executable_sha256,
      crypto.createHash('sha256').update('#!/bin/sh\nexec MiniBrowser "$@"\n').digest('hex'));
    assert.equal(locked.payload_files, 2);
    assert.equal(locked.payload_bytes,
      Buffer.byteLength('#!/bin/sh\nexec MiniBrowser "$@"\nlocked WebKit engine\n'));
    assert.match(locked.payload_sha256, /^[0-9a-f]{64}$/);
    assert.equal(contract.validateBrowserIdentity(locked, locked, locked).passed, true);

    fs.writeFileSync(engine, 'altered WebKit engine\n');
    const altered = contract.lockedPlaywrightBrowserIdentity(root, 'webkit', launcher);
    assert.equal(altered.executable_sha256, locked.executable_sha256);
    assert.notEqual(altered.payload_sha256, locked.payload_sha256);
    assert.equal(contract.validateBrowserIdentity(altered, locked, altered).passed, false);

    const overrideLauncher = path.join(root, 'cache', 'webkit-2092', 'pw_run.sh');
    fs.mkdirSync(path.dirname(overrideLauncher), { recursive: true });
    fs.writeFileSync(overrideLauncher, '#!/bin/sh\noverride\n');
    const override = contract.lockedPlaywrightBrowserIdentity(root, 'webkit', overrideLauncher);
    assert.equal(override.revision, '2092');
    assert.equal(override.executable_locator, 'webkit@2092/pw_run.sh');

    const custom = path.join(root, 'custom-webkit');
    fs.writeFileSync(custom, 'custom\n');
    assert.throws(() => contract.lockedPlaywrightBrowserIdentity(root, 'webkit', custom),
      /one locked WebKit product/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('browser payload digest is deterministic and rejects escaping symlinks', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'browser-payload-tree-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'browser-payload-outside-'));
  try {
    const payload = path.join(root, 'webkit-2336');
    fs.mkdirSync(path.join(payload, 'lib'), { recursive: true });
    fs.writeFileSync(path.join(payload, 'lib', 'engine.so'), 'engine\n');
    fs.symlinkSync('engine.so', path.join(payload, 'lib', 'engine-current.so'));
    const first = contract.browserPayloadEvidence(payload);
    const second = contract.browserPayloadEvidence(payload);
    assert.deepEqual(second, first);
    assert.equal(first.payload_files, 1);
    assert.equal(first.payload_bytes, Buffer.byteLength('engine\n'));

    fs.writeFileSync(path.join(outside, 'escape.so'), 'outside\n');
    fs.symlinkSync(path.join(outside, 'escape.so'), path.join(payload, 'escape.so'));
    assert.throws(() => contract.browserPayloadEvidence(payload), /symlink escapes/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  }
});

test('deep-link and route-override semantics are bound to manifest targets and raw presentation', () => {
  const plan = contract.buildExpectedAuditPlan(ROOT);
  const deepLinks = { mode: 'fresh-professor-deep-links', errors: [], passed: true,
    records: plan.deepLinkTargets.map(expected => {
      const scope = expected.route === 'OPTIONAL' ? 'ALL' : 'LIVE+REQUIRED';
      const target = { lesson: expected.lesson, scene: expected.scene, stage: expected.stage,
        sceneRoute: expected.sceneRoute, stageRoute: expected.route,
        durationMinutes: expected.durationMinutes };
      const hash = `#${encodeURIComponent(expected.scene)}/${encodeURIComponent(expected.stage)}`;
      return { route: expected.route, lesson: expected.lesson, target, expectedScope: scope,
        state: snapshotFixture(expected, scope, 'desktop'), freshContext: true,
        storageInitiallyEmpty: true, requestedHash: hash, observedHash: hash,
        errors: [], passed: true };
    }) };
  assert.equal(contract.recordSemantics(deepLinks, 'fresh-professor-deep-links', plan, ROOT), true);
  const contaminated = structuredClone(deepLinks);
  contaminated.records[0].storageInitiallyEmpty = false;
  assert.equal(contract.recordSemantics(
    contaminated, 'fresh-professor-deep-links', plan, ROOT), false);
  const redirected = structuredClone(deepLinks);
  redirected.records[0].observedHash = '#forged/stage';
  assert.equal(contract.recordSemantics(redirected, 'fresh-professor-deep-links', plan, ROOT), false);

  const overrides = { mode: 'route-overrides', expected: plan.overrideTargets.length,
    declared: plan.overrideTargets.length, visible: plan.overrideTargets.length,
    errors: [], passed: true,
    records: plan.overrideTargets.map(expected => {
      const scope = expected.route === 'OPTIONAL' ? 'ALL' : 'LIVE+REQUIRED';
      const target = { ...expected, stageRoute: expected.route };
      return { lesson: expected.lesson, scene: expected.scene, stage: expected.stage,
        sceneRoute: expected.sceneRoute, effectiveRoute: expected.route,
        durationMinutes: expected.durationMinutes,
        desktop: snapshotFixture(target, scope, 'desktop'),
        mobile: snapshotFixture(target, scope, 'mobile'),
        teacher: { visible: true, visibility: { effectiveOpacity: 1,
          positiveArea: true, unoccluded: true },
        kicker: `${expected.route} · ${expected.type} · ${expected.durationMinutes} min`,
        override: `Ruta efectiva ${expected.route}; la escena declara ${expected.sceneRoute}.`, routeVisible: true,
        overrideVisible: true, durationVisible: true },
        errors: [], passed: true };
    }) };
  assert.equal(contract.recordSemantics(overrides, 'route-overrides', plan, ROOT), true);
  const wrongDuration = structuredClone(overrides);
  wrongDuration.records[0].durationMinutes += 1;
  assert.equal(contract.recordSemantics(wrongDuration, 'route-overrides', plan, ROOT), false);
  const forgedPresentation = structuredClone(overrides);
  forgedPresentation.records[0].desktop.presentation.badge = 'FORGED';
  assert.equal(contract.recordSemantics(forgedPresentation, 'route-overrides', plan, ROOT), false);
  const occludedTeacher = structuredClone(overrides);
  occludedTeacher.records[0].teacher.visibility.unoccluded = false;
  assert.equal(contract.recordSemantics(occludedTeacher, 'route-overrides', plan, ROOT), false);
});

test('success evidence requires the exact visual and negative-fixture screenshots', () => {
  const audit = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-screenshot-contract-'));
  try {
    const visuals = contract.VISUAL_SAMPLES.map(sample => ({
      mode: 'visual-sample', sample, screenshot: `visual-${sample}-l1-scene.png`,
    }));
    const names = ['fixture-intermediate-overflow-detected.png',
      ...visuals.map(record => record.screenshot)];
    names.forEach(name => fs.writeFileSync(path.join(audit, name), solidPng(
      name.startsWith('fixture-') ? 1280 : 1440, name.startsWith('fixture-') ? 720 : 900)));
    const summary = { screenshots: names, results: visuals,
      screenshot_evidence: contract.screenshotEvidence(audit, names) };
    assert.equal(validator.validateScreenshots(summary, audit).passed, true);

    assert.equal(validator.validateScreenshots({ screenshots: [], results: visuals }, audit).passed, false);
    fs.rmSync(path.join(audit, names[0]));
    assert.equal(validator.validateScreenshots(summary, audit).passed, false);
  } finally {
    fs.rmSync(audit, { recursive: true, force: true });
  }
});

test('screenshot validation rejects empty and malformed PNG evidence', () => {
  const audit = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-empty-png-'));
  try {
    const visuals = contract.VISUAL_SAMPLES.map(sample => ({ mode: 'visual-sample', sample,
      screenshot: `visual-${sample}-l1-scene.png` }));
    const names = ['fixture-intermediate-overflow-detected.png',
      ...visuals.map(record => record.screenshot)];
    names.forEach(name => fs.writeFileSync(path.join(audit, name), Buffer.alloc(0)));
    const summary = { screenshots: names, results: visuals, screenshot_evidence: [] };
    const result = validator.validateScreenshots(summary, audit);
    assert.equal(result.passed, false);
    assert.match(result.pngError, /PNG signature/);
    fs.writeFileSync(path.join(audit, names[0]), Buffer.from('png'));
    assert.equal(validator.validateScreenshots(summary, audit).passed, false);
    const forgedHeader = solidPng(1, 1);
    forgedHeader.writeUInt32BE(1280, 16);
    const typeAndData = forgedHeader.subarray(12, 29);
    forgedHeader.writeUInt32BE(contract.crc32(typeAndData), 29);
    assert.throws(() => contract.parsePngBuffer(forgedHeader), /pixel stream/);

    const oversizedDeclaration = declaredPng(8192, 8192, Buffer.alloc(1));
    assert.throws(() => contract.parsePngBuffer(oversizedDeclaration), /safety limit/);
    const inflatedPastDeclaredRow = declaredPng(1, 1, Buffer.alloc(1024));
    assert.throws(() => contract.parsePngBuffer(inflatedPastDeclaredRow), /IDAT stream/);
  } finally {
    fs.rmSync(audit, { recursive: true, force: true });
  }
});

test('input evidence contains exactly 32 files including index and L15', () => {
  const evidence = contract.inputEvidence(ROOT);
  assert.equal(evidence.files.length, 32);
  assert.equal(new Set(evidence.files.map(item => item.path)).size, 32);
  assert.ok(evidence.files.some(item => item.path === 'index.html'));
  assert.ok(evidence.files.some(item => item.path === '15-final-exam/examen.html'));
  assert.equal(contract.validateInputEvidence(evidence, ROOT).passed, true);

  for (const target of ['index.html', '15-final-exam/examen.html']) {
    const tampered = structuredClone(evidence);
    tampered.files.find(item => item.path === target).sha256 = '0'.repeat(64);
    assert.equal(contract.validateInputEvidence(tampered, ROOT).passed, false);
  }
  const omitted = structuredClone(evidence);
  omitted.files = omitted.files.filter(item => item.path !== 'index.html');
  assert.equal(contract.validateInputEvidence(omitted, ROOT).passed, false);
  const duplicated = structuredClone(evidence);
  duplicated.files[0] = structuredClone(duplicated.files[1]);
  assert.equal(contract.validateInputEvidence(duplicated, ROOT).passed, false);
});

test('source SHA rejects a CI value different from checked-out HEAD', () => {
  assert.throws(() => contract.sourceHead(ROOT, '0'.repeat(40)), /does not match/);
});

test('bootstrap SHA failure replaces stale green evidence with one incomplete artifact', () => {
  const parent = path.join(ROOT, 'artifacts');
  fs.mkdirSync(parent, { recursive: true });
  const audit = fs.mkdtempSync(path.join(parent, 'desktop-bootstrap-test-'));
  try {
    fs.rmSync(audit, { recursive: true });
    contract.prepareAuditDirectory(ROOT, audit);
    fs.writeFileSync(path.join(audit, 'desktop-audit.json'), '{"passed":true}\n');
    const run = spawnSync(process.execPath,
      [path.join(ROOT, 'framework/_build/desktop_e2e.js'), '--audit-dir', audit], {
        cwd: ROOT, encoding: 'utf8',
        env: { ...process.env, GITHUB_SHA: '0'.repeat(40) },
      });
    assert.equal(run.status, 1);
    assert.equal(fs.existsSync(path.join(audit, 'desktop-audit.json')), false);
    const names = fs.readdirSync(audit).sort();
    assert.deepEqual(names, [contract.AUDIT_OWNER_FILE, 'desktop-audit-incomplete.json'].sort());
    const incomplete = JSON.parse(fs.readFileSync(
      path.join(audit, 'desktop-audit-incomplete.json'), 'utf8'));
    assert.equal(incomplete.completed, false);
    assert.equal(incomplete.passed, false);
    assert.equal(incomplete.phase, 'source-sha');
  } finally {
    fs.rmSync(audit, { recursive: true, force: true });
  }
});

test('bootstrap fails at provenance when tracked inputs are missing', () => {
  const fixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'desktop-bootstrap-repo-'));
  const copy = relative => {
    const target = path.join(fixtureRoot, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(ROOT, relative), target);
  };
  try {
    [
      'framework/_build/desktop_e2e.js',
      'framework/_build/desktop_evidence_contract.js',
      'framework/_build/doc_assets/learning_runtime.js',
      '15-final-exam/examen.html',
      'index.html',
    ].forEach(copy);
    for (let number = 1; number <= 14; number++) {
      copy(`pedagogy/lessons/${String(number).padStart(2, '0')}.yml`);
    }
    const documents = contract.discoverLessons(ROOT);
    documents.forEach(item => {
      const target = path.join(fixtureRoot, item.relative);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.writeFileSync(target, '<!doctype html><title>fixture</title>\n');
    });
    for (const args of [
      ['init', '-q'], ['add', '.'],
      ['-c', 'user.name=Audit Fixture', '-c', 'user.email=audit@example.invalid',
        'commit', '-qm', 'fixture'],
    ]) {
      const git = spawnSync('git', args, { cwd: fixtureRoot, encoding: 'utf8' });
      assert.equal(git.status, 0, git.stderr);
    }
    const environment = { ...process.env };
    delete environment.GITHUB_SHA;
    const runFailure = (missing, phase) => {
      const source = path.join(fixtureRoot, missing);
      const contents = fs.readFileSync(source);
      fs.rmSync(source);
      const audit = path.join(fixtureRoot, 'artifacts', `missing-${phase}`);
      contract.prepareAuditDirectory(fixtureRoot, audit);
      fs.writeFileSync(path.join(audit, 'desktop-audit.json'), '{"passed":true}\n');
      const run = spawnSync(process.execPath,
        [path.join(fixtureRoot, 'framework/_build/desktop_e2e.js'), '--audit-dir', audit], {
          cwd: fixtureRoot, encoding: 'utf8', env: environment,
        });
      assert.equal(run.status, 1);
      assert.deepEqual(fs.readdirSync(audit).sort(),
        [contract.AUDIT_OWNER_FILE, 'desktop-audit-incomplete.json'].sort());
      const incomplete = JSON.parse(fs.readFileSync(
        path.join(audit, 'desktop-audit-incomplete.json'), 'utf8'));
      assert.equal(incomplete.phase, phase);
      assert.equal(incomplete.completed, false);
      fs.mkdirSync(path.dirname(source), { recursive: true });
      fs.writeFileSync(source, contents);
    };
    runFailure('index.html', 'source-sha');
    runFailure(documents[0].relative, 'source-sha');
  } finally {
    fs.rmSync(fixtureRoot, { recursive: true, force: true });
  }
});

test('workflow installs the lockfile and validates evidence before fail-closed upload', () => {
  const workflow = fs.readFileSync(path.join(ROOT, '.github/workflows/course.yml'), 'utf8');
  const desktopRun = workflow.indexOf('node framework/_build/desktop_e2e.js');
  const independentValidation = workflow.indexOf('node framework/_build/validate_desktop_audit.js');
  const upload = workflow.indexOf('actions/upload-artifact@');
  assert.ok(workflow.includes('npm ci'));
  assert.ok(!workflow.includes('npm install --no-save'));
  assert.match(workflow, /validate_desktop_audit\.js --verify-browser/);
  assert.match(workflow, /requirements-pages-lock\.txt/);
  assert.ok(desktopRun >= 0 && desktopRun < independentValidation && independentValidation < upload);
  assert.match(workflow.slice(Math.max(0, independentValidation - 180), independentValidation),
    /if: always\(\)/);
  const uploadStep = workflow.slice(workflow.lastIndexOf('\n      - name:', upload),
    workflow.indexOf('\n      - name:', upload + 1));
  assert.match(uploadStep, /if: success\(\)[\s\S]*if-no-files-found: error/);
  assert.match(workflow.slice(upload), /if: failure\(\)[\s\S]*if-no-files-found: warn/);

  const packageJson = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
  const packageLock = JSON.parse(fs.readFileSync(path.join(ROOT, 'package-lock.json'), 'utf8'));
  assert.equal(packageJson.engines.node, '20.19.4');
  assert.equal(packageJson.devDependencies.playwright, '1.62.1');
  assert.equal(packageLock.packages['node_modules/playwright'].version, '1.62.1');

  const pagesWorkflow = fs.readFileSync(path.join(ROOT, '.github/workflows/pages.yml'), 'utf8');
  assert.ok((pagesWorkflow.match(/npm ci/g) || []).length >= 2);
  assert.ok(!pagesWorkflow.includes('npm install --no-save'));
});

test('runtime assets retain modal, scroller, and breakpoint arbitration', () => {
  const runtime = fs.readFileSync(
    path.join(ROOT, 'framework/_build/doc_assets/learning_runtime.js'), 'utf8');
  const styles = fs.readFileSync(
    path.join(ROOT, 'framework/_build/doc_assets/learning_runtime.css'), 'utf8');
  const docgen = fs.readFileSync(path.join(ROOT, 'framework/_build/docgen.py'), 'utf8');
  assert.match(styles, /body\.lr-modal-open::before\{[^}]*z-index:69/);
  assert.match(styles, /body\.mode-aula>\.lr-scene-active>\.scrolly\{display:grid/);
  assert.match(runtime, /window\.LEARNING_MODAL_BACKGROUND=setModalBackground/);
  assert.match(runtime, /window\.GUIDE_DRAWER\?\.close\(\{restoreFocus:false\}\)/);
  assert.ok(runtime.indexOf('if(openDrawer){') < runtime.indexOf("move(1,true)"));
  assert.ok(runtime.indexOf('if(scrollerOwnsKey(active,event.key))return;')
    < runtime.indexOf("move(1,true)"));
  assert.ok(docgen.indexOf("classList.contains('lr-modal-open')")
    < docgen.indexOf("['ArrowDown','ArrowUp','PageDown','PageUp']"));
  assert.ok(docgen.indexOf("closest('[data-lr-scroller=\"true\"]')")
    < docgen.indexOf('e.preventDefault();'));
  assert.match(docgen, /window\.LEARNING_TEACHER_DRAWER\?\.close\(\{restoreFocus:false\}\)/);
  assert.doesNotMatch(docgen, /event\.key==='Escape'/);
});

test('smoke isolates persisted study state from fresh classroom traversal', () => {
  const smoke = fs.readFileSync(path.join(ROOT, 'framework/_build/e2e_check.js'), 'utf8');
  assert.match(smoke, /const studyDesktop = await browser\.newContext/);
  assert.match(smoke, /const aulaDesktop = await browser\.newContext/);
  assert.match(smoke, /const studyPage = await studyDesktop\.newPage\(\)/);
  assert.match(smoke, /const aulaPage = await aulaDesktop\.newPage\(\)/);
  assert.doesNotMatch(smoke, /const desktop = await browser\.newContext/);
});

test('runner and independent replay retain clean navigation, full plans, deterministic visuals, and both stage surfaces', () => {
  const runner = fs.readFileSync(path.join(ROOT, 'framework/_build/desktop_e2e.js'), 'utf8');
  const replay = fs.readFileSync(
    path.join(ROOT, 'framework/_build/validate_desktop_audit.js'), 'utf8');
  const prepareStart = runner.indexOf('async function prepare(');
  const traverseStart = runner.indexOf('async function traverse(', prepareStart);
  assert.ok(prepareStart >= 0 && traverseStart > prepareStart);
  const prepare = runner.slice(prepareStart, traverseStart);
  assert.match(prepare, /localStorage\.clear\(\)[\s\S]*history\.replaceState/);
  assert.ok(prepare.indexOf('history.replaceState') < prepare.indexOf('page.reload()'));
  assert.doesNotMatch(runner, /\.slice\(0,\s*48\)/);
  assert.doesNotMatch(replay, /\.slice\(0,\s*48\)/);
  assert.match(runner,
    /\{ present: false, applicable: false, passed: false \}/);
  assert.match(runner,
    /drawers\.guide\.present && drawers\.guide\.passed/);

  const visualStart = runner.indexOf('async function visualAudit(');
  const visualEnd = runner.indexOf('async function indexAudit(', visualStart);
  const visual = runner.slice(visualStart, visualEnd);
  assert.match(visual, /newContext\(\{ viewport, reducedMotion: 'reduce' \}\)/);
  assert.match(visual, /addInitScript\(evidenceContract\.VISUAL_AUDIT_INIT_SCRIPT\)/);
  assert.match(replay, /reducedMotion: 'reduce'/);
  assert.match(replay, /addInitScript\(contract\.VISUAL_AUDIT_INIT_SCRIPT\)/);

  assert.match(runner, /\[activeStep, activeFigure\]\.filter\(Boolean\)/);
  assert.match(replay, /\[(?:activeStep|step),\s*(?:activeFigure|figure)\]\.filter\(Boolean\)/);
});
