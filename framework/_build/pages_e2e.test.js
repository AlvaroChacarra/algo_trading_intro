const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const evidenceContract = require('./desktop_evidence_contract');

const {
  browserErrorText,
  countMarkerOccurrences,
  createRuntimeFailureMonitor,
  evidenceTargetIdentity,
  executeSmokeOnce,
  installOfflineRouting,
  installWorkerDiagnostics,
  isCleanLabResult,
  isAllowedOfflineRequest,
  isRuntimeDiagnosticUrl,
  labTargetsForLessons,
  launchExactWebKit,
  parseArguments,
  parseKernelExecutionPrompt,
  resolveRunPlan,
  retryInFreshContexts,
  validatePagesEvidence,
  writePagesEvidenceAtomic,
} = require('./pages_e2e');

const lessons = Array.from({ length: 14 }, (_, index) => ({
  number: index + 1,
  relative: `${String(index + 1).padStart(2, '0')}-lesson/presentation/lesson-doc.html`,
}));

function fakeWebKitIdentity() {
  return {
    schema: 'playwright-browser/v2',
    name: 'webkit',
    product: 'webkit',
    version: '26.5',
    playwright: '1.62.1',
    revision: '2336',
    executable_locator: 'webkit@2336/pw_run.sh',
    executable_sha256: 'a'.repeat(64),
    executable_bytes: 3049,
    payload_sha256: 'b'.repeat(64),
    payload_bytes: 306401261,
    payload_files: 37,
  };
}

function completeEvidence() {
  const browser = fakeWebKitIdentity();
  const labAttempt = notebook => ({
    reason: '', staticOk: true, responseOk: true, status: 200,
    labPath: '/algo_trading_intro/jupyter/lab/index.html',
    expectedNotebook: notebook, requestedNotebook: notebook, documentNameMatches: true,
    codeCells: 4, kernelReady: true, dispatchCount: 1, kernelPromptCount: 1,
    kernelExecutionCount: 1, markerSeen: true, markerOccurrences: 1,
    markerSha256: 'e'.repeat(64), kernelIdle: true, stderr: false, labHome: 1,
    pageErrors: [], externalRequests: [],
  });
  const target = (id, notebook) => ({
    kind: 'lab', id, passed: true,
    outcome: { failures: 0, successfulAttempt: 1, attempts: [labAttempt(notebook)] },
  });
  return {
    schema: 'pages-e2e-evidence/v1',
    started_at: '2026-08-28T00:00:00.000Z',
    completed_at: '2026-08-28T00:01:00.000Z',
    failed_at: null,
    source_sha: 'c'.repeat(40),
    integrity_sha256: 'd'.repeat(64),
    browser,
    locked_browser: browser,
    browser_validation: evidenceContract.validateBrowserIdentity(browser, browser, browser),
    scope: { runSite: false, labLessons: [8] },
    targets: [
      target('L8-build', '08-order-types-matching/exercises/08_build_exercises.ipynb'),
      target('L8-auxiliary', '08-order-types-matching/exercises/08_auxiliary.ipynb'),
    ],
    outcome: { completed: true, passed: true, failures: 0, error: null },
  };
}

test('CLI and environment select one explicit evidence path without ambiguity', () => {
  const cwd = path.resolve('/tmp/pages-e2e-cli');
  assert.deepEqual(parseArguments([
    'built-site', '--evidence', 'artifacts/pages-e2e/lab-08.json',
  ], {}, cwd), {
    site: path.join(cwd, 'built-site'),
    evidencePath: path.join(cwd, 'artifacts/pages-e2e/lab-08.json'),
  });
  assert.equal(parseArguments(['built-site'], {
    WORK2_PAGES_EVIDENCE: 'artifacts/pages-e2e/site.json',
  }, cwd).evidencePath, path.join(cwd, 'artifacts/pages-e2e/site.json'));
  assert.throws(() => parseArguments(['--evidence'], {}, cwd), /requires an explicit JSON path/);
  assert.throws(() => parseArguments(['site', '--unknown'], {}, cwd), /unknown Pages E2E option/);
  assert.throws(() => parseArguments([
    'site', '--evidence', 'a.json',
  ], { WORK2_PAGES_EVIDENCE: 'b.json' }, cwd), /mutually exclusive/);
});

