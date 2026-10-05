const {chromium}=require('playwright');
const fs=require('fs');
const output=process.env.QA_OUTPUT||'/tmp/kvapps-language-qa';fs.mkdirSync(output,{recursive:true});
const base=process.argv[2]||'http://127.0.0.1:8768/';
const files=['index','paper-drift','support','privacy','terms'];
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});let checks=0;const errors=[];
 for(const width of base.startsWith('https:')?[390]:[320,390,1440]){
  const context=await browser.newContext({viewport:{width,height:844},locale:'vi-VN'});const page=await context.newPage();page.setDefaultTimeout(15000);page.on('pageerror',e=>errors.push(e.message));
  for(const name of files){
   await page.evaluate(()=>localStorage.clear()).catch(()=>{});
   const response=await page.goto(new URL(name+'.html',base).href,{waitUntil:'networkidle'});
   if(response.status()!==200)throw Error('HTTP '+name);
   if(await page.locator('html').getAttribute('lang')!=='en')throw Error('Default not English '+name);
   for(const lang of ['en','vi','en']){
    if(lang==='vi'||checks)await page.locator(`[data-language="${lang}"]`).click();
    await page.waitForFunction(l=>document.documentElement.lang===l,lang);
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Overflow '+name+' '+lang+' '+width);
    if(lang==='en'){
     const vietnamese=await page.evaluate(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const bad=[];while(w.nextNode()){const n=w.currentNode;if(!n.parentElement.closest('script,style,[data-language-switch]')&&/[ăâđêôơưĂÂĐÊÔƠƯ]/u.test(n.textContent))bad.push(n.textContent)}return bad;});
     if(vietnamese.length)throw Error('Untranslated English '+name+JSON.stringify(vietnamese));
    }
    if(lang==='vi'&&!await page.locator('h1').innerText().then(t=>/Paper|Ứng dụng|Hỗ trợ|Chính sách|Điều khoản/.test(t)))throw Error('Vietnamese heading '+name);
    for(const img of await page.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());}
    const links=await page.locator('a[href]').evaluateAll(a=>a.map(el=>el.href));
    for(const target of new Set(links)){const u=new URL(target);if(u.origin!==new URL(base).origin)continue;const r=await page.request.get(u.href);if(r.status()!==200)throw Error('Link '+u.href);if(u.hash&&! (await r.text()).includes('id="'+decodeURIComponent(u.hash.slice(1))+'"'))throw Error('Anchor '+u.href);}
    if(width===390){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:output+'/'+name+'-'+lang+'.png',fullPage:true});}
    checks++;
   }
  }
  // Explicit choice overrides a previous choice, persists across pages, and retains deep links.
  await page.goto(new URL('support.html?lang=vi#paper-drift',base).href,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.documentElement.lang==='vi');
  await page.waitForFunction(()=>Math.abs(document.querySelector('#paper-drift').getBoundingClientRect().top)<80);
  await page.locator('[data-language="en"]').click();
  if(!page.url().endsWith('?lang=en#paper-drift'))throw Error('Lost anchor on switch');
  await page.goto(new URL('privacy.html',base).href,{waitUntil:'networkidle'});
  if(await page.locator('html').getAttribute('lang')!=='en')throw Error('Choice not persisted');
  await page.locator('[data-language="vi"]').click();
  await page.goto(new URL('terms.html',base).href,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.documentElement.lang==='vi');
  await page.goto(new URL('paper-drift.html?lang=en',base).href,{waitUntil:'networkidle'});
  if(await page.locator('html').getAttribute('lang')!=='en')throw Error('Query override failed');
  await context.close();
 }
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const fallback=await nojs.newPage();await fallback.goto(new URL('paper-drift.html',base).href);if(! (await fallback.locator('body').innerText()).includes('One current.'))throw Error('English fallback');await nojs.close();
 if(errors.length)throw Error(errors.join('\n'));await browser.close();
 console.log(JSON.stringify({base,checks,languages:['en','vi'],errors,status:'passed'}));
})().catch(e=>{console.error(e);process.exit(1)});
