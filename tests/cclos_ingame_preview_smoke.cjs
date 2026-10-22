// SPDX-License-Identifier: GPL-2.0-or-later
// Optional browser check; trace fixtures cannot execute any emulator actions.
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),out=path.resolve(process.argv[2]||path.join(root,'artifacts/ingame-preview'));
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.PREVIEW_BROWSER_CHANNEL?{channel:process.env.PREVIEW_BROWSER_CHANNEL}:{})});
 const page=await browser.newPage(),errors=[],requests=[],cases=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
 await page.goto('file:///'+root.replaceAll('\\','/')+'/design/cclos-ingame-preview.html');
 for(const width of [1280,1920,736,360]){
  await page.setViewportSize({width,height:900});
  for(const scene of ['menu-mixed','menu-empty','menu-saved']){
   await page.locator('#scene').selectOption(scene);
   for(const [focus,label]of [['slots',0],['session',1]]){
    await page.locator('#'+focus).click();
    for(let row=0;row<5;row++){
     await page.locator('#item').selectOption(String(row));
     const state=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,label:document.querySelector('#screen').getAttribute('aria-label')}));
     if(state.scroll>state.width||!state.label.endsWith('selection '+(label*5+row)))throw new Error('Selection/overflow '+scene+'/'+focus+'/'+row);
     cases.push({width,scene,focus,row,status:'PASS'});
     if(width===1280&&scene==='menu-mixed'&&row===(focus==='slots'?0:2))await page.screenshot({path:path.join(out,'cclos-m5-'+focus+'.png'),fullPage:true});
    }
   }
  }
  for(const scene of ['menu-toast','menu-toast-fade','menu-toast-long','menu-no-atlas']){
   await page.locator('#scene').selectOption(scene);
   if(!await page.locator('#item').isDisabled())throw new Error('Fixed trace should disable selection controls');
   if(await page.locator('#item').inputValue()!=='0')throw new Error('Fixed trace should identify slot 1');
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
   if(overflow)throw new Error('Overflow '+scene);
   cases.push({width,scene,status:'PASS'});
   if(width===1280&&scene==='menu-toast')await page.screenshot({path:path.join(out,'cclos-m5-notification.png'),fullPage:true});
  }
 }
 if(errors.length||requests.some(u=>/^https?:/.test(u)))throw new Error('Browser errors/external request');
 const report={status:'PASS',cases,pageErrors:errors,externalRequests:0,xboxRuntime:'NOT RUN',renderer:'Installed Edge / Playwright; host trace, approximate browser font rasterization'};
 fs.writeFileSync(path.join(out,'cclos-ingame-preview-qa.json'),JSON.stringify(report,null,2)+'\n');
 await browser.close();console.log(JSON.stringify({status:'PASS',cases:cases.length,externalRequests:0}));
})().catch(e=>{console.error(e);process.exitCode=1});