test('WebKit lock and full-payload identity are established before exact launch validation', async t => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-webkit-launch-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const launcher = path.join(directory, 'pw_run.sh');
  fs.writeFileSync(launcher, '#!/bin/sh\n');
  const identity = fakeWebKitIdentity();
  const events = [];
  const browser = {
    browserType: () => ({ name: () => 'webkit' }),
    version: () => '26.5',
    close: async () => events.push('close'),
  };
  const contract = {
    lockedPlaywrightBrowserIdentity: (root, name, executable) => {
      events.push('lock');
      assert.equal(root, directory);
      assert.equal(name, 'webkit');
      assert.equal(executable, launcher);
      return identity;
    },
    validateBrowserIdentity: (declared, locked, observed) => {
      events.push('validate');
      assert.deepEqual(locked, identity);
      assert.deepEqual(declared, observed);
      return evidenceContract.validateBrowserIdentity(declared, locked, observed);
    },
  };
  const webkit = {
    executablePath: () => launcher,
    launch: async options => {
      events.push('launch');
      assert.deepEqual(options, { executablePath: launcher });
      return browser;
    },
  };
  const phases = [];
  const result = await launchExactWebKit(webkit, {
    root: directory,
    contract,
    playwrightVersion: '1.62.1',
    onPhase: phase => phases.push(phase),
  });
  assert.equal(result.validation.passed, true);
  assert.deepEqual(events, ['lock', 'launch', 'validate']);
  assert.deepEqual(phases, ['browser-identity', 'browser-launch', 'browser-validation']);
  await result.browser.close();
  assert.deepEqual(events, ['lock', 'launch', 'validate', 'close']);
});

test('WebKit is closed when observed identity collection or validation fails', async t => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-webkit-close-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const launcher = path.join(directory, 'pw_run.sh');
  fs.writeFileSync(launcher, '#!/bin/sh\n');
  let closes = 0;
  const webkit = {
    executablePath: () => launcher,
    launch: async () => ({
      browserType: () => { throw new Error('identity probe failed'); },
      version: () => '26.5',
      close: async () => { closes += 1; },
    }),
  };
  await assert.rejects(() => launchExactWebKit(webkit, {
    root: directory,
    contract: {
      lockedPlaywrightBrowserIdentity: () => fakeWebKitIdentity(),
      validateBrowserIdentity: () => { throw new Error('must not be reached'); },
    },
    playwrightVersion: '1.62.1',
  }), /identity probe failed/);
  assert.equal(closes, 1);
});

test('nonce cardinality and kernel prompt parsing are exact and fail closed', () => {
  const marker = 'WORK2_L8_OK_0123456789abcdef';
  assert.equal(countMarkerOccurrences(['noise', marker, `${marker}\n${marker}`], marker), 3);
  assert.equal(countMarkerOccurrences(['WORK2_L8_OK'], marker), 0);
  assert.throws(() => countMarkerOccurrences([null], marker), /must be a string/);
  assert.equal(parseKernelExecutionPrompt('[1]:'), 1);
  assert.equal(parseKernelExecutionPrompt(' [ 42 ] '), 42);
  for (const prompt of ['[*]:', '[]:', '[0]:', '[1,2]:', '1', '', null]) {
    assert.equal(parseKernelExecutionPrompt(prompt), null);
  }
});

test('evidence writer confines, validates, atomically publishes, and never overwrites', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-evidence-root-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const evidence = completeEvidence();
  assert.equal(validatePagesEvidence(evidence).passed, true);
  const target = path.join(root, 'artifacts', 'pages-e2e', 'lab-08.json');
  assert.equal(evidenceTargetIdentity(root, target).target, target);
  assert.equal(writePagesEvidenceAtomic(root, target, evidence), target);
  assert.deepEqual(JSON.parse(fs.readFileSync(target, 'utf8')), evidence);
  assert.throws(() => writePagesEvidenceAtomic(root, target, evidence), /refusing to overwrite/);
  assert.throws(() => evidenceTargetIdentity(root, path.join(root, 'outside.json')), /unsafe/);
  assert.throws(() => evidenceTargetIdentity(
    root, path.join(root, 'artifacts', 'pages-e2e', 'nested', 'x.json'),
  ), /unsafe/);
  const altered = { ...evidence, browser: { ...evidence.browser, payload_sha256: 'e'.repeat(64) } };
  assert.equal(validatePagesEvidence(altered).passed, false);
  assert.equal(validatePagesEvidence({ ...evidence, targets: evidence.targets.slice(0, 1) }).passed, false);
  const duplicateNonce = structuredClone(evidence);
  duplicateNonce.targets[0].outcome.attempts[0].markerOccurrences = 2;
  assert.equal(validatePagesEvidence(duplicateNonce).passed, false);
  const wrongKind = structuredClone(evidence);
  wrongKind.targets[0].kind = 'site';
  assert.equal(validatePagesEvidence(wrongKind).passed, false);
});

