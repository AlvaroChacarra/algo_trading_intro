/* Mobile/WebKit acceptance test for the built Pages artifact and project base path. */
const fs = require('fs');
const http = require('http');
const path = require('path');
const crypto = require('crypto');
const evidenceContract = require('./desktop_evidence_contract');

const ROOT = path.resolve(__dirname, '..', '..');
const DEFAULT_SITE = path.resolve('_site');
const PAGES_EVIDENCE_SCHEMA = 'pages-e2e-evidence/v1';
const EVIDENCE_ENV = 'WORK2_PAGES_EVIDENCE';
const BASE = '/algo_trading_intro/';
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.mjs': 'text/javascript',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.wasm': 'application/wasm', '.woff2': 'font/woff2' };

function server(site = DEFAULT_SITE) {
  return http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (!pathname.startsWith(BASE)) { res.writeHead(404).end(); return; }
    let relative = pathname.slice(BASE.length);
    if (!relative || relative.endsWith('/')) relative += 'index.html';
    const target = path.resolve(site, relative);
    if (!target.startsWith(site + path.sep) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
      res.writeHead(404).end(); return;
    }
    res.setHeader('Content-Type', TYPES[path.extname(target)] || 'application/octet-stream');
    fs.createReadStream(target).pipe(res);
  });
}

function lessonSamples(site = DEFAULT_SITE) {
  const lessons = [];
  for (const directory of fs.readdirSync(site)) {
    const match = /^(\d\d)-/.exec(directory);
    const number = match ? Number(match[1]) : 0;
    const presentation = path.join(site, directory, 'presentation');
    if (number < 1 || number > 14 || !fs.existsSync(presentation)) continue;
    const docs = fs.readdirSync(presentation).filter(file => file.endsWith('-doc.html'));
    if (docs.length !== 1) throw new Error(`${directory}: expected one interactive document`);
    lessons.push({ number, relative: `${directory}/presentation/${docs[0]}` });
  }
  lessons.sort((a, b) => a.number - b.number);
  if (lessons.length !== 14 || lessons.some((item, index) => item.number !== index + 1)) {
    throw new Error(`Pages artifact does not contain L1-L14: ${lessons.map(item => item.number)}`);
  }
  return lessons;
}

function parseArguments(argv = process.argv.slice(2), env = process.env, cwd = process.cwd()) {
  let siteArgument = null;
  let evidenceArgument = null;
  for (let index = 0; index < argv.length; index++) {
    const argument = argv[index];
    if (argument === '--evidence') {
      if (evidenceArgument !== null) throw new Error('--evidence may be specified only once');
      if (index + 1 >= argv.length || !argv[index + 1] || argv[index + 1].startsWith('--')) {
        throw new Error('--evidence requires an explicit JSON path');
      }
      evidenceArgument = argv[++index];
    } else if (argument.startsWith('-')) {
      throw new Error(`unknown Pages E2E option: ${argument}`);
    } else if (siteArgument === null) {
      siteArgument = argument;
    } else {
      throw new Error(`unexpected extra Pages E2E argument: ${argument}`);
    }
  }

  const environmentEvidence = env[EVIDENCE_ENV];
  if (evidenceArgument !== null && environmentEvidence !== undefined && environmentEvidence !== '') {
    throw new Error(`--evidence and ${EVIDENCE_ENV} are mutually exclusive`);
  }
  if (environmentEvidence !== undefined && environmentEvidence !== ''
      && typeof environmentEvidence !== 'string') {
    throw new Error(`${EVIDENCE_ENV} must be a path string`);
  }
  const evidence = evidenceArgument === null ? environmentEvidence : evidenceArgument;
  return {
    site: path.resolve(cwd, siteArgument || '_site'),
    evidencePath: evidence ? path.resolve(cwd, evidence) : null,
  };
}

function sha256File(filename) {
  const stat = fs.lstatSync(filename);
  if (stat.isSymbolicLink() || !stat.isFile()) {
    throw new Error(`integrity manifest must be a regular file: ${filename}`);
  }
  return crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
}

function pagesIntegritySha256(site) {
  return sha256File(path.join(site, '.pages-integrity.json'));
}

function evidenceTargetIdentity(root, requestedPath) {
  if (typeof requestedPath !== 'string' || !requestedPath) {
    throw new Error('Pages evidence requires a non-empty explicit path');
  }
  const realRoot = fs.realpathSync.native(root);
  const artifacts = path.join(realRoot, 'artifacts');
  const evidenceDirectory = path.join(artifacts, 'pages-e2e');
  const target = path.resolve(requestedPath);
  const basename = path.basename(target);
  if (path.dirname(target) !== evidenceDirectory
      || !/^[A-Za-z0-9][A-Za-z0-9._-]*\.json$/.test(basename)) {
    throw new Error(`unsafe Pages evidence path (expected artifacts/pages-e2e/<name>.json): ${target}`);
  }
  for (const directory of [artifacts, evidenceDirectory]) {
    if (!fs.existsSync(directory)) continue;
    const stat = fs.lstatSync(directory);
    if (stat.isSymbolicLink() || !stat.isDirectory()
        || fs.realpathSync.native(directory) !== directory) {
      throw new Error(`unsafe Pages evidence directory: ${directory}`);
    }
  }
  return { realRoot, artifacts, evidenceDirectory, target };
}

function expectedEvidenceTargetIds(scope) {
  if (!scope || typeof scope !== 'object' || typeof scope.runSite !== 'boolean'
      || !Array.isArray(scope.labLessons)) {
    throw new Error('invalid Pages evidence scope');
  }
  const lessons = scope.labLessons;
  if (lessons.some(lesson => !Number.isSafeInteger(lesson) || lesson < 1 || lesson > 14)
      || new Set(lessons).size !== lessons.length) {
    throw new Error('Pages evidence scope has invalid or duplicate lab lessons');
  }
  const ids = scope.runSite ? ['mobile-webkit-site'] : [];
  for (const lesson of lessons) ids.push(`L${lesson}-build`, `L${lesson}-auxiliary`);
  if (!ids.length) throw new Error('Pages evidence scope declares no targets');
  return ids;
}

