'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const util = require('util');
const { execFileSync, spawnSync } = require('child_process');
const browserContract = require('./desktop_evidence_contract');

const ROOT = path.resolve(__dirname, '..', '..');
const BASE_PATH = '/algo_trading_intro/';
const INTEGRITY_NAME = '.pages-integrity.json';
const EVIDENCE_SCHEMA = 'pages-e2e-evidence/v1';
const SHA40 = /^[0-9a-f]{40}$/;
const SHA256 = /^[0-9a-f]{64}$/;
const MAX_JSON_BYTES = 32 * 1024 * 1024;
const SCOPE_FIELDS = [
  'runSite', 'labLessons', 'maxLabAttempts', 'kernelTimeoutMs',
  'outputTimeoutMs', 'readyStableMs', 'idleStableMs',
];
const TOP_LEVEL_FIELDS = [
  'schema', 'started_at', 'completed_at', 'failed_at', 'source_sha',
  'integrity_sha256', 'browser', 'locked_browser', 'browser_validation',
  'scope', 'targets', 'outcome',
];
const DEFAULT_SCOPE_LIMITS = Object.freeze({
  maxLabAttempts: 2,
  kernelTimeoutMs: 120000,
  outputTimeoutMs: 90000,
  readyStableMs: 750,
  idleStableMs: 1500,
});

function invariant(condition, message) {
  if (!condition) throw new Error(message);
}

function sorted(value) {
  return [...value].sort();
}

function exactKeys(value, expected, label) {
  invariant(value && typeof value === 'object' && !Array.isArray(value),
    `${label} must be an object`);
  const actual = sorted(Object.keys(value));
  invariant(util.isDeepStrictEqual(actual, sorted(expected)),
    `${label} has unexpected or missing fields: ${JSON.stringify(actual)}`);
}

function isInside(root, target) {
  const relative = path.relative(root, target);
  return relative === '' || (!path.isAbsolute(relative) && relative !== '..'
    && !relative.startsWith(`..${path.sep}`));
}

function assertRealDirectory(directory, label) {
  const requested = path.resolve(directory);
  const stat = fs.lstatSync(requested);
  invariant(stat.isDirectory() && !stat.isSymbolicLink(), `${label} must be a real directory`);
  invariant(fs.realpathSync.native(requested) === requested,
    `${label} or one of its ancestors is a symlink`);
  return requested;
}

function assertRegularFile(filename, label) {
  const requested = path.resolve(filename);
  const stat = fs.lstatSync(requested);
  invariant(stat.isFile() && !stat.isSymbolicLink(), `${label} must be a regular file`);
  invariant(fs.realpathSync.native(requested) === requested,
    `${label} or one of its ancestors is a symlink`);
  invariant(Number.isSafeInteger(stat.size) && stat.size >= 0 && stat.size <= MAX_JSON_BYTES,
    `${label} exceeds the JSON safety limit`);
  return { filename: requested, stat };
}

