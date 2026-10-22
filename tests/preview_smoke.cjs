// SPDX-License-Identifier: GPL-2.0-or-later
// Optional host-only smoke check. Requires Playwright and a local browser.
const fs = require('fs');
const path = require('path');
const {chromium} = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const output = path.resolve(process.argv[2] || path.join(root, 'artifacts', 'preview'));
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({headless:true, ...(process.env.PREVIEW_BROWSER_CHANNEL ? {channel:process.env.PREVIEW_BROWSER_CHANNEL} : {})});
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  const requests = [];
  page.on('request', request => requests.push(request.url()));
  await page.goto('file:///' + root.replaceAll('\\','/') + '/design/cclos-concept-m0.html');
  const results = [];
  for (const width of [1280,1920,736,360]) {
    await page.setViewportSize({width,height:780});
    for (const [scene,label] of [['tiles','01 / Tile library'],['list','02 / Compact library'],['pause','03 / In-game menu'],['empty','04 / Empty library']]) {
      await page.getByRole('button',{name:label,exact:true}).click();
      const layout = await page.evaluate(() => ({width:innerWidth,scroll:document.documentElement.scrollWidth}));
      if (layout.scroll > layout.width) throw new Error(`Overflow: ${width}/${scene}`);
      if (!await page.locator('#' + scene).isVisible()) throw new Error('Scene did not activate');
      results.push({width,scene,status:'PASS',horizontalOverflow:false});
      if (width === 1280) await page.screenshot({path:path.join(output,'cclos-'+scene+'.png'),fullPage:true});
    }
  }
  await page.setViewportSize({width:1280,height:780});
  await page.getByRole('button',{name:'02 / Compact library',exact:true}).click();
  await page.locator('.row[data-title="Verdant"]').click();
  if (await page.locator('#detail-title').textContent() !== 'VERDANT') throw new Error('Detail title failed');
  await page.locator('.detail .launch').click();
  if (!(await page.locator('#notice').textContent()).includes('no emulator or storage action')) throw new Error('Mock action label failed');
  await page.getByRole('button',{name:'Folders',exact:true}).click();
  if (await page.getByRole('button',{name:'Folders',exact:true}).getAttribute('aria-pressed') !== 'true') throw new Error('Nav failed');
  await page.getByRole('button',{name:'All Games',exact:true}).click();
  await page.getByRole('button',{name:'01 / Tile library',exact:true}).click();
  await page.locator('.tile[data-title="Orbital"]').click();
  await page.screenshot({path:path.join(output,'cclos-tile-library.png'),fullPage:true});
  await page.getByRole('button',{name:'02 / Compact library',exact:true}).click();
  await page.screenshot({path:path.join(output,'cclos-compact-library.png'),fullPage:true});
  await page.getByRole('button',{name:'03 / In-game menu',exact:true}).click();
  await page.screenshot({path:path.join(output,'cclos-ingame-menu.png'),fullPage:true});
  if (errors.length) throw new Error(errors.join('\n'));
  if (requests.some(url => /^https?:/.test(url))) throw new Error('Unexpected network request');
  const report = {status:'PASS',renderer:'Installed Microsoft Edge / Playwright, host-only',results,selectionUpdates:'PASS',mockActions:'PASS',navigation:'PASS',pageErrors:errors,externalRequests:0,xboxRuntime:'NOT RUN'};
  fs.writeFileSync(path.join(output,'preview-qa.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify(report));
})().catch(error => {console.error(error);process.exit(1)});