function siteReplayCheckSetPassed(checks) {
  if (!Array.isArray(checks) || checks.length !== 40) return false;
  const ids = checks.map(check => check?.id);
  if (ids.some(id => typeof id !== 'string') || new Set(ids).size !== ids.length) return false;
  const fixed = [
    'page:index',
    'page:06-oop-iii-inheritance/checkpoint.html',
    'page:15-final-exam/examen.html',
    'page:01-python-i-data-model/exercises/01_build_exercises.html',
    'page:08-order-types-matching/exercises/08_auxiliary.html',
    'page:14-avellaneda-stoikov/exercises/14_build_exercises.html',
    'index:actions', 'index:blocks', 'index:return-home',
    'site:late-page-errors', 'site:close-page-errors', 'site:external-requests',
    ...Array.from({ length: 14 }, (_, index) => `mobile-fallback:L${index + 1}`),
  ];
  if (!fixed.every(id => ids.includes(id))) return false;
  const presentationLessons = ids.flatMap(id => {
    const match = /^page:(\d\d)-[^/]+\/presentation\/[^/]+-doc\.html$/.exec(id);
    return match ? [Number(match[1])] : [];
  }).sort((left, right) => left - right);
  return JSON.stringify(presentationLessons) === JSON.stringify(
    Array.from({ length: 14 }, (_, index) => index + 1));
}

function validatePagesEvidence(evidence) {
  const errors = [];
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return { passed: false, errors: ['evidence must be an object'] };
  }
  if (evidence.schema !== PAGES_EVIDENCE_SCHEMA) errors.push('schema mismatch');
  if (!evidence.outcome || typeof evidence.outcome !== 'object'
      || typeof evidence.outcome.completed !== 'boolean'
      || typeof evidence.outcome.passed !== 'boolean'
      || !Number.isSafeInteger(evidence.outcome.failures) || evidence.outcome.failures < 0) {
    errors.push('invalid outcome');
  }
  if (!Array.isArray(evidence.targets)) errors.push('targets must be an array');
  const targets = Array.isArray(evidence.targets) ? evidence.targets : [];
  if (targets.some(target => !target || typeof target !== 'object'
      || typeof target.id !== 'string' || !target.id
      || !['site', 'lab'].includes(target.kind)
      || typeof target.passed !== 'boolean'
      || !target.outcome || typeof target.outcome !== 'object'
      || !Number.isSafeInteger(target.outcome.failures) || target.outcome.failures < 0)) {
    errors.push('invalid target outcome');
  }
  if (targets.some(target => target?.passed !== (target?.outcome?.failures === 0))) {
    errors.push('target pass/failure mismatch');
  }

  if (evidence.outcome?.completed === true) {
    if (!/^[0-9a-f]{40}$/.test(evidence.source_sha || '')) errors.push('invalid source SHA');
    if (!/^[0-9a-f]{64}$/.test(evidence.integrity_sha256 || '')) {
      errors.push('invalid integrity SHA');
    }
    const browserValidation = evidence.browser_validation;
    const recomputed = browserValidation && evidenceContract.validateBrowserIdentity(
      browserValidation.declared, browserValidation.locked, browserValidation.observed);
    if (!recomputed?.passed || JSON.stringify(recomputed) !== JSON.stringify(browserValidation)
        || JSON.stringify(evidence.browser) !== JSON.stringify(browserValidation.declared)
        || JSON.stringify(evidence.locked_browser) !== JSON.stringify(browserValidation.locked)) {
      errors.push('invalid exact browser identity');
    }
    if (!targets.length) errors.push('completed evidence has no targets');
    try {
      const expected = expectedEvidenceTargetIds(evidence.scope).sort();
      const observed = targets.map(target => target.id).sort();
      if (new Set(observed).size !== observed.length
          || JSON.stringify(observed) !== JSON.stringify(expected)) {
        errors.push('target set does not match shard scope');
      }
    } catch (error) {
      errors.push(error.message);
    }
    for (const target of targets) {
      const expectedKind = target.id === 'mobile-webkit-site' ? 'site'
        : /^L(?:[1-9]|1[0-4])-(?:build|auxiliary)$/.test(target.id) ? 'lab' : null;
      if (target.kind !== expectedKind) {
        errors.push(`target kind does not match id: ${target.id}`);
        continue;
      }
      if (target.kind === 'site') {
        const checks = target.outcome.checks;
        const failedChecks = Array.isArray(checks)
          ? checks.filter(check => check?.passed !== true).length : -1;
        if (!siteReplayCheckSetPassed(checks)
            || checks.some(check => typeof check?.id !== 'string'
              || typeof check?.passed !== 'boolean')
            || failedChecks !== target.outcome.failures) {
          errors.push(`invalid site replay outcome: ${target.id}`);
        }
      } else if (target.kind === 'lab') {
        const attempts = target.outcome.attempts;
        const successful = target.outcome.successfulAttempt;
        if (!Array.isArray(attempts) || attempts.length < 1
            || (target.passed && (!Number.isSafeInteger(successful)
              || successful !== attempts.length || !isCleanLabResult(attempts[successful - 1])))
            || (!target.passed && successful !== null)
            || (!target.passed && attempts.some(isCleanLabResult))) {
          errors.push(`invalid lab replay outcome: ${target.id}`);
        }
      }
    }
    const targetFailures = targets.reduce((total, target) =>
      total + (Number.isSafeInteger(target?.outcome?.failures) ? target.outcome.failures : 0), 0);
    if (evidence.outcome.failures !== targetFailures) errors.push('failure count mismatch');
    const derivedPass = targetFailures === 0 && targets.every(target => target.passed);
    if (evidence.outcome.passed !== derivedPass) errors.push('outcome pass mismatch');
    if (evidence.outcome.error !== null) errors.push('completed evidence must not contain an error');
  } else if (evidence.outcome) {
    if (evidence.outcome.passed !== false) errors.push('incomplete evidence cannot pass');
    if (!evidence.outcome.error || typeof evidence.outcome.error.name !== 'string'
        || typeof evidence.outcome.error.message !== 'string') {
      errors.push('incomplete evidence requires an error');
    }
  }
  return { passed: errors.length === 0, errors };
}