function sha256Buffer(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function readJsonRegular(filename, label) {
  const identity = assertRegularFile(filename, label);
  const bytes = fs.readFileSync(identity.filename);
  let value;
  try { value = JSON.parse(bytes.toString('utf8')); }
  catch (error) { throw new Error(`${label} is invalid JSON: ${error.message}`); }
  return { value, bytes, sha256: sha256Buffer(bytes), filename: identity.filename };
}

function safeRelative(value, label) {
  invariant(typeof value === 'string' && value.length > 0 && !value.includes('\\'),
    `${label} path must be a non-empty POSIX path`);
  invariant(!path.posix.isAbsolute(value) && path.posix.normalize(value) === value
    && value !== '.' && !value.startsWith('../') && !value.includes('/../'),
  `${label} path is unsafe: ${JSON.stringify(value)}`);
  return value;
}

function walkRegularFiles(root) {
  const files = new Map();
  let visited = 0;
  const visit = directory => {
    for (const name of fs.readdirSync(directory).sort()) {
      const candidate = path.join(directory, name);
      const relative = path.relative(root, candidate).split(path.sep).join('/');
      const stat = fs.lstatSync(candidate);
      invariant(!stat.isSymbolicLink(), `Pages artifact contains a symlink: ${relative}`);
      if (stat.isDirectory()) {
        visit(candidate);
      } else if (stat.isFile()) {
        invariant(Number.isSafeInteger(stat.size) && stat.size >= 0,
          `Pages artifact contains an unsafe file size: ${relative}`);
        files.set(relative, { filename: candidate, size: stat.size });
      } else {
        throw new Error(`Pages artifact contains a special file: ${relative}`);
      }
      visited += 1;
      invariant(visited <= 250000, 'Pages artifact exceeds the traversal safety limit');
    }
  };
  visit(root);
  return files;
}

function parseRecordArray(value, label, { nonEmpty = true } = {}) {
  invariant(Array.isArray(value) && (!nonEmpty || value.length > 0),
    `${label} must be ${nonEmpty ? 'a non-empty ' : 'an '}array`);
  const records = new Map();
  const identities = [];
  for (const record of value) {
    exactKeys(record, ['path', 'size', 'sha256'], `${label} record`);
    const identity = safeRelative(record.path, label);
    invariant(!records.has(identity), `${label} duplicates ${identity}`);
    invariant(Number.isSafeInteger(record.size) && record.size >= 0,
      `${label} has an invalid size for ${identity}`);
    invariant(typeof record.sha256 === 'string' && SHA256.test(record.sha256),
      `${label} has an invalid SHA-256 for ${identity}`);
    identities.push(identity);
    records.set(identity, record);
  }
  invariant(util.isDeepStrictEqual(identities, sorted(identities)), `${label} is not sorted`);
  return records;
}

function discoverSiteLessons(site, files) {
  const lessons = [];
  for (const entry of fs.readdirSync(site, { withFileTypes: true })) {
    const match = /^(\d\d)-/.exec(entry.name);
    if (!match) continue;
    invariant(entry.isDirectory(), `lesson entry is not a directory: ${entry.name}`);
    const number = Number(match[1]);
    if (number < 1 || number > 14) continue;
    const presentation = path.join(site, entry.name, 'presentation');
    const presentationStat = fs.lstatSync(presentation);
    invariant(presentationStat.isDirectory() && !presentationStat.isSymbolicLink(),
      `L${number} presentation is not a real directory`);
    const documents = fs.readdirSync(presentation)
      .filter(name => name.endsWith('-doc.html')).sort();
    invariant(documents.length === 1, `L${number} must publish exactly one interactive document`);
    const relative = `${entry.name}/presentation/${documents[0]}`;
    invariant(files.has(relative), `L${number} interactive document is not a regular file`);
    lessons.push({ number, directory: entry.name, relative });
  }
  lessons.sort((left, right) => left.number - right.number);
  invariant(lessons.length === 14
    && lessons.every((lesson, index) => lesson.number === index + 1),
  `Pages artifact does not contain exactly L1-L14: ${lessons.map(item => item.number)}`);
  return lessons;
}

function inspectSite(root, requestedSite, head) {
  const realRoot = fs.realpathSync.native(root);
  const site = assertRealDirectory(requestedSite, 'Pages site root');
  invariant(isInside(realRoot, site) && site !== realRoot,
    'Pages site root must be a child of the repository');
  const files = walkRegularFiles(site);
  invariant(files.has(INTEGRITY_NAME), 'Pages integrity manifest is missing');
  const integrityRecord = readJsonRegular(path.join(site, INTEGRITY_NAME),
    'Pages integrity manifest');
  const integrity = integrityRecord.value;
  exactKeys(integrity, [
    'schema', 'hash_algorithm', 'github_sha', 'build_inputs',
    'source_manifest_sha256', 'source_files', 'pyodide_archive_sha256',
    'config', 'pyodide_files', 'files',
  ], 'Pages integrity manifest');
  invariant(integrity.schema === 2 && integrity.hash_algorithm === 'SHA-256',
    'Pages integrity manifest has an unsupported schema');
  invariant(integrity.github_sha === head,
    'Pages integrity manifest SHA does not match checked-out HEAD');
  invariant(typeof integrity.source_manifest_sha256 === 'string'
    && SHA256.test(integrity.source_manifest_sha256), 'invalid source manifest SHA-256');
  invariant(typeof integrity.pyodide_archive_sha256 === 'string'
    && SHA256.test(integrity.pyodide_archive_sha256), 'invalid Pyodide archive SHA-256');
  const buildInputs = parseRecordArray(integrity.build_inputs, 'build_inputs');
  const sourceFiles = parseRecordArray(integrity.source_files, 'source_files');
  const publicFiles = parseRecordArray(integrity.files, 'files');
  const pyodideFiles = parseRecordArray(integrity.pyodide_files, 'pyodide_files');
  invariant(buildInputs.has('framework/_build/pages_public_manifest.json'),
    'build_inputs omits the public manifest');
  invariant(sourceFiles.size > 0, 'source_files is empty');
  const actual = new Map([...files].filter(([identity]) => identity !== INTEGRITY_NAME));
  invariant(util.isDeepStrictEqual(sorted(actual.keys()), sorted(publicFiles.keys())),
    'Pages integrity file set differs from the regular-file tree');
  for (const [identity, record] of publicFiles) {
    invariant(actual.get(identity).size === record.size,
      `Pages integrity size differs for ${identity}`);
  }
  exactKeys(integrity.config, ['path', 'sha256'], 'Pages JupyterLite config');
  invariant(integrity.config.path === 'jupyter/jupyter-lite.json'
    && SHA256.test(integrity.config.sha256 || '')
    && publicFiles.get(integrity.config.path)?.sha256 === integrity.config.sha256,
  'Pages JupyterLite config is not pinned to the public file record');
  const expectedPyodide = [...publicFiles.values()]
    .filter(record => record.path.startsWith('jupyter/static/pyodide/'));
  invariant(expectedPyodide.length > 0
    && util.isDeepStrictEqual(expectedPyodide, integrity.pyodide_files),
  'Pages Pyodide record set is not the exact public subset');
  invariant(pyodideFiles.size === expectedPyodide.length,
    'Pages Pyodide file set contains duplicates');
  const lessons = discoverSiteLessons(site, files);
  return { site, files, integrity, integritySha256: integrityRecord.sha256, lessons };
}

function defaultGit(root) {
  return args => execFileSync('git', args, {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

function repositoryState(root, githubSha, git = defaultGit(root)) {
  invariant(typeof githubSha === 'string' && SHA40.test(githubSha),
    'GITHUB_SHA is required and must be 40 lowercase hexadecimal characters');
  const head = git(['rev-parse', '--verify', 'HEAD']).trim();
  invariant(SHA40.test(head), `repository HEAD is invalid: ${head}`);
  const commit = git(['rev-parse', '--verify', `${githubSha}^{commit}`]).trim();
  invariant(commit === githubSha, 'GITHUB_SHA does not resolve to the expected commit');
  invariant(head === githubSha, `GITHUB_SHA ${githubSha} does not match HEAD ${head}`);
  const status = git(['status', '--porcelain=v1', '--untracked-files=no']).trim();
  invariant(status === '', 'tracked worktree or index differs from HEAD');
  return { head, githubSha, trackedClean: true };
}

function runCheckPages(root, site, env = process.env, runner = spawnSync) {
  const python = env.PAGES_AUDIT_PYTHON || env.PYTHON || 'python3';
  const checker = path.join(root, 'framework', '_build', 'check_pages.py');
  const result = runner(python, [checker, site, '--base-path', BASE_PATH], {
    cwd: root,
    env,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (result.error) throw new Error(`cannot execute check_pages.py: ${result.error.message}`);
  invariant(result.status === 0,
    `check_pages.py rejected the artifact: ${(result.stderr || result.stdout || '').trim()}`);
  return { status: result.status, stdout: (result.stdout || '').trim() };
}

function lockedWebKitIdentity(root) {
  const playwrightModule = require.resolve('playwright', { paths: [root] });
  const { webkit } = require(playwrightModule);
  const executable = fs.realpathSync.native(webkit.executablePath());
  const stat = fs.lstatSync(executable);
  invariant(stat.isFile() && !stat.isSymbolicLink() && stat.size > 0,
    'locked WebKit launcher is not a non-empty regular file');
  return browserContract.lockedPlaywrightBrowserIdentity(root, 'webkit', executable);
}

function validIsoDate(value) {
  if (typeof value !== 'string') return false;
  const time = Date.parse(value);
  return Number.isFinite(time) && new Date(time).toISOString() === value;
}

function validateBrowserEvidence(evidence, lockedBrowser) {
  invariant(util.isDeepStrictEqual(evidence.locked_browser, lockedBrowser),
    'evidence locked_browser differs from the independently recomputed WebKit payload');
  const recomputed = browserContract.validateBrowserIdentity(
    evidence.browser, lockedBrowser, evidence.browser);
  invariant(recomputed.passed, 'evidence does not identify the exact locked WebKit browser');
  invariant(util.isDeepStrictEqual(evidence.browser_validation, recomputed),
    'browser_validation differs from independent recomputation');
}

function validateScope(scope, expected) {
  exactKeys(scope, SCOPE_FIELDS, 'evidence scope');
  invariant(scope.runSite === (expected.kind === 'site'), 'evidence runSite scope mismatch');
  const lessons = expected.kind === 'site' ? [] : [expected.lesson];
  invariant(util.isDeepStrictEqual(scope.labLessons, lessons), 'evidence labLessons scope mismatch');
  for (const [field, value] of Object.entries(DEFAULT_SCOPE_LIMITS)) {
    invariant(scope[field] === value, `evidence scope ${field} differs from the audited contract`);
  }
}

function expectedSiteCheckIds(lessons) {
  return [
    'page:index',
    ...lessons.map(lesson => `page:${lesson.relative}`),
    'page:06-oop-iii-inheritance/checkpoint.html',
    'page:15-final-exam/examen.html',
    'page:01-python-i-data-model/exercises/01_build_exercises.html',
    'page:08-order-types-matching/exercises/08_auxiliary.html',
    'page:14-avellaneda-stoikov/exercises/14_build_exercises.html',
    ...lessons.map(lesson => `mobile-fallback:L${lesson.number}`),
    'index:actions', 'index:blocks', 'index:return-home',
    'site:late-page-errors', 'site:close-page-errors', 'site:external-requests',
  ];
}

function validateSiteCheck(check) {
  invariant(check && typeof check === 'object' && !Array.isArray(check),
    'site check must be an object');
  invariant(typeof check.id === 'string' && check.passed === true,
    'site check must have a passing id');
  if (check.id.startsWith('page:')) {
    exactKeys(check, ['id', 'passed', 'status', 'pageErrors', 'horizontalOverflow',
      'hasHome', 'homeTallEnough', 'notebookOk'], `site check ${check.id}`);
    invariant(check.status === 200 && check.pageErrors === 0
      && check.horizontalOverflow === false && check.hasHome === true
      && check.homeTallEnough === true && check.notebookOk === true,
    `site page check is not substantively clean: ${check.id}`);
  } else if (check.id.startsWith('mobile-fallback:')) {
    exactKeys(check, ['id', 'passed', 'requested', 'mode', 'marked', 'navHidden',
      'toolbar', 'scope', 'horizontal'], `site check ${check.id}`);
    invariant(check.requested === 'aula' && check.mode === 'estudio'
      && check.marked === true && check.navHidden === true && check.toolbar === true
      && check.scope === 'LIVE+REQUIRED' && check.horizontal === false,
    `mobile fallback check is not substantively clean: ${check.id}`);
  } else if (check.id === 'index:actions') {
    exactKeys(check, ['id', 'passed', 'observed', 'expected'], check.id);
    invariant(check.observed === 42 && check.expected === 42, 'index action count is not 42');
  } else if (check.id === 'index:blocks') {
    exactKeys(check, ['id', 'passed', 'observed', 'expected'], check.id);
    invariant(check.observed === 4 && check.expected === 4, 'index block count is not 4');
  } else if (check.id === 'index:return-home') {
    exactKeys(check, ['id', 'passed', 'returnedPath'], check.id);
    invariant([BASE_PATH, `${BASE_PATH}index.html`].includes(check.returnedPath),
      'course return link does not resolve to the project root');
  } else {
    exactKeys(check, ['id', 'passed', 'observed'], check.id);
    invariant(check.observed === 0, `${check.id} records a non-zero failure count`);
  }
}

function validateSiteTarget(target, siteInfo) {
  exactKeys(target, ['kind', 'id', 'passed', 'outcome'], 'site evidence target');
  invariant(target.kind === 'site' && target.id === 'mobile-webkit-site'
    && target.passed === true, 'site evidence target identity or outcome is invalid');
  const outcome = target.outcome;
  exactKeys(outcome, ['failures', 'sampledPages', 'mobileFallbackLessons',
    'pageErrors', 'externalRequests', 'checks'], 'site target outcome');
  const expectedIds = expectedSiteCheckIds(siteInfo.lessons);
  invariant(outcome.failures === 0 && outcome.sampledPages === 20
    && outcome.mobileFallbackLessons === 14 && outcome.pageErrors === 0
    && outcome.externalRequests === 0 && Array.isArray(outcome.checks)
    && outcome.checks.length === expectedIds.length,
  'site target summary is not a complete clean run');
  const ids = outcome.checks.map(check => check?.id);
  invariant(new Set(ids).size === ids.length
    && util.isDeepStrictEqual(sorted(ids), sorted(expectedIds)),
  'site target check set is not the closed 40-check contract');
  outcome.checks.forEach(validateSiteCheck);
  return [];
}

const ATTEMPT_FIELDS = [
  'reason', 'staticOk', 'responseOk', 'status', 'labPath', 'expectedNotebook',
  'requestedNotebook', 'documentNameMatches', 'codeCells', 'kernelReady',
  'dispatchCount', 'kernelPromptCount', 'kernelExecutionCount', 'markerSeen',
  'markerOccurrences', 'markerSha256', 'kernelIdle', 'stderr', 'labHome',
  'pageErrors', 'externalRequests',
];

function validateAttemptShape(attempt, label) {
  exactKeys(attempt, ATTEMPT_FIELDS, label);
  invariant(typeof attempt.reason === 'string'
    && typeof attempt.staticOk === 'boolean' && typeof attempt.responseOk === 'boolean'
    && (attempt.status === null || Number.isSafeInteger(attempt.status))
    && typeof attempt.labPath === 'string'
    && (attempt.expectedNotebook === null || typeof attempt.expectedNotebook === 'string')
    && (attempt.requestedNotebook === null || typeof attempt.requestedNotebook === 'string')
    && typeof attempt.documentNameMatches === 'boolean'
    && Number.isSafeInteger(attempt.codeCells) && attempt.codeCells >= 0
    && typeof attempt.kernelReady === 'boolean'
    && Number.isSafeInteger(attempt.dispatchCount) && attempt.dispatchCount >= 0
    && Number.isSafeInteger(attempt.kernelPromptCount) && attempt.kernelPromptCount >= 0
    && (attempt.kernelExecutionCount === null || Number.isSafeInteger(attempt.kernelExecutionCount))
    && typeof attempt.markerSeen === 'boolean'
    && Number.isSafeInteger(attempt.markerOccurrences) && attempt.markerOccurrences >= 0
    && (attempt.markerSha256 === null || SHA256.test(attempt.markerSha256))
    && typeof attempt.kernelIdle === 'boolean' && typeof attempt.stderr === 'boolean'
    && Number.isSafeInteger(attempt.labHome) && attempt.labHome >= 0
    && Array.isArray(attempt.pageErrors) && attempt.pageErrors.every(item => typeof item === 'string')
    && Array.isArray(attempt.externalRequests)
    && attempt.externalRequests.every(item => typeof item === 'string'),
  `${label} contains malformed fields`);
}

function isCleanLabAttempt(attempt, notebookPath) {
  return attempt.reason === '' && attempt.staticOk === true && attempt.responseOk === true
    && attempt.status === 200 && attempt.labPath.startsWith(`${BASE_PATH}jupyter/lab/`)
    && attempt.expectedNotebook === notebookPath && attempt.requestedNotebook === notebookPath
    && attempt.documentNameMatches === true && attempt.codeCells > 0
    && attempt.kernelReady === true && attempt.dispatchCount === 1
    && attempt.kernelPromptCount === 1 && attempt.kernelExecutionCount === 1
    && attempt.markerSeen === true && attempt.markerOccurrences === 1
    && SHA256.test(attempt.markerSha256 || '') && attempt.kernelIdle === true
    && attempt.stderr === false && attempt.labHome === 1
    && attempt.pageErrors.length === 0 && attempt.externalRequests.length === 0;
}

function expectedLabTarget(siteInfo, lessonNumber, suffix) {
  const lesson = siteInfo.lessons[lessonNumber - 1];
  const nn = String(lessonNumber).padStart(2, '0');
  const basename = suffix === 'build' ? `${nn}_build_exercises` : `${nn}_auxiliary`;
  const staticPath = `${lesson.directory}/exercises/${basename}.html`;
  const notebookPath = `${lesson.directory}/exercises/${basename}.ipynb`;
  invariant(siteInfo.files.has(staticPath), `Pages site omits ${staticPath}`);
  invariant(siteInfo.files.has(`jupyter/files/${notebookPath}`),
    `Pages Jupyter projection omits ${notebookPath}`);
  return { id: `L${lessonNumber}-${suffix}`, staticPath, notebookPath };
}

function validateLabTarget(target, expected, maxAttempts) {
  exactKeys(target, ['kind', 'id', 'lesson', 'staticPath', 'notebookPath',
    'passed', 'outcome'], `lab target ${expected.id}`);
  invariant(target.kind === 'lab' && target.id === expected.id
    && target.lesson === expected.lesson && target.staticPath === expected.staticPath
    && target.notebookPath === expected.notebookPath && target.passed === true,
  `lab target ${expected.id} identity or path differs from the site contract`);
  const outcome = target.outcome;
  exactKeys(outcome, ['failures', 'successfulAttempt', 'attempts'],
    `lab outcome ${expected.id}`);
  invariant(outcome.failures === 0 && Array.isArray(outcome.attempts)
    && outcome.attempts.length >= 1 && outcome.attempts.length <= maxAttempts
    && outcome.successfulAttempt === outcome.attempts.length,
  `lab outcome ${expected.id} is not a bounded successful retry sequence`);
  outcome.attempts.forEach((attempt, index) => {
    validateAttemptShape(attempt, `${expected.id} attempt ${index + 1}`);
    const clean = isCleanLabAttempt(attempt, expected.notebookPath);
    invariant(clean === (index === outcome.attempts.length - 1),
      `${expected.id} successful/failed attempt ordering is inconsistent`);
  });
  return outcome.attempts.at(-1).markerSha256;
}

function validateLabTargets(targets, expected, siteInfo, maxAttempts) {
  invariant(Array.isArray(targets) && targets.length === 2,
    `lab-${expected.lesson} evidence must contain exactly two targets`);
  const expectedTargets = ['build', 'auxiliary'].map(suffix => ({
    lesson: expected.lesson,
    ...expectedLabTarget(siteInfo, expected.lesson, suffix),
  }));
  const byId = new Map(targets.map(target => [target?.id, target]));
  invariant(byId.size === 2 && expectedTargets.every(item => byId.has(item.id)),
    `lab-${expected.lesson} target set is not build+auxiliary`);
  return expectedTargets.map(item => validateLabTarget(byId.get(item.id), item, maxAttempts));
}

function validateEvidence(evidence, context) {
  const { head, integritySha256, lockedBrowser, expected, siteInfo } = context;
  exactKeys(evidence, TOP_LEVEL_FIELDS, 'Pages WebKit evidence');
  invariant(evidence.schema === EVIDENCE_SCHEMA, 'Pages evidence schema mismatch');
  invariant(validIsoDate(evidence.started_at) && validIsoDate(evidence.completed_at)
    && evidence.failed_at === null
    && Date.parse(evidence.completed_at) >= Date.parse(evidence.started_at),
  'Pages evidence timestamps do not describe a completed run');
  invariant(evidence.source_sha === head, 'Pages evidence source SHA does not match HEAD');
  invariant(evidence.integrity_sha256 === integritySha256,
    'Pages evidence does not bind the exact integrity manifest bytes');
  validateBrowserEvidence(evidence, lockedBrowser);
  validateScope(evidence.scope, expected);
  exactKeys(evidence.outcome, ['completed', 'passed', 'failures', 'error'],
    'Pages evidence outcome');
  invariant(evidence.outcome.completed === true && evidence.outcome.passed === true
    && evidence.outcome.failures === 0 && evidence.outcome.error === null,
  'Pages evidence is incomplete or records failures');
  let markers = [];
  if (expected.kind === 'site') {
    invariant(Array.isArray(evidence.targets) && evidence.targets.length === 1,
      'site evidence must contain exactly one target');
    markers = validateSiteTarget(evidence.targets[0], siteInfo);
  } else {
    markers = validateLabTargets(evidence.targets, expected, siteInfo,
      evidence.scope.maxLabAttempts);
  }
  invariant(new Set(markers).size === markers.length,
    'a lab shard reuses a marker digest across targets');
  return { kind: expected.kind, lesson: expected.lesson || null,
    targetIds: evidence.targets.map(target => target.id), markers };
}

function expectedEvidenceName(expected) {
  return expected.kind === 'site' ? 'site.json' : `lab-${expected.lesson}.json`;
}

function validateEvidenceFile(filename, context) {
  const resolved = path.resolve(filename);
  invariant(isInside(fs.realpathSync.native(context.root), resolved),
    'Pages evidence must be inside the repository');
  const directory = assertRealDirectory(path.dirname(resolved), 'Pages evidence directory');
  invariant(path.dirname(resolved) === directory, 'Pages evidence directory identity changed');
  invariant(path.basename(resolved) === expectedEvidenceName(context.expected),
    `Pages evidence filename must be ${expectedEvidenceName(context.expected)}`);
  const record = readJsonRegular(resolved, 'Pages evidence');
  return validateEvidence(record.value, context);
}

function validateAggregateBrowserLock(root, lockedBrowser) {
  const lock = readJsonRegular(path.join(root, 'package-lock.json'), 'npm lockfile').value;
  const version = lock?.packages?.['node_modules/playwright']?.version;
  invariant(typeof version === 'string' && version.length > 0,
    'npm lockfile does not pin Playwright');
  const selfValidation = browserContract.validateBrowserIdentity(
    lockedBrowser, lockedBrowser, lockedBrowser);
  invariant(selfValidation.passed && lockedBrowser.name === 'webkit'
    && lockedBrowser.product === 'webkit' && lockedBrowser.playwright === version,
  'aggregate WebKit identity is malformed or differs from package-lock.json');
}

function validateAggregateDirectory(directory, context) {
  const root = fs.realpathSync.native(context.root);
  const resolved = assertRealDirectory(directory, 'Pages aggregate evidence directory');
  invariant(isInside(root, resolved), 'Pages aggregate evidence must be inside the repository');
  const expectedNames = [
    'site.json',
    ...Array.from({ length: 14 }, (_, index) => `lab-${index + 1}.json`),
  ];
  const entries = fs.readdirSync(resolved, { withFileTypes: true });
  invariant(entries.every(entry => entry.isFile() && !entry.isSymbolicLink()),
    'Pages aggregate evidence directory contains a non-regular entry');
  const actualNames = entries.map(entry => entry.name).sort();
  invariant(util.isDeepStrictEqual(actualNames, sorted(expectedNames)),
    `Pages aggregate evidence set differs: ${JSON.stringify(actualNames)}`);
  const records = new Map(expectedNames.map(name => [name,
    readJsonRegular(path.join(resolved, name), `Pages evidence ${name}`).value]));
  const aggregateLockedBrowser = context.lockedBrowser
    || records.get('site.json')?.locked_browser;
  if (!context.lockedBrowser) validateAggregateBrowserLock(root, aggregateLockedBrowser);
  const results = [];
  for (const name of expectedNames) {
    const expected = name === 'site.json'
      ? { kind: 'site' }
      : { kind: 'lab', lesson: Number(/^lab-(\d+)\.json$/.exec(name)[1]) };
    results.push(validateEvidence(records.get(name), { ...context,
      lockedBrowser: aggregateLockedBrowser, expected }));
  }
  const targetIds = results.flatMap(result => result.targetIds);
  const expectedTargetIds = ['mobile-webkit-site', ...Array.from({ length: 14 }, (_, index) => {
    const lesson = index + 1;
    return [`L${lesson}-build`, `L${lesson}-auxiliary`];
  }).flat()];
  invariant(new Set(targetIds).size === targetIds.length
    && util.isDeepStrictEqual(sorted(targetIds), sorted(expectedTargetIds)),
  'Pages aggregate target set is not the closed site+L1-L14 contract');
  const markers = results.flatMap(result => result.markers);
  invariant(markers.length === 28 && new Set(markers).size === markers.length,
    'Pages aggregate evidence reuses or omits lab marker digests');
  return { evidenceFiles: results.length, targets: targetIds.length, markers: markers.length };
}

function parseArguments(argv = process.argv.slice(2), cwd = process.cwd()) {
  const parsed = { site: path.resolve(cwd, '_site'), evidence: null,
    aggregate: null, scope: null, lesson: null };
  const values = new Set(['--site', '--evidence', '--aggregate', '--scope', '--lesson']);
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 1) {
    const option = argv[index];
    invariant(values.has(option), `unknown Pages audit option: ${option}`);
    invariant(!seen.has(option), `${option} may be specified only once`);
    seen.add(option);
    invariant(index + 1 < argv.length && !argv[index + 1].startsWith('--'),
      `${option} requires a value`);
    const value = argv[++index];
    if (option === '--site') parsed.site = path.resolve(cwd, value);
    else if (option === '--evidence') parsed.evidence = path.resolve(cwd, value);
    else if (option === '--aggregate') parsed.aggregate = path.resolve(cwd, value);
    else if (option === '--scope') parsed.scope = value;
    else if (option === '--lesson') parsed.lesson = value;
  }
  invariant(Boolean(parsed.evidence) !== Boolean(parsed.aggregate),
    'choose exactly one of --evidence or --aggregate');
  if (parsed.aggregate) {
    invariant(parsed.scope === null || parsed.scope === 'aggregate',
      '--aggregate only accepts --scope aggregate');
    invariant(parsed.lesson === null, '--aggregate cannot select one lesson');
    parsed.scope = 'aggregate';
  } else {
    invariant(['site', 'lab'].includes(parsed.scope),
      '--evidence requires --scope site or --scope lab');
    if (parsed.scope === 'site') {
      invariant(parsed.lesson === null, '--scope site cannot select a lesson');
    } else {
      invariant(typeof parsed.lesson === 'string' && /^(?:[1-9]|1[0-4])$/.test(parsed.lesson),
        '--scope lab requires --lesson 1..14');
      parsed.lesson = Number(parsed.lesson);
    }
  }
  return parsed;
}

function validateAudit(options, dependencies = {}) {
  const root = fs.realpathSync.native(dependencies.root || ROOT);
  const environment = dependencies.environment || process.env;
  const state = (dependencies.repositoryState || repositoryState)(
    root, environment.GITHUB_SHA, dependencies.git || defaultGit(root));
  const siteInfo = (dependencies.inspectSite || inspectSite)(root, options.site, state.head);
  (dependencies.runCheckPages || runCheckPages)(root, siteInfo.site, environment);
  // Every shard independently hashes the installed WebKit registry payload. The
  // aggregate job only consumes immutable artifacts from those successful jobs,
  // so it cross-checks their common identity against package-lock.json without
  // downloading and hashing the same browser a sixteenth time.
  const lockedBrowser = options.scope === 'aggregate' ? null
    : (dependencies.lockedWebKitIdentity || lockedWebKitIdentity)(root);
  const context = { root, head: state.head, integritySha256: siteInfo.integritySha256,
    lockedBrowser, siteInfo };
  const evidence = options.scope === 'aggregate'
    ? validateAggregateDirectory(options.aggregate, context)
    : validateEvidenceFile(options.evidence, { ...context,
      expected: options.scope === 'site' ? { kind: 'site' }
        : { kind: 'lab', lesson: options.lesson } });
  return { passed: true, sourceSha: state.head,
    integritySha256: siteInfo.integritySha256, scope: options.scope, evidence };
}

function main() {
  try {
    const result = validateAudit(parseArguments());
    console.log(`Pages audit passed: ${JSON.stringify(result)}`);
  } catch (error) {
    console.error(`Pages audit failed: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  DEFAULT_SCOPE_LIMITS,
  expectedSiteCheckIds,
  inspectSite,
  isCleanLabAttempt,
  lockedWebKitIdentity,
  parseArguments,
  repositoryState,
  runCheckPages,
  validateAggregateDirectory,
  validateAudit,
  validateEvidence,
  validateEvidenceFile,
};

if (require.main === module) main();
