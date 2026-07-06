/* e2e_check.js — abre cada documento del curso (y el examen), recorre su
   scrollytelling y falla si hay CUALQUIER error de página. Lo usa el CI. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');

function findDocs() {
  const out = [];
  for (const d of fs.readdirSync(ROOT)) {
    const pres = path.join(ROOT, d, 'presentation');
    if (/^\d\d-/.test(d) && fs.existsSync(pres)) {
      for (const f of fs.readdirSync(pres)) {
        if (f.endsWith('-doc.html')) out.push(path.join(pres, f));
      }
    }
  }
  const exam = path.join(ROOT, '15-final-exam', 'examen.html');
  if (fs.existsSync(exam)) out.push(exam);
  const index = path.join(ROOT, 'index.html');
  if (fs.existsSync(index)) out.push(index);
  return out.sort();
}

(async () => {
  const docs = findDocs();
  if (docs.length < 15) {
    console.error(`solo se encontraron ${docs.length} documentos`);
    process.exit(1);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  let failures = 0;

  for (const doc of docs) {
    const errs = [];
    const handler = e => errs.push(e.message);
    page.on('pageerror', handler);
    await page.goto('file://' + doc);
    await page.waitForTimeout(600);
    // recorrer el scrolly para disparar todas las etapas
    const steps = await page.$$('.scrolly .step');
    for (let i = 0; i < steps.length; i++) {
      await page.evaluate(el => window.scrollBy(
        0, el.getBoundingClientRect().top - window.innerHeight / 2), steps[i]);
      await page.waitForTimeout(250);
    }
    const hscroll = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
    page.off('pageerror', handler);

    const name = path.relative(ROOT, doc);
    if (errs.length || hscroll) {
      failures++;
      console.error(`✗ ${name}  errores=${errs.length} hscroll=${hscroll}`);
      errs.slice(0, 3).forEach(e => console.error('   ', e.slice(0, 120)));
    } else {
      console.log(`✓ ${name}`);
    }
  }
  await browser.close();
  process.exit(failures ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