function writePagesEvidenceAtomic(root, requestedPath, evidence) {
  const validation = validatePagesEvidence(evidence);
  if (!validation.passed) {
    throw new Error(`refusing invalid Pages evidence: ${validation.errors.join('; ')}`);
  }
  let identity = evidenceTargetIdentity(root, requestedPath);
  for (const directory of [identity.artifacts, identity.evidenceDirectory]) {
    if (!fs.existsSync(directory)) fs.mkdirSync(directory, { recursive: false });
  }
  identity = evidenceTargetIdentity(root, requestedPath);
  if (fs.existsSync(identity.target)) {
    throw new Error(`refusing to overwrite existing Pages evidence: ${identity.target}`);
  }

  const temporary = `${identity.target}.${process.pid}.${crypto.randomBytes(8).toString('hex')}.tmp`;
  let descriptor = null;
  try {
    descriptor = fs.openSync(temporary, 'wx', 0o600);
    fs.writeFileSync(descriptor, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
    fs.fsyncSync(descriptor);
    fs.closeSync(descriptor);
    descriptor = null;
    // A same-directory hard link publishes the fully fsynced inode atomically
    // and fails with EEXIST instead of replacing evidence from an earlier run.
    fs.linkSync(temporary, identity.target);
    fs.unlinkSync(temporary);
    const directoryDescriptor = fs.openSync(identity.evidenceDirectory, 'r');
    try { fs.fsyncSync(directoryDescriptor); } finally { fs.closeSync(directoryDescriptor); }
  } catch (error) {
    if (descriptor !== null) fs.closeSync(descriptor);
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
    throw error;
  }
  return identity.target;
}

async function launchExactWebKit(webkit, {
  root = ROOT,
  contract = evidenceContract,
  playwrightVersion = require('playwright/package.json').version,
  onPhase = () => {},
  onLocked = () => {},
  onObserved = () => {},
} = {}) {
  const browserExecutable = fs.realpathSync.native(webkit.executablePath());
  onPhase('browser-identity');
  const locked = contract.lockedPlaywrightBrowserIdentity(root, 'webkit', browserExecutable);
  onLocked(locked);
  onPhase('browser-launch');
  const browser = await webkit.launch({ executablePath: browserExecutable });
  try {
    const observed = {
      ...locked,
      name: browser.browserType().name(),
      version: browser.version(),
      playwright: playwrightVersion,
    };
    onPhase('browser-validation');
    const validation = contract.validateBrowserIdentity(observed, locked, observed);
    onObserved(observed, validation);
    if (!validation.passed) {
      throw new Error(`launched WebKit does not match lock: ${JSON.stringify(validation)}`);
    }
    return { browser, locked, observed, validation, executablePath: browserExecutable };
  } catch (error) {
    try { await browser.close(); } catch (_closeError) { /* identity failure remains authoritative */ }
    throw error;
  }
}

function positiveInteger(raw, name, fallback) {
  if (raw === undefined || raw === '') return fallback;
  if (!/^\d+$/.test(raw) || Number(raw) < 1) {
    throw new Error(`${name} must be a positive integer, got ${JSON.stringify(raw)}`);
  }
  return Number(raw);
}

function resolveRunPlan(lessons, env = process.env) {
  const scope = env.WORK2_PAGES_SCOPE || 'all';
  if (!['all', 'site', 'lab'].includes(scope)) {
    throw new Error(`WORK2_PAGES_SCOPE must be all, site, or lab; got ${JSON.stringify(scope)}`);
  }

  const rawLesson = env.WORK2_PAGES_LESSON;
  let selectedLessons = lessons;
  if (rawLesson !== undefined && rawLesson !== '') {
    if (!/^\d+$/.test(rawLesson)) {
      throw new Error(`WORK2_PAGES_LESSON must be an integer from 1 to 14, got ${JSON.stringify(rawLesson)}`);
    }
    const lessonNumber = Number(rawLesson);
    selectedLessons = lessons.filter(lesson => lesson.number === lessonNumber);
    if (selectedLessons.length !== 1) {
      throw new Error(`WORK2_PAGES_LESSON=${rawLesson} does not identify exactly one published lesson`);
    }
  } else if (scope === 'lab') {
    throw new Error('WORK2_PAGES_SCOPE=lab requires WORK2_PAGES_LESSON=1..14');
  }

  if (scope === 'site' && rawLesson) {
    throw new Error('WORK2_PAGES_LESSON cannot be combined with WORK2_PAGES_SCOPE=site');
  }

  return {
    runSite: scope !== 'lab',
    labLessons: scope === 'site' ? [] : selectedLessons,
    maxLabAttempts: positiveInteger(env.WORK2_PAGES_ATTEMPTS, 'WORK2_PAGES_ATTEMPTS', 2),
    kernelTimeout: positiveInteger(env.WORK2_PAGES_KERNEL_TIMEOUT_MS,
      'WORK2_PAGES_KERNEL_TIMEOUT_MS', 120000),
    outputTimeout: positiveInteger(env.WORK2_PAGES_OUTPUT_TIMEOUT_MS,
      'WORK2_PAGES_OUTPUT_TIMEOUT_MS', 90000),
    readyStableMs: positiveInteger(env.WORK2_PAGES_READY_STABLE_MS,
      'WORK2_PAGES_READY_STABLE_MS', 750),
    idleStableMs: positiveInteger(env.WORK2_PAGES_IDLE_STABLE_MS,
      'WORK2_PAGES_IDLE_STABLE_MS', 1500),
  };
}

function isAllowedOfflineRequest(requestUrl, siteOrigin) {
  let parsed;
  try {
    parsed = new URL(requestUrl);
  } catch {
    return false;
  }
  if (['data:', 'blob:', 'about:'].includes(parsed.protocol)) return true;
  if (parsed.origin === siteOrigin) return true;
  if (['ws:', 'wss:'].includes(parsed.protocol)) {
    const site = new URL(siteOrigin);
    const matchingProtocol = (parsed.protocol === 'ws:' && site.protocol === 'http:') ||
      (parsed.protocol === 'wss:' && site.protocol === 'https:');
    return matchingProtocol && parsed.hostname === site.hostname && parsed.port === site.port;
  }
  return false;
}

function browserErrorText(error) {
  const candidates = [error && error.message, error && error.stack, String(error)];
  return candidates.find(value => typeof value === 'string' && value.trim() &&
    value !== 'undefined' && value !== '[object Object]') || 'unknown browser error';
}

function createRuntimeFailureMonitor() {
  let rejectFailure;
  let failed = false;
  const promise = new Promise((_resolve, reject) => { rejectFailure = reject; });
  // An error may arrive during navigation, before the kernel wait attaches its
  // race handler. Keep the rejection observed without changing its outcome.
  promise.catch(() => {});
  return {
    promise,
    fail(message) {
      if (failed) return;
      failed = true;
      rejectFailure(new Error(message));
    },
  };
}

function isRuntimeDiagnosticUrl(raw) {
  try {
    const pathname = new URL(raw).pathname;
    return pathname.includes('/static/pyodide/') || pathname.includes('/pypi/') ||
      /\/(?:coincident|comlink)\.worker\.[0-9a-f]+\.js$/.test(pathname);
  } catch {
    return false;
  }
}

async function installWorkerDiagnostics(page) {
  await page.addInitScript(() => {
    const NativeWorker = globalThis.Worker;
    if (typeof NativeWorker !== 'function') return;
    globalThis.Worker = new Proxy(NativeWorker, {
      construct(target, args) {
        const worker = Reflect.construct(target, args, target);
        worker.addEventListener('error', event => {
          const detail = {
            message: event.message || null,
            filename: event.filename || null,
            lineno: event.lineno || null,
            colno: event.colno || null,
            error: event.error ? String(event.error) : null,
          };
          console.error(`WORK2_WORKER_ERROR ${JSON.stringify(detail)}`);
        });
        worker.addEventListener('messageerror', event => {
          console.error(`WORK2_WORKER_MESSAGE_ERROR ${String(event.data)}`);
        });
        return worker;
      },
    });
  });
}

async function installOfflineRouting(context, origin) {
  const externalRequests = [];
  const siteOrigin = new URL(origin).origin;
  await context.route('**/*', async route => {
    const requestUrl = route.request().url();
    if (isRuntimeDiagnosticUrl(requestUrl)) {
      console.log(`JupyterLite runtime request: ${requestUrl}`);
    }
    if (isAllowedOfflineRequest(requestUrl, siteOrigin)) {
      await route.continue();
    } else {
      externalRequests.push(requestUrl);
      await route.abort('blockedbyclient');
    }
  });
  await context.routeWebSocket(/.*/, async webSocket => {
    const requestUrl = webSocket.url();
    if (isAllowedOfflineRequest(requestUrl, siteOrigin)) {
      webSocket.connectToServer();
    } else {
      externalRequests.push(requestUrl);
      await webSocket.close({ code: 1008, reason: 'external network blocked' });
    }
  });
  return externalRequests;
}

async function waitForKernelIdle(page, { timeout, stableMs }) {
  const selector = '.jp-NotebookPanel-toolbar .jp-Toolbar-kernelStatus';
  const handle = await page.waitForFunction(({ statusSelector, stableFor }) => {
    const status = document.querySelector(statusSelector);
    if (!status) {
      window.__work2KernelIdleSince = 0;
      return false;
    }
    if (status.querySelector('.jp-KernelStatus-error')) {
      return { state: 'error' };
    }
    const idle = Boolean(status.querySelector('.jp-KernelStatus-success')) &&
      !status.querySelector('.jp-KernelStatus-spinner, .jp-KernelStatus-none');
    if (!idle) {
      window.__work2KernelIdleSince = 0;
      return false;
    }
    if (!window.__work2KernelIdleSince) window.__work2KernelIdleSince = performance.now();
    return performance.now() - window.__work2KernelIdleSince >= stableFor
      ? { state: 'idle' }
      : false;
  }, { statusSelector: selector, stableFor: stableMs }, { timeout, polling: 100 });
  const status = await handle.jsonValue();
  await handle.dispose();
  await page.evaluate(() => { delete window.__work2KernelIdleSince; });
  if (!status || status.state !== 'idle') {
    throw new Error(`JupyterLite kernel reached terminal state ${status && status.state}`);
  }
}

function countMarkerOccurrences(texts, marker) {
  if (!Array.isArray(texts) || typeof marker !== 'string' || !marker) {
    throw new Error('marker cardinality requires an output-text array and non-empty marker');
  }
  return texts.reduce((total, text) => {
    if (typeof text !== 'string') throw new Error('marker output text must be a string');
    let count = 0;
    let offset = 0;
    while ((offset = text.indexOf(marker, offset)) !== -1) {
      count += 1;
      offset += marker.length;
    }
    return total + count;
  }, 0);
}

function parseKernelExecutionPrompt(prompt) {
  if (typeof prompt !== 'string') return null;
  const match = /^\s*\[\s*(\d+)\s*\]\s*:?\s*$/.exec(prompt);
  if (!match) return null;
  const count = Number(match[1]);
  return Number.isSafeInteger(count) && count > 0 ? count : null;
}

async function executeSmokeOnce({
  page,
  editor,
  output,
  smoke,
  selectAll,
  executionState,
  kernelTimeout,
  outputTimeout,
  readyStableMs,
  idleStableMs,
  waitForIdle = waitForKernelIdle,
}) {
  await waitForIdle(page, { timeout: kernelTimeout, stableMs: readyStableMs });
  executionState.kernelReady = true;
  await editor.click({ force: true });
  await page.keyboard.press(selectAll);
  await page.keyboard.insertText(smoke);
  executionState.dispatchCount += 1;
  await page.keyboard.press('Shift+Enter');
  await output.waitFor({ state: 'visible', timeout: outputTimeout });
  executionState.markerSeen = true;
  await waitForIdle(page, { timeout: kernelTimeout, stableMs: idleStableMs });
  executionState.kernelIdle = true;
}

async function retryInFreshContexts({
  createContext,
  runInContext,
  accepts,
  maxAttempts,
  onRetry = () => {},
}) {
  let lastResult = null;
  const attempts = [];
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const context = await createContext();
    try {
      lastResult = await runInContext(context, attempt);
    } catch (error) {
      lastResult = { reason: error.message, pageErrors: [] };
    } finally {
      await context.close();
    }
    // pageerror is delivered synchronously with the page task. Yield once so
    // errors raised while the context is closing remain part of the verdict.
    await new Promise(resolve => setImmediate(resolve));
    attempts.push(lastResult);
    if (accepts(lastResult)) return { passed: true, attempt, result: lastResult, attempts };
    if (attempt < maxAttempts) onRetry(lastResult, attempt);
  }
  return { passed: false, attempt: maxAttempts, result: lastResult, attempts };
}