test('evidence path rejects a symlinked artifacts ancestor', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-evidence-symlink-root-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-evidence-symlink-out-'));
  t.after(() => {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  });
  fs.symlinkSync(outside, path.join(root, 'artifacts'), 'dir');
  assert.throws(() => evidenceTargetIdentity(
    root, path.join(root, 'artifacts', 'pages-e2e', 'site.json'),
  ), /unsafe Pages evidence directory/);
});

test('offline routing permits local/data/blob/about and blocks every remote origin', async () => {
  let handler = null;
  let webSocketHandler = null;
  const context = {
    route: async (pattern, callback) => {
      assert.equal(pattern, '**/*');
      handler = callback;
    },
    routeWebSocket: async (pattern, callback) => {
      assert.ok(pattern instanceof RegExp);
      webSocketHandler = callback;
    },
  };
  const external = await installOfflineRouting(
    context, 'http://127.0.0.1:4321/algo_trading_intro/',
  );
  assert.equal(typeof handler, 'function');
  assert.equal(typeof webSocketHandler, 'function');
  assert.equal(isAllowedOfflineRequest(
    'http://127.0.0.1:4321/algo_trading_intro/index.html', 'http://127.0.0.1:4321',
  ), true);
  assert.equal(isAllowedOfflineRequest(
    'https://cdn.example/x.js', 'http://127.0.0.1:4321',
  ), false);
  assert.equal(isAllowedOfflineRequest(
    'ws://127.0.0.1:4321/kernel', 'http://127.0.0.1:4321',
  ), true);

  const events = [];
  const dispatch = async requestUrl => handler({
    request: () => ({ url: () => requestUrl }),
    continue: async () => events.push(`continue:${requestUrl}`),
    abort: async reason => events.push(`abort:${reason}:${requestUrl}`),
  });
  for (const requestUrl of [
    'http://127.0.0.1:4321/algo_trading_intro/index.html',
    'data:text/plain,ok',
    'blob:http://127.0.0.1:4321/1234',
    'about:blank',
  ]) await dispatch(requestUrl);
  for (const requestUrl of [
    'https://cdn.example/x.js',
    'http://127.0.0.1:9999/other-origin',
  ]) await dispatch(requestUrl);

  const dispatchWebSocket = async requestUrl => webSocketHandler({
    url: () => requestUrl,
    connectToServer: () => events.push(`connect:${requestUrl}`),
    close: async options => events.push(`close:${options.code}:${requestUrl}`),
  });
  await dispatchWebSocket('ws://127.0.0.1:4321/kernel');
  await dispatchWebSocket('wss://stream.example/quotes');

  assert.deepEqual(external, [
    'https://cdn.example/x.js',
    'http://127.0.0.1:9999/other-origin',
    'wss://stream.example/quotes',
  ]);
  assert.equal(events.filter(event => event.startsWith('continue:')).length, 4);
  assert.equal(events.filter(event => event.startsWith('abort:blockedbyclient:')).length, 2);
  assert.deepEqual(events.filter(event => event.startsWith('connect:')), [
    'connect:ws://127.0.0.1:4321/kernel',
  ]);
  assert.deepEqual(events.filter(event => event.startsWith('close:1008:')), [
    'close:1008:wss://stream.example/quotes',
  ]);
});

test('browser error diagnostics never collapse to undefined', () => {
  assert.equal(browserErrorText(new Error('worker failed')), 'worker failed');
  assert.equal(browserErrorText({ stack: 'worker stack' }), 'worker stack');
  assert.equal(browserErrorText(undefined), 'unknown browser error');
});

