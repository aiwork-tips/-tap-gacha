#!/usr/bin/env python3
"""Browser regression for modular RC02. Runs against the served test branch."""
import os, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT/'qa-screenshots'
SHOTS.mkdir(exist_ok=True)
URL = os.getenv('QA_URL','http://127.0.0.1:8877/index.html')
passed=[]
errors=[]

def check(label, ok):
    if not ok: raise AssertionError(f'{label} FAILED; JS errors: {errors}')
    passed.append(label)
    print('PASS:',label,flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
    page=context.new_page()
    page.on('pageerror',lambda err:errors.append(str(err)))
    response=page.goto(URL,wait_until='load',timeout=60000)
    check('HTTP 200',response.status==200)
    page.wait_for_timeout(500)
    def state():
        return page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    check('home initializes',page.locator('#homeScreen.active').count()==1 and state()['schemaVersion']==3)
    check('six screens',page.locator('section.screen').count()==6)
    page.screenshot(path=str(SHOTS/'home-390.png'))
    before=state()
    page.locator('#goTap').click(force=True)
    check('tap navigation',page.locator('#tapScreen.active').count()==1)
    page.locator('#tapZone').click(force=True)
    after=state()
    check('tap PT saved',after['points']==before['points']+before['tapPower'])
    check('tap stats saved',after['stats']['taps']==before['stats']['taps']+1)
    page.locator('#backHome').click(force=True)
    page.locator('[data-home-go="gacha"]').click(force=True)
    check('gacha navigation',page.locator('#gachaScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/'gacha-390.png'))
    before=state()
    page.locator('.gacha-draw[data-pulls="1000"]').click(force=True)
    after=state()
    check('1000 pulls costs 1000 PT',after['points']==before['points']-1000)
    check('1000 pulls counted',after['stats']['gachaPulls']==before['stats']['gachaPulls']+1000)
    check('roster shards awarded',sum(int(c.get('shards',0)) for c in after['characters'].values())>0)
    page.locator('#gachaBackHome').click(force=True)
    page.locator('[data-home-go="character"]').click(force=True)
    check('character navigation',page.locator('#characterScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/'character-390.png'))
    page.locator('#charRosterToggle').click(force=True)
    check('roster expanded',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='true')
    page.locator('#charRosterToggle').click(force=True)
    check('roster collapsed',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='false')
    check('15 character tiles',page.locator('#characterGrid [data-character-id]').count()==15)
    page.locator('#charBackHome').click(force=True)
    page.locator('[data-home-go="shop"]').click(force=True)
    check('shop navigation',page.locator('#shopScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/'shop-390.png'))
    before=state()
    page.locator('#shopBuyKey').click(force=True)
    after=state()
    check('key purchase PT and key saved',after['points']==before['points']-5000 and after['keys']==before['keys']+1)
    page.locator('#shopBackHome').click(force=True)
    page.locator('[data-home-go="quest"]').click(force=True)
    check('quest navigation',page.locator('#questScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/'quest-390.png'))
    page.locator('#questBackHome').click(force=True)
    before=state()
    page.reload(wait_until='load',timeout=60000)
    after=state()
    check('reload preserves progress',all(before[k]==after[k] for k in ('points','keys','stats')))
    missing=page.evaluate("Array.from(document.images).filter(i => i.getAttribute('src') && i.complete && !i.naturalWidth).map(i=>i.src)")
    check('visible images load',not missing)
    page.set_viewport_size({'width':320,'height':568})
    page.locator('[data-home-go="character"]').click(force=True)
    page.screenshot(path=str(SHOTS/'character-320.png'))
    check('320px no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
    check('no JavaScript runtime errors',not errors)
    (ROOT/'qa-results.json').write_text(json.dumps({'passed':len(passed),'checks':passed,'runtime_errors':errors,'broken_images':missing},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ALL {len(passed)} CHECKS PASS',flush=True)

    # Isolated deterministic fixture: validate cap, MAX, repeated 10-level hold and save reload.
    training=context.new_page()
    training.on('pageerror',lambda err:errors.append('training: '+str(err)))
    training.goto(URL,wait_until='load',timeout=60000)
    training.evaluate("""() => {
      const s=JSON.parse(localStorage.getItem('tapgacha_save_v3'));
      s.characters.c001={owned:true,level:1,cap:50,shards:5000};
      s.keys=3;s.points=12450;
      localStorage.setItem('tapgacha_save_v3',JSON.stringify(s));
    }""")
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
    training.screenshot(path=str(SHOTS/'character-trained-390.png'))
    check('training no runtime errors',not errors)
    training.close()

    browser.close()