async function runSiteAcceptance(browser, origin, lessons) {
  const samples = [
    '',
    ...lessons.map(item => item.relative),
    '06-oop-iii-inheritance/checkpoint.html',
    '15-final-exam/examen.html',
    '01-python-i-data-model/exercises/01_build_exercises.html',
    '08-order-types-matching/exercises/08_auxiliary.html',
    '14-avellaneda-stoikov/exercises/14_build_exercises.html',
  ];
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3, isMobile: true, hasTouch: true, serviceWorkers: 'block' });
  const externalRequests = await installOfflineRouting(context, origin);
  const page = await context.newPage();
  const pageErrors = [];
  const reportedErrors = new Set();
  page.on('pageerror', error => pageErrors.push({ message: error.message, url: page.url() }));
  let failures = 0;
  const checks = [];

  for (const sample of samples) {
    const errorStart = pageErrors.length;
    const response = await page.goto(origin + sample, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const errors = pageErrors.slice(errorStart);
    errors.forEach(error => reportedErrors.add(error));
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
    const hasHome = sample === '' || await page.locator('.course-home').count() === 1;
    const homeTallEnough = sample === '' || await page.locator('.course-home').evaluate(
      element => element.getBoundingClientRect().height >= 44);
    const notebookOk = !sample.includes('/exercises/') ||
      await page.locator('.jp-Notebook').count() === 1;
    const passed = Boolean(response && response.ok()) && errors.length === 0 && !overflow
      && hasHome && homeTallEnough && notebookOk;
    checks.push({ id: `page:${sample || 'index'}`, passed,
      status: response ? response.status() : null, pageErrors: errors.length,
      horizontalOverflow: overflow, hasHome, homeTallEnough, notebookOk });
    if (!passed) {
      failures++;
      console.error(`✗ ${sample || 'index'} status=${response && response.status()} ` +
        `errors=${errors.length} overflow=${overflow} home=${hasHome && homeTallEnough} notebook=${notebookOk}`);
      errors.slice(0, 3).forEach(error => console.error('  ', error.message));
    } else {
      console.log(`✓ ${sample || 'index'}`);
    }
  }

  // Every educational lesson uses the same vertical fallback and explicit OPTIONAL opt-in.
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
    const passed = fallback.requested === 'aula' && fallback.mode === 'estudio'
      && fallback.marked && fallback.navHidden && fallback.toolbar
      && fallback.scope === 'LIVE+REQUIRED' && !fallback.horizontal;
    checks.push({ id: `mobile-fallback:L${lesson.number}`, passed, ...fallback });
    if (!passed) {
      failures++; console.error(`✗ L${lesson.number} mobile aula fallback ${JSON.stringify(fallback)}`);
    } else {
      console.log(`✓ L${lesson.number} mobile aula fallback → vertical study renderer`);
    }
  }

  await page.goto(origin);
  const actions = await page.locator('.lc-actions a').count();
  checks.push({ id: 'index:actions', passed: actions === 42, observed: actions, expected: 42 });
  if (actions !== 42) { failures++; console.error(`✗ index actions=${actions}, expected 42`); }
  const blocks = await page.locator('.course-block').count();
  checks.push({ id: 'index:blocks', passed: blocks === 4, observed: blocks, expected: 4 });
  if (blocks !== 4) { failures++; console.error(`✗ index blocks=${blocks}, expected 4`); }
  await page.locator('.lc-actions a').first().click();
  await page.locator('.course-home').click();
  const returnedPath = new URL(page.url()).pathname;
  const returned = [BASE, BASE + 'index.html'].includes(returnedPath);
  checks.push({ id: 'index:return-home', passed: returned, returnedPath });
  if (!returned) {
    failures++; console.error(`✗ course return resolved to ${page.url()}`);
  }

  // Keep the pageerror listener alive for the full mobile context. Errors that
  // arrive after an individual page's short geometry settle still fail closed.
  await page.waitForTimeout(500);
  const lateErrors = pageErrors.filter(error => !reportedErrors.has(error));
  checks.push({ id: 'site:late-page-errors', passed: lateErrors.length === 0,
    observed: lateErrors.length });
  if (lateErrors.length) {
    failures++;
    console.error(`✗ WebKit emitted ${lateErrors.length} late/unattributed page errors`);
    lateErrors.slice(0, 3).forEach(error => console.error(`   ${error.url}: ${error.message}`));
    lateErrors.forEach(error => reportedErrors.add(error));
  }
  await context.close();
  await new Promise(resolve => setImmediate(resolve));
  const closeErrors = pageErrors.filter(error => !reportedErrors.has(error));
  checks.push({ id: 'site:close-page-errors', passed: closeErrors.length === 0,
    observed: closeErrors.length });
  if (closeErrors.length) {
    failures++;
    console.error(`✗ WebKit emitted ${closeErrors.length} page errors while closing`);
    closeErrors.slice(0, 3).forEach(error => console.error(`   ${error.url}: ${error.message}`));
  }
  checks.push({ id: 'site:external-requests', passed: externalRequests.length === 0,
    observed: externalRequests.length });
  if (externalRequests.length) {
    failures++;
    console.error(`✗ WebKit blocked ${externalRequests.length} external site requests`);
    externalRequests.slice(0, 3).forEach(url => console.error('  external:', url));
  }
  return {
    failures,
    targets: [{
      kind: 'site',
      id: 'mobile-webkit-site',
      passed: failures === 0,
      outcome: {
        failures,
        sampledPages: samples.length,
        mobileFallbackLessons: lessons.length,
        pageErrors: pageErrors.length,
        externalRequests: externalRequests.length,
        checks,
      },
    }],
  };
}

