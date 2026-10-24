/* Run with Playwright available on NODE_PATH and a local preview server. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
let playwright;
try {
  playwright = require('playwright');
} catch {
  playwright = require('../.tools/browser/node_modules/playwright');
}

const base = process.env.BOOK_URL || 'http://127.0.0.1:8765';
const output = path.resolve('.build/qa');
const pages = fs.readdirSync('docs').filter(name => name.endsWith('.html'));
const expected = [...fs.readFileSync('_quarto.yml', 'utf8')
  .matchAll(/^\s+-\s+(\S+)\.qmd\s*$/gm)].map(match => `${match[1]}.html`);
assert.ok(expected.length > 0, 'No configured chapters found.');
assert.deepEqual([...pages].sort(), [...expected].sort(),
  'Rendered chapters are missing or stale; finish make html before browser checks.');

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await playwright.chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE || undefined,
  });
  const results = [];
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 960 } });
      // The book must work with all non-local requests blocked.
      await context.route('**/*', route => {
        const url = new URL(route.request().url());
        return url.origin === new URL(base).origin ? route.continue() : route.abort();
      });
      const page = await context.newPage();
      let errors;
      page.on('pageerror', error => errors.push(error.message));
      page.on('console', message => {
        if (message.type() === 'error') errors.push(`${message.text()} ${message.location().url}`);
      });
      page.on('requestfailed', request => errors.push(
        `${request.failure().errorText} ${request.url()}`));
      page.on('response', response => {
        if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
      });
      for (const name of pages) {
        errors = [];
        await page.goto(`${base}/${name}`, { waitUntil: 'networkidle' });
        await page.evaluate(() => document.fonts.ready);
        const state = await page.evaluate(() => ({
          brokenImages: [...document.images].filter(img => !img.complete || !img.naturalWidth)
            .map(img => img.getAttribute('src')),
          mathCount: document.querySelectorAll('.math').length,
          unrenderedMath: [...document.querySelectorAll('.math')]
            .filter(el => !el.querySelector('.katex')).map(el => el.textContent),
          mathErrors: [...document.querySelectorAll('.katex-error, mjx-merror')]
            .map(el => el.textContent),
          pageWidth: document.documentElement.scrollWidth,
          viewportWidth: innerWidth,
        }));
        results.push({ name, width, ...state, errors: [...errors] });
        assert.deepEqual(errors, [], `${name} at ${width}px: browser errors`);
        assert.deepEqual(state.brokenImages, [], `${name}: broken images`);
        assert.deepEqual(state.unrenderedMath, [], `${name}: unrendered math`);
        assert.deepEqual(state.mathErrors, [], `${name}: invalid math`);
        assert.ok(state.pageWidth <= state.viewportWidth + 1,
          `${name}: page overflows (${state.pageWidth} > ${state.viewportWidth})`);
        await page.screenshot({ path: path.join(output, `${name}-${width}.png`) });
      }
      await context.close();
    }
    console.log(`PASS: ${results.length} page/viewport checks with external requests blocked.`);
  } finally {
    fs.writeFileSync(path.join(output, 'browser-report.json'), JSON.stringify(results, null, 2) + '\n');
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
