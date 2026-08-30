'use strict';

const assert = require('node:assert/strict');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');
const browserContract = require('./desktop_evidence_contract');
const {
  DEFAULT_SCOPE_LIMITS,
  expectedSiteCheckIds,
  inspectSite,
  parseArguments,
  repositoryState,
  runCheckPages,
  validateAggregateDirectory,
  validateAudit,
  validateEvidence,
  validateEvidenceFile,
} = require('./validate_pages_audit');

const HEAD = 'c'.repeat(40);
const INTEGRITY_SHA = 'd'.repeat(64);

function webkitIdentity() {
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

function fakeSiteInfo() {
  const lessons = Array.from({ length: 14 }, (_, index) => {
    const number = index + 1;
    const nn = String(number).padStart(2, '0');
    return { number, directory: `${nn}-lesson`,
      relative: `${nn}-lesson/presentation/${nn}-doc.html` };
  });
  const files = new Map();
  for (const lesson of lessons) {
    const nn = String(lesson.number).padStart(2, '0');
    for (const basename of [`${nn}_build_exercises`, `${nn}_auxiliary`]) {
      files.set(`${lesson.directory}/exercises/${basename}.html`, {});
      files.set(`jupyter/files/${lesson.directory}/exercises/${basename}.ipynb`, {});
    }
  }
  return { lessons, files };
}

function siteCheck(id) {
  if (id.startsWith('page:')) {
    return { id, passed: true, status: 200, pageErrors: 0,
      horizontalOverflow: false, hasHome: true, homeTallEnough: true, notebookOk: true };
  }
  if (id.startsWith('mobile-fallback:')) {
    return { id, passed: true, requested: 'aula', mode: 'estudio', marked: true,
      navHidden: true, toolbar: true, scope: 'LIVE+REQUIRED', horizontal: false };
  }
  if (id === 'index:actions') return { id, passed: true, observed: 42, expected: 42 };
  if (id === 'index:blocks') return { id, passed: true, observed: 4, expected: 4 };
  if (id === 'index:return-home') {
    return { id, passed: true, returnedPath: '/algo_trading_intro/' };
  }
  return { id, passed: true, observed: 0 };
}

function baseEvidence(scope, targets) {
  const browser = webkitIdentity();
  const browserValidation = browserContract.validateBrowserIdentity(browser, browser, browser);
  return {
    schema: 'pages-e2e-evidence/v1',
    started_at: '2026-08-28T00:00:00.000Z',
    completed_at: '2026-08-28T00:01:00.000Z',
    failed_at: null,
    source_sha: HEAD,
    integrity_sha256: INTEGRITY_SHA,
    browser: structuredClone(browser),
    locked_browser: structuredClone(browser),
    browser_validation: structuredClone(browserValidation),
    scope: { ...scope, ...DEFAULT_SCOPE_LIMITS },
    targets,
    outcome: { completed: true, passed: true, failures: 0, error: null },
  };
}

function siteEvidence(siteInfo) {
  const checks = expectedSiteCheckIds(siteInfo.lessons).map(siteCheck);
  return baseEvidence({ runSite: true, labLessons: [] }, [{
    kind: 'site', id: 'mobile-webkit-site', passed: true,
    outcome: { failures: 0, sampledPages: 20, mobileFallbackLessons: 14,
      pageErrors: 0, externalRequests: 0, checks },
  }]);
}

function labAttempt(notebookPath, markerSha256) {
  return {
    reason: '', staticOk: true, responseOk: true, status: 200,
    labPath: '/algo_trading_intro/jupyter/lab/index.html',
    expectedNotebook: notebookPath, requestedNotebook: notebookPath,
    documentNameMatches: true, codeCells: 4, kernelReady: true,
    dispatchCount: 1, kernelPromptCount: 1, kernelExecutionCount: 1,
    markerSeen: true, markerOccurrences: 1, markerSha256, kernelIdle: true,
    stderr: false, labHome: 1, pageErrors: [], externalRequests: [],
  };
}

function marker(lesson, suffix) {
  return crypto.createHash('sha256').update(`${lesson}:${suffix}`).digest('hex');
}

function labEvidence(siteInfo, lessonNumber) {
  const lesson = siteInfo.lessons[lessonNumber - 1];
  const nn = String(lessonNumber).padStart(2, '0');
  const target = suffix => {
    const basename = suffix === 'build' ? `${nn}_build_exercises` : `${nn}_auxiliary`;
    const notebookPath = `${lesson.directory}/exercises/${basename}.ipynb`;
    return {
      kind: 'lab', id: `L${lessonNumber}-${suffix}`, lesson: lessonNumber,
      staticPath: `${lesson.directory}/exercises/${basename}.html`, notebookPath,
      passed: true,
      outcome: { failures: 0, successfulAttempt: 1,
        attempts: [labAttempt(notebookPath, marker(lessonNumber, suffix))] },
    };
  };
  return baseEvidence({ runSite: false, labLessons: [lessonNumber] },
    [target('build'), target('auxiliary')]);
}

function context(siteInfo, expected) {
  return { head: HEAD, integritySha256: INTEGRITY_SHA,
    lockedBrowser: webkitIdentity(), expected, siteInfo };
}

test('CLI selects one explicit shard or the closed aggregate mode', () => {
  const cwd = path.resolve('/tmp/pages-audit-cli');
  assert.deepEqual(parseArguments([
    '--site', 'built', '--evidence', 'artifacts/pages-e2e/lab-8.json',
    '--scope', 'lab', '--lesson', '8',
  ], cwd), {
    site: path.join(cwd, 'built'),
    evidence: path.join(cwd, 'artifacts/pages-e2e/lab-8.json'),
    aggregate: null, scope: 'lab', lesson: 8,
  });
  assert.equal(parseArguments(['--aggregate', 'evidence'], cwd).scope, 'aggregate');
  assert.throws(() => parseArguments([
    '--evidence', 'site.json', '--scope', 'lab',
  ], cwd), /requires --lesson/);
  assert.throws(() => parseArguments([
    '--evidence', 'site.json', '--aggregate', 'all', '--scope', 'site',
  ], cwd), /exactly one/);
  assert.throws(() => parseArguments([
    '--evidence', 'a', '--evidence', 'b', '--scope', 'site',
  ], cwd), /only once/);
});

test('repository provenance requires exact HEAD, GITHUB_SHA, and a clean tracked tree', () => {
  const calls = [];
  const git = args => {
    calls.push(args);
    if (args[0] === 'status') return '';
    return HEAD;
  };
  assert.deepEqual(repositoryState('/repo', HEAD, git),
    { head: HEAD, githubSha: HEAD, trackedClean: true });
  assert.deepEqual(calls, [
    ['rev-parse', '--verify', 'HEAD'],
    ['rev-parse', '--verify', `${HEAD}^{commit}`],
    ['status', '--porcelain=v1', '--untracked-files=no'],
  ]);
  assert.throws(() => repositoryState('/repo', undefined, git), /GITHUB_SHA is required/);
  assert.throws(() => repositoryState('/repo', 'a'.repeat(40), args =>
    args[0] === 'status' ? '' : HEAD), /does not resolve/);
  assert.throws(() => repositoryState('/repo', HEAD, args =>
    args[0] === 'status' ? ' M tracked.txt' : HEAD), /differs from HEAD/);
});

test('independent site and lab evidence validation rejects provenance and semantic tampering', () => {
  const siteInfo = fakeSiteInfo();
  const site = siteEvidence(siteInfo);
  assert.equal(validateEvidence(site, context(siteInfo, { kind: 'site' })).kind, 'site');
  const lab = labEvidence(siteInfo, 8);
  assert.deepEqual(validateEvidence(lab,
    context(siteInfo, { kind: 'lab', lesson: 8 })).targetIds,
  ['L8-build', 'L8-auxiliary']);

  const dirtySha = structuredClone(lab);
  dirtySha.source_sha = 'e'.repeat(40);
  assert.throws(() => validateEvidence(dirtySha,
    context(siteInfo, { kind: 'lab', lesson: 8 })), /source SHA/);
  const wrongIntegrity = structuredClone(lab);
  wrongIntegrity.integrity_sha256 = 'e'.repeat(64);
  assert.throws(() => validateEvidence(wrongIntegrity,
    context(siteInfo, { kind: 'lab', lesson: 8 })), /integrity manifest bytes/);
  const payloadSwap = structuredClone(lab);
  payloadSwap.browser.payload_sha256 = 'e'.repeat(64);
  assert.throws(() => validateEvidence(payloadSwap,
    context(siteInfo, { kind: 'lab', lesson: 8 })), /exact locked WebKit/);
  const falseKernel = structuredClone(lab);
  falseKernel.targets[0].outcome.attempts[0].kernelExecutionCount = 2;
  assert.throws(() => validateEvidence(falseKernel,
    context(siteInfo, { kind: 'lab', lesson: 8 })), /attempt ordering/);
  const missingCheck = structuredClone(site);
  missingCheck.targets[0].outcome.checks.pop();
  assert.throws(() => validateEvidence(missingCheck,
    context(siteInfo, { kind: 'site' })), /complete clean run/);
});

test('aggregate mode requires exactly site.json and lab-1..14.json with 29 unique targets', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-audit-aggregate-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const evidenceDirectory = path.join(root, 'artifacts', 'pages-e2e');
  fs.mkdirSync(evidenceDirectory, { recursive: true });
  fs.writeFileSync(path.join(root, 'package-lock.json'), JSON.stringify({
    packages: { 'node_modules/playwright': { version: '1.62.1' } },
  }));
  const siteInfo = fakeSiteInfo();
  fs.writeFileSync(path.join(evidenceDirectory, 'site.json'),
    `${JSON.stringify(siteEvidence(siteInfo))}\n`);
  for (let lesson = 1; lesson <= 14; lesson += 1) {
    fs.writeFileSync(path.join(evidenceDirectory, `lab-${lesson}.json`),
      `${JSON.stringify(labEvidence(siteInfo, lesson))}\n`);
  }
  const result = validateAggregateDirectory(evidenceDirectory, {
    root, head: HEAD, integritySha256: INTEGRITY_SHA,
    siteInfo,
  });
  assert.deepEqual(result, { evidenceFiles: 15, targets: 29, markers: 28 });
  let browserLockCalls = 0;
  const audit = validateAudit({ site: path.join(root, '_site'), evidence: null,
    aggregate: evidenceDirectory, scope: 'aggregate', lesson: null }, {
    root,
    environment: { GITHUB_SHA: HEAD },
    repositoryState: () => ({ head: HEAD, githubSha: HEAD, trackedClean: true }),
    inspectSite: () => ({ ...siteInfo, site: path.join(root, '_site'),
      integritySha256: INTEGRITY_SHA }),
    runCheckPages: () => ({ status: 0 }),
    lockedWebKitIdentity: () => { browserLockCalls += 1; throw new Error('must not run'); },
  });
  assert.equal(audit.passed, true);
  assert.equal(browserLockCalls, 0);
  fs.writeFileSync(path.join(evidenceDirectory, 'extra.json'), '{}\n');
  assert.throws(() => validateAggregateDirectory(evidenceDirectory, {
    root, head: HEAD, integritySha256: INTEGRITY_SHA,
    siteInfo,
  }), /aggregate evidence set differs/);
});

