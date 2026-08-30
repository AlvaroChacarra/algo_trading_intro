'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { execFileSync } = require('child_process');

const DESKTOP_VIEWPORTS = ['1280x720', '1440x900', '1920x1080', '2560x1440'];
const ALL_VIEWPORTS = [...DESKTOP_VIEWPORTS, '390x844'];
const VISUAL_SAMPLES = [
  'hero', 'recall', 'code-state', 'simulator',
  'architecture', 'mathematical', 'bridge', 'quiz',
];
const AUDIT_OWNER_FILE = '.desktop-audit-owner.json';
const AUDIT_OWNER_SCHEMA = 'desktop-audit-owner/v1';
const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const MAX_PNG_INFLATED_BYTES = 64 * 1024 * 1024;
const BROWSER_IDENTITY_SCHEMA = 'playwright-browser/v2';
const BROWSER_IDENTITY_FIELDS = [
  'schema', 'name', 'product', 'version', 'playwright', 'revision',
  'executable_locator', 'executable_sha256', 'executable_bytes',
  'payload_sha256', 'payload_bytes', 'payload_files',
];
const PLAYWRIGHT_BROWSER_PRODUCTS = Object.freeze({
  chromium: Object.freeze(['chromium', 'chromium-headless-shell']),
  webkit: Object.freeze(['webkit']),
});
const BROWSER_PAYLOAD_DIGEST_SCHEMA = 'playwright-browser-payload/v1';

function playwrightBrowserProducts(browserName) {
  return Object.prototype.hasOwnProperty.call(PLAYWRIGHT_BROWSER_PRODUCTS, browserName)
    ? PLAYWRIGHT_BROWSER_PRODUCTS[browserName] : null;
}
const VISUAL_AUDIT_INIT_SCRIPT = `(() => {
  Object.defineProperty(window, '__DESKTOP_VISUAL_AUDIT__', {
    value: 'visual-v1', configurable: false, enumerable: true, writable: false,
  });
  Object.defineProperty(Math, 'random', {
    value: () => 0.5, configurable: false, writable: false,
  });
  const nativeSetInterval = window.setInterval.bind(window);
  const nativeClearInterval = window.clearInterval.bind(window);
  window.setInterval = (_handler, _delay, ..._args) =>
    nativeSetInterval(() => {}, 2147483647);
  window.clearInterval = intervalId => nativeClearInterval(intervalId);
})();`;

const posix = value => value.split(path.sep).join('/');

function auditDirectoryIdentity(root, auditDirectory) {
  const realRoot = fs.realpathSync(root);
  const artifacts = path.join(realRoot, 'artifacts');
  const target = path.resolve(auditDirectory);
  if (path.dirname(target) !== artifacts || path.basename(target) === AUDIT_OWNER_FILE) {
    throw new Error(`unsafe --audit-dir (expected artifacts/<direct-child>): ${auditDirectory}`);
  }
  if (fs.existsSync(artifacts)) {
    const artifactsStat = fs.lstatSync(artifacts);
    if (artifactsStat.isSymbolicLink() || !artifactsStat.isDirectory()
        || fs.realpathSync(artifacts) !== artifacts) {
      throw new Error(`unsafe artifacts directory (must be a real directory): ${artifacts}`);
    }
  }
  if (fs.existsSync(target)) {
    const targetStat = fs.lstatSync(target);
    if (targetStat.isSymbolicLink() || !targetStat.isDirectory()
        || fs.realpathSync(target) !== target) {
      throw new Error(`unsafe --audit-dir (symlinks and non-directories are forbidden): ${target}`);
    }
  }
  return { realRoot, artifacts, target, relative: posix(path.relative(realRoot, target)) };
}

function auditOwner(identity) {
  return { schema: AUDIT_OWNER_SCHEMA, owner: 'framework/_build/desktop_e2e.js',
    audit_directory: identity.relative };
}

function validateAuditOwner(root, auditDirectory) {
  let identity;
  try { identity = auditDirectoryIdentity(root, auditDirectory); }
  catch (error) { return { passed: false, error: error.message }; }
  const marker = path.join(identity.target, AUDIT_OWNER_FILE);
  if (!fs.existsSync(marker)) return { passed: false, error: 'audit ownership marker missing' };
  const markerStat = fs.lstatSync(marker);
  if (markerStat.isSymbolicLink() || !markerStat.isFile()) {
    return { passed: false, error: 'audit ownership marker must be a regular file' };
  }
  let declared;
  try { declared = JSON.parse(fs.readFileSync(marker, 'utf8')); }
  catch (error) { return { passed: false, error: `invalid audit ownership marker: ${error.message}` }; }
  const expected = auditOwner(identity);
  const passed = JSON.stringify(declared) === JSON.stringify(expected);
  return { passed, error: passed ? null : 'audit ownership marker mismatch', marker, identity };
}

function prepareAuditDirectory(root, auditDirectory) {
  const identity = auditDirectoryIdentity(root, auditDirectory);
  if (!fs.existsSync(identity.artifacts)) fs.mkdirSync(identity.artifacts, { recursive: false });
  if (fs.existsSync(identity.target)) {
    const ownership = validateAuditOwner(root, identity.target);
    if (!ownership.passed) {
      throw new Error(`refusing to clear unowned audit directory: ${ownership.error}`);
    }
    fs.rmSync(identity.target, { recursive: true, force: false });
  }
  fs.mkdirSync(identity.target, { recursive: false });
  fs.writeFileSync(path.join(identity.target, AUDIT_OWNER_FILE),
    `${JSON.stringify(auditOwner(identity), null, 2)}\n`, { flag: 'wx' });
  return identity.target;
}

function discoverLessons(root) {
  const lessons = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const match = /^(\d\d)-/.exec(entry.name);
    if (!entry.isDirectory() || !match) continue;
    const number = Number(match[1]);
    if (number < 1 || number > 14) continue;
    const presentation = path.join(root, entry.name, 'presentation');
    const html = fs.existsSync(presentation)
      ? fs.readdirSync(presentation).filter(name => name.endsWith('-doc.html')) : [];
    if (html.length !== 1) {
      throw new Error(`L${number}: expected one interactive document, found ${html.length}`);
    }
    const manifest = path.join(root, 'pedagogy', 'lessons', `${String(number).padStart(2, '0')}.yml`);
    const contract = JSON.parse(fs.readFileSync(manifest, 'utf8'));
    lessons.push({
      lesson: `L${number}`, number, contract,
      manifest: posix(path.relative(root, manifest)),
      relative: posix(path.join(entry.name, 'presentation', html[0])),
    });
  }
  lessons.sort((left, right) => left.number - right.number);
  if (lessons.length !== 14 || lessons.some((item, index) => item.number !== index + 1)) {
    throw new Error(`expected L1-L14 documents, found ${lessons.map(item => item.lesson).join(', ')}`);
  }
  return lessons;
}

function effectiveStates(lesson) {
  return lesson.contract.scenes.flatMap(scene => {
    const stages = scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }];
    return stages.map(stage => ({
      lesson: lesson.lesson,
      scene: scene.id,
      stage: stage.id,
      sceneRoute: scene.route,
      route: stage.route || scene.route,
      durationMinutes: stage.duration_minutes ?? scene.duration_minutes,
      layout: scene.layout || 'focus',
      type: scene.type,
    }));
  });
}