// Static notebooks expose a touch-friendly lab link; every lesson must also
// execute a meaningful, lesson-specific offline smoke in JupyterLite.
const LAB_SMOKES = {
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
    13: `from exchange.strategies import MarketMaker\nfrom exchange.simulation import MMSimulation\nm = MarketMaker('BTC')\nr = MMSimulation(m,steps=2,A=0).run()\nassert len(r.pnl) == 2\nprint('WORK2_L13_OK')`,
    14: `from exchange.strategies import AvellanedaStoikov\ns = AvellanedaStoikov('BTC',horizon=10); s.inventory=1; s.time=10\nassert s.reservation_price(100) == 100\nprint('WORK2_L14_OK')`,
};

function labTargetsForLessons(lessons) {
  const targets = lessons.flatMap(lesson => {
    const directory = lesson.relative.split('/')[0];
    const nn = String(lesson.number).padStart(2, '0');
    return [
      { label: `L${lesson.number}-build`, lesson: lesson.number,
        staticPath: `${directory}/exercises/${nn}_build_exercises.html`,
        notebookPath: `${directory}/exercises/${nn}_build_exercises.ipynb`,
        marker: `WORK2_L${lesson.number}_OK`, smoke: LAB_SMOKES[lesson.number] },
      { label: `L${lesson.number}-auxiliary`, lesson: lesson.number,
        staticPath: `${directory}/exercises/${nn}_auxiliary.html`,
        notebookPath: `${directory}/exercises/${nn}_auxiliary.ipynb`,
        marker: `WORK2_L${lesson.number}_AUX_OK`,
        // The auxiliary notebook must prove the same lesson-specific runtime
        // surface as the build notebook. A generic print would only certify
        // that a kernel started, not that the staged course package works.
        smoke: LAB_SMOKES[lesson.number] },
    ];
  });
  return targets;
}