test('shard evidence rejects a non-canonical name and a symlinked evidence directory', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-audit-shard-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-audit-shard-out-'));
  t.after(() => {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  });
  const siteInfo = fakeSiteInfo();
  const realDirectory = path.join(root, 'artifacts', 'pages-e2e-real');
  fs.mkdirSync(realDirectory, { recursive: true });
  fs.writeFileSync(path.join(realDirectory, 'wrong.json'), JSON.stringify(siteEvidence(siteInfo)));
  assert.throws(() => validateEvidenceFile(path.join(realDirectory, 'wrong.json'), {
    root, ...context(siteInfo, { kind: 'site' }),
  }), /filename must be site.json/);

  fs.writeFileSync(path.join(outside, 'site.json'), JSON.stringify(siteEvidence(siteInfo)));
  fs.symlinkSync(outside, path.join(root, 'evidence-link'));
  assert.throws(() => validateEvidenceFile(path.join(root, 'evidence-link', 'site.json'), {
    root, ...context(siteInfo, { kind: 'site' }),
  }), /real directory|symlink/);
});

function sha256File(filename) {
  return crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
}

function makeInspectableSite(root) {
  const site = path.join(root, '_site');
  fs.mkdirSync(site);
  for (let lesson = 1; lesson <= 14; lesson += 1) {
    const nn = String(lesson).padStart(2, '0');
    const presentation = path.join(site, `${nn}-lesson`, 'presentation');
    fs.mkdirSync(presentation, { recursive: true });
    fs.writeFileSync(path.join(presentation, `${nn}-doc.html`), '<!doctype html>\n');
  }
  const config = path.join(site, 'jupyter', 'jupyter-lite.json');
  const pyodide = path.join(site, 'jupyter', 'static', 'pyodide', 'pyodide.js');
  fs.mkdirSync(path.dirname(config), { recursive: true });
  fs.mkdirSync(path.dirname(pyodide), { recursive: true });
  fs.writeFileSync(config, '{}\n');
  fs.writeFileSync(pyodide, 'payload\n');
  const files = [];
  const visit = directory => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const candidate = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(candidate);
      else {
        const relative = path.relative(site, candidate).split(path.sep).join('/');
        files.push({ path: relative, size: fs.statSync(candidate).size,
          sha256: sha256File(candidate) });
      }
    }
  };
  visit(site);
  files.sort((left, right) => left.path.localeCompare(right.path));
  const pyodideFiles = files.filter(record => record.path.startsWith('jupyter/static/pyodide/'));
  const configRecord = files.find(record => record.path === 'jupyter/jupyter-lite.json');
  const integrity = {
    schema: 2, hash_algorithm: 'SHA-256', github_sha: HEAD,
    build_inputs: [{ path: 'framework/_build/pages_public_manifest.json', size: 0,
      sha256: '0'.repeat(64) }],
    source_manifest_sha256: '1'.repeat(64),
    source_files: [{ path: 'index.html', size: 0, sha256: '2'.repeat(64) }],
    pyodide_archive_sha256: '3'.repeat(64),
    config: { path: configRecord.path, sha256: configRecord.sha256 },
    pyodide_files: pyodideFiles,
    files,
  };
  fs.writeFileSync(path.join(site, '.pages-integrity.json'), `${JSON.stringify(integrity)}\n`);
  return site;
}