test('runtime startup errors fail fast and preserve the first cause', async () => {
  const monitor = createRuntimeFailureMonitor();
  monitor.fail('first startup failure');
  monitor.fail('later noise');
  await assert.rejects(monitor.promise, /first startup failure/);
});

test('runtime diagnostics select only kernel bootstrap resources', () => {
  assert.equal(isRuntimeDiagnosticUrl(
    'http://127.0.0.1:4321/jupyter/static/pyodide/ipython.whl',
  ), true);
  assert.equal(isRuntimeDiagnosticUrl(
    'http://127.0.0.1:4321/jupyter/pypi/all.json?sha256=abc',
  ), true);
  assert.equal(isRuntimeDiagnosticUrl(
    'http://127.0.0.1:4321/jupyter/extensions/x/static/comlink.worker.abc123.js',
  ), true);
  assert.equal(isRuntimeDiagnosticUrl(
    'http://127.0.0.1:4321/jupyter/lab/index.html',
  ), false);
});

test('worker diagnostics are installed before navigation', async () => {
  let installer = null;
  await installWorkerDiagnostics({
    addInitScript: async callback => { installer = callback; },
  });
  assert.equal(typeof installer, 'function');
});

test('WORK2_PAGES_LESSON selects exactly one lab shard and rejects bad input', () => {
  const plan = resolveRunPlan(lessons, {
    WORK2_PAGES_SCOPE: 'lab',
    WORK2_PAGES_LESSON: '8',
  });
  assert.equal(plan.runSite, false);
  assert.deepEqual(plan.labLessons.map(lesson => lesson.number), [8]);

  assert.throws(
    () => resolveRunPlan(lessons, { WORK2_PAGES_SCOPE: 'lab' }),
    /requires WORK2_PAGES_LESSON/,
  );
  assert.throws(
    () => resolveRunPlan(lessons, { WORK2_PAGES_LESSON: 'all' }),
    /must be an integer/,
  );
  assert.throws(
    () => resolveRunPlan(lessons, { WORK2_PAGES_LESSON: '15' }),
    /does not identify exactly one/,
  );
});

test('the 14 shards cover the exact 28-notebook core publication set', () => {
  const targets = labTargetsForLessons(lessons);
  assert.equal(targets.length, 28);
  assert.equal(new Set(targets.map(target => target.staticPath)).size, 28);
  assert.equal(new Set(targets.map(target => target.notebookPath)).size, 28);
  assert.equal(targets.filter(target => target.label.endsWith('-build')).length, 14);
  assert.equal(targets.filter(target => target.label.endsWith('-auxiliary')).length, 14);
  assert.ok(!targets.some(target => target.label === 'RFQ-annex'));
  for (let lesson = 1; lesson <= 14; lesson++) {
    const build = targets.find(target => target.label === `L${lesson}-build`);
    const auxiliary = targets.find(target => target.label === `L${lesson}-auxiliary`);
    assert.equal(auxiliary.smoke, build.smoke,
      `L${lesson} auxiliary must exercise its lesson-specific runtime surface`);
  }
});

test('the E2E server declares JavaScript MIME for Pyodide modules', () => {
  const source = fs.readFileSync(path.resolve(__dirname, 'pages_e2e.js'), 'utf8');
  assert.match(source, /'\.mjs': 'text\/javascript'/);
  assert.ok((source.match(/serviceWorkers: 'block'/g) || []).length >= 2);
});

test('one context sends exactly one execution after ready and waits for idle', async () => {
  const events = [];
  const executionState = {
    dispatchCount: 0,
    kernelReady: false,
    markerSeen: false,
    kernelIdle: false,
  };
  const page = {
    keyboard: {
      press: async key => events.push(`press:${key}`),
      insertText: async text => events.push(`text:${text}`),
    },
  };
  const editor = { click: async options => events.push(`click:${options.force}`) };
  const output = {
    waitFor: async options => events.push(`output:${options.state}:${options.timeout}`),
  };
  const waitForIdle = async (_page, options) => events.push(`idle:${options.stableMs}`);

  await executeSmokeOnce({
    page,
    editor,
    output,
    smoke: "print('WORK2_L8_OK')",
    selectAll: 'Control+A',
    executionState,
    kernelTimeout: 120000,
    outputTimeout: 90000,
    readyStableMs: 750,
    idleStableMs: 1500,
    waitForIdle,
  });

  assert.deepEqual(events, [
    'idle:750',
    'click:true',
    'press:Control+A',
    "text:print('WORK2_L8_OK')",
    'press:Shift+Enter',
    'output:visible:90000',
    'idle:1500',
  ]);
  assert.deepEqual(executionState, {
    dispatchCount: 1,
    kernelReady: true,
    markerSeen: true,
    kernelIdle: true,
  });
});