function isCleanLabResult(result) {
  return Boolean(result && result.staticOk && result.responseOk &&
    result.labPath && result.labPath.startsWith(BASE + 'jupyter/lab/') &&
    result.requestedNotebook === result.expectedNotebook && result.documentNameMatches === true &&
    result.codeCells > 0 && result.kernelReady && result.dispatchCount === 1 &&
    result.kernelPromptCount === 1 && result.kernelExecutionCount === 1 &&
    result.markerSeen && result.markerOccurrences === 1
    && /^[0-9a-f]{64}$/.test(result.markerSha256 || '') && result.kernelIdle &&
    !result.stderr && result.labHome === 1 &&
    result.pageErrors.length === 0 && result.externalRequests.length === 0 && !result.reason);
}

async function runLabAttempt(context, origin, target, plan) {
    const staticPath = target.staticPath;
    const pageErrors = [];
    const externalRequests = await installOfflineRouting(context, origin);
    const labPage = await context.newPage();
    const runtimeFailure = createRuntimeFailureMonitor();
    labPage.on('worker', worker => {
      console.log(`WORK2_WORKER_CREATED ${worker.url()}`);
      worker.evaluate(() => ({
        location: globalThis.location && globalThis.location.href,
        crossOriginIsolated: globalThis.crossOriginIsolated,
        sharedArrayBuffer: typeof globalThis.SharedArrayBuffer,
      })).then(
        detail => console.log(`WORK2_WORKER_READY ${JSON.stringify(detail)}`),
        error => console.error(`WORK2_WORKER_EVALUATE_ERROR ${browserErrorText(error)}`),
      );
    });
    labPage.on('pageerror', error => {
      const message = browserErrorText(error);
      pageErrors.push(message);
      console.error(`JupyterLite pageerror: ${message}`);
      runtimeFailure.fail(`JupyterLite pageerror: ${message}`);
    });
    labPage.on('console', message => {
      if (message.type() === 'error') {
        const detail = message.text() || 'empty console message';
        console.error(`JupyterLite console.error: ${detail}`);
      }
    });
    labPage.on('requestfailed', request => {
      const detail = `JupyterLite request failed: ${request.url()} ` +
        `${request.failure() && request.failure().errorText || 'unknown failure'}`;
      console.error(detail);
    });
    labPage.on('response', response => {
      if (isRuntimeDiagnosticUrl(response.url())) {
        console.log(`JupyterLite runtime HTTP ${response.status()}: ${response.url()}`);
      }
      if (response.status() >= 400) {
        const detail = `JupyterLite HTTP ${response.status()}: ${response.url()}`;
        console.error(detail);
      }
    });
    await installWorkerDiagnostics(labPage);
    const result = {
      reason: '',
      staticOk: false,
      responseOk: false,
      status: null,
      codeCells: 0,
      kernelReady: false,
      dispatchCount: 0,
      kernelPromptCount: 0,
      kernelExecutionCount: null,
      markerSeen: false,
      markerOccurrences: 0,
      markerSha256: null,
      kernelIdle: false,
      stderr: false,
      labHome: 0,
      labPath: '',
      expectedNotebook: target.notebookPath,
      requestedNotebook: null,
      documentNameMatches: false,
      pageErrors,
      externalRequests,
      cellText: 'cell unavailable',
    };
    let firstCodeCell = null;
    const executionState = {
      dispatchCount: 0,
      kernelReady: false,
      markerSeen: false,
      kernelIdle: false,
    };

    try {
      const staticResponse = await labPage.goto(origin + staticPath, {
        waitUntil: 'domcontentloaded',
      });
      result.staticOk = Boolean(staticResponse && staticResponse.ok());
      const labLink = labPage.locator('.course-lab');
      const linkOk = await labLink.count() === 1 &&
        await labLink.evaluate(element => element.getBoundingClientRect().height) >= 44;
      if (!linkOk) {
        throw new Error('rendered notebook has no touch-friendly lab link');
      }

      const labUrlValue = new URL(await labLink.getAttribute('href'), labPage.url());
      result.requestedNotebook = labUrlValue.searchParams.get('path');
      if (result.requestedNotebook !== target.notebookPath
          || labUrlValue.searchParams.get('mode') !== 'single-document') {
        throw new Error(`lab link points to ${result.requestedNotebook}, expected ${target.notebookPath}`);
      }
      const labUrl = labUrlValue.href;
      const response = await labPage.goto(labUrl, { waitUntil: 'domcontentloaded' });
      result.responseOk = Boolean(response && response.ok());
      result.status = response && response.status();
      result.labPath = new URL(labPage.url()).pathname;

      const notebook = labPage.locator('.jp-Notebook').first();
      await notebook.waitFor({ state: 'visible', timeout: 45000 });
      const notebookName = path.posix.basename(target.notebookPath);
      result.documentNameMatches = await labPage
        .locator('.lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel')
        .filter({ hasText: notebookName }).count() > 0;
      if (!result.documentNameMatches) {
        throw new Error(`JupyterLite did not open ${notebookName}`);
      }
      result.codeCells = await notebook.locator('.jp-CodeCell').count();
      firstCodeCell = notebook.locator('.jp-CodeCell').first();
      const editor = firstCodeCell.locator('.cm-content[data-language="python"]');
      await editor.waitFor({ state: 'visible', timeout: plan.kernelTimeout });
      const executionMarker = `${target.marker}_${crypto.randomBytes(12).toString('hex')}`;
      result.markerSha256 = crypto.createHash('sha256').update(executionMarker).digest('hex');
      const output = firstCodeCell.locator('.jp-OutputArea-output').filter({ hasText: executionMarker });
      await executeSmokeOnce({
        page: labPage,
        editor,
        output,
        smoke: `${target.smoke}\nprint(${JSON.stringify(executionMarker)})`,
        selectAll: process.platform === 'darwin' ? 'Meta+A' : 'Control+A',
        executionState,
        kernelTimeout: plan.kernelTimeout,
        outputTimeout: plan.outputTimeout,
        readyStableMs: plan.readyStableMs,
        idleStableMs: plan.idleStableMs,
        waitForIdle: (page, options) => Promise.race([
          waitForKernelIdle(page, options), runtimeFailure.promise,
        ]),
      });
      const outputTexts = await firstCodeCell.locator('.jp-OutputArea-output').allTextContents();
      result.markerOccurrences = countMarkerOccurrences(outputTexts, executionMarker);
      const promptTexts = await firstCodeCell.locator('.jp-InputPrompt').allTextContents();
      result.kernelPromptCount = promptTexts.length;
      result.kernelExecutionCount = promptTexts.length === 1
        ? parseKernelExecutionPrompt(promptTexts[0]) : null;
      result.cellText = await firstCodeCell.innerText().catch(() => 'cell unavailable');
      result.stderr = await firstCodeCell.locator(
        '.jp-OutputArea-output[data-mime-type="application/vnd.jupyter.stderr"]'
      ).count() > 0 || result.cellText.includes('Traceback (most recent call last)');
    } catch (error) {
      result.reason = error.message;
      result.cellText = firstCodeCell
        ? await firstCodeCell.innerText().catch(() => 'cell unavailable')
        : 'cell unavailable';
      const diagnostic = await labPage.evaluate(() => {
        const status = document.querySelector(
          '.jp-NotebookPanel-toolbar .jp-Toolbar-kernelStatus',
        );
        const notices = [...document.querySelectorAll(
          '.jp-Notification, .jp-Dialog-content, .jp-LogConsole-output',
        )].map(node => node.textContent && node.textContent.trim()).filter(Boolean).slice(0, 5);
        return { status: status ? status.outerHTML : null, notices };
      }).catch(diagnosticError => ({ diagnosticError: String(diagnosticError) }));
      console.error(`WORK2_KERNEL_DOM ${JSON.stringify(diagnostic)}`);
    } finally {
      result.kernelReady = executionState.kernelReady;
      result.dispatchCount = executionState.dispatchCount;
      result.markerSeen = executionState.markerSeen;
      result.kernelIdle = executionState.kernelIdle;
      result.labHome = await labPage.locator('.course-home').count().catch(() => 0);
      result.labPath = new URL(labPage.url()).pathname;
    }
    return result;
}