function buildExpectedAuditPlan(root) {
  const lessons = discoverLessons(root);
  const ids = ['negative-fixture'];
  const traversalStates = {};
  for (const viewport of DESKTOP_VIEWPORTS) {
    for (const item of lessons) {
      const id = `aula:${item.lesson}:${viewport}:LIVE`;
      ids.push(id);
      traversalStates[id] = effectiveStates(item).filter(state => state.route === 'LIVE');
    }
  }
  for (const item of lessons) {
    const states = effectiveStates(item);
    const combinedId = `aula-profesor:${item.lesson}:1440x900:LIVE+REQUIRED`;
    ids.push(combinedId);
    traversalStates[combinedId] = states.filter(state => ['LIVE', 'REQUIRED'].includes(state.route));
    if (states.some(state => state.route === 'OPTIONAL')) {
      const allId = `aula-profesor:${item.lesson}:1440x900:ALL`;
      ids.push(allId);
      traversalStates[allId] = states;
    }
  }
  for (const item of lessons) ids.push(`estudio:${item.lesson}:1440x900`);
  for (const item of lessons) ids.push(`mobile-fallback:${item.lesson}:390x844`);
  for (const item of lessons) ids.push(`persistence-isolation:${item.lesson}:1440x900`);
  ids.push('fresh-professor-deep-links', 'route-overrides');
  VISUAL_SAMPLES.forEach(sample => ids.push(`visual-sample:${sample}`));
  ids.push('index:course-map:1440x900');
  ALL_VIEWPORTS.forEach(viewport => ids.push(`assessment-linear:L15:${viewport}`));
  ids.push('input-integrity');
  const traversedStates = lessons.reduce((total, item) => {
    const states = effectiveStates(item);
    const live = states.filter(state => state.route === 'LIVE').length;
    const required = states.filter(state => state.route === 'REQUIRED').length;
    const all = states.length;
    return total + live * DESKTOP_VIEWPORTS.length + live + required
      + (states.some(state => state.route === 'OPTIONAL') ? all : 0);
  }, 0);
  const overrideTargets = lessons.flatMap(item => effectiveStates(item)
    .filter(state => state.route !== state.sceneRoute));
  const overrideIds = overrideTargets
    .map(state => `${state.lesson}:${state.scene}/${state.stage}`);
  const deepLinkTargets = ['REQUIRED', 'OPTIONAL'].map(route => {
    const target = lessons.flatMap(effectiveStates).find(state => state.route === route);
    if (!target) throw new Error(`no ${route} deep-link target exists`);
    return { ...target, route };
  });
  const deepLinkIds = deepLinkTargets.map(target =>
    `${target.route}:${target.lesson}:${target.scene}/${target.stage}`);
  return { ids, lessons, traversedStates, traversalStates,
    overrideIds, overrideTargets, deepLinkIds, deepLinkTargets };
}