test('an output timeout never sends a second execution in the same context', async () => {
  const pressed = [];
  const executionState = {
    dispatchCount: 0,
    kernelReady: false,
    markerSeen: false,
    kernelIdle: false,
  };
  const page = {
    keyboard: {
      press: async key => pressed.push(key),
      insertText: async () => {},
    },
  };

  await assert.rejects(() => executeSmokeOnce({
    page,
    editor: { click: async () => {} },
    output: { waitFor: async () => { throw new Error('output timeout'); } },
    smoke: 'print(1)',
    selectAll: 'Control+A',
    executionState,
    kernelTimeout: 1,
    outputTimeout: 1,
    readyStableMs: 1,
    idleStableMs: 1,
    waitForIdle: async () => {},
  }), /output timeout/);

  assert.equal(pressed.filter(key => key === 'Shift+Enter').length, 1);
  assert.equal(executionState.dispatchCount, 1);
  assert.equal(executionState.kernelReady, true);
  assert.equal(executionState.markerSeen, false);
  assert.equal(executionState.kernelIdle, false);
});

test('a failed lesson retry uses and closes a new context', async () => {
  const events = [];
  let nextId = 0;
  const outcome = await retryInFreshContexts({
    createContext: async () => {
      const id = ++nextId;
      events.push(`create:${id}`);
      return { id, close: async () => events.push(`close:${id}`) };
    },
    runInContext: async context => {
      events.push(`run:${context.id}`);
      return { ok: context.id === 2, pageErrors: [] };
    },
    accepts: result => result.ok,
    maxAttempts: 2,
    onRetry: (_result, attempt) => events.push(`retry:${attempt}`),
  });

  assert.equal(outcome.passed, true);
  assert.equal(outcome.attempt, 2);
  assert.deepEqual(outcome.attempts.map(result => result.ok), [false, true]);
  assert.deepEqual(events, [
    'create:1', 'run:1', 'close:1', 'retry:1',
    'create:2', 'run:2', 'close:2',
  ]);
});

test('pageerror, duplicate dispatch/kernel execution, and nonce cardinality remain fail-closed', () => {
  const clean = {
    reason: '',
    staticOk: true,
    responseOk: true,
    labPath: '/algo_trading_intro/jupyter/lab/index.html',
    expectedNotebook: '08-order-types-matching/exercises/08_build_exercises.ipynb',
    requestedNotebook: '08-order-types-matching/exercises/08_build_exercises.ipynb',
    documentNameMatches: true,
    codeCells: 4,
    kernelReady: true,
    dispatchCount: 1,
    kernelPromptCount: 1,
    kernelExecutionCount: 1,
    markerSeen: true,
    markerOccurrences: 1,
    markerSha256: 'e'.repeat(64),
    kernelIdle: true,
    stderr: false,
    labHome: 1,
    pageErrors: [],
    externalRequests: [],
  };
  assert.equal(isCleanLabResult(clean), true);
  assert.equal(isCleanLabResult({ ...clean, pageErrors: ['PyProxy/GIL race'] }), false);
  assert.equal(isCleanLabResult({ ...clean, dispatchCount: 2 }), false);
  assert.equal(isCleanLabResult({ ...clean, kernelExecutionCount: 2 }), false);
  assert.equal(isCleanLabResult({ ...clean, kernelPromptCount: 2 }), false);
  assert.equal(isCleanLabResult({ ...clean, markerOccurrences: 0 }), false);
  assert.equal(isCleanLabResult({ ...clean, markerOccurrences: 2 }), false);
  assert.equal(isCleanLabResult({ ...clean, kernelIdle: false }), false);
  assert.equal(isCleanLabResult({ ...clean, externalRequests: ['https://cdn.invalid/x'] }), false);
});

