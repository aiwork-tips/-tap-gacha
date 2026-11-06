#!/usr/bin/env python3
"""Browser regression for the modular game on the served test branch."""
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
    page.wait_for_function("document.querySelector('#goTap .v117-plaque').naturalWidth > 0")
    check('RC11 awakening plaque and live label',page.locator('#goTap .v117-plaque').get_attribute('src').endswith('rc11-awakening.webp')
          and page.locator('#goTap .v117-copy strong').inner_text()=='覚醒核へ')
    check('RC12 awakening plaque is narrower, taller and centered',page.locator('#goTap').evaluate("""button => {
      const scene = button.offsetParent.getBoundingClientRect();
      const bounds = button.getBoundingClientRect();
      return Math.abs(bounds.width / scene.width - .56) < .003 &&
        Math.abs(bounds.height / scene.height - .121) < .003 &&
        Math.abs(bounds.left + bounds.width / 2 - (scene.left + scene.width / 2)) < 1;
    }"""))
    check('RC13 RANK divider cover stays clear of the gold rim',page.locator('.kit-rank').evaluate("""rank => {
      const art = rank.querySelector('.kit-hud-art');
      const scale = Math.min(art.clientWidth / art.naturalWidth, art.clientHeight / art.naturalHeight);
      const artTop = (art.clientHeight - art.naturalHeight * scale) / 2;
      const cover = getComputedStyle(rank, '::after');
      const top = parseFloat(cover.top);
      const bottom = top + parseFloat(cover.height);
      return cover.backgroundImage.includes('radial-gradient') && cover.boxShadow === 'none' &&
        top < artTop + 187 * scale && bottom > artTop + 187 * scale &&
        bottom < artTop + 240 * scale;
    }"""))
    # Verify the picture frames and live controls in the rendered layout.
    page.locator('[data-home-go="character"]').click(force=True)
    page.wait_for_function("""() => document.querySelector('#characterScreen .character-background').naturalWidth > 0""")
    check('RC09 temple art is visible behind the entire screen', page.evaluate("""() =>
      getComputedStyle(document.querySelector('#characterScreen .character-background')).opacity === '1'
    """))
    check('RC09 title is live text',page.locator('#characterScreen h2').inner_text()=='キャラ育成')
    check('detail and roster panels retain their independent frames',page.evaluate("""() => {
      const frames = [...document.querySelectorAll('#characterScreen .char-gilt')];
      return frames.length >= 9 && frames.every(frame => {
        const style = getComputedStyle(frame);
        return style.borderImageSource === 'none' && style.borderTopStyle === 'solid' &&
          parseFloat(style.borderTopWidth) > 0 && style.borderTopColor !== 'rgba(0, 0, 0, 0)';
      });
    }"""))
    picture_files=['rc12-compact.webp']*2+['rc12-stat.webp']*3+['rc11-quantity.webp']*2+[
        'rc11-max.webp','rc11-level-up.webp','rc11-cap-unlock.webp'
    ]
    check('RC12 each generated frame replaces the old border and background',page.locator('#characterScreen .char-art-frame').evaluate_all("""
      (frames, files) => frames.length === files.length && frames.every((frame, index) => {
        const shell = getComputedStyle(frame);
        const art = getComputedStyle(frame, '::before');
        return shell.borderTopWidth === '0px' && shell.borderImageSource === 'none' &&
          shell.boxShadow === 'none' && shell.backgroundImage === 'none' &&
          shell.backgroundColor === 'rgba(0, 0, 0, 0)' &&
          art.backgroundImage.includes(files[index]) && art.backgroundSize === '100% 100%';
      })
    """,picture_files))
    check('RC11 the quantity buttons have no surrounding box',page.locator('.char-level-quantity').evaluate("""group => {
      const css = getComputedStyle(group);
      return css.borderTopWidth === '0px' && css.backgroundImage === 'none' &&
        css.backgroundColor === 'rgba(0, 0, 0, 0)';
    }"""))
    catalog=page.locator('#characterGrid .char-tile').evaluate_all("""tiles =>
      Object.fromEntries(tiles.map(tile => [
        tile.dataset.characterId,
        {name:tile.getAttribute('aria-label'), rarity:tile.querySelector('em').textContent.length}
      ]))
    """)
    detail=page.locator('#characterDetail').bounding_box()
    portrait=page.locator('#selectedPortrait').bounding_box()
    check('RC09 portrait fills the left third',detail is not None and portrait is not None and .29<portrait['width']/detail['width']<.38)
    check('RC09 live stats remain readable',page.locator('#charTotalLevels').inner_text()=='0' and page.locator('#charTotalLevels').is_visible())
    page.locator('#charRosterFilter').select_option('owned')
    check('RC09 owned filter shows the empty roster message',page.locator('#characterGrid .char-tile').count()==0 and page.locator('#charRosterEmpty').is_visible())
    page.locator('#charRosterFilter').select_option('all')
    page.locator('#charBackHome').click(force=True)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-home-390.png'))
    before=state()
    page.locator('#goTap').click(force=True)
    check('tap navigation',page.locator('#tapScreen.active').count()==1)
    check('RC11 tap return label only shows the text',page.locator('#backHome text').text_content()=='ホームへ戻る')
    page.locator('#tapZone').click(force=True)
    after=state()
    check('tap PT saved',after['points']==before['points']+before['tapPower'])
    check('tap stats saved',after['stats']['taps']==before['stats']['taps']+1)
    check('tap chest progress advances',after.get('tapRewardProgress',{}).get('count',0)==before.get('tapRewardProgress',{}).get('count',0)+1)
    page.locator('#backHome').click(force=True)
    page.locator('[data-home-go="gacha"]').click(force=True)
    check('gacha navigation',page.locator('#gachaScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-gacha-390.png'))
    for pulls, width, height, guaranteed in ((100,393,654,1),(1000,320,568,10)):
        page.set_viewport_size({'width':width,'height':height})
        before=state()
        page.locator(f'.gacha-draw[data-pulls="{pulls}"]').click()
        after=state()
        check(f'{pulls} pulls cost {pulls} PT',after['points']==before['points']-pulls)
        check(f'{pulls} pulls counted',after['stats']['gachaPulls']==before['stats']['gachaPulls']+pulls)
        check(f'{pulls} pulls guarantee {guaranteed} rarest characters',after['stats']['star3Pulls']-before['stats']['star3Pulls']>=guaranteed)
        check(f'{pulls} result heading',page.locator('.summary-title h3').inner_text()==f'{pulls:,}連の結果')
        rows=page.locator('#gachaResult .summary-row').evaluate_all("""rows => rows.map(row => {
          const name = row.querySelector('.s-name');
          const shards = row.querySelector('.s-shards');
          return {
            id:row.dataset.characterId, name:name.textContent,
            rarity:row.querySelector('.s-rarity').textContent.length,
            count:Number(row.querySelector('.s-count b').textContent.replaceAll(',', '')),
            shards:shards ? Number(shards.textContent.split('+')[1].replaceAll(',', '')) : 0,
            isNew:Boolean(row.querySelector('.s-new')), rare:row.classList.contains('star3'),
            fits:name.clientWidth > 0 && name.scrollWidth <= name.clientWidth && name.scrollHeight <= name.clientHeight
          };
        })""")
        check(f'{pulls} full names and rarity are readable at {width}px',rows and all(
            row['fits'] and row['name']==catalog[row['id']]['name'] and row['rarity']==catalog[row['id']]['rarity']
            and row['rare']==(row['rarity']==3) for row in rows
        ))
        expected={}
        for cid, record in after['characters'].items():
            previous=before['characters'].get(cid,{})
            count=record.get('count',int(record.get('owned',False)))-previous.get('count',int(previous.get('owned',False)))
            if count>0:
                expected[cid]=(count,record.get('shards',0)-previous.get('shards',0),not previous.get('owned',False))
        check(f'{pulls} per-character counts, new pulls and shards match the save',len(rows)==len(expected) and {
            row['id']:(row['count'],row['shards'],row['isNew']) for row in rows
        }==expected)
        rarity_totals=[int(value.replace(',','')) for value in page.locator('.summary-rarity b').all_text_contents()]
        check(f'{pulls} rarity totals reconcile with the result list',sum(rarity_totals)==pulls and rarity_totals==[
            sum(row['count'] for row in rows if row['rarity']==rarity) for rarity in (1,2,3)
        ])
        page.screenshot(path=str(SHOTS/f'{ENGINE}-gacha-{pulls}-{width}.png'))
        check(f'{pulls} every result is reachable and draw buttons clear the nav',page.evaluate("""() => {
          const list = document.querySelector('.summary-list');
          const actions = document.querySelector('.gacha-actions').getBoundingClientRect();
          const nav = document.querySelector('.gacha-bottom-nav').getBoundingClientRect();
          const startsAtTop = list.scrollTop === 0;
          list.scrollTop = list.scrollHeight;
          return startsAtTop && list.clientHeight > 0 && list.scrollWidth <= list.clientWidth &&
            list.lastElementChild.getBoundingClientRect().bottom <= list.getBoundingClientRect().bottom + 1 &&
            actions.bottom <= nav.top;
        }"""))
    check('roster shards awarded',sum(int(c.get('shards',0)) for c in after['characters'].values())>0)
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#gachaBackHome').click(force=True)
    page.locator('[data-home-go="character"]').click(force=True)
    check('character navigation',page.locator('#characterScreen.active').count()==1)
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-390.png'))
    page.locator('#charRosterToggle').click(force=True)
    check('roster expanded with visible collapse label',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='true'
          and page.locator('.char-roster-action-text').inner_text()=='縮める')
    page.locator('#charRosterToggle').click(force=True)
    check('roster collapsed with visible expand label',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='false'
          and page.locator('.char-roster-action-text').inner_text()=='広げる')
    page.locator('#charRosterToggle').click()
    page.locator('#characterGrid [data-character-id="c001"]').click()
    check('RC13 choosing a card restores the expand label',page.locator('#charRosterToggle').get_attribute('aria-pressed')=='false'
          and page.locator('.char-roster-action-text').inner_text()=='広げる')
    check('15 character tiles',page.locator('#characterGrid [data-character-id]').count()==15)
    before=state()
    page.locator('#charRosterSort').select_option('rarity')
    check('RC09 rarity sort moves the highest rarity to the front',page.locator('#characterGrid .char-tile em').first.inner_text()=='★★★')
    page.locator('#charRosterSort').select_option('default')
    check('RC09 roster display controls preserve the save',state()==before)
    page.locator('#charBuyKey').click()
    after=state()
    check('RC09 character screen key button updates and saves PT and keys',after['points']==before['points']-5000 and after['keys']==before['keys']+1)
    check('RC11 the framed PT value updates after key purchase',page.locator('#charPT').inner_text()==f"{after['points']:,}")
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
    page.set_viewport_size({'width':393,'height':654})
    check('RC09 two full roster rows fit above the iPhone navigation',page.evaluate("""() => {
      const scroll = document.getElementById('charRosterScroll').getBoundingClientRect();
      const tile = document.querySelectorAll('#characterGrid .char-tile')[9].getBoundingClientRect();
      const nav = document.querySelector('#characterScreen .character-bottom-nav').getBoundingClientRect();
      return tile.bottom <= scroll.bottom && scroll.bottom <= nav.top;
    }"""))
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-393x654.png'))
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
      s.characters.c002={owned:true,level:30,cap:50,shards:14};
      s.characters.c003={owned:true,level:100,cap:100,shards:1351};
      s.keys=2;s.points=12450;
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
    check('RC11 the image-framed stats remain live after training',training.evaluate("""() => {
      const save = JSON.parse(localStorage.getItem('tapgacha_save_v3'));
      const owned = Object.values(save.characters).filter(character => character.owned);
      const levels = owned.reduce((sum, character) => sum + (character.level || 1), 0);
      return document.getElementById('charOwned').textContent === `${owned.length} / 15` &&
        document.getElementById('charTotalLevels').textContent === levels.toLocaleString('ja-JP') &&
        document.getElementById('charTapPower').textContent === save.tapPower.toLocaleString('ja-JP');
    }"""))
    before_max=tstate()
    training.locator('#charQuantityMax').click()
    check('RC12 selecting MAX does not change the save',tstate()==before_max)
    check('RC12 MAX is the only selected quantity',training.locator('.char-quantity-button[aria-pressed="true"]').count()==1
          and training.locator('#charQuantityMax').get_attribute('aria-pressed')=='true'
          and training.locator('#charQuantityMax').evaluate("button => button.classList.contains('is-selected')"))
    check('RC12 MAX previews levels and shard cost',training.locator('#charLevelUp .char-action-note').inner_text()=='×39 ・ 欠片 252')
    training.locator('#charLevelUp').click()
    after_max=tstate()
    check('MAX stops at level cap 50',after_max['characters']['c001']['level']==50 and training.locator('#charLevelUp').is_disabled())
    check('RC12 MAX charges only the previewed cost on level up',after_max['characters']['c001']['shards']==before_max['characters']['c001']['shards']-252
          and after_max['stats']['levelUps']==before_max['stats']['levelUps']+39)
    check('MAX does not auto unlock cap or consume keys',after_max['characters']['c001']['cap']==50 and after_max['keys']==before_max['keys'])
    check('RC09 cap badge appears at the current cap',training.locator('#charCapBadge').is_visible())
    keys_before=tstate()['keys']
    training.locator('#charLimitBreak').click(force=True)
    check('cap unlock reaches 100 and consumes one key',tstate()['characters']['c001']['cap']==100 and tstate()['keys']==keys_before-1)
    training.locator('#charQuantity10').click()
    box=training.locator('#charLevelUp').bounding_box()
    assert box is not None
    training.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
    training.mouse.down()
    try:
        training.wait_for_function("""() =>
          JSON.parse(localStorage.getItem('tapgacha_save_v3')).characters.c001.level > 60
        """, polling=100, timeout=3500)
    finally:
        training.mouse.up()
    check('holding 10-level mode repeatedly trains',tstate()['characters']['c001']['level']>60)
    check('training updates saved tap power',tstate()['tapPower']>=2)
    levels_before=tstate()['characters']['c001']['level']
    training.reload(wait_until='load')
    check('trained level survives reload',tstate()['characters']['c001']['level']==levels_before)
    training.locator('[data-home-go="character"]').click(force=True)
    training.locator('#characterGrid [data-character-id="c001"]').click(force=True)
    check('trained character detail visible after reload',training.locator('#characterScreen.active').count()==1 and 'Lv' in training.locator('#selectedLevel').inner_text())
    check('RC09 gauge, quantity buttons and actions occupy separate rows', training.evaluate("""() => {
      const detail = document.getElementById('characterDetail');
      const gaugeBottom = detail.querySelector('.char-shard-track').getBoundingClientRect().bottom;
      const actionsTop = detail.querySelector('.char-actions').getBoundingClientRect().top;
      const buttons = [...detail.querySelectorAll('.char-quantity-button')];
      return buttons.length === 3 && buttons.every(button => {
        const bounds = button.getBoundingClientRect();
        return bounds.height > 0 && bounds.top > gaugeBottom && bounds.bottom < actionsTop;
      });
    }"""))
    training.locator('#charFavoriteButton').click()
    check('RC09 portrait button saves the home favorite',tstate()['favoriteCharacterId']=='c001')
    training.screenshot(path=str(SHOTS/f'{ENGINE}-character-trained-390.png'))
    training.locator('#characterGrid [data-character-id="c002"]').click()
    before_max=tstate()
    training.locator('#charQuantityMax').click()
    check('RC12 MAX previews the affordable levels below cap',tstate()==before_max
          and training.locator('#charLevelUp .char-action-note').inner_text()=='×2 ・ 欠片 13')
    training.locator('#charLevelUp').click()
    trained=tstate()['characters']['c002']
    check('RC12 MAX stops when the remaining shards cannot buy another level',trained['level']==32 and trained['cap']==50
          and trained['shards']==1 and training.locator('#charLevelUp').is_disabled())
    training.locator('#characterGrid [data-character-id="c003"]').click()
    unlock_note=training.locator('#charLimitBreak .char-action-note')
    check('RC13 cap notice shows the exact key shortage',tstate()['keys']==1 and training.locator('#charLimitBreak').is_disabled()
          and unlock_note.inner_text()=='鍵 1 / 2（あと1個）')
    training.locator('#charBuyKey').click()
    check('RC13 buying the missing key refreshes the unlock action',tstate()['keys']==2 and training.locator('#charLimitBreak').is_enabled()
          and unlock_note.inner_text()=='（鍵 2個）')
    training.locator('#charLimitBreak').click()
    check('RC13 the newly enabled unlock action saves cap and key use',tstate()['characters']['c003']['cap']==150 and tstate()['keys']==0)
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