function visualSampleTargets(lessons) {
  const scenes = lessons.flatMap(item => item.contract.scenes.map(scene => ({ item, scene })));
  const choose = (name, predicate, preferred) => {
    const candidates = scenes.filter(predicate);
    const selected = candidates.find(candidate => candidate.item.number === preferred) || candidates[0];
    if (!selected) throw new Error(`no declared scene matches visual sample ${name}`);
    const stages = selected.scene.stages?.length
      ? selected.scene.stages : [{ id: 'stage', route: selected.scene.route }];
    const stage = stages[0];
    return { name, lesson: selected.item.lesson, relative: selected.item.relative,
      scene: selected.scene.id, stage: stage.id, sceneRoute: selected.scene.route,
      route: stage.route || selected.scene.route,
      durationMinutes: stage.duration_minutes ?? selected.scene.duration_minutes };
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

function recordId(record) {
  switch (record?.mode) {
    case 'negative-fixture': return 'negative-fixture';
    case 'aula': return `aula:${record.lesson}:${record.viewport}:${record.scope}`;
    case 'aula-profesor': return `aula-profesor:${record.lesson}:${record.viewport}:${record.scope}`;
    case 'estudio': return `estudio:${record.lesson}:${record.viewport}`;
    case 'mobile-fallback': return `mobile-fallback:${record.lesson}:${record.viewport}`;
    case 'persistence-isolation': return `persistence-isolation:${record.lesson}:${record.viewport}`;
    case 'fresh-professor-deep-links': return 'fresh-professor-deep-links';
    case 'route-overrides': return 'route-overrides';
    case 'visual-sample': return `visual-sample:${record.sample}`;
    case 'index': return `index:${record.lesson}:${record.viewport}`;
    case 'assessment-linear': return `assessment-linear:${record.lesson}:${record.viewport}`;
    case 'input-integrity': return 'input-integrity';
    default: return null;
  }
}

function attachRecordIds(results) {
  return results.map(record => ({ ...record, check_id: recordId(record) }));
}

function validateRecordSet(results, plan) {
  const declared = results.map(record => record.check_id);
  const observed = results.map(record => recordId(record));
  const counts = new Map();
  observed.forEach(id => counts.set(id, (counts.get(id) || 0) + 1));
  const expected = new Set(plan.ids);
  const missing = plan.ids.filter(id => !counts.has(id));
  const unexpected = observed.filter(id => !expected.has(id));
  const duplicates = [...counts].filter(([, count]) => count > 1)
    .map(([id, count]) => ({ id, count }));
  const invalid = observed.filter(id => typeof id !== 'string' || !id);
  const idMismatches = results.flatMap((record, index) => {
    const computed = observed[index];
    return declared[index] === computed ? [] : [{ index, declared: declared[index], computed }];
  });
  return {
    expected: plan.ids.length,
    observed: observed.length,
    missing, unexpected, duplicates, invalid, idMismatches,
    passed: missing.length === 0 && unexpected.length === 0
      && duplicates.length === 0 && invalid.length === 0 && idMismatches.length === 0
      && observed.length === plan.ids.length,
  };
}

function exactUnique(values, expected) {
  const left = [...values].sort();
  const right = [...expected].sort();
  return left.length === new Set(left).size && JSON.stringify(left) === JSON.stringify(right);
}

function validateCoverage(results, plan) {
  const recordsById = new Map(results.map(record => [recordId(record), record]));
  const traversalChecks = Object.entries(plan.traversalStates).map(([id, expectedStates]) => {
    const record = recordsById.get(id);
    const states = Array.isArray(record?.states) ? record.states : [];
    const expectedIdentities = expectedStates.map(state =>
      `${state.lesson}:${state.scene}/${state.stage}:${state.sceneRoute}->${state.route}`);
    const observedIdentities = states.map(state =>
      `${record?.lesson}:${state.scene}/${state.stage}:${state.sceneRoute}->${state.stageRoute}`);
    const exactSequence = JSON.stringify(observedIdentities) === JSON.stringify(expectedIdentities);
    const unique = observedIdentities.length === new Set(observedIdentities).size;
    const errorsEmpty = Array.isArray(record?.errors) && record.errors.length === 0;
    const passedStates = states.every(state => state.passed === true);
    const valid = Boolean(record) && record.passed === true && errorsEmpty && passedStates
      && exactSequence && unique && record.expected === expectedStates.length
      && record.visited === expectedStates.length && states.length === expectedStates.length;
    return { id, expected: expectedStates.length, observed: states.length,
      exactSequence, unique, errorsEmpty, passedStates, passed: valid };
  });
  const traversedStates = traversalChecks.reduce((total, item) => total + item.observed, 0);
  const traversalCountsValid = traversalChecks.length === Object.keys(plan.traversalStates).length
    && traversalChecks.every(item => item.passed);
  const overrideRecord = results.find(record => record.mode === 'route-overrides');
  const overrideRecords = Array.isArray(overrideRecord?.records) ? overrideRecord.records : [];
  const observedOverrides = overrideRecords
    .map(item => `${item.lesson}:${item.scene}/${item.stage}`);
  const overridesValid = Boolean(overrideRecord)
    && overrideRecord.expected === plan.overrideIds.length
    && overrideRecord.declared === plan.overrideIds.length
    && overrideRecord.visible === plan.overrideIds.length
    && exactUnique(observedOverrides, plan.overrideIds)
    && overrideRecords.every(item => item.passed === true
      && Array.isArray(item.errors) && item.errors.length === 0
      && item.sceneRoute !== item.effectiveRoute);
  const deepLinkRecord = results.find(record => record.mode === 'fresh-professor-deep-links');
  const deepLinkRecords = Array.isArray(deepLinkRecord?.records) ? deepLinkRecord.records : [];
  const observedDeepLinks = deepLinkRecords.map(item =>
    `${item.route}:${item.lesson}:${item.target?.scene}/${item.target?.stage}`);
  const deepLinksValid = Boolean(deepLinkRecord)
    && exactUnique(observedDeepLinks, plan.deepLinkIds)
    && deepLinkRecords.every(item => item.passed === true && item.freshContext === true
      && Array.isArray(item.errors) && item.errors.length === 0);
  return {
    documents: [...plan.lessons.map(item => item.lesson), 'L15'],
    runtime_lessons: plan.lessons.map(item => item.lesson),
    assessment: ['L15'],
    viewports: ALL_VIEWPORTS,
    expected_records: plan.ids.length,
    traversed_states: traversedStates,
    expected_traversed_states: plan.traversedStates,
    override_ids: observedOverrides,
    expected_override_ids: plan.overrideIds,
    deep_link_ids: observedDeepLinks,
    expected_deep_link_ids: plan.deepLinkIds,
    traversal_checks: traversalChecks,
    passed: traversalCountsValid && traversedStates === plan.traversedStates
      && overridesValid && deepLinksValid,
  };
}

function updateDigestFromFile(digest, filename) {
  const descriptor = fs.openSync(filename, 'r');
  const block = Buffer.allocUnsafe(1024 * 1024);
  try {
    for (;;) {
      const bytes = fs.readSync(descriptor, block, 0, block.length, null);
      if (!bytes) break;
      digest.update(block.subarray(0, bytes));
    }
  } finally {
    fs.closeSync(descriptor);
  }
}

function sha256(filename) {
  const digest = crypto.createHash('sha256');
  updateDigestFromFile(digest, filename);
  return digest.digest('hex');
}

function updateDigestField(digest, value) {
  const encoded = Buffer.from(String(value), 'utf8');
  const length = Buffer.allocUnsafe(4);
  length.writeUInt32BE(encoded.length);
  digest.update(length);
  digest.update(encoded);
}

function pathIsInside(root, target) {
  const relative = path.relative(root, target);
  return relative === '' || (!path.isAbsolute(relative) && relative !== '..'
    && !relative.startsWith(`..${path.sep}`));
}

function browserPayloadEvidence(registryDirectory) {
  const requestedRoot = path.resolve(registryDirectory);
  const rootStat = fs.lstatSync(requestedRoot);
  if (rootStat.isSymbolicLink() || !rootStat.isDirectory()) {
    throw new Error(`browser registry payload must be a real directory: ${requestedRoot}`);
  }
  const realRoot = fs.realpathSync.native(requestedRoot);
  if (realRoot !== requestedRoot) {
    throw new Error(`browser registry payload contains a symlinked root: ${requestedRoot}`);
  }
  const digest = crypto.createHash('sha256');
  updateDigestField(digest, BROWSER_PAYLOAD_DIGEST_SCHEMA);
  let payloadBytes = 0;
  let payloadFiles = 0;

  const visit = directory => {
    const names = fs.readdirSync(directory).sort();
    for (const name of names) {
      const candidate = path.join(directory, name);
      const relative = posix(path.relative(realRoot, candidate));
      const candidateStat = fs.lstatSync(candidate);
      const mode = candidateStat.mode & 0o7777;
      if (candidateStat.isDirectory()) {
        updateDigestField(digest, 'directory');
        updateDigestField(digest, relative);
        updateDigestField(digest, mode);
        visit(candidate);
      } else if (candidateStat.isSymbolicLink()) {
        const target = fs.readlinkSync(candidate);
        let resolved;
        try { resolved = fs.realpathSync.native(candidate); }
        catch (error) {
          throw new Error(`browser payload contains a broken symlink ${relative}: ${error.message}`);
        }
        if (!pathIsInside(realRoot, resolved)) {
          throw new Error(`browser payload symlink escapes its registry directory: ${relative}`);
        }
        updateDigestField(digest, 'symlink');
        updateDigestField(digest, relative);
        updateDigestField(digest, mode);
        updateDigestField(digest, target);
      } else if (candidateStat.isFile()) {
        if (!Number.isSafeInteger(candidateStat.size) || candidateStat.size < 0
            || !Number.isSafeInteger(payloadBytes + candidateStat.size)) {
          throw new Error(`browser payload size is unsafe: ${relative}`);
        }
        updateDigestField(digest, 'file');
        updateDigestField(digest, relative);
        updateDigestField(digest, mode);
        updateDigestField(digest, candidateStat.size);
        updateDigestFromFile(digest, candidate);
        payloadBytes += candidateStat.size;
        payloadFiles += 1;
      } else {
        throw new Error(`browser payload contains a special file: ${relative}`);
      }
    }
  };
  visit(realRoot);
  if (!payloadFiles || !payloadBytes) {
    throw new Error(`browser registry payload is empty: ${realRoot}`);
  }
  return {
    payload_sha256: digest.digest('hex'),
    payload_bytes: payloadBytes,
    payload_files: payloadFiles,
  };
}

let crcTable = null;
function crc32(buffer) {
  if (!crcTable) {
    crcTable = Array.from({ length: 256 }, (_, value) => {
      let current = value;
      for (let bit = 0; bit < 8; bit++) {
        current = (current & 1) ? (0xedb88320 ^ (current >>> 1)) : (current >>> 1);
      }
      return current >>> 0;
    });
  }
  let crc = 0xffffffff;
  for (const byte of buffer) crc = crcTable[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function parsePngBuffer(buffer) {
  if (!Buffer.isBuffer(buffer) || buffer.length < PNG_SIGNATURE.length
      || !buffer.subarray(0, PNG_SIGNATURE.length).equals(PNG_SIGNATURE)) {
    throw new Error('invalid PNG signature');
  }
  let offset = PNG_SIGNATURE.length;
  const chunks = [];
  while (offset < buffer.length) {
    if (offset + 12 > buffer.length) throw new Error('truncated PNG chunk');
    const length = buffer.readUInt32BE(offset);
    const end = offset + 12 + length;
    if (end > buffer.length) throw new Error('truncated PNG chunk data');
    const typeBuffer = buffer.subarray(offset + 4, offset + 8);
    const type = typeBuffer.toString('ascii');
    if (!/^[A-Za-z]{4}$/.test(type)) throw new Error('invalid PNG chunk type');
    const data = buffer.subarray(offset + 8, offset + 8 + length);
    const declaredCrc = buffer.readUInt32BE(offset + 8 + length);
    const actualCrc = crc32(Buffer.concat([typeBuffer, data]));
    if (declaredCrc !== actualCrc) throw new Error(`invalid PNG CRC for ${type}`);
    chunks.push({ type, length, data });
    offset = end;
    if (type === 'IEND') break;
  }
  if (offset !== buffer.length) throw new Error('PNG contains trailing data after IEND');
  if (chunks[0]?.type !== 'IHDR' || chunks[0].length !== 13) throw new Error('invalid PNG IHDR');
  const ihdr = chunks[0].data;
  const width = ihdr.readUInt32BE(0);
  const height = ihdr.readUInt32BE(4);
  const bitDepth = ihdr[8];
  const colorType = ihdr[9];
  const validDepths = { 0: [1, 2, 4, 8, 16], 2: [8, 16], 3: [1, 2, 4, 8],
    4: [8, 16], 6: [8, 16] };
  if (!width || !height || !validDepths[colorType]?.includes(bitDepth)
      || ihdr[10] !== 0 || ihdr[11] !== 0 || ihdr[12] !== 0
      || chunks.filter(chunk => chunk.type === 'IHDR').length !== 1) {
    throw new Error('invalid PNG dimensions, colour model, or encoding');
  }
  const idat = chunks.filter(chunk => chunk.type === 'IDAT');
  if (!idat.length || idat.some(chunk => chunk.length === 0)) throw new Error('PNG IDAT missing or empty');
  if (chunks.at(-1)?.type !== 'IEND' || chunks.at(-1).length !== 0
      || chunks.filter(chunk => chunk.type === 'IEND').length !== 1) throw new Error('invalid PNG IEND');
  const channels = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[colorType];
  const rowBits = BigInt(width) * BigInt(channels) * BigInt(bitDepth);
  const rowBytesBig = (rowBits + 7n) / 8n;
  const expectedBytesBig = (rowBytesBig + 1n) * BigInt(height);
  if (expectedBytesBig > BigInt(MAX_PNG_INFLATED_BYTES)) {
    throw new Error(`PNG inflated pixel stream exceeds ${MAX_PNG_INFLATED_BYTES} byte safety limit`);
  }
  const rowBytes = Number(rowBytesBig);
  const expectedBytes = Number(expectedBytesBig);
  let pixels;
  try {
    pixels = zlib.inflateSync(Buffer.concat(idat.map(chunk => chunk.data)), {
      maxOutputLength: expectedBytes,
    });
  } catch (error) {
    throw new Error(`invalid PNG IDAT stream: ${error.message}`);
  }
  if (pixels.length !== expectedBytes) {
    throw new Error(`PNG pixel stream has ${pixels.length} bytes; expected ${expectedBytes}`);
  }
  for (let row = 0; row < height; row++) {
    if (pixels[row * (rowBytes + 1)] > 4) throw new Error('invalid PNG row filter');
  }
  return { width, height, bitDepth, colorType, chunks: chunks.map(chunk => chunk.type) };
}

function pngEvidence(filename) {
  const buffer = fs.readFileSync(filename);
  const parsed = parsePngBuffer(buffer);
  return { name: path.basename(filename), bytes: buffer.length,
    sha256: crypto.createHash('sha256').update(buffer).digest('hex'),
    width: parsed.width, height: parsed.height };
}

function screenshotEvidence(auditDirectory, names) {
  return [...names].sort().map(name => pngEvidence(path.join(auditDirectory, name)));
}

function browserRegistryDirectory(product, revision) {
  return `${product.replace(/-/g, '_')}-${revision}`;
}

function browserExecutableLocator(executablePath, entries, browserName) {
  const realExecutable = fs.realpathSync.native(executablePath);
  const stat = fs.statSync(realExecutable);
  if (!stat.isFile() || stat.size <= 0) {
    throw new Error(`browser executable must be a non-empty regular file: ${realExecutable}`);
  }
  const parts = path.normalize(realExecutable).split(path.sep).filter(Boolean);
  const matches = entries.flatMap(entry => {
    const directory = browserRegistryDirectory(entry.name, entry.revision);
    const index = parts.findIndex(part => process.platform === 'win32'
      ? part.toLowerCase() === directory.toLowerCase() : part === directory);
    if (index < 0 || index === parts.length - 1) return [];
    return [{ entry, index, suffix: parts.slice(index + 1).join('/') }];
  });
  if (matches.length !== 1) {
    const label = browserName === 'chromium' ? 'Chromium' : 'WebKit';
    throw new Error(`browser executable is not inside one locked ${label} product: ${realExecutable}`);
  }
  const match = matches[0];
  let registryDirectory = realExecutable;
  for (let index = match.index; index < parts.length - 1; index++) {
    registryDirectory = path.dirname(registryDirectory);
  }
  return {
    realExecutable,
    stat,
    entry: match.entry,
    registryDirectory,
    locator: `${match.entry.name}@${match.entry.revision}/${match.suffix}`,
  };
}

function lockedPlaywrightBrowserIdentity(root, browserName, executablePath) {
  const products = playwrightBrowserProducts(browserName);
  if (!products) {
    throw new Error(`unsupported Playwright browser identity: ${browserName}`);
  }
  let selectedExecutable = executablePath;
  if (selectedExecutable === undefined) {
    const playwrightModule = require.resolve('playwright', { paths: [root] });
    selectedExecutable = require(playwrightModule)[browserName].executablePath();
  }
  if (typeof selectedExecutable !== 'string' || !path.isAbsolute(selectedExecutable)) {
    throw new Error('lockedPlaywrightBrowserIdentity requires an absolute executable path');
  }
  const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
  const playwright = lock.packages?.['node_modules/playwright']?.version || null;
  const browsers = JSON.parse(fs.readFileSync(
    path.join(root, 'node_modules/playwright-core/browsers.json'), 'utf8'));
  const baseEntries = (browsers.browsers || [])
    .filter(item => products.includes(item.name));
  const registeredProducts = baseEntries.map(item => item.name).sort();
  if (typeof playwright !== 'string' || !playwright
      || JSON.stringify(registeredProducts) !== JSON.stringify([...products].sort())
      || baseEntries.some(item => !item.revision || !item.browserVersion)) {
    throw new Error(`Playwright lock and ${browserName} browser registry are incomplete`);
  }
  const entries = baseEntries.flatMap(entry => {
    const revisions = [...new Set([
      String(entry.revision || ''),
      ...Object.values(entry.revisionOverrides || {}).map(value => String(value || '')),
    ].filter(Boolean))];
    return revisions.map(revision => ({ ...entry, revision }));
  });
  const located = browserExecutableLocator(selectedExecutable, entries, browserName);
  const payload = browserPayloadEvidence(located.registryDirectory);
  return {
    schema: BROWSER_IDENTITY_SCHEMA,
    name: browserName,
    product: located.entry.name,
    version: located.entry.browserVersion,
    playwright,
    revision: located.entry.revision,
    executable_locator: located.locator,
    executable_sha256: sha256(located.realExecutable),
    executable_bytes: located.stat.size,
    ...payload,
  };
}

function lockedBrowserIdentity(root, executablePath) {
  return lockedPlaywrightBrowserIdentity(root, 'chromium', executablePath);
}

function exactBrowserIdentity(identity) {
  if (!identity || typeof identity !== 'object' || Array.isArray(identity)
      || JSON.stringify(Object.keys(identity).sort())
        !== JSON.stringify([...BROWSER_IDENTITY_FIELDS].sort())) return false;
  const products = playwrightBrowserProducts(identity.name);
  return identity.schema === BROWSER_IDENTITY_SCHEMA
    && Boolean(products) && products.includes(identity.product)
    && typeof identity.version === 'string' && identity.version.length > 0
    && typeof identity.playwright === 'string' && identity.playwright.length > 0
    && typeof identity.revision === 'string' && identity.revision.length > 0
    && typeof identity.executable_locator === 'string'
    && identity.executable_locator.startsWith(`${identity.product}@${identity.revision}/`)
    && typeof identity.executable_sha256 === 'string'
    && /^[0-9a-f]{64}$/.test(identity.executable_sha256)
    && Number.isSafeInteger(identity.executable_bytes) && identity.executable_bytes > 0
    && typeof identity.payload_sha256 === 'string'
    && /^[0-9a-f]{64}$/.test(identity.payload_sha256)
    && Number.isSafeInteger(identity.payload_bytes) && identity.payload_bytes > 0
    && Number.isSafeInteger(identity.payload_files) && identity.payload_files > 0;
}

function validateBrowserIdentity(declared, locked, observed = null) {
  const exactMatch = (left, right) => exactBrowserIdentity(left) && exactBrowserIdentity(right)
    && BROWSER_IDENTITY_FIELDS.every(field => left[field] === right[field]);
  const staticMatch = exactMatch(declared, locked);
  const observedMatch = observed === null || exactMatch(observed, declared);
  return { locked, declared, observed, staticMatch, observedMatch,
    passed: staticMatch && observedMatch };
}

function expectedInputPaths(root) {
  const lessons = discoverLessons(root);
  return [
    'framework/_build/desktop_e2e.js',
    'framework/_build/doc_assets/learning_runtime.js',
    ...lessons.map(item => item.manifest),
    ...lessons.map(item => item.relative),
    'index.html',
    '15-final-exam/examen.html',
  ];
}

function inputEvidence(root) {
  return {
    files: expectedInputPaths(root).map(relative => ({
      path: relative,
      sha256: sha256(path.join(root, relative)),
    })),
  };
}

function validateInputEvidence(evidence, root) {
  let current;
  try { current = inputEvidence(root); }
  catch (error) { return { passed: false, error: error.message }; }
  const files = Array.isArray(evidence?.files) ? evidence.files : [];
  const paths = files.map(item => item.path);
  const expectedPaths = current.files.map(item => item.path);
  const unique = paths.length === new Set(paths).size;
  const exactPaths = unique && JSON.stringify([...paths].sort()) === JSON.stringify([...expectedPaths].sort());
  const declared = new Map(files.map(item => [item.path, item.sha256]));
  const hashesMatch = current.files.every(item => declared.get(item.path) === item.sha256);
  return { expected: expectedPaths.length, observed: files.length, exactPaths, hashesMatch,
    passed: exactPaths && hashesMatch && files.length === expectedPaths.length };
}

function sameInputEvidence(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

const isTrue = value => value === true;
const isFalse = value => value === false;
const emptyArray = value => Array.isArray(value) && value.length === 0;
const allTrue = (value, fields) => Boolean(value) && fields.every(field => value[field] === true);
const finiteNumber = value => typeof value === 'number' && Number.isFinite(value);

function positiveBox(box) {
  return Boolean(box) && ['left', 'top', 'right', 'bottom', 'width', 'height']
    .every(field => finiteNumber(box[field]))
    && box.width > 0.5 && box.height > 0.5
    && box.right >= box.left && box.bottom >= box.top;
}

function visibilityEvidencePassed(visibility) {
  return allTrue(visibility, ['rendered', 'positiveArea', 'unoccluded'])
    && finiteNumber(visibility.effectiveOpacity)
    && visibility.effectiveOpacity > 0.01 && visibility.effectiveOpacity <= 1.000001;
}

function scrollReachabilityEvidencePassed(item) {
  const documentEvidence = item?.documentScroller === true;
  const documentFieldsValid = documentEvidence
    ? item.selector === 'document.scrollingElement' && item.targetReachable === true
      && item.declaredAxis === 'vertical' && item.overflowX === false && item.overflowY === true
      && item.clipsTargetX === false && item.clipsTargetY === true
      && finiteNumber(item.targetScrollTop) && finiteNumber(item.maximumScrollTop)
      && item.targetScrollTop >= 0 && item.maximumScrollTop > 0
      && item.targetScrollTop <= item.maximumScrollTop
    : item?.selector !== 'document.scrollingElement'
      && (item?.documentScroller === undefined || item?.documentScroller === false)
      && item?.targetReachable === undefined;
  return Boolean(item) && documentFieldsValid
    && typeof item.selector === 'string' && item.selector.length > 0
    && item.declared === true && ['horizontal', 'vertical', 'both'].includes(item.declaredAxis)
    && allTrue(item, ['real', 'focusable', 'axisMatches', 'reachedEnd'])
    && typeof item.overflowX === 'boolean' && typeof item.overflowY === 'boolean'
    && typeof item.clipsTargetX === 'boolean' && typeof item.clipsTargetY === 'boolean'
    && (item.overflowX || item.overflowY);
}

function stageOverflowEvidencePassed(state) {
  return typeof state?.stageOverflow === 'boolean' && state.stageOverflowAccessible === true
    && Array.isArray(state.stageOverflowChecks)
    && state.stageOverflowChecks.every(item => ['step', 'figure'].includes(item.kind)
      && ['scrollWidth', 'clientWidth', 'scrollHeight', 'clientHeight']
        .every(field => finiteNumber(item[field]) && item[field] >= 0)
      && typeof item.overflowX === 'boolean' && typeof item.overflowY === 'boolean'
      && item.overflowX === (item.scrollWidth > item.clientWidth + 2)
      && item.overflowY === (item.scrollHeight > item.clientHeight + 2)
      && item.overflow === (item.overflowX || item.overflowY) && item.accessible === true
      && Array.isArray(item.scrollReachability)
      && (!item.overflowX || item.scrollReachability.some(evidence =>
        scrollReachabilityEvidencePassed(evidence) && evidence.overflowX))
      && (!item.overflowY || item.scrollReachability.some(evidence =>
        scrollReachabilityEvidencePassed(evidence) && evidence.overflowY)))
    && state.stageOverflow === state.stageOverflowChecks.some(item => item.overflow);
}

function essentialEvidencePassed(state) {
  const checks = Array.isArray(state?.essentialChecks) ? state.essentialChecks : [];
  const rawInside = typeof state?.essentialInsideViewport === 'boolean'
    ? state.essentialInsideViewport : state?.essentialInside;
  return Number.isInteger(state?.essentialCount) && state.essentialCount > 0
    && checks.length === state.essentialCount
    && typeof rawInside === 'boolean' && state.essentialAccessible === true
    && emptyArray(state.unresolvedEssentialSelectors) && emptyArray(state.essentialFailures)
    && checks.every(item => typeof item.selector === 'string' && item.selector.length > 0
      && typeof item.label === 'string' && item.label.length > 0
      && positiveBox(item.box) && item.effectiveVisible === true
      && item.positiveArea === true && finiteNumber(item.effectiveOpacity)
      && item.effectiveOpacity > 0.01 && item.effectiveOpacity <= 1.000001
      && typeof item.unoccluded === 'boolean' && item.accessible === true
      && typeof item.scrollReachable === 'boolean'
      && Array.isArray(item.scrollReachability) && Array.isArray(item.diagnosticFailures)
      && emptyArray(item.failures)
      && (item.unoccluded === true || item.scrollReachable === true)
      && (!item.scrollReachable || item.scrollReachability.some(evidence =>
        scrollReachabilityEvidencePassed(evidence)
          && (evidence.clipsTargetX || evidence.clipsTargetY))));
}

function runtimeStateMatches(state, expected) {
  const runtime = state?.runtimeState;
  return Boolean(runtime) && runtime.scene === expected.scene && runtime.stage === expected.stage
    && runtime.route === expected.route && runtime.sceneRoute === expected.sceneRoute
    && runtime.routeScope === state.scope;
}

function hasNoRecordedErrors(value) {
  if (!value || typeof value !== 'object') return true;
  if (Array.isArray(value)) return value.every(hasNoRecordedErrors);
  return Object.entries(value).every(([key, item]) =>
    (key === 'errors' ? Array.isArray(item) && item.length === 0 : hasNoRecordedErrors(item)));
}

function desktopStatePassed(state) {
  const expected = state?.expected;
  const expectedMobileText = expected
    ? `Ruta · ${expected.stageRoute} · ${expected.durationMinutes} min · Estudio · ${expected.scene}`
    : null;
  const expectedLiveText = expected
    ? `${expected.scene}, ruta ${expected.stageRoute}, ${expected.durationMinutes} minutos, `
      + `etapa ${expected.stagePosition} de ${expected.stageTotal}`
    : null;
  const expectedTeacherKicker = expected
    ? `${expected.stageRoute} · ${expected.type} · ${expected.durationMinutes} min` : null;
  const rawPresentation = Boolean(expected && state.routePresentation && state.liveRegion)
    && state.routePresentation.badgeRoute === expected.stageRoute
    && state.routePresentation.badgeDuration === `${expected.durationMinutes} min`
    && state.routePresentation.navRoute === expected.stageRoute
    && (state.routePresentation.teacherRoute === null
      || state.routePresentation.teacherRoute === expected.stageRoute)
    && (state.routePresentation.teacherKicker === null
      || state.routePresentation.teacherKicker === expectedTeacherKicker)
    && state.routePresentation.mobileText === expectedMobileText
    && state.routePresentation.expectedMobileText === expectedMobileText
    && state.routePresentation.mobileRouteVisible === true
    && state.routePresentation.mobileDurationVisible === true
    && state.liveRegion.text === expectedLiveText
    && state.liveRegion.expected === expectedLiveText;
  const rawControls = Number.isInteger(state?.position) && Number.isInteger(state?.total)
    && state.position >= 1 && state.position <= state.total
    && state.controlEvidence?.previousDisabled === (state.position === 1)
    && state.controlEvidence?.nextDisabled === (state.position === state.total);
  return state?.evidenceSchema === 'desktop-state/v3'
    && Number.isInteger(state.viewport?.width) && state.viewport.width > 0
    && Number.isInteger(state.viewport?.height) && state.viewport.height > 0
    && state.activeSceneCount === 1 && visibilityEvidencePassed(state.activeVisibility)
    && positiveBox(state.sceneBox) && positiveBox(state.controlsBox) && positiveBox(state.navBox)
    && essentialEvidencePassed(state) && stageOverflowEvidencePassed(state)
    && runtimeStateMatches(state, { scene: expected?.scene, stage: expected?.stage,
      route: expected?.stageRoute, sceneRoute: expected?.sceneRoute })
    && state.layout === expected?.layout && state.type === expected?.type
    && state.layoutApplied === true && rawControls && rawPresentation
    && allTrue(state, ['stateMatches', 'controlState', 'oneSceneActive', 'sceneInsideViewport',
    'controlsInsideViewport', 'navInsideViewport', 'essentialAccessible',
    'stageOverflowAccessible', 'layoutMatches',
    'routeProgressMatches', 'savedProgressMatches', 'scrollAuditPassed',
    'routePresentationMatches', 'liveRegionMatches', 'getStateConsistent'])
    && isFalse(state.bodyOverflow) && isFalse(state.horizontalOverflow)
    && state.bodyScrollPosition?.x === 0 && state.bodyScrollPosition?.y === 0
    && emptyArray(state.undeclaredScrollers) && emptyArray(state.hiddenFocusable)
    && Array.isArray(state.scrollerChecks) && state.scrollerChecks.every(item =>
      allTrue(item, ['real', 'focusable', 'axisMatches', 'reachedEnd']));
}

function drawerPassed(drawer) {
  const expectedKeys = ['ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp', 'Space'];
  return allTrue(drawer, ['present', 'opened', 'backgroundInert', 'outsideFocusBlocked',
    'reverseLoop', 'forwardLoop', 'modalKeysBlocked', 'closed', 'noExposedFocusable',
    'focusRestored', 'backgroundRestored'])
    && Number.isInteger(drawer.focusableCount) && drawer.focusableCount > 0
    && drawer.backgroundClickBlocked?.clicks === 0
    && allTrue(drawer.backgroundClickBlocked, ['stateUnchanged', 'focusInside'])
    && drawer.nativeScroll?.scrollable === true && drawer.nativeScroll?.offset > 0
    && Array.isArray(drawer.modalNavigation)
    && JSON.stringify(drawer.modalNavigation.map(item => item.key)) === JSON.stringify(expectedKeys)
    && drawer.modalNavigation.every(item => item.unchanged === true && item.focusInside === true);
}

function coordinationPassed(coordination) {
  return coordination?.applicable === true
    && allTrue(coordination.afterHandoff,
      ['teacherClosed', 'guideOpen', 'exactlyOneOpen', 'focusInsideGuide', 'modalClass'])
    && allTrue(coordination.idempotentClose, ['focusUnchanged', 'guideStillOpen'])
    && coordination.closed === true
    && allTrue(coordination.reverseHandoff,
      ['guideClosed', 'teacherOpen', 'exactlyOneOpen', 'focusInsideTeacher', 'modalClass'])
    && coordination.reverseClosed === true;
}

function navigationPassed(navigation, professor) {
  const persistence = navigation?.persistence;
  const targetPath = persistence?.target
    ? `${persistence.target.scene}/${persistence.target.stage}` : null;
  const expectedHash = targetPath ? `#${targetPath.split('/').map(encodeURIComponent).join('/')}` : null;
  const rawPersistence = Boolean(targetPath)
    && navigation.hashTargetMatches === true && navigation.storageTargetMatches === true
    && navigation.storageClearedForHashRestore === true
    && persistence.hash === expectedHash && persistence.hashTarget === targetPath
    && persistence.storageTarget?.scene === persistence.target.scene
    && persistence.storageTarget?.stage === persistence.target.stage
    && persistence.storageVersion === 2 && persistence.progressValid === true
    && persistence.restored?.scene === persistence.target.scene
    && persistence.restored?.stage === persistence.target.stage;
  const basic = allTrue(navigation, ['backward', 'forward', 'tabOrderPassed', 'focusVisible',
    'reloadPersistence', 'hashWritten', 'progress', 'courseHome'])
    && Number.isInteger(navigation?.tabOrder?.count) && navigation.tabOrder.count > 0
    && navigation.tabOrder.wrapped === true && emptyArray(navigation.tabOrder.hiddenFocus)
    && rawPersistence;
  if (!professor) return basic;
  return basic && navigation.drawersPassed === true
    && drawerPassed(navigation.drawers?.teacher) && drawerPassed(navigation.drawers?.guide)
    && coordinationPassed(navigation.drawers?.coordination);
}

function traversalRecordPassed(record, expectedStates) {
  const states = Array.isArray(record?.states) ? record.states : [];
  if (states.length !== expectedStates.length || record.expected !== expectedStates.length
      || record.visited !== expectedStates.length || !hasNoRecordedErrors(record)) return false;
  return states.every((state, index) => {
    const expected = expectedStates[index];
    return state.scene === expected.scene && state.stage === expected.stage
      && state.sceneRoute === expected.sceneRoute && state.stageRoute === expected.route
      && state.expected?.scene === expected.scene && state.expected?.stage === expected.stage
      && state.expected?.sceneRoute === expected.sceneRoute
      && state.expected?.stageRoute === expected.route
      && state.expected?.durationMinutes === expected.durationMinutes
      && state.expected?.layout === expected.layout && state.expected?.type === expected.type
      && state.layout === expected.layout && state.type === expected.type
      && state.position === index + 1 && state.total === expectedStates.length
      && desktopStatePassed(state);
  });
}

function visibleStudyStatePassed(state, scope, optionalAvailable) {
  return state?.officialAvailable === true && state.optionalAvailable === optionalAvailable
    && state.routeScope === scope && state.vertical === true && state.horizontalOverflow === false
    && state.progressReady === true && state.progressTotalsMatch === true
    && state.getStateConsistent === true && Number.isInteger(state.optionalCount)
    && state.optionalCount >= 0 && Boolean(state.runtimeState);
}

function expectedFlowStates(lesson, scopeRoutes, targetRoutes = scopeRoutes) {
  return lesson.contract.scenes.flatMap(scene => {
    const stages = (scene.stages?.length ? scene.stages : [{ id: 'stage', route: scene.route }])
      .map(stage => ({ ...stage, route: stage.route || scene.route }))
      .filter(stage => scopeRoutes.includes(stage.route));
    return stages.map((stage, index) => ({ lesson: lesson.lesson, scene: scene.id, stage: stage.id,
      sceneRoute: scene.route, route: stage.route,
      durationMinutes: stage.duration_minutes ?? scene.duration_minutes,
      stagePosition: index + 1, stageTotal: stages.length }))
      .filter(state => targetRoutes.includes(state.route));
  });
}

function flowStatePassed(state, expected, index, total) {
  const expectedLive = `${expected.scene}, ruta ${expected.route}, ${expected.durationMinutes} minutos, `
    + `etapa ${expected.stagePosition} de ${expected.stageTotal}`;
  const saved = state?.savedRuntimeState;
  const rawPersistence = Boolean(saved?.progress && state?.runtimeState?.progress)
    && saved.scene === expected.scene && saved.stage === expected.stage
    && saved.routeScope === state.scope
    && ['LIVE', 'REQUIRED', 'OPTIONAL'].every(route => {
      const current = state.runtimeState.progress[route];
      const stored = saved.progress[route];
      return current && stored && current.total === stored.total
        && current.visited === stored.visited && current.percent === stored.percent
        && current.complete === stored.complete;
    });
  return state?.evidenceSchema === 'desktop-flow-state/v3'
    && Number.isInteger(state.viewport?.width) && state.viewport.width > 0
    && Number.isInteger(state.viewport?.height) && state.viewport.height > 0
    && state.activeSceneCount === 1 && visibilityEvidencePassed(state.sceneVisibility)
    && positiveBox(state.sceneBox) && essentialEvidencePassed(state)
    && stageOverflowEvidencePassed(state) && rawPersistence
    && state.scene === expected.scene && state.stage === expected.stage
    && state.sceneRoute === expected.sceneRoute && state.stageRoute === expected.route
    && state.expected?.durationMinutes === expected.durationMinutes
    && state.position === index + 1 && state.total === total
    && state.navigated === true && state.targetMatches === true && state.rendered === true
    && state.sceneHorizontalInside === true && state.horizontalOverflow === false
    && typeof state.essentialInside === 'boolean' && state.essentialAccessible === true
    && emptyArray(state.essentialFailures)
    && emptyArray(state.unresolvedEssentialSelectors) && state.stageOverflowAccessible === true
    && state.scrollAuditPassed === true && emptyArray(state.undeclaredScrollers)
    && emptyArray(state.hiddenFocusable) && Array.isArray(state.scrollerChecks)
    && state.scrollerChecks.every(item => allTrue(item,
      ['real', 'focusable', 'axisMatches', 'reachedEnd']))
    && state.routePresentationMatches === true
    && state.routePresentation?.badgeRoute === expected.route
    && state.routePresentation?.badgeDuration === `${expected.durationMinutes} min`
    && state.liveRegionMatches === true && state.liveRegion?.text === expectedLive
    && state.liveRegion?.expected === expectedLive && state.progressConsistent === true
    && runtimeStateMatches(state, expected);
}

function flowAuditPassed(flow, lesson, scopeRoutes, targetRoutes = scopeRoutes) {
  if (!lesson) return false;
  const expected = expectedFlowStates(lesson, scopeRoutes, targetRoutes);
  const states = Array.isArray(flow?.states) ? flow.states : [];
  return JSON.stringify(flow?.scopeRoutes) === JSON.stringify(scopeRoutes)
    && JSON.stringify(flow?.targetRoutes) === JSON.stringify(targetRoutes)
    && flow?.expected === expected.length && flow?.visited === expected.length
    && states.length === expected.length
    && states.every((state, index) => flowStatePassed(state, expected[index], index, expected.length));
}

function observerPassed(observer) {
  return Boolean(observer?.target)
    && observer.hashMatches === true && observer.storageMatches === true
    && observer.state?.getStateConsistent === true
    && observer.state.runtimeState?.scene === observer.target.scene
    && observer.state.runtimeState?.stage === observer.target.stage
    && observer.state.runtimeState?.route === observer.target.route;
}

function snapshotPassed(snapshot, target) {
  const route = target?.stageRoute || target?.route;
  return Boolean(snapshot && target && route) && snapshot.scene === target.scene
    && snapshot.stage === target.stage && snapshot.route === route
    && snapshot.sceneRoute === target.sceneRoute && snapshot.targetMatches === true
    && snapshot.getStateConsistent === true
    && runtimeStateMatches(snapshot, { scene: target.scene, stage: target.stage,
      route, sceneRoute: target.sceneRoute });
}

function snapshotPresentationPassed(snapshot, target, surface) {
  const presentation = snapshot?.presentation;
  const route = target?.stageRoute || target?.route;
  if (!presentation || !route || !Number.isFinite(target.durationMinutes)) return false;
  if (surface === 'mobile') {
    return presentation.mobileVisible === true
      && visibilityEvidencePassed(presentation.mobileVisibility)
      && typeof presentation.mobile === 'string'
      && presentation.mobile === `Ruta · ${route} · ${target.durationMinutes} min · Aula → estudio · ${target.scene}`;
  }
  return presentation.badgeVisible === true && presentation.navVisible === true
    && visibilityEvidencePassed(presentation.badgeVisibility)
    && visibilityEvidencePassed(presentation.navVisibility)
    && presentation.badge === route && presentation.nav === route
    && presentation.badgeDuration === `${target.durationMinutes} min`;
}

function breakpointSeamsPassed(seams) {
  const records = Array.isArray(seams?.records) ? seams.records : [];
  const expectedWidths = [900, 901, 920, 960, 961];
  return JSON.stringify(records.map(item => item.width)) === JSON.stringify(expectedWidths)
    && records.every(item => item.width === 900
      ? item.effectiveMode === 'estudio' && item.display === 'flex'
        && item.toolbarVisible === true && item.horizontalOverflow === false
      : item.effectiveMode === 'aula' && item.display === 'grid'
        && item.oneScene === true && item.panelsDoNotOverlap === true
        && item.bodyOverflowHidden === true && item.horizontalOverflow === false);
}

function recordSemantics(record, id, plan, root) {
  if (!record || !hasNoRecordedErrors(record)) return false;
  const expectedTraversal = plan.traversalStates[id];
  if (expectedTraversal) {
    if (!traversalRecordPassed(record, expectedTraversal)) return false;
    if (record.mode === 'aula') {
      return navigationPassed(record.navigation, false)
        && record.studentRouteSafety?.scopeControlHidden === true
        && record.studentRouteSafety?.scope === 'LIVE'
        && record.studentRouteSafety?.nonLiveNavVisible === 0;
    }
    if (record.scope === 'LIVE+REQUIRED') {
      return record.scopeControl === true && navigationPassed(record.professor, true);
    }
    return record.scope === 'ALL' && record.scopeControl === true
      && record.states.every(state => state.routeProgressMatches === true);
  }
  switch (record.mode) {
    case 'negative-fixture': {
      const clippingDetected = Array.isArray(record.after?.essentialFailures)
        && record.after.essentialFailures.some(item => Array.isArray(item.failures)
          && item.failures.some(failure => failure.kind === 'clipping-ancestor'));
      const scrollers = Array.isArray(record.scrollerKeyboard) ? record.scrollerKeyboard : [];
      return desktopStatePassed(record.before) && !desktopStatePassed(record.after) && clippingDetected
        && JSON.stringify(scrollers.map(item => [item.selector, item.key, item.property]))
          === JSON.stringify([['#lr-horizontal-keyboard-fixture', 'ArrowRight', 'scrollLeft'],
            ['#lr-vertical-keyboard-fixture', 'PageDown', 'scrollTop']])
        && scrollers.every(item => item.offset > 0 && typeof item.beforeState === 'string'
          && item.state === item.beforeState)
        && breakpointSeamsPassed(record.breakpointSeams);
    }
    case 'estudio': {
      const initial = record.initial;
      const lesson = plan.lessons.find(item => item.lesson === record.lesson);
      const zeroMotion = record.motion?.reduced === true
        && typeof record.motion.transition === 'string'
        && record.motion.transition.split(',').every(value => parseFloat(value) === 0);
      const optional = initial?.optionalCount === 0
        ? record.explicitOptIn?.applicable === false
        : record.explicitOptIn?.applicable === true
          && visibleStudyStatePassed(record.optedIn, 'ALL', initial.optionalCount)
          && visibleStudyStatePassed(record.optedOut, 'LIVE+REQUIRED', 0)
          && visibleStudyStatePassed(record.explicitOptIn.state, 'ALL', initial.optionalCount);
      return visibleStudyStatePassed(initial, 'LIVE+REQUIRED', 0)
        && observerPassed(record.observerSync) && record.toggleVisible === true
        && flowAuditPassed(record.officialFlow, lesson, ['LIVE', 'REQUIRED'])
        && flowAuditPassed(record.optionalFlow, lesson,
          ['LIVE', 'REQUIRED', 'OPTIONAL'], ['OPTIONAL'])
        && zeroMotion && optional;
    }
    case 'mobile-fallback': {
      const initial = record;
      const lesson = plan.lessons.find(item => item.lesson === record.lesson);
      const optional = record.optionalCount === 0
        ? record.optionalOptIn?.applicable === false
        : record.optionalOptIn?.applicable === true
          && visibleStudyStatePassed(record.optionalOptIn.state, 'ALL', record.optionalCount);
      return visibleStudyStatePassed(initial, 'LIVE+REQUIRED', 0)
        && initial.requestedMode === 'aula' && initial.effectiveMode === 'estudio'
        && initial.runtimeMode === 'estudio' && initial.marked === true && initial.navHidden === true
        && initial.toolbarVisible === true && initial.toolbarHeight >= 44
        && initial.reducedMotion === true && observerPassed(record.observerSync)
        && flowAuditPassed(record.officialFlow, lesson, ['LIVE', 'REQUIRED'])
        && flowAuditPassed(record.optionalFlow, lesson,
          ['LIVE', 'REQUIRED', 'OPTIONAL'], ['OPTIONAL'])
        && record.toggleCorrect === true && optional && drawerPassed(record.mobileDrawer);
    }
    case 'persistence-isolation': {
      const lesson = plan.lessons.find(item => item.lesson === record.lesson);
      const live = lesson ? effectiveStates(lesson).filter(state => state.route === 'LIVE') : [];
      if (!live.length) return false;
      const expectedHashTarget = live[Math.min(1, live.length - 1)];
      const expectedStorageTarget = live[live.length - 1];
      const exactTarget = (target, expected) => target?.lesson === expected.lesson
        && target.scene === expected.scene && target.stage === expected.stage
        && target.sceneRoute === expected.sceneRoute && target.stageRoute === expected.route
        && target.durationMinutes === expected.durationMinutes;
      const expectedHash = `#${encodeURIComponent(expectedHashTarget.scene)}`
        + `/${encodeURIComponent(expectedHashTarget.stage)}`;
      const hashTarget = { ...expectedHashTarget, stageRoute: expectedHashTarget.route };
      const storageTarget = { ...expectedStorageTarget, stageRoute: expectedStorageTarget.route };
      return exactTarget(record.hashOnly?.target, expectedHashTarget)
        && record.hashOnly.storageInitiallyEmpty === true
        && record.hashOnly.requestedHash === expectedHash
        && record.hashOnly.observedHash === expectedHash
        && snapshotPassed(record.hashOnly.state, hashTarget)
        && snapshotPresentationPassed(record.hashOnly.state, hashTarget, 'desktop')
        && exactTarget(record.storageOnly?.target, expectedStorageTarget)
        && record.storageOnly?.seededStorageTarget?.scene === expectedStorageTarget.scene
        && record.storageOnly?.seededStorageTarget?.stage === expectedStorageTarget.stage
        && record.storageOnly.requestedWithoutHash === true
        && record.storageOnly.hashCleared === true
        && snapshotPassed(record.storageOnly.state, storageTarget)
        && snapshotPresentationPassed(record.storageOnly.state, storageTarget, 'desktop');
    }
    case 'fresh-professor-deep-links': {
      const records = Array.isArray(record.records) ? record.records : [];
      const observed = records.map(item =>
        `${item.route}:${item.lesson}:${item.target?.scene}/${item.target?.stage}`);
      return exactUnique(observed, plan.deepLinkIds) && records.every(item => {
        const expected = plan.deepLinkTargets.find(target => target.route === item.route);
        if (!expected) return false;
        const expectedHash = `#${encodeURIComponent(expected.scene)}/${encodeURIComponent(expected.stage)}`;
        const exactTarget = item.lesson === expected.lesson
          && item.target?.scene === expected.scene && item.target?.stage === expected.stage
          && item.target?.sceneRoute === expected.sceneRoute
          && item.target?.stageRoute === expected.route
          && item.target?.durationMinutes === expected.durationMinutes;
        return exactTarget && item.freshContext === true && item.storageInitiallyEmpty === true
          && item.requestedHash === expectedHash && item.observedHash === expectedHash
          && item.expectedScope === item.state?.scope
          && item.expectedScope === (item.route === 'OPTIONAL' ? 'ALL' : 'LIVE+REQUIRED')
          && snapshotPassed(item.state, expected)
          && snapshotPresentationPassed(item.state, expected, 'desktop');
      });
    }
    case 'route-overrides': {
      const records = Array.isArray(record.records) ? record.records : [];
      const ids = records.map(item => `${item.lesson}:${item.scene}/${item.stage}`);
      return record.expected === plan.overrideIds.length && record.declared === plan.overrideIds.length
        && record.visible === plan.overrideIds.length && exactUnique(ids, plan.overrideIds)
        && records.every(item => {
          const expected = plan.overrideTargets.find(target => target.lesson === item.lesson
            && target.scene === item.scene && target.stage === item.stage);
          if (!expected) return false;
          const target = { ...expected, stageRoute: expected.route };
          return item.sceneRoute === expected.sceneRoute && item.effectiveRoute === expected.route
            && item.durationMinutes === expected.durationMinutes
            && expected.sceneRoute !== expected.route
            && snapshotPassed(item.desktop, target) && snapshotPassed(item.mobile, target)
            && snapshotPresentationPassed(item.desktop, target, 'desktop')
            && snapshotPresentationPassed(item.mobile, target, 'mobile')
            && item.teacher?.visible === true && item.teacher.routeVisible === true
            && item.teacher.overrideVisible === true && item.teacher.durationVisible === true
            && visibilityEvidencePassed({ rendered: item.teacher.visible,
              positiveArea: item.teacher.visibility?.positiveArea,
              effectiveOpacity: item.teacher.visibility?.effectiveOpacity,
              unoccluded: item.teacher.visibility?.unoccluded })
            && item.teacher.kicker
              === `${expected.route} · ${expected.type} · ${expected.durationMinutes} min`
            && item.teacher.override
              === `Ruta efectiva ${expected.route}; la escena declara ${expected.sceneRoute}.`;
        });
    }
    case 'visual-sample': {
      const target = visualSampleTargets(plan.lessons).find(item => item.name === record.sample);
      return Boolean(target) && record.lesson === target.lesson && record.scene === target.scene
        && record.stage === target.stage && typeof record.screenshot === 'string'
        && record.screenshot.startsWith(`visual-${record.sample}-`)
        && record.determinism?.auditMode === 'visual-v1'
        && record.determinism?.reducedMotion === true
        && JSON.stringify(record.determinism?.randomProbe) === JSON.stringify([0.5, 0.5])
        && desktopStatePassed(record.geometry);
    }
    case 'index':
      return record.blocks === 4 && record.actions === 42 && record.source === 'runtime'
        && JSON.stringify(record.outputs) === JSON.stringify(['50%', '25%'])
        && record.assessmentLinearLabel === true && record.horizontalOverflow === false;
    case 'assessment-linear':
      return record.lesson === 'L15' && record.linear === true && record.noSceneRuntime === true
        && record.questions === 40 && record.horizontalOverflow === false;
    case 'input-integrity': {
      return record.inputsStable === true && record.inputValidation?.passed === true
        && record.inputValidation?.exactPaths === true && record.inputValidation?.hashesMatch === true
        && record.inputValidation?.expected === record.inputValidation?.observed;
    }
    default: return false;
  }
}

function validateResultSemantics(results, plan, root) {
  const records = Array.isArray(results) ? results : [];
  const byId = new Map(records.map(record => [recordId(record), record]));
  const checks = plan.ids.map(id => ({ id, passed: recordSemantics(byId.get(id), id, plan, root) }));
  return { expected: plan.ids.length, observed: records.length, checks,
    passed: records.length === plan.ids.length && checks.every(check => check.passed) };
}

function sourceHead(root, environmentSha = process.env.GITHUB_SHA) {
  const head = execFileSync('git', ['rev-parse', '--verify', 'HEAD'], {
    cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
  if (!/^[0-9a-f]{40}$/.test(head)) throw new Error(`invalid git HEAD: ${head}`);
  if (environmentSha && environmentSha !== head) {
    throw new Error(`GITHUB_SHA ${environmentSha} does not match checked-out HEAD ${head}`);
  }
  const trackedChanges = execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], {
    cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
  if (trackedChanges) {
    throw new Error('tracked worktree differs from HEAD; evidence requires a clean checkout');
  }
  return head;
}

module.exports = {
  AUDIT_OWNER_FILE,
  ALL_VIEWPORTS,
  BROWSER_IDENTITY_SCHEMA,
  DESKTOP_VIEWPORTS,
  MAX_PNG_INFLATED_BYTES,
  VISUAL_SAMPLES,
  VISUAL_AUDIT_INIT_SCRIPT,
  attachRecordIds,
  auditDirectoryIdentity,
  browserPayloadEvidence,
  buildExpectedAuditPlan,
  crc32,
  desktopStatePassed,
  discoverLessons,
  flowStatePassed,
  inputEvidence,
  lockedBrowserIdentity,
  lockedPlaywrightBrowserIdentity,
  navigationPassed,
  parsePngBuffer,
  pngEvidence,
  prepareAuditDirectory,
  recordId,
  recordSemantics,
  sameInputEvidence,
  screenshotEvidence,
  sourceHead,
  traversalRecordPassed,
  validateAuditOwner,
  validateBrowserIdentity,
  validateCoverage,
  validateInputEvidence,
  validateRecordSet,
  validateResultSemantics,
  visualSampleTargets,
};