function failureReason(result) {
  return result.reason || result.pageErrors?.[0] || result.externalRequests?.[0] ||
    `status ${result.status}, dispatches ${result.dispatchCount}, ` +
    `kernel count ${result.kernelExecutionCount}, nonce count ${result.markerOccurrences}`;
}

function labAttemptEvidence(result) {
  if (!result || typeof result !== 'object') return { reason: 'attempt returned no result' };
  return {
    reason: result.reason || '',
    staticOk: Boolean(result.staticOk),
    responseOk: Boolean(result.responseOk),
    status: result.status ?? null,
    labPath: result.labPath || '',
    expectedNotebook: result.expectedNotebook || null,
    requestedNotebook: result.requestedNotebook || null,
    documentNameMatches: Boolean(result.documentNameMatches),
    codeCells: result.codeCells || 0,
    kernelReady: Boolean(result.kernelReady),
    dispatchCount: result.dispatchCount || 0,
    kernelPromptCount: result.kernelPromptCount || 0,
    kernelExecutionCount: result.kernelExecutionCount ?? null,
    markerSeen: Boolean(result.markerSeen),
    markerOccurrences: result.markerOccurrences || 0,
    markerSha256: result.markerSha256 || null,
    kernelIdle: Boolean(result.kernelIdle),
    stderr: Boolean(result.stderr),
    labHome: result.labHome || 0,
    pageErrors: Array.isArray(result.pageErrors) ? [...result.pageErrors] : [],
    externalRequests: Array.isArray(result.externalRequests) ? [...result.externalRequests] : [],
  };
}

async function runLabAcceptance(browser, origin, labLessons, plan) {
  let failures = 0;
  const targets = [];
  for (const target of labTargetsForLessons(labLessons)) {
    // Every attempt owns a fresh browser context. A cold kernel, lost shortcut,
    // output timeout, stderr, or pageerror discards that complete lesson run.
    // No attempt sends a second execution into the same Pyodide worker.
    const outcome = await retryInFreshContexts({
      createContext: () => browser.newContext({ viewport: { width: 1280, height: 900 },
        serviceWorkers: 'block' }),
      runInContext: context => runLabAttempt(context, origin, target, plan),
      accepts: isCleanLabResult,
      maxAttempts: plan.maxLabAttempts,
      onRetry: result => console.warn(
        `↻ ${target.label} JupyterLite clean-context retry after: ${failureReason(result)}`),
    });
    const lastFailure = outcome.result;
    targets.push({
      kind: 'lab',
      id: target.label,
      lesson: target.lesson,
      staticPath: target.staticPath,
      notebookPath: target.notebookPath,
      passed: outcome.passed,
      outcome: {
        failures: outcome.passed ? 0 : 1,
        successfulAttempt: outcome.passed ? outcome.attempt : null,
        attempts: outcome.attempts.map(labAttemptEvidence),
      },
    });
    if (outcome.passed) {
      const recovered = outcome.attempt > 1 ? ' after clean-context retry' : '';
      console.log(`✓ ${target.label} JupyterLite offline smoke ` +
        `(${lastFailure.codeCells} code cells; one dispatch/one kernel execution)${recovered}`);
    } else {
      failures++;
      console.error(`✗ ${target.label} JupyterLite status=${lastFailure && lastFailure.status} ` +
        `cells=${lastFailure && lastFailure.codeCells} dispatches=${lastFailure && lastFailure.dispatchCount} ` +
        `kernelCount=${lastFailure && lastFailure.kernelExecutionCount} ` +
        `nonceCount=${lastFailure && lastFailure.markerOccurrences} ` +
        `stderr=${lastFailure && lastFailure.stderr} home=${lastFailure && lastFailure.labHome} ` +
        `kernelReady=${lastFailure && lastFailure.kernelReady} idle=${lastFailure && lastFailure.kernelIdle} ` +
        `errors=${lastFailure && lastFailure.pageErrors ? lastFailure.pageErrors.length : 0} ` +
        `external=${lastFailure && lastFailure.externalRequests ? lastFailure.externalRequests.length : 0}`);
      if (lastFailure && lastFailure.reason) console.error('  ', lastFailure.reason);
      if (lastFailure && lastFailure.pageErrors) {
        lastFailure.pageErrors.slice(0, 3).forEach(error => console.error('  ', error));
      }
      if (lastFailure && lastFailure.externalRequests) {
        lastFailure.externalRequests.slice(0, 3).forEach(url => console.error('  external:', url));
      }
      if (lastFailure && lastFailure.cellText) {
        console.error(`  first cell: ${lastFailure.cellText.slice(0, 1200)}`);
      }
    }
  }
  return { failures, targets };
}