test('the deployable Pages artifact is gated by every WebKit result', () => {
  const workflow = fs.readFileSync(
    path.resolve(__dirname, '../../.github/workflows/pages.yml'),
    'utf8',
  );
  assert.match(workflow, /on:\s*\n\s*push:\s*\n\s*pull_request:/);
  assert.doesNotMatch(workflow, /pages-site-\$\{\{ github\.run_id \}\}-\$\{\{ github\.run_attempt \}\}/);
  assert.ok((workflow.match(/pages-site-\$\{\{ github\.run_id \}\}/g) || []).length >= 4);
  assert.doesNotMatch(workflow,
    /pages-e2e-[^\n]*\$\{\{ github\.run_attempt \}\}/);
  assert.match(workflow, /name: pages-e2e-site-\$\{\{ github\.run_id \}\}/);
  assert.match(workflow,
    /name: pages-e2e-lab-\$\{\{ matrix\.lesson \}\}-\$\{\{ github\.run_id \}\}/);
  assert.match(workflow, /pattern: pages-e2e-\*-\$\{\{ github\.run_id \}\}/);
  assert.ok((workflow.match(/overwrite: true/g) || []).length >= 3);
  assert.match(workflow, /pip install --requirement requirements-pages-lock\.txt/);
  assert.match(workflow,
    /needs: \[course-contract, build, webkit-site, jupyterlite, pages-audit\]/);
  assert.match(workflow, /needs\.course-contract\.result == 'success'/);
  assert.match(workflow, /needs\.webkit-site\.result == 'success'/);
  assert.match(workflow, /needs\.jupyterlite\.result == 'success'/);
  assert.match(workflow, /needs\.pages-audit\.result == 'success'/);
  assert.match(workflow, /--aggregate artifacts\/pages-e2e/);
  assert.equal((workflow.match(/actions\/upload-pages-artifact@/g) || []).length, 1);
  const siteJob = workflow.slice(workflow.indexOf('\n  webkit-site:'),
    workflow.indexOf('\n  jupyterlite:'));
  assert.ok(siteJob.indexOf('node framework/_build/pages_e2e.js')
    < siteJob.indexOf('node framework/_build/validate_pages_audit.js'));
  assert.ok(siteJob.indexOf('node framework/_build/validate_pages_audit.js')
    < siteJob.indexOf('actions/upload-artifact@'));
  const labJob = workflow.slice(workflow.indexOf('\n  jupyterlite:'),
    workflow.indexOf('\n  pages-audit:'));
  assert.ok(labJob.indexOf('node framework/_build/pages_e2e.js')
    < labJob.indexOf('node framework/_build/validate_pages_audit.js'));
  assert.ok(labJob.indexOf('node framework/_build/validate_pages_audit.js')
    < labJob.indexOf('actions/upload-artifact@'));
  const aggregateJob = workflow.slice(workflow.indexOf('\n  pages-audit:'),
    workflow.indexOf('\n  package:'));
  assert.doesNotMatch(aggregateJob, /playwright install|npm ci/);
  const packageJob = workflow.slice(workflow.indexOf('\n  package:'), workflow.indexOf('\n  deploy:'));
  assert.match(packageJob, /actions\/upload-pages-artifact@[0-9a-f]{40} # v5\.0\.0/);
  const deployJob = workflow.slice(workflow.indexOf('\n  deploy:'));
  assert.match(deployJob, /github\.ref == 'refs\/heads\/main'/);
});

test('every third-party action is pinned to an immutable commit', () => {
  for (const workflowName of ['pages.yml', 'course.yml']) {
    const workflow = fs.readFileSync(
      path.resolve(__dirname, `../../.github/workflows/${workflowName}`),
      'utf8',
    );
    const actionRefs = [...workflow.matchAll(/uses:\s+actions\/[^@\s]+@([^\s#]+)/g)];
    assert.ok(actionRefs.length > 0, `${workflowName} should invoke actions`);
    for (const actionRef of actionRefs) {
      assert.match(actionRef[1], /^[0-9a-f]{40}$/, `${workflowName}: ${actionRef[0]}`);
    }
  }
});