test('site inspection validates integrity structure and rejects artifact symlinks', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-audit-site-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const site = makeInspectableSite(root);
  const inspected = inspectSite(root, site, HEAD);
  assert.equal(inspected.lessons.length, 14);
  assert.match(inspected.integritySha256, /^[0-9a-f]{64}$/);
  fs.symlinkSync('01-doc.html', path.join(site, '01-lesson', 'presentation', 'alias.html'));
  assert.throws(() => inspectSite(root, site, HEAD), /contains a symlink/);
});

test('check_pages integration preserves argv and fails closed on a non-zero checker', () => {
  let observed;
  const success = (_command, args, options) => {
    observed = { args, options };
    return { status: 0, stdout: 'Pages OK\n', stderr: '' };
  };
  const result = runCheckPages('/repo', '/repo/_site', {
    GITHUB_SHA: HEAD, PAGES_AUDIT_PYTHON: '/python',
  }, success);
  assert.equal(result.status, 0);
  assert.deepEqual(observed.args, [
    '/repo/framework/_build/check_pages.py', '/repo/_site',
    '--base-path', '/algo_trading_intro/',
  ]);
  assert.throws(() => runCheckPages('/repo', '/repo/_site', {}, () =>
    ({ status: 1, stdout: '', stderr: 'tampered' })), /tampered/);
});