function evidenceScope(plan) {
  return {
    runSite: plan.runSite,
    labLessons: plan.labLessons.map(lesson => lesson.number),
    maxLabAttempts: plan.maxLabAttempts,
    kernelTimeoutMs: plan.kernelTimeout,
    outputTimeoutMs: plan.outputTimeout,
    readyStableMs: plan.readyStableMs,
    idleStableMs: plan.idleStableMs,
  };
}

async function main() {
  const startedAt = new Date().toISOString();
  const options = parseArguments();
  let lessons = null;
  let plan = null;
  let phase = 'integrity';
  let sourceSha = null;
  let integritySha256 = null;
  let lockedBrowser = null;
  let browserEvidence = null;
  let browserValidation = null;
  let app = null;
  let browser = null;
  let failures = 0;
  const targets = [];
  let terminalError = null;

  if (options.evidencePath) {
    const identity = evidenceTargetIdentity(ROOT, options.evidencePath);
    if (fs.existsSync(identity.target)) {
      throw new Error(`refusing to overwrite existing Pages evidence: ${identity.target}`);
    }
  }

  try {
    integritySha256 = pagesIntegritySha256(options.site);
    if (options.evidencePath) {
      phase = 'source-sha';
      sourceSha = evidenceContract.sourceHead(ROOT);
    }
    phase = 'lesson-discovery';
    lessons = lessonSamples(options.site);
    plan = resolveRunPlan(lessons);
    phase = 'playwright-load';
    const { webkit } = require('playwright');
    // Lock and hash the complete registry payload before any browser process is launched.
    const launch = await launchExactWebKit(webkit, {
      onPhase: value => { phase = value; },
      onLocked: value => { lockedBrowser = value; },
      onObserved: (observed, validation) => {
        browserEvidence = observed;
        browserValidation = validation;
      },
    });
    browser = launch.browser;
    lockedBrowser = launch.locked;
    browserEvidence = launch.observed;
    browserValidation = launch.validation;
    phase = 'server';
    app = server(options.site);
    await new Promise((resolve, reject) => {
      const onError = error => reject(error);
      app.once('error', onError);
      app.listen(0, '127.0.0.1', () => {
        app.off('error', onError);
        resolve();
      });
    });
    const port = app.address().port;
    const origin = `http://127.0.0.1:${port}${BASE}`;

    if (plan.runSite) {
      phase = 'site-acceptance';
      const siteResult = await runSiteAcceptance(browser, origin, lessons);
      failures += siteResult.failures;
      targets.push(...siteResult.targets);
    }
    if (plan.labLessons.length) {
      phase = 'lab-acceptance';
      const labResult = await runLabAcceptance(browser, origin, plan.labLessons, plan);
      failures += labResult.failures;
      targets.push(...labResult.targets);
    }
    phase = 'integrity-recheck';
    const finalIntegritySha256 = pagesIntegritySha256(options.site);
    if (finalIntegritySha256 !== integritySha256) {
      throw new Error('Pages integrity manifest changed during WebKit acceptance');
    }
    phase = 'complete';
  } catch (error) {
    terminalError = error;
  } finally {
    if (browser) {
      try { await browser.close(); } catch (error) { if (!terminalError) terminalError = error; }
    }
    if (app?.listening) {
      try {
        await new Promise((resolve, reject) =>
          app.close(error => error ? reject(error) : resolve()));
      }
      catch (error) { if (!terminalError) terminalError = error; }
    }
  }

  if (options.evidencePath) {
    const targetFailures = targets.reduce((total, target) => total + target.outcome.failures, 0);
    const evidence = {
      schema: PAGES_EVIDENCE_SCHEMA,
      started_at: startedAt,
      completed_at: terminalError ? null : new Date().toISOString(),
      failed_at: terminalError ? new Date().toISOString() : null,
      source_sha: sourceSha,
      integrity_sha256: integritySha256,
      browser: browserEvidence,
      locked_browser: lockedBrowser,
      browser_validation: browserValidation,
      scope: plan ? evidenceScope(plan) : null,
      targets,
      outcome: terminalError ? {
        completed: false,
        passed: false,
        failures: Math.max(1, targetFailures),
        error: { name: terminalError.name, message: terminalError.message, phase },
      } : {
        completed: true,
        passed: failures === 0,
        failures,
        error: null,
      },
    };
    try {
      writePagesEvidenceAtomic(ROOT, options.evidencePath, evidence);
    } catch (evidenceError) {
      terminalError = terminalError
        ? new Error(`${terminalError.message}; evidence write failed: ${evidenceError.message}`)
        : evidenceError;
    }
  }

  if (terminalError) throw terminalError;
  process.exitCode = failures ? 1 : 0;
}

module.exports = {
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
  pagesIntegritySha256,
  parseArguments,
  parseKernelExecutionPrompt,
  positiveInteger,
  resolveRunPlan,
  retryInFreshContexts,
  validatePagesEvidence,
  waitForKernelIdle,
  writePagesEvidenceAtomic,
};

if (require.main === module) {
  main().catch(error => {
    console.error(error);
    process.exitCode = 1;
  });
}
