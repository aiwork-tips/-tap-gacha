#!/usr/bin/env python3
"""Browser regression for modular RC02. Runs against the served test branch."""
import os, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT/'qa-screenshots'
SHOTS.mkdir(exist_ok=True)
URL = os.getenv('QA_URL','http://127.0.0.1:8877/index.html')
ENGINE = os.getenv('QA_BROWSER','chromium').strip().lower()
assert ENGINE in ('chromium','webkit'), ENGINE
passed=[]
errors=[]

def check(label, ok):
    if not ok: raise AssertionError(f'{label} FAILED; JS errors: {errors}')
    passed.append(label)
    print('PASS:',label,flush=True)

with sync_playwright() as pw:
    launch = {'headless': True}
    if ENGINE=='chromium': launch['args']=['--no-sandbox','--disable-dev-shm-usage']
    browser=getattr(pw,ENGINE).launch(**launch)
    context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
    page=context.new_page()
    page.on('pageerror',lambda err:errors.append(str(err)))
    resource_failures=[]
    page.on('response',lambda response:resource_failures.append(f'{response.status} {response.url}') if response.status>=400 and ('/assets/' in response.url or '/css/' in response.url or '/js/' in response.url) else None)
    page.on('requestfailed',lambda request:resource_failures.append(f'failed {request.url}') if ('/assets/' in request.url or '/css/' in request.url or '/js/' in request.url) else None)
    response=page.goto(URL,wait_until='load',timeout=60000)
    check('HTTP 200',response.status==200)
    page.wait_for_timeout(500)
    def state():
        return page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    check('home initializes',page.locator('#homeScreen.active').count()==1 and state()['schemaVersion']==3)
    check('six screens',page.locator('section.screen').count()==6)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-home-390.png'))
    before=state()
    page.locator('#goTap').click(force=True)
    check('tap navigation',page.locator('#tapScreen.active').count()==1)
    page.locator('#tapZone').click(force=True)
    after=state()
    check('tap PT saved',after['points']==before['points']+before['tapPower'])
    check('tap stats saved',after['stats']['taps']==before['stats']['taps']+1)
    check('tap chest progress advances',after.get('tapRewardProgress',{}).get('count',0)==before.get('tapRewardProgress',{}).get('count',0)+1)
    page.locator('#backHome').click(force=True)
    page.locator('[data-home-go="gacha"]').click(force=True)
    check('gacha navigation',page.locator('#gachaScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-gacha-390.png'))
    before=state()
    page.locator('.gacha-draw[data-pulls="1000"]').click(force=True)
    after=state()
    check('1000 pulls costs 1000 PT',after['points']==before['points']-1000)
    check('1000 pulls counted',after['stats']['gachaPulls']==before['stats']['gachaPulls']+1000)
    check('roster shards awarded',sum(int(c.get('shards',0)) for c in after['characters'].values())>0)
    page.locator('#gachaBackHome').click(force=True)
    page.locator('[data-home-go="character"]').click(force=True)
    check('character navigation',page.locator('#characterScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-390.png'))
    page.locator('#charRosterToggle').click(force=True)
    check('roster expanded',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='true')
    page.locator('#charRosterToggle').click(force=True)
    check('roster collapsed',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='false')
    check('15 character tiles',page.locator('#characterGrid [data-character-id]').count()==15)
    page.locator('#charBackHome').click(force=True)
    page.locator('[data-home-go="shop"]').click(force=True)
    check('shop navigation',page.locator('#shopScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-shop-390.png'))
    before=state()
    page.locator('#shopBuyKey').click(force=True)
    after=state()
    check('key purchase PT and key saved',after['points']==before['points']-5000 and after['keys']==before['keys']+1)
    page.locator('#shopBackHome').click(force=True)
    page.locator('[data-home-go="quest"]').click(force=True)
    check('quest navigation',page.locator('#questScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-quest-390.png'))
    page.locator('#questBackHome').click(force=True)
    before=state()
    page.reload(wait_until='load',timeout=60000)
    after=state()
    check('reload preserves progress',all(before[k]==after[k] for k in ('points','keys','stats')))
    check('tap chest progress survives navigation and reload',after['tapRewardProgress']['count']==before['tapRewardProgress']['count'])
    missing=page.evaluate("Array.from(document.images).filter(i => i.getAttribute('src') && i.complete && !i.naturalWidth).map(i=>i.src)")
    check('visible images load',not missing)
    page.set_viewport_size({'width':320,'height':568})
    page.locator('[data-home-go="character"]').click(force=True)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-320.png'))
    check('320px no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
    check('320px roster is vertically scrollable',page.evaluate("""() => {let el=document.querySelector('#characterScreen .char-scroll');return el && el.scrollHeight>el.clientHeight && getComputedStyle(el).overflowY!=='hidden'}"""))
    page.set_viewport_size({'width':430,'height':932})
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-430.png'))
    check('430px no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
    check('all game asset responses are successful',not resource_failures)
    check('no JavaScript runtime errors',not errors)

    # Isolated deterministic fixture: validate cap, MAX, repeated 10-level hold and save reload.
    training=context.new_page()
    training.on('pageerror',lambda err:errors.append('training: '+str(err)))
    training.goto(URL,wait_until='load',timeout=60000)
    # pagehide saves the in-memory game state on reload. Apply the fixture *before*
    # the new document's game script, once, to avoid overwriting it with the old state.
    training.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_training_fixture_applied')) return;
      const s=JSON.parse(localStorage.getItem('tapgacha_save_v3'));
      s.characters.c001={owned:true,level:1,cap:50,shards:5000};
      s.keys=3;s.points=12450;
      localStorage.setItem('tapgacha_save_v3',JSON.stringify(s));
      sessionStorage.setItem('__qa_training_fixture_applied','1');
    })()""")
    training.reload(wait_until='load')
    training.locator('[data-home-go="character"]').click(force=True)
    training.locator('#characterGrid [data-character-id="c001"]').click(force=True)
    training.locator('#charQuantity10').click(force=True)
    training.locator('#charLevelUp').click(force=True)
    tstate=lambda:training.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    check('10-level training batch',tstate()['characters']['c001']['level']==11)
    training.locator('#charQuantityMax').click(force=True)
    check('MAX stops at level cap 50',tstate()['characters']['c001']['level']==50)
    keys_before=tstate()['keys']
    training.locator('#charLimitBreak').click(force=True)
    check('cap unlock reaches 100 and consumes one key',tstate()['characters']['c001']['cap']==100 and tstate()['keys']==keys_before-1)
    box=training.locator('#charLevelUp').bounding_box()
    assert box is not None
    training.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
    training.mouse.down()
    training.wait_for_timeout(950)
    training.mouse.up()
    check('holding 10-level mode repeatedly trains',tstate()['characters']['c001']['level']>60)
    levels_before=tstate()['characters']['c001']['level']
    training.reload(wait_until='load')
    check('trained level survives reload',tstate()['characters']['c001']['level']==levels_before)
    training.screenshot(path=str(SHOTS/f'{ENGINE}-character-trained-390.png'))
    check('training no runtime errors',not errors)
    training.close()
    # Data safety: corrupted unified saves must never be overwritten.
    protected=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    protected.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_corrupt_seeded')) return;
      localStorage.setItem('tapgacha_save_v3','{not-json');
      sessionStorage.setItem('__qa_corrupt_seeded','1');
    })()""")
    protect_page=protected.new_page()
    protect_page.on('pageerror',lambda err:errors.append('corrupt: '+str(err)))
    protect_page.goto(URL,wait_until='load')
    check('corrupt unified save remains intact',protect_page.evaluate("localStorage.getItem('tapgacha_save_v3')")=='{not-json')
    protect_page.locator('#goTap').click(force=True)
    protect_page.locator('#tapZone').click(force=True)
    check('corrupted save blocks game writes',protect_page.evaluate("localStorage.getItem('tapgacha_save_v3')")=='{not-json')
    protect_page.reload(wait_until='load')
    check('corrupt save protected across reload',protect_page.evaluate("localStorage.getItem('tapgacha_save_v3')")=='{not-json')
    protected.close()
    # Existing client legacy keys take precedence and become a v3 save.
    old=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    old.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_legacy_seeded')) return;
      localStorage.setItem('tapgacha_pt','777');
      localStorage.setItem('tapgacha_collection',JSON.stringify({c01:{owned:true,level:2,shards:15}}));
      localStorage.setItem('gV2',JSON.stringify({pts:9999}));
      sessionStorage.setItem('__qa_legacy_seeded','1');
    })()""")
    old_page=old.new_page()
    old_page.on('pageerror',lambda err:errors.append('legacy: '+str(err)))
    old_page.goto(URL,wait_until='load')
    imported=old_page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    check('legacy points preserve current-key priority',imported['points']==777)
    check('legacy character ID normalizes without losing levels',imported['characters']['c001']['level']==2 and imported['characters']['c001']['shards']==15)
    old_page.reload(wait_until='load')
    check('legacy migration remains stable after reload',old_page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3')).points")==777)
    old.close()
    check('new save safety checks produce no runtime exceptions',not errors)
    (ROOT/f'qa-results-{ENGINE}.json').write_text(json.dumps({'browser':ENGINE,'passed':len(passed),'checks':passed,'runtime_errors':errors,'broken_images':missing,'resource_failures':resource_failures},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ALL {len(passed)} CHECKS PASS',flush=True)
    browser.close()
