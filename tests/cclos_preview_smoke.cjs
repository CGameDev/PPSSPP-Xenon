// SPDX-License-Identifier: GPL-2.0-or-later
// Optional browser review check. The renderer data comes from native method traces.
const fs = require('fs');
const path = require('path');
const {chromium} = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const output = path.resolve(process.argv[2] || path.join(root, 'artifacts', 'cclos-preview'));
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({headless:true, ...(process.env.PREVIEW_BROWSER_CHANNEL ? {channel:process.env.PREVIEW_BROWSER_CHANNEL} : {})});
  const page = await browser.newPage();
  const errors = [], requests = [], results = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('request', r => requests.push(r.url()));
  await page.goto('file:///' + root.replaceAll('\\','/') + '/design/cclos-preview.html');
  for (const width of [1280,1920,736,360]) {
    await page.setViewportSize({width,height:900});
    for (const scene of ['normal','empty','missing','long','folder','recent','loading']) {
      await page.locator('#scene').selectOption(scene);
      for (const view of ['grid','list']) {
        await page.locator('#'+view).click();
        const layout = await page.evaluate(() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
          label:document.querySelector('#screen').getAttribute('aria-label'), text:[...document.querySelectorAll('svg text')].map(t=>t.textContent)}));
        if (layout.scroll>layout.width) throw new Error('Page overflow: '+width+'/'+view+'/'+scene);
        if (!layout.label.includes(scene==='recent'?'grid':view)) throw new Error('View selection failed');
        if (scene==='long' && !layout.text.some(t=>t.endsWith('...'))) throw new Error('Truncation trace missing');
        if (await page.locator('#'+view).getAttribute('aria-pressed')!=='true') throw new Error('Control state failed');
        results.push({width,scene,view,status:'PASS'});
        if (width===1280 && scene==='normal') await page.screenshot({path:path.join(output,'cclos-m4-'+view+'.png'),fullPage:true});
      }
    }
  }
  await page.locator('#scene').selectOption('normal');
  await page.locator('#grid').click();
  await page.keyboard.press('v');
  if (await page.locator('#list').getAttribute('aria-pressed')!=='true') throw new Error('Keyboard view switch failed');
  if (errors.length) throw new Error(errors.join('\n'));
  if (requests.some(u=>/^https?:/.test(u))) throw new Error('Unexpected external request');
  const report={status:'PASS',renderer:'Installed Edge / Playwright; host SVG trace visualization',
    results,keyboardSwitch:'PASS',externalRequests:0,pageErrors:errors,
    limitations:'Fictional artwork; approximate browser text rasterization. No Xbox execution or visual acceptance.'};
  fs.writeFileSync(path.join(output,'cclos-preview-qa.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:'PASS',scenarios:results.length,externalRequests:0}));
})().catch(e=>{console.error(e);process.exitCode=1});
