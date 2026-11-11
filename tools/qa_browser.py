#!/usr/bin/env python3
"""Browser regression for the modular game on the served test branch."""
import os, json, sys, subprocess
from datetime import datetime, timezone
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
    if not ok:
        failed_page=globals().get('battle') if label.startswith('RC25') else globals().get('reward')
        if label.startswith(('RC27', 'RC29', 'RC30', 'RC31')):
            failed_page=globals().get('stage_page')
        if failed_page and not failed_page.is_closed():
            failed_page.screenshot(path=str(SHOTS/f'{ENGINE}-failure.png'))
        raise AssertionError(f'{label} FAILED; JS errors: {errors}')
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
    page.locator('#loginGiftEntry').click()
    check('RC22 login gift test is isolated from the normal game',
          page.locator('#loginGiftDialog').is_hidden() and page.locator('#loginGiftBadge').is_hidden()
          and 'loginGift' not in state())
    page.locator('.kit-transfer').click()
    check('RC23 formation preview remains isolated from the normal game',
          page.locator('#homeScreen.active').count()==1 and 'partyIds' not in state())
    check('nine screens with the battle stage',page.locator('section.screen').count()==9)
    def nav_geometry():
        return page.locator('.screen.active > .kit-shared-nav').evaluate('''nav => {
          const rect = el => {
            const {x, y, width, height} = el.getBoundingClientRect();
            return [x, y, width, height];
          };
          return [rect(nav), ...Array.from(nav.querySelectorAll('button'), button => {
            const image = button.querySelector('img');
            return [rect(button), rect(image), image.getAttribute('src')];
          })];
        }''')
    for width,height in ((320,568),(393,654),(430,844)):
        page.set_viewport_size({'width':width,'height':height})
        baseline=nav_geometry()
        aligned=True
        for name,screen in (('キャラ','character'),('ガチャ','gacha'),('図鑑','dex')):
            page.locator(f'.screen.active > .kit-shared-nav [aria-label="{name}"]').click()
            aligned=aligned and page.locator(f'#{screen}Screen.active').count()==1 and nav_geometry()==baseline
        aligned=aligned and page.locator('#dexBack').inner_text()=='ホーム'
        page.locator('#dexBack').click()
        for screen in ('shop','quest'):
            page.locator(f'[data-home-go="{screen}"]').click()
            aligned=aligned and page.locator(f'#{screen}Screen.active').count()==1 and nav_geometry()==baseline
            page.locator(f'#{screen}BackHome').click()
        check(f'RC17 shared menus align on all six screens at {width}px',aligned)
    page.set_viewport_size({'width':390,'height':844})
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
    picture_files=['rc12-compact.webp']*2+['rc12-stat.webp']*3+['rc11-level-up.webp']*2+['rc11-cap-unlock.webp']
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
    check('RC18 direct training has no surrounding selection box',page.locator('.char-actions').evaluate("""group => {
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
    page.set_viewport_size({'width':393,'height':654})
    dex_before=state()
    page.locator('.kit-archive').click()
    dex_cards=page.locator('#dexGrid .dex-card')
    check('RC14 home archive opens all 15 entries',page.locator('#dexScreen.active').count()==1
          and dex_cards.count()==15 and page.locator('#dexOwnedCount').inner_text()=='0 / 15')
    page.locator('[data-dex-filter="owned"]').click()
    check('RC14 owned filter has a clear empty state',dex_cards.count()==0 and page.locator('#dexEmpty').is_visible())
    dex_unowned_filter=page.locator('[data-dex-filter="unowned"]')
    dex_unowned_filter.click()
    dex_scroll=page.locator('#dexList')
    scroll_pos=dex_scroll.evaluate("""list => {
      list.scrollTop=list.scrollHeight;
      return list.scrollTop;
    }""")
    dex_cards.last.click()
    check('RC14 unowned records show name and rarity without stats or lore',page.locator('#dexName').inner_text()=='白銀の聖騎士'
          and page.locator('#dexRarity').inner_text()=='★★★' and page.locator('#dexUnowned').is_visible()
          and not page.locator('#dexElement').is_visible()
          and page.locator('#dexLore').inner_text()=='このキャラを召喚すると、記録が解放されます。')
    page.locator('#dexBack').click()
    check('RC14 returning from a record restores filter and scroll',dex_unowned_filter.get_attribute('aria-pressed')=='true'
          and dex_cards.count()==15 and scroll_pos>0 and abs(dex_scroll.evaluate('list => list.scrollTop')-scroll_pos)<=1)
    page.locator('[data-dex-filter="all"]').click()
    page.locator('#dexBack').click()
    page.locator('#homeScreen [data-nav="図鑑"]').click()
    check('RC14 shared book tab opens the archive',page.locator('#dexScreen.active [aria-current="page"]').get_attribute('aria-label')=='図鑑')
    page.wait_for_function("document.querySelector('#dexGrid img').naturalWidth > 0")
    check('RC16 the archive shows the active tab line and archive swordsman art',page.locator('[data-dex-filter="all"]').evaluate(
        "tab => tab.getAttribute('aria-pressed') === 'true' && getComputedStyle(tab, '::after').height === '2px'")
          and page.locator('[data-dex-id="c006"] img').get_attribute('src')=='assets/dex-swordsman.webp')
    page.screenshot(path=str(SHOTS/f'{ENGINE}-archive-393.png'))
    page.locator('#dexBack').click()
    check('RC14 browsing the archive preserves the save',state()==dex_before)
    page.set_viewport_size({'width':390,'height':844})
    before=state()
    page.locator('#goTap').click(force=True)
    check('tap navigation',page.locator('#tapScreen.active').count()==1)
    check('RC11 tap return label only shows the text',page.locator('#backHome text').text_content()=='ホームへ戻る')
    tap_gap=page.locator('#powerBox').evaluate("""value => new Promise(resolve =>
      requestAnimationFrame(() => {
        const label = document.querySelector('.v15-top-label').getBoundingClientRect();
        resolve(value.getBoundingClientRect().top - label.bottom);
      })
    )""")
    page.screenshot(path=str(SHOTS/f'{ENGINE}-tap-390.png'))
    check(f'RC14 TapPower label and value are separated ({tap_gap:.2f}px)',tap_gap>=-0.7)
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
    check('RC19 newly summoned characters start with a level 100 cap',after['characters'] and all(
        r.get('cap')==100 and r.get('trainingCapStep')==100 for r in after['characters'].values() if r['owned']
    ))
    page.locator('[data-gacha-nav="図鑑"]').click()
    acquired={cid:record for cid,record in after['characters'].items() if record.get('owned')}
    page.locator('[data-dex-filter="owned"]').click()
    check('RC14 new summons appear in the archive at 320px',page.locator('#dexScreen.active').count()==1
          and page.locator('#dexOwnedCount').inner_text()==f'{len(acquired)} / 15' and dex_cards.count()==len(acquired)
          and dex_scroll.evaluate('list => list.scrollWidth <= list.clientWidth'))
    cid=next(iter(acquired))
    page.locator(f'#dexGrid [data-dex-id="{cid}"]').click()
    check('RC15 acquired records show art, name and story without training stats',page.locator('#dexName').inner_text()==catalog[cid]['name']
          and page.locator('#dexRarity').inner_text()=='★'*catalog[cid]['rarity']
          and page.locator('#dexPortrait').get_attribute('src').startswith('assets/')
          and page.locator('.dex-profile').evaluate(
              "profile => getComputedStyle(profile, '::after').borderImageSource.includes('dex-gold-frame.webp')")
          and page.locator('#dexLevel, #dexShards').count()==0 and 'Lv' not in dex_cards.first.inner_text()
          and page.locator('#dexLore').inner_text()!='このキャラを召喚すると、記録が解放されます。' and state()==after)
    page.wait_for_function("document.querySelector('#dexPortrait').naturalWidth > 0")
    page.screenshot(path=str(SHOTS/f'{ENGINE}-archive-record-320.png'))
    page.locator('#dexScreen [data-nav="ガチャ"]').click()
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
    check('RC20 normal game cannot award simulated ad points',
          page.locator('#shopRewardWatch').is_disabled()
          and page.locator('#shopRewardPreviewLabel').is_hidden())
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
    for width,height in ((320,568),(390,636),(430,735),(393,654)):
        page.set_viewport_size({'width':width,'height':height})
        check(f'RC18 ten full roster cards fit in {width}x{height} without expanding',page.evaluate("""() => {
          const roster = document.getElementById('charRosterScroll');
          roster.scrollTop = 0;
          const scroll = roster.getBoundingClientRect();
          const tiles = Array.from(roster.querySelectorAll('.char-tile')).slice(0,10);
          const nav = document.querySelector('#characterScreen .character-bottom-nav').getBoundingClientRect();
          return tiles.length === 10 && tiles.every(tile => {
            const rect = tile.getBoundingClientRect();
            return rect.top >= scroll.top && rect.bottom <= scroll.bottom;
          }) && scroll.bottom <= nav.top && document.getElementById('charRosterToggle').getAttribute('aria-pressed') === 'false';
        }"""))
    page.screenshot(path=str(SHOTS/f'{ENGINE}-character-393x654.png'))
    check('all game asset responses are successful',not resource_failures)
    check('no JavaScript runtime errors',not errors)

    # Isolated deterministic fixture: validate direct training, status, caps and reload.
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
      s.characters.c003={owned:true,level:100,cap:100,shards:1351,keysUsed:1};
      s.characters.c004={owned:true,level:151,cap:151,shards:0};
      s.characters.c005={owned:true,level:150,cap:150,shards:1536,keysUsed:3};
      s.characters.c006={owned:true,level:1,cap:50,shards:2};
      s.characters.c007={owned:false,shards:0};
      s.characters.c008={owned:true,level:300,cap:300,shards:0,keysUsed:3,trainingCapStep:100};
      s.keys=2;s.points=12450;
      localStorage.setItem('tapgacha_save_v3',JSON.stringify(s));
      sessionStorage.setItem('__qa_training_fixture_applied','1');
    })()""")
    training.reload(wait_until='load')
    training.locator('[data-home-go="character"]').click(force=True)
    training.locator('#characterGrid [data-character-id="c001"]').click(force=True)
    tstate=lambda:training.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    tile_status=lambda cid:training.locator(f'#characterGrid [data-character-id="{cid}"] small')
    migrated=tstate()
    check('RC19 migration preserves prior unlock stages, levels, shards and keys',
          migrated['characters']['c001']['cap']==100
          and migrated['characters']['c003']==dict(owned=True,level=100,cap=200,shards=1351,keysUsed=1,trainingCapStep=100)
          and migrated['characters']['c005']==dict(owned=True,level=150,cap=300,shards=1536,keysUsed=3,trainingCapStep=100)
          and migrated['points']==12450 and migrated['keys']==2)
    check('RC19 cards show migrated training states and visible marks',
          tile_status('c001').get_attribute('data-training-state')=='ready'
          and '↑' in tile_status('c001').inner_text()
          and tile_status('c003').get_attribute('data-training-state')=='ready'
          and tile_status('c004').get_attribute('data-training-state')=='max'
          and tile_status('c004').inner_text()=='MAX'
          and tile_status('c005').get_attribute('data-training-state')=='ready'
          and tile_status('c006').get_attribute('data-training-state')=='short'
          and tile_status('c007').inner_text()=='未所持')
    one=training.locator('#charLevelUp')
    bulk=training.locator('#charLevelUpMax')
    start=tstate()
    check('RC18 the direct single action shows its price before tapping',one.locator('.char-button-ink').inner_text()=='＋1'
          and one.locator('.char-action-note').inner_text()=='欠片 3')
    one.click()
    check('RC18 one tap trains one level and saves the exact price',tstate()['characters']['c001']['level']==2
          and tstate()['characters']['c001']['shards']==4997 and tstate()['stats']['levelUps']==start['stats'].get('levelUps',0)+1)
    trained_save=tstate()
    training.locator('[data-character-nav="図鑑"]').click()
    training.locator('#dexGrid [data-dex-id="c001"]').click()
    check('RC15 archive uses the illustrated lore and preserves the trained character',training.locator('#dexLore').text_content().startswith('金の輪と白い翼を持つ天使見習い。')
          and training.locator('#dexStoryTitle').inner_text()=='書庫の記録' and tstate()==trained_save)
    training.locator('#dexScreen [data-nav="キャラ"]').click()
    check('RC11 the image-framed stats remain live after training',training.evaluate("""() => {
      const save = JSON.parse(localStorage.getItem('tapgacha_save_v3'));
      const owned = Object.values(save.characters).filter(character => character.owned);
      const levels = owned.reduce((sum, character) => sum + (character.level || 1), 0);
      return document.getElementById('charOwned').textContent === `${owned.length} / 15` &&
        document.getElementById('charTotalLevels').textContent === levels.toLocaleString('ja-JP') &&
        document.getElementById('charTapPower').textContent === save.tapPower.toLocaleString('ja-JP');
    }"""))
    before_max=tstate()
    check('RC18 bulk button shows levels and exact shard cost before tapping',
          bulk.locator('.char-button-ink').inner_text()=='まとめて＋98'
          and bulk.locator('.char-action-note').inner_text()=='欠片 815')
    bulk.click()
    after_max=tstate()
    check('RC18 one tap of bulk stops at the current cap and updates the card',
          after_max['characters']['c001']['level']==100 and one.is_disabled() and bulk.is_disabled()
          and tile_status('c001').get_attribute('data-training-state')=='capped'
          and tile_status('c001').locator('svg').count()==1)
    check('RC18 bulk charges the previewed cost and counts the earned levels',
          after_max['characters']['c001']['shards']==before_max['characters']['c001']['shards']-815
          and after_max['stats']['levelUps']==before_max['stats']['levelUps']+98)
    check('RC19 training reaches level 100 without using keys',after_max['characters']['c001']['cap']==100 and after_max['keys']==before_max['keys'])
    check('RC09 cap badge appears at the current cap',training.locator('#charCapBadge').is_visible())
    keys_before=tstate()['keys']
    training.locator('#charLimitBreak').click(force=True)
    check('RC19 cap unlock reaches 200 and consumes one key',
          tstate()['characters']['c001']['cap']==200 and tstate()['keys']==keys_before-1
          and tstate()['characters']['c001']['keysUsed']==1)
    check('RC18 unlocking makes the card immediately trainable',tile_status('c001').get_attribute('data-training-state')=='ready')
    box=one.bounding_box()
    assert box is not None
    training.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
    training.mouse.down()
    try:
        training.wait_for_function("""() =>
          JSON.parse(localStorage.getItem('tapgacha_save_v3')).characters.c001.level >= 103
        """, polling=100, timeout=3500)
    finally:
        training.mouse.up()
    check('RC18 holding the +1 button repeatedly trains',tstate()['characters']['c001']['level']>=103)
    check('training updates saved tap power',tstate()['tapPower']>=2)
    levels_before=tstate()['characters']['c001']['level']
    training.reload(wait_until='load')
    check('RC19 trained level survives reload without migrating the caps again',
          tstate()['characters']['c001']['level']==levels_before and tstate()['characters']['c001']['cap']==200
          and tstate()['characters']['c005']['cap']==300)
    training.locator('[data-home-go="character"]').click(force=True)
    training.locator('#characterGrid [data-character-id="c001"]').click(force=True)
    check('trained character detail visible after reload',training.locator('#characterScreen.active').count()==1 and 'Lv' in training.locator('#selectedLevel').inner_text())
    check('RC18 training buttons fit below the gauge and unlock sits with the keys', training.evaluate("""() => {
      const detail = document.getElementById('characterDetail');
      const gaugeBottom = detail.querySelector('.char-shard-track').getBoundingClientRect().bottom;
      const detailBottom = detail.getBoundingClientRect().bottom;
      const buttons = [...detail.querySelectorAll('.char-actions button')];
      const keys = document.getElementById('charLimitBreak').closest('.char-buy');
      return keys && buttons.length === 2 && buttons.every(button => {
        const bounds = button.getBoundingClientRect();
        return bounds.height >= 36 && bounds.top > gaugeBottom && bounds.bottom <= detailBottom;
      });
    }"""))
    training.locator('#charFavoriteButton').click()
    check('RC09 portrait button saves the home favorite',tstate()['favoriteCharacterId']=='c001')
    training.screenshot(path=str(SHOTS/f'{ENGINE}-character-trained-390.png'))
    training.locator('#characterGrid [data-character-id="c002"]').click()
    before_max=tstate()
    check('RC18 bulk previews the affordable levels across a cost tier',tstate()==before_max
          and bulk.locator('.char-button-ink').inner_text()=='まとめて＋2'
          and bulk.locator('.char-action-note').inner_text()=='欠片 13')
    bulk.click()
    trained=tstate()['characters']['c002']
    check('RC18 bulk stops at shard shortage and updates the card',trained['level']==32 and trained['cap']==100
          and trained['shards']==1 and one.is_disabled() and bulk.is_disabled()
          and tile_status('c002').get_attribute('data-training-state')=='short')
    training.locator('#characterGrid [data-character-id="c005"]').click()
    check('RC19 the migrated level 150 character previews 128 levels for 1536 shards',
          training.locator('#selectedLevel').inner_text()=='Lv 150 / 300'
          and bulk.locator('.char-button-ink').inner_text()=='まとめて＋128'
          and bulk.locator('.char-action-note').inner_text()=='欠片 1,536')
    training.locator('#characterGrid [data-character-id="c003"]').click()
    bulk.click()
    check('RC19 a previously unlocked character can train to its migrated cap',
          tstate()['characters']['c003']['level']==200 and tstate()['characters']['c003']['shards']==151)
    unlock_note=training.locator('#charLimitBreak .char-action-note')
    check('RC13 cap notice shows the exact key shortage',tstate()['keys']==1 and training.locator('#charLimitBreak').is_disabled()
          and unlock_note.inner_text()=='鍵 1 / 2（あと1個）')
    training.locator('#charBuyKey').click()
    check('RC13 buying the missing key refreshes the unlock action',tstate()['keys']==2 and training.locator('#charLimitBreak').is_enabled()
          and unlock_note.inner_text()=='（鍵 2個）')
    before_unlock=tstate()
    training.evaluate("""() => {
      const setItem=Storage.prototype.setItem;
      Storage.prototype.setItem=function(key,value){
        if(this===localStorage && key==='tapgacha_save_v3'){
          Storage.prototype.setItem=setItem;
          throw new Error('Simulated storage write failure');
        }
        return setItem.call(this,key,value);
      };
    }""")
    training.locator('#charLimitBreak').click()
    check('RC19 a failed unlock rolls back the key debit and cap',tstate()==before_unlock
          and training.locator('#charKeys').inner_text()=='2'
          and training.locator('#selectedLevel').inner_text()=='Lv 200 / 200'
          and training.locator('#charLimitBreak').is_enabled())
    training.locator('#charLimitBreak').click()
    check('RC19 the second unlock reaches 300 and consumes exactly two keys',
          tstate()['characters']['c003']['cap']==300 and tstate()['characters']['c003']['keysUsed']==3
          and tstate()['keys']==0)
    training.locator('#characterGrid [data-character-id="c008"]').click()
    check('RC19 the level 300 cap still offers another unlock for three keys',
          training.locator('#selectedLevel').inner_text()=='Lv 300 / 300'
          and tile_status('c008').get_attribute('data-training-state')=='capped'
          and unlock_note.inner_text()=='鍵 0 / 3（あと3個）')
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
      localStorage.setItem('tapgacha_collection',JSON.stringify({
        c01:{owned:true,level:2,shards:15},
        c02:{owned:true,level:150,cap:150,shards:100,keysUsed:3}
      }));
      localStorage.setItem('gV2',JSON.stringify({pts:9999}));
      sessionStorage.setItem('__qa_legacy_seeded','1');
    })()""")
    old_page=old.new_page()
    old_page.on('pageerror',lambda err:errors.append('legacy: '+str(err)))
    old_page.goto(URL,wait_until='load')
    imported=old_page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3'))")
    check('legacy points preserve current-key priority',imported['points']==777)
    check('legacy character ID normalizes without losing levels',imported['characters']['c001']['level']==2 and imported['characters']['c001']['shards']==15)
    check('RC19 imported legacy caps use the new scale including missing cap fields',
          imported['characters']['c001']['cap']==100 and imported['characters']['c002']['cap']==300)
    old_page.reload(wait_until='load')
    check('legacy migration remains stable after reload',old_page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3')).points")==777)
    old_page.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_recover_mirror')) return;
      sessionStorage.setItem('__qa_recover_mirror','1');
      localStorage.removeItem('tapgacha_save_v3');
    })()""")
    old_page.reload(wait_until='load')
    check('RC19 fallback from the mirrored collection does not double migrated caps',
          old_page.evaluate("JSON.parse(localStorage.getItem('tapgacha_save_v3')).characters")==imported['characters'])
    old.close()
    preview = browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    preview.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_reward_seeded'))return;
      localStorage.setItem('tapgacha_save_v3',JSON.stringify({
        schemaVersion:3,points:4100,tapPower:41,keys:1,
        characters:Object.fromEntries(Array.from({length:10},(_,index)=>[
          'c'+String(index+1).padStart(3,'0'),
          {owned:true,level:100,cap:100,shards:12,trainingCapStep:100}
        ])),
        ad:{remaining:3,lastResetDate:'2026-11-07'}
      }));
      localStorage.setItem('tapgacha_pt','4100');
      localStorage.setItem('tapgacha_power','41');
      localStorage.setItem('tapgacha_collection','{}');
      sessionStorage.setItem('__qa_reward_seeded','1');
    })()""")
    reward = preview.new_page()
    reward.on('pageerror',lambda err:errors.append('reward: '+str(err)))
    reward.clock.install(time=datetime(2026,11,7,13,0,tzinfo=timezone.utc))
    reward.goto(URL + '?reward-preview=1',wait_until='load')
    live_before = reward.evaluate("Object.entries(localStorage).sort()")
    reward.locator('[data-home-go="shop"]').click()
    button = reward.locator('#shopRewardWatch')
    remaining = reward.locator('#shopRewardRemaining')
    wallet = reward.locator('#shopPT')
    check('RC20 reward preview uses current save and TapPower',button.is_enabled()
          and remaining.inner_text()=='3' and wallet.inner_text()=='4,100'
          and reward.locator('#shopRewardAmount').inner_text()=='+2,050')
    check('RC21 displayed reward is identified as a per-view amount',
          reward.locator('.shop-reward-amount').inner_text()=='1回 +2,050 PT')
    for width,height in ((320,568),(393,654),(390,844),(430,932)):
        reward.set_viewport_size({'width':width,'height':height})
        check(f'RC20 reward artwork and readable controls fit at {width}x{height}',reward.evaluate(r"""async () => {
          const panel = document.querySelector('.shop-reward');
          const button = document.querySelector('#shopRewardWatch');
          const chrome = panel.getBoundingClientRect();
          const buttonBox = button.getBoundingClientRect();
          const title = document.querySelector('#shopRewardTitle').getBoundingClientRect();
          const amount = document.querySelector('.shop-reward-amount').getBoundingClientRect();
          const filters = document.querySelector('.shop-filters').getBoundingClientRect();
          const scroll = document.querySelector('#shopProductScroll');
          const panelStyle = getComputedStyle(panel);
          const buttonStyle = getComputedStyle(button,'::before');
          const images = await Promise.all([panelStyle,buttonStyle].map(async style => {
            const path = style.backgroundImage.match(/^url\(["']?(.+?)["']?\)$/)?.[1];
            if(!path)return false;
            const art = new Image();
            art.src=path;
            await art.decode().catch(()=>{});
            return art.naturalWidth>0;
          }));
          return images.every(Boolean) && panelStyle.borderTopWidth==='0px'
            && getComputedStyle(button).borderTopWidth==='0px'
            && chrome.left>=0 && chrome.right<=innerWidth && chrome.bottom<=filters.top
            && title.right<=amount.left && buttonBox.height>=44 && buttonBox.bottom<chrome.bottom
            && scroll.clientHeight>=120 && scroll.scrollHeight>scroll.clientHeight;
        }"""))
        reward.screenshot(path=str(SHOTS/f'{ENGINE}-shop-reward-{width}x{height}.png'))
    def rstate():
        return reward.evaluate("JSON.parse(sessionStorage.getItem('tapgacha_reward_rc20_preview'))")
    reward.evaluate("""() => {
      const setItem=Storage.prototype.setItem;
      Storage.prototype.setItem=function(key,value){
        if(this===sessionStorage && key==='tapgacha_reward_rc20_preview'){
          Storage.prototype.setItem=setItem;
          throw new Error('Simulated preview save failure');
        }
        return setItem.call(this,key,value);
      };
    }""")
    button.click()
    check('RC20 failed preview write rolls back PT and the daily counter',
          rstate()['points']==4100 and remaining.inner_text()=='3' and wallet.inner_text()=='4,100')
    for count,pt in ((2,6150),(1,8200),(0,10250)):
        button.click()
        check(f'RC20 completed preview awards 2,050 PT with {count} uses left',
              rstate()['points']==pt and rstate()['ad']['remaining']==count
              and remaining.inner_text()==str(count) and wallet.inner_text()==f'{pt:,}')
    check('RC20 exhausted reward button is disabled',button.is_disabled())
    reward.reload(wait_until='load')
    reward.locator('[data-home-go="shop"]').click()
    check('RC20 exhausted counter persists across reload',button.is_disabled() and remaining.inner_text()=='0')
    exhausted = rstate()
    reward.clock.pause_at(datetime(2026,11,7,14,59,59,999000,tzinfo=timezone.utc))
    check('RC21 exhausted counter stays disabled until JST midnight',
          button.is_disabled() and remaining.inner_text()=='0')
    reward.clock.run_for(1)
    check('RC21 open shop recovers automatically at JST midnight',
          reward.locator('#shopScreen.active').count()==1 and button.is_enabled()
          and remaining.inner_text()=='3' and rstate()==exhausted)
    reward.clock.resume()
    button.click()
    check('RC20 next day awards once and records the reset date',rstate()['points']==12300
          and rstate()['ad']['lastResetDate']=='2026-11-08' and remaining.inner_text()=='2')
    reward.locator('#shopBackHome').click()
    entry = reward.locator('#loginGiftEntry')
    gift = reward.locator('#loginGiftDialog')
    claim = reward.locator('#loginGiftClaim')
    close = reward.locator('#loginGiftClose')
    gift_count = reward.locator('#loginGiftCount')
    gift_amount = reward.locator('#loginGiftAmount')
    check('RC22 home shows a claim badge on an unclaimed day',reward.locator('#loginGiftBadge').is_visible())
    entry.click()
    check('RC22 gift entry opens a modal with the first reward and the seven-step calendar',
          gift.is_visible() and claim.is_enabled() and gift_amount.inner_text()=='100 PT'
          and gift.locator('#loginGiftCalendar li').count()==7 and gift_count.inner_text()=='0')
    for width,height in ((320,568),(390,844),(393,654),(430,932)):
        reward.set_viewport_size({'width':width,'height':height})
        check(f'RC22 gift art and interactive controls fit at {width}x{height}',reward.evaluate(r"""async () => {
          const gift = document.querySelector('#loginGiftDialog');
          const titleRange = document.createRange();
          titleRange.selectNodeContents(document.querySelector('#loginGiftTitle'));
          const title = titleRange.getBoundingClientRect();
          const close = document.querySelector('#loginGiftClose').getBoundingClientRect();
          const claim = document.querySelector('#loginGiftClaim').getBoundingClientRect();
          const foot = document.querySelector('#loginGiftRenewal').getBoundingClientRect();
          const milestone = document.querySelector('.login-gift-milestone');
          const bounds = gift.getBoundingClientRect();
          const artworks = await Promise.all([gift, milestone, document.querySelector('#loginGiftClaim')].map(async el => {
            const src = getComputedStyle(el).backgroundImage.match(/^url\(["']?(.+?)["']?\)$/)?.[1];
            if(!src)return false;
            const art = new Image();
            art.src=src;
            await art.decode().catch(()=>{});
            return art.naturalWidth>0;
          }));
          return gift.matches(':modal') && artworks.every(Boolean)
            && bounds.left>=0 && bounds.right<=innerWidth && bounds.top>=0 && bounds.bottom<=innerHeight
            && gift.scrollHeight<=gift.clientHeight+1 && gift.scrollWidth<=gift.clientWidth+1
            && title.right<=close.left && title.top-bounds.top>=bounds.height*.15
            && claim.height>=44 && foot.bottom<bounds.bottom && close.height>=44;
        }"""))
        if width in (320,390):
            reward.screenshot(path=str(SHOTS/f'{ENGINE}-login-gift-{width}x{height}.png'))
    before_gift = rstate()
    reward.evaluate("""() => {
      const setItem=Storage.prototype.setItem;
      Storage.prototype.setItem=function(key,value){
        if(this===sessionStorage && key==='tapgacha_reward_rc20_preview'){
          Storage.prototype.setItem=setItem;
          throw new Error('Simulated gift save failure');
        }
        return setItem.call(this,key,value);
      };
    }""")
    claim.click()
    check('RC22 failed gift write rolls back PT, key balance and receipt',
          rstate()==before_gift and gift_count.inner_text()=='0' and claim.is_enabled()
          and reward.locator('#loginGiftChestClosed').is_visible()
          and reward.locator('#loginGiftMessage').inner_text()=='保存できませんでした')
    claim.click()
    check('RC22 first claim opens the chest and updates the home PT by exactly 100',
          rstate()['points']==before_gift['points']+100 and rstate()['keys']==before_gift['keys']
          and rstate()['loginGift']=={'claims':1,'lastClaimDate':'2026-11-08'}
          and claim.is_disabled() and gift_count.inner_text()=='1'
          and reward.locator('#loginGiftChestOpen').is_visible()
          and reward.locator('#homePT').inner_text()==f"{before_gift['points']+100:,}")
    reward.locator('#loginGiftClaim').dispatch_event('click')
    check('RC22 repeated claim on the same day cannot change the saved balance',
          rstate()['points']==before_gift['points']+100 and rstate()['loginGift']['claims']==1)
    close.click()
    check('RC22 close returns to the home screen and removes the claim badge',
          gift.is_hidden() and reward.locator('#homeScreen.active').count()==1
          and reward.locator('#loginGiftBadge').is_hidden())
    reward.reload(wait_until='load')
    entry.click()
    check('RC22 claimed state survives reload and reopening the gift modal',
          claim.is_disabled() and gift_count.inner_text()=='1'
          and reward.locator('#loginGiftChestOpen').is_visible())
    reward.clock.pause_at(datetime(2026,11,8,14,59,59,999000,tzinfo=timezone.utc))
    check('RC22 open gift stays claimed until JST midnight',claim.is_disabled())
    reward.clock.run_for(1)
    check('RC22 open gift advances automatically to the next reward at JST midnight',
          gift.is_visible() and claim.is_enabled() and gift_amount.inner_text()=='150 PT'
          and gift_count.inner_text()=='1' and rstate()['loginGift']['claims']==1)
    reward.clock.resume()
    reward.clock.fast_forward(3*86_400_000)
    claim.click()
    check('RC22 skipped days preserve gift progress',
          rstate()['loginGift']=={'claims':2,'lastClaimDate':'2026-11-12'}
          and rstate()['points']==before_gift['points']+250)
    for amount,step in ((200,3),(250,4),(300,5),(500,6)):
        reward.clock.fast_forward(86_400_000)
        previous = rstate()
        assert gift_amount.inner_text()==f'{amount} PT'
        claim.click()
        check(f'RC22 gift {step} adds exactly {amount} PT',
              rstate()['points']==previous['points']+amount and rstate()['loginGift']['claims']==step)
    reward.clock.fast_forward(86_400_000)
    reward.set_viewport_size({'width':320,'height':568})
    check('RC22 seventh gift displays a highlighted key milestone and stays fully visible',
          gift_amount.inner_text()=='上限解放の鍵 ×1'
          and gift.locator('.login-gift-milestone').get_attribute('aria-current')=='step'
          and gift.evaluate('el => el.scrollHeight <= el.clientHeight+1'))
    reward.screenshot(path=str(SHOTS/f'{ENGINE}-login-gift-key-320.png'))
    claim.click()
    check('RC22 seventh gift adds exactly one key and completes the cycle',
          rstate()['keys']==before_gift['keys']+1 and rstate()['points']==before_gift['points']+1500
          and rstate()['loginGift']['claims']==7 and gift_count.inner_text()=='7' and claim.is_disabled()
          and reward.locator('#homeKeys').inner_text()==str(before_gift['keys']+1))
    reward.clock.fast_forward(86_400_000)
    check('RC22 next cycle starts from the first gift after the seventh day',
          claim.is_enabled() and gift_count.inner_text()=='0' and gift_amount.inner_text()=='100 PT')
    claim.click()
    check('RC22 next cycle saves the first receipt without duplicating the key',
          rstate()['loginGift']['claims']==1 and rstate()['keys']==before_gift['keys']+1
          and rstate()['points']==before_gift['points']+1600)
    check('RC22 preview gifts leave all live save keys byte-for-byte unchanged',
          reward.evaluate("Object.entries(localStorage).sort()")==live_before)
    reward.locator('#loginGiftClose').click()
    reward.locator('.kit-transfer').click()
    pids=lambda:reward.locator('#partySlots [data-party-slot]').evaluate_all("els => els.map(el=>el.querySelector('.party-slot-name').textContent)")
    draft_before=pids()
    reward.screenshot(path=str(SHOTS/f'{ENGINE}-party-initial.png'))
    check('RC23 transfer opens three owned characters as an uncommitted draft',
          reward.locator('#partyScreen.active').count()==1
          and draft_before==['白翼のアルム','鉄骸兵','冥牙クロウル'] and 'partyIds' not in rstate())
    candidates=reward.locator('#partyRoster .party-candidate')
    check('RC23 every formed character is natively disabled and clearly labelled',
          candidates.count()==10 and reward.locator('#partyRoster .party-candidate:disabled').count()==3
          and reward.locator('[data-party-character="c001"]').is_disabled()
          and reward.locator('[data-party-character="c001"] .party-candidate-state').inner_text()=='編成中 1')
    reward.locator('[data-party-character="c001"]').evaluate("el=>{el.click();el.dispatchEvent(new MouseEvent('click',{bubbles:true}));}")
    check('RC23 direct and synthetic clicks cannot reselect a formed character',pids()==draft_before and 'partyIds' not in rstate())
    reward.locator('[data-party-slot="1"]').click()
    check('RC24 the replacement target has one explicit active badge',
          reward.locator('#partySlots [aria-pressed="true"]').count()==1
          and reward.locator('[data-party-slot="1"] .party-slot-marker').inner_text()=='2枠・入替中'
          and '2枠目を選択中' in reward.locator('#partyHint').inner_text())
    reward.locator('[data-party-character="c004"]').click()
    check('RC23 replacing a slot immediately disables the new member and releases the old one',
          pids()==['白翼のアルム','夜叉','冥牙クロウル']
          and reward.locator('[data-party-character="c004"]').is_disabled()
          and reward.locator('[data-party-character="c002"]').is_enabled()
          and 'partyIds' not in rstate())
    reward.locator('#partyBackHome').click()
    reward.locator('.kit-transfer').click()
    check('RC23 leaving without confirmation discards the draft',pids()==draft_before and 'partyIds' not in rstate())
    reward.locator('[data-party-slot="2"]').click()
    reward.locator('[data-party-character="c004"]').click()
    previous=rstate()
    roster_before_feedback=reward.locator('#partyRosterScroll').bounding_box()
    reward.locator('#partyConfirm').click()
    saved=rstate()
    check('RC23 confirming saves three unique owned IDs without changing resources',
          saved.get('partyIds')==['c001','c002','c004']
          and {k:v for k,v in saved.items() if k!='partyIds'}==previous
          and reward.locator('#partyResult').inner_text()=='3体の編成を保存しました')
    check('RC24 the save receipt does not consume roster space',reward.locator('#partyRosterScroll').bounding_box()==roster_before_feedback)
    reward.clock.fast_forward(2800)
    check('RC24 the saved receipt disappears automatically without moving the roster',
          reward.locator('#partyResult').inner_text()==''
          and reward.locator('#partyRosterScroll').bounding_box()==roster_before_feedback)
    reward.reload(wait_until='load')
    reward.locator('.kit-transfer').click()
    check('RC23 confirmed formation survives reload with matching disabled rows',
          pids()==['白翼のアルム','鉄骸兵','夜叉']
          and reward.locator('[data-party-character="c004"]').is_disabled()
          and reward.locator('[data-party-character="c003"]').is_enabled())
    reward.locator('[data-party-character="c005"]').click()
    previous=rstate()
    reward.evaluate("""() => {
      window.__partyStorageSet=Storage.prototype.setItem;
      Storage.prototype.setItem=function(key,value){
        if(this===sessionStorage&&key==='tapgacha_reward_rc20_preview')throw new DOMException('quota','QuotaExceededError');
        return window.__partyStorageSet.call(this,key,value);
      };
    }""")
    reward.locator('#partyConfirm').click()
    check('RC23 failed persistence rolls back canonical formation while keeping a retryable draft',
          rstate()==previous and reward.evaluate("tapGacha.getSave().partyIds")==previous['partyIds']
          and pids()==['黒耀ヴァルグ','鉄骸兵','夜叉']
          and '保存できませんでした' in reward.locator('#partyResult').inner_text())
    reward.clock.fast_forward(3000)
    check('RC24 a failed-save explanation stays available for retry','保存できませんでした' in reward.locator('#partyResult').inner_text())
    reward.evaluate("() => {Storage.prototype.setItem=window.__partyStorageSet;}")
    reward.locator('#partyConfirm').click()
    check('RC23 a retry saves the pending draft exactly once',rstate()['partyIds']==['c005','c002','c004'])
    party_backup=rstate()
    reward.add_init_script("""(() => {
      const next=sessionStorage.getItem('__qa_party_next');
      if(next){
        sessionStorage.removeItem('__qa_party_next');
        sessionStorage.setItem('tapgacha_reward_rc20_preview',next);
      }
    })()""")
    reward.evaluate("""() => {
      const s=JSON.parse(sessionStorage.getItem('tapgacha_reward_rc20_preview'));
      s.characters=Object.fromEntries(Array.from({length:15},(_,i)=>['c'+String(i+1).padStart(3,'0'),
        {owned:true,level:100,cap:100,shards:12,trainingCapStep:100}]));
      s.partyIds=['c01','c01','c999',null,'c002','c015'];
      sessionStorage.setItem('__qa_party_next',JSON.stringify(s));
    }""")
    reward.reload(wait_until='load')
    reward.locator('.kit-transfer').click()
    check('RC23 formation normalizes legacy IDs and discards duplicates or unknown characters',
          reward.locator('#partyRoster .party-candidate').count()==15
          and pids()==['白翼のアルム','鉄骸兵','白銀の聖騎士'])
    reward.locator('#partyConfirm').click()
    check('RC23 only canonical owned IDs are written on confirmation',rstate()['partyIds']==['c001','c002','c015'])
    reward.locator('[data-party-character="c009"]').click()
    for width,height in ((320,568),(360,600),(393,654),(390,636),(390,844),(430,932)):
        reward.set_viewport_size({'width':width,'height':height})
        party_nav=reward.locator('#partyScreen > .kit-shared-nav').evaluate("""nav=>[nav,...nav.querySelectorAll('button'),...nav.querySelectorAll('button>img')].map(el=>{const r=el.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})""")
        home_nav=reward.locator('#homeScreen > .kit-shared-nav').evaluate("""nav=>{
          const home=nav.closest('.screen');home.classList.add('active');
          const boxes=[nav,...nav.querySelectorAll('button'),...nav.querySelectorAll('button>img')].map(el=>{const r=el.getBoundingClientRect();return [r.x,r.y,r.width,r.height]});
          home.classList.remove('active');return boxes;
        }""")
        if party_nav!=home_nav:print('RC23 NAV GEOMETRY',json.dumps({'party':party_nav,'home':home_nav}),flush=True)
        check(f'RC23 shared menu retains identical artwork positions at {width}x{height}',party_nav==home_nav)
        layout=reward.evaluate(r"""async () => {
          const root=document.querySelector('#partyScreen'),roster=document.querySelector('#partyRosterScroll');
          const nav=root.querySelector('.kit-shared-nav').getBoundingClientRect();
          const rects=['.party-header','.party-slots','.party-hint','.party-footer'].map(s=>root.querySelector(s).getBoundingClientRect());
          const names=[...root.querySelectorAll('.party-slot-name,.party-candidate-name')];
          const frames=[root.querySelector('.party-header h1'),root.querySelector('.party-back'),root.querySelector('.party-slot'),root.querySelector('.party-candidate'),root.querySelector('.party-confirm')];
          const ready=await Promise.all(frames.map(el=>{
            const css=getComputedStyle(el,el.matches('.party-slot,.party-candidate')?'::after':null);
            const match=css.backgroundImage.match(/url\(["']?(.*?)["']?\)/);if(!match)return false;
            return new Promise(resolve=>{const image=new Image();image.onload=()=>resolve(image.naturalWidth>0);image.onerror=()=>resolve(false);image.src=match[1]});
          }));
          const badNames=names.filter(el=>el.scrollWidth>el.clientWidth+1||el.scrollHeight>el.clientHeight+1||parseFloat(getComputedStyle(el).fontSize)<12)
            .map(el=>({name:el.textContent,width:el.clientWidth,scrollWidth:el.scrollWidth,height:el.clientHeight,scrollHeight:el.scrollHeight,font:getComputedStyle(el).fontSize}));
          return {artReady:ready.every(Boolean),controlsFit:rects.every(r=>r.left>=-1&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<nav.top),
            rosterScrollable:roster.clientHeight>=72&&roster.scrollHeight>roster.clientHeight,namesFit:badNames.length===0,
            noDoubleFrames:[...root.querySelectorAll('.party-slot,.party-candidate,.party-confirm,.party-back')].every(el=>getComputedStyle(el).borderTopWidth==='0px'),
            badNames:badNames,rosterHeight:roster.clientHeight,rosterScrollHeight:roster.scrollHeight};
        }""")
        print('RC24 readable layout',width,height,json.dumps(layout,ensure_ascii=False),flush=True)
        check(f'RC24 formation controls and live names remain readable at {width}x{height}',
              all(layout[k] for k in ('artReady','controlsFit','rosterScrollable','namesFit','noDoubleFrames')))
        reward.locator('#partyRosterScroll').evaluate('el=>el.scrollTop=0')
        visible_cards=reward.evaluate("""() => {
          const panel=document.querySelector('#partyRosterScroll'),p=panel.getBoundingClientRect();
          const cards=[...document.querySelectorAll('#partyRoster .party-candidate')];
          const fully=cards.filter(el=>{const r=el.getBoundingClientRect();return r.left>=p.left-1&&r.right<=p.right+1&&r.top>=p.top-1&&r.bottom<=p.bottom+1});
          return {count:fully.length,firstRowColumns:new Set(cards.slice(0,4).map(el=>Math.round(el.getBoundingClientRect().x))).size,
            smallTargets:cards.some(el=>{const r=el.getBoundingClientRect();return r.width<44||r.height<44}),
            panel: {width:p.width,height:p.height}, card:cards[0].getBoundingClientRect().toJSON()};
        }""")
        print('RC24 visible roster',width,height,json.dumps(visible_cards),flush=True)
        check(f'RC24 at least eight full cards fit in four columns at {width}x{height}',
              visible_cards['count']>=8 and visible_cards['firstRowColumns']==4 and not visible_cards['smallTargets'])
        reward.locator('#partyRosterScroll').evaluate('el=>el.scrollTop=el.scrollHeight')
        check(f'RC23 all fifteen characters stay reachable by scrolling at {width}px',reward.locator('[data-party-character="c015"]').evaluate("el=>{const r=el.getBoundingClientRect(),s=el.closest('.party-roster-scroll').getBoundingClientRect();return r.top>=s.top-1&&r.bottom<=s.bottom+1}"))
        reward.locator('#partyRosterScroll').evaluate('el=>el.scrollTop=0')
        reward.screenshot(path=str(SHOTS/f'{ENGINE}-party-{width}x{height}.png'))
    reward.locator('#partyScreen [data-nav="キャラ"]').click()
    check('RC23 formation menu navigates to existing training normally',reward.locator('#characterScreen.active').count()==1)
    for count in (0,1,2):
        reward.evaluate("""count => {
          const s=JSON.parse(sessionStorage.getItem('tapgacha_reward_rc20_preview'));
          s.characters=Object.fromEntries(Array.from({length:count},(_,i)=>['c'+String(i+1).padStart(3,'0'),{owned:true,level:1,cap:100,shards:0,trainingCapStep:100}]));
          s.partyIds=['c015','c001','c001'];
          sessionStorage.setItem('__qa_party_next',JSON.stringify(s));
        }""",count)
        reward.reload(wait_until='load')
        reward.locator('.kit-transfer').click()
        check(f'RC23 the formation supports {count} owned characters without adding unowned members',
              reward.locator('#partyRoster .party-candidate').count()==count
              and reward.locator('#partyRoster .party-candidate:disabled').count()==count
              and reward.locator('#partySlots button:disabled').count()==3-count
              and reward.locator('#partyConfirm').is_enabled()==bool(count)
              and reward.locator('#partyEmpty').is_visible()==(count==0))
        if count:
            reward.locator('#partyConfirm').click()
            check(f'RC23 a smaller owned formation of {count} members can be saved',rstate()['partyIds']==[f'c00{i+1}' for i in range(count)])
    reward.evaluate("s=>sessionStorage.setItem('__qa_party_next',JSON.stringify(s))",party_backup)
    reward.reload(wait_until='load')
    check('RC23 formation changes leave every live localStorage key unchanged',reward.evaluate("Object.entries(localStorage).sort()")==live_before)
    preview.close()
    # Independent motion preview: deliberately seeded with opaque save sentinels.
    battle_context=browser.new_context(viewport={'width':393,'height':654},is_mobile=True,has_touch=True)
    battle_context.add_init_script("""(() => {
      if(sessionStorage.getItem('__qa_battle_seeded'))return;
      localStorage.setItem('tapgacha_save_v3','{live-save-do-not-touch');
      localStorage.setItem('tapgacha_pt','12345');
      sessionStorage.setItem('tapgacha_reward_rc20_preview','{review-save-do-not-touch');
      sessionStorage.setItem('__qa_battle_seeded','1');
    })()""")
    battle=battle_context.new_page()
    battle.on('pageerror',lambda err:errors.append('battle: '+str(err)))
    battle.on('response',lambda response:resource_failures.append(f'{response.status} {response.url}') if response.status>=400 and ('/assets/' in response.url or '/css/' in response.url or '/js/' in response.url) else None)
    battle_url=URL.rsplit('/',1)[0]+'/battle-preview.html'
    battle.clock.install(time=datetime(2026,11,8,2,0,tzinfo=timezone.utc))
    battle.goto(battle_url,wait_until='load')
    battle.wait_for_function('window.battlePreview?.snapshot().ready')
    battle.clock.pause_at(datetime(2026,11,8,2,0,10,tzinfo=timezone.utc))
    bstate=lambda:battle.evaluate('battlePreview.snapshot()')
    storage_before=battle.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')
    check('RC25 all four separate sprites initialize with three live portrait controls',
          battle.locator('.actor').count()==4 and battle.locator('.hero-card').count()==3
          and bstate()['hp']==dict(c001=100,c002=100,c003=100,guardian=100)
          and battle.locator('#battleAuto').is_enabled())
    check('RC25 sprites retain transparent exterior pixels',battle.evaluate("""() => [...document.querySelectorAll('.actor img')].every(img=>{
      const canvas=document.createElement('canvas');canvas.width=img.naturalWidth;canvas.height=img.naturalHeight;
      const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);
      return [[0,0],[canvas.width-1,0],[0,canvas.height-1],[canvas.width-1,canvas.height-1]].every(([x,y])=>ctx.getImageData(x,y,1,1).data[3]<10);
    })"""))
    for width,height in ((320,568),(360,600),(390,636),(393,654),(390,844),(430,932)):
        battle.set_viewport_size({'width':width,'height':height})
        geometry=battle.evaluate("""() => {
          const root=document.querySelector('#battleApp'),f=document.querySelector('#battleField').getBoundingClientRect();
          const actors=[...document.querySelectorAll('.actor')].map(el=>el.getBoundingClientRect());
          const controls=[...document.querySelectorAll('.battle-header,.battle-status,.battle-party,.battle-controls,.battle-note')].map(el=>el.getBoundingClientRect());
          const targets=[...document.querySelectorAll('button,.battle-home')].map(el=>el.getBoundingClientRect());
          return {fit:controls.every(r=>r.left>=-1&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1),
            actorsFit:actors.every(r=>r.left>=f.left-1&&r.right<=f.right+1&&r.top>=f.top-1&&r.bottom+6<=f.bottom+1),
            touch:targets.every(r=>r.width>=44&&r.height>=44),
            names:[...document.querySelectorAll('.hero-name')].every(el=>el.scrollWidth<=el.clientWidth+1&&el.scrollHeight<=el.clientHeight+1&&parseFloat(getComputedStyle(el).fontSize)>=12),
            images:[...document.images].every(img=>img.complete&&img.naturalWidth>0),
            noOverflow:root.scrollHeight<=root.clientHeight+1&&document.documentElement.scrollWidth<=innerWidth,
            field:{width:f.width,height:f.height}};
        }""")
        print('RC25 battle layout',width,height,json.dumps(geometry),flush=True)
        check(f'RC25 all sprites, labels and touch controls fit at {width}x{height}',
              all(geometry[k] for k in ('fit','actorsFit','touch','names','images','noOverflow')))
        battle.screenshot(path=str(SHOTS/f'{ENGINE}-battle-{width}x{height}.png'))
    battle.set_viewport_size({'width':393,'height':654})
    battle.locator('#card-c001').click()
    check('RC25 a manual attack begins with a windup before damage',
          bstate()['busy'] and bstate()['phase']=='windup' and bstate()['hp']['guardian']==100)
    battle.locator('#card-c002').evaluate("el=>el.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    battle.clock.fast_forward(310)
    check('RC25 queued clicks cannot duplicate a manual impact',
          bstate()['impacts']==1 and bstate()['hp']['guardian']==86
          and battle.locator('.enemy-caption').inner_text()=='水晶の守護者')
    battle.screenshot(path=str(SHOTS/f'{ENGINE}-battle-holy-impact.png'))
    battle.clock.fast_forward(470)
    check('RC25 a manual attack returns to idle after its recovery',
          not bstate()['busy'] and battle.locator('#battleEffects').locator(':scope > *').count()==0
          and battle.locator('#card-c002').is_enabled())
    for hero,remaining in (('c002',88),('c003',84)):
        battle.locator('#battleReset').click()
        battle.locator('#card-'+hero).click()
        battle.clock.fast_forward(310)
        check(f'RC25 {hero} has its own attack and matching live HP',bstate()['active']==hero and bstate()['hp']['guardian']==remaining)
        battle.screenshot(path=str(SHOTS/f'{ENGINE}-battle-{hero}-impact.png'))
        battle.clock.fast_forward(470)
    battle.locator('#battleReset').click()
    for _ in range(3):
        battle.locator('#actor-guardian').click()
        battle.clock.fast_forward(310)
        battle.clock.fast_forward(470)
    check('RC25 enemy attacks rotate across all three allies and update their cards',
          all(bstate()['hp'][hero]==82 for hero in ('c001','c002','c003'))
          and battle.locator('.hero-percent').all_inner_texts()==['82%','82%','82%'])
    battle.locator('#battleReset').click()
    battle.locator('#battleAuto').click()
    battle.clock.fast_forward(100)
    battle.locator('#battleAuto').click()
    paused=bstate()
    battle.clock.fast_forward(4000)
    check('RC25 pausing before impact freezes the action and HP',bstate()==paused and paused['paused'] and paused['hp']['guardian']==100)
    battle.locator('#battleAuto').click()
    battle.clock.fast_forward(199)
    check('RC25 resume preserves the exact remaining windup',bstate()['hp']['guardian']==100)
    battle.clock.fast_forward(2)
    check('RC25 resumed windup applies its impact exactly once',bstate()['hp']['guardian']==86 and bstate()['impacts']==1)
    battle.locator('#battleAuto').click()
    paused=bstate()
    battle.clock.fast_forward(4000)
    check('RC25 pausing after impact also freezes recovery',bstate()==paused and paused['phase']=='impact')
    battle.locator('#battleSpeed').click()
    paused=bstate()
    battle.clock.fast_forward(1000)
    check('RC25 changing speed while paused keeps the action paused',bstate()==paused and paused['speed']==2)
    battle.locator('#battleAuto').click()
    battle.clock.fast_forward(231)
    battle.clock.fast_forward(261)
    battle.clock.fast_forward(151)
    check('RC25 double speed advances the same action sequence',bstate()['hp']['guardian']==74 and bstate()['impacts']==2)
    for _ in range(60):
        if bstate()['complete']:break
        battle.clock.fast_forward(400)
    double_result=bstate()
    check('RC25 auto playback stops cleanly at the end of the preview',
          double_result['complete'] and not double_result['auto'] and not double_result['busy']
          and double_result['hp']['guardian']==0 and double_result['impacts']==10)
    battle.clock.fast_forward(5000)
    check('RC25 no attacks run after completion',bstate()==double_result)
    battle.screenshot(path=str(SHOTS/f'{ENGINE}-battle-complete.png'))
    battle.locator('#battleAuto').click()
    check('RC25 completed playback can restart with fresh HP',
          bstate()['auto'] and bstate()['phase']=='windup' and bstate()['impacts']==0
          and all(v==100 for v in bstate()['hp'].values()))
    battle.locator('#battleReset').click()
    battle.locator('#battleSpeed').click()
    battle.locator('#battleAuto').click()
    for _ in range(60):
        if bstate()['complete']:break
        battle.clock.fast_forward(600)
    check('RC25 playback speed does not alter the demo outcome',
          bstate()['complete'] and bstate()['hp']==double_result['hp'] and bstate()['impacts']==double_result['impacts'])
    battle.locator('#battleReset').click()
    battle.locator('#card-c003').click()
    battle.clock.fast_forward(120)
    battle.locator('#battleReset').click()
    reset_state=bstate()
    battle.clock.fast_forward(5000)
    check('RC25 reset cancels an in-flight attack and its pending damage',
          bstate()==reset_state and not reset_state['busy'] and reset_state['impacts']==0
          and all(v==100 for v in reset_state['hp'].values()))
    battle.locator('#card-c001').click()
    battle.clock.fast_forward(100)
    battle.locator('#battleSpeed').click()
    battle.clock.fast_forward(99)
    check('RC25 mid-attack speed changes preserve elapsed logical time',bstate()['hp']['guardian']==100)
    battle.clock.fast_forward(2)
    check('RC25 speed changes cannot duplicate an impact',bstate()['hp']['guardian']==86 and bstate()['impacts']==1)
    battle.locator('#battleReset').click()
    battle.locator('#battleAuto').click()
    battle.clock.fast_forward(50)
    battle.evaluate("() => {Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));}")
    hidden_state=bstate()
    battle.clock.fast_forward(5000)
    check('RC25 hiding the page pauses playback without background damage',hidden_state['paused'] and bstate()==hidden_state)
    battle.evaluate("() => {delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));}")
    check('RC25 returning to the page keeps explicit resume available',bstate()['paused'] and battle.locator('#battleAuto').inner_text()=='再開')
    battle.locator('#battleReset').click()
    for _ in range(18):
        battle.locator('#actor-guardian').click()
        battle.clock.fast_forward(160)
        battle.clock.fast_forward(240)
    check('RC25 depleted ally HP stays at zero and ends the preview',
          bstate()['complete'] and all(bstate()['hp'][hero]==0 for hero in ('c001','c002','c003'))
          and battle.locator('.hero-card:disabled').count()==3)
    check('RC25 all preview actions preserve every local and session save byte',
          battle.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==storage_before)
    battle.locator('#battleReset').click()
    battle.reload(wait_until='load')
    battle.wait_for_function('battlePreview.snapshot().ready')
    check('RC25 reloading starts a fresh visual preview while preserving game saves',
          all(v==100 for v in bstate()['hp'].values())
          and battle.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==storage_before)
    battle.locator('#battleReset').click()
    check('RC26 field caption has no HP percent', '%' not in battle.locator('.enemy-caption').inner_text())
    check('RC26 HP percent sits inside each thick bar',battle.evaluate("""() => [...document.querySelectorAll('.hero-hp')].every(el=>{const a=el.getBoundingClientRect(),b=el.querySelector('.hero-percent').getBoundingClientRect();return a.height>=12&&b.top>=a.top&&b.bottom<=a.bottom;})"""))
    battle.locator('#skill-c001').click()
    battle.evaluate("document.querySelector('#skill-c001').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    battle.clock.fast_forward(310)
    check('RC26 skill applies its own damage once',bstate()['hp']['guardian']==76 and bstate()['impacts']==1)
    battle.clock.fast_forward(470)
    check('RC26 skill cooldown disables only the used skill',battle.locator('#skill-c001').is_disabled() and battle.locator('#skill-c002').is_enabled())
    battle.locator('#battleAuto').click()
    battle.locator('#battleAuto').click()
    paused=bstate()
    battle.clock.fast_forward(9000)
    check('RC26 pause freezes skill cooldowns',bstate()==paused)
    battle.locator('#battleAuto').click()
    battle.clock.fast_forward(780)
    battle.locator('#battleAuto').click()
    battle.locator('#battleReset').click()
    check('RC26 reset clears skill cooldowns and HP',not any(bstate()['cooldowns'].values()) and all(v==100 for v in bstate()['hp'].values()))
    battle.locator('#skill-c002').click()
    battle.clock.fast_forward(780)
    check('RC26 iron skill has distinct damage',bstate()['hp']['guardian']==78)
    battle.clock.fast_forward(8000)
    check('RC26 cooldown ends and allows the skill again',battle.locator('#skill-c002').is_enabled())
    battle.locator('#skill-c003').click()
    battle.clock.fast_forward(780)
    check('RC26 wolf skill has distinct damage',bstate()['hp']['guardian']==52)
    battle.evaluate("window.dispatchEvent(new Event('pagehide'))")
    battle.evaluate("window.dispatchEvent(new Event('pageshow'))")
    battle.clock.fast_forward(8100)
    check('RC26 restored pages resume skill cooldowns',battle.locator('#skill-c003').is_enabled())
    battle.screenshot(path=str(SHOTS/f'{ENGINE}-battle-skills.png'))
    battle.locator('#battleReset').click()
    # The exact standalone builder is also used for the downloadable HTML.
    subprocess.run([sys.executable,str(ROOT/'tools/build_battle_preview.py')],check=True,cwd=ROOT)
    portable_context=browser.new_context(viewport={'width':393,'height':654},is_mobile=True,has_touch=True)
    portable=portable_context.new_page()
    portable.on('pageerror',lambda err:errors.append('portable battle: '+str(err)))
    external=[]
    portable.on('request',lambda request:external.append(request.url) if request.resource_type!='document' and request.url.startswith(('http:','https:')) else None)
    portable.clock.install(time=datetime(2026,11,8,2,0,tzinfo=timezone.utc))
    portable.goto(URL.rsplit('/',1)[0]+'/tapgacha-battle-preview-RC26.html',wait_until='load')
    portable.wait_for_function('battlePreview.snapshot().ready')
    portable.clock.pause_at(datetime(2026,11,8,2,0,10,tzinfo=timezone.utc))
    portable.locator('#card-c001').click()
    portable.clock.fast_forward(310)
    check('RC25 the standalone HTML runs the same live attack without external assets',
          portable.evaluate('battlePreview.snapshot().hp.guardian')==86 and not external)
    portable_context.close()
    battle_context.close()
    reduced=browser.new_context(viewport={'width':320,'height':568},is_mobile=True,has_touch=True,reduced_motion='reduce')
    battle=reduced.new_page()
    battle.on('pageerror',lambda err:errors.append('reduced motion battle: '+str(err)))
    battle.clock.install(time=datetime(2026,11,8,2,0,tzinfo=timezone.utc))
    battle.goto(battle_url,wait_until='load')
    battle.wait_for_function('battlePreview.snapshot().ready')
    battle.clock.pause_at(datetime(2026,11,8,2,0,10,tzinfo=timezone.utc))
    battle.locator('#card-c001').click()
    battle.clock.fast_forward(310)
    check('RC25 reduced-motion mode keeps HP feedback with no shaking or idle animation',
          battle.evaluate("battlePreview.snapshot().hp.guardian===86 && getComputedStyle(document.querySelector('.actor-idle')).animationName==='none' && document.querySelector('#battleApp').getAnimations({subtree:true}).length===0"))
    reduced.close()
    # Run the stage through the same formation screen players use, with an existing save.
    stage_context = browser.new_context(viewport={'width':393,'height':654}, is_mobile=True, has_touch=True)
    stage_context.add_init_script("""localStorage.setItem('tapgacha_save_v3', JSON.stringify({
      schemaVersion: 3, points: 333, keys: 2, tapPower: 5, partyIds: ['c002','c001','c003'],
      characters: {
        c001: {owned:true, level:1, cap:100, shards:1},
        c002: {owned:true, level:10, cap:100, shards:2},
        c003: {owned:true, level:10, cap:100, shards:3},
        c004: {owned:true, level:30, cap:100, shards:4},
        c005: {owned:true, level:1, cap:100, shards:5},
        c006: {owned:true, level:1, cap:100, shards:6},
        c007: {owned:true, level:1, cap:100, shards:7},
        c008: {owned:true, level:1, cap:100, shards:8},
        c009: {owned:true, level:1, cap:100, shards:9},
        c010: {owned:true, level:1, cap:100, shards:10}
      }
    }));""")
    stage_page = stage_context.new_page()
    stage_page.on('pageerror', lambda error: errors.append('RC27 stage: ' + str(error)))
    stage_page.on('response', lambda response: resource_failures.append(f'{response.status} {response.url}')
                  if response.status >= 400 and any(path in response.url for path in ('/assets/', '/js/', '/css/')) else None)
    stage_page.clock.install(time=datetime(2026,11,11,3,0,tzinfo=timezone.utc))
    stage_page.goto(URL+'?reward-preview=1', wait_until='load')
    stage_page.locator('.kit-transfer').click()
    before_stage = stage_page.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    stage_page.clock.pause_at(datetime(2026,11,11,3,0,30,tzinfo=timezone.utc))
    check('RC27 formation order and levels determine displayed stats', 
          stage_page.locator('.stage-name').all_inner_texts()==['鉄骸兵','白翼のアルム','冥牙クロウル']
          and stage_page.locator('.stage-level').all_inner_texts()==['Lv10','Lv1','Lv10']
          and stage_page.locator('.stage-stats').all_inner_texts()==['HP 245 · 攻 16','HP 120 · 攻 14','HP 136 · 攻 30']
          and stage_page.locator('#stageTrialLabel').is_hidden())
    for width,height in ((320,568),(393,654),(390,844),(430,932)):
        stage_page.set_viewport_size({'width':width,'height':height})
        check(f'RC27 battlefield and controls fit at {width}x{height}', stage_page.locator('.stage-app').evaluate("""root => {
          const fits = el => {
            const r = el.getBoundingClientRect();
            return r.left >= 0 && r.right <= innerWidth + 1 && r.top >= 0 && r.bottom <= innerHeight + 1;
          };
          return root.scrollHeight <= root.clientHeight + 1 &&
            [...root.querySelectorAll('button')].every(el => fits(el) && el.clientHeight >= 44 && el.clientWidth >= 44) &&
            [...root.querySelectorAll('.stage-skill')].every(el => el.getBoundingClientRect().bottom <= root.querySelector('.stage-controls').getBoundingClientRect().top) &&
            [...root.querySelectorAll('.stage-name,.stage-stats')].every(el => el.scrollWidth <= el.clientWidth + 1) &&
            [...root.querySelectorAll('.stage-card-hp')].every(el => el.getBoundingClientRect().height >= 12) &&
            [...root.querySelectorAll('img')].every(img => img.complete && img.naturalWidth > 0) &&
            root.querySelector('.stage-enemy-caption').textContent === '水晶の守護者';
        }"""))
        stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-stage-{width}x{height}.png'), animations='disabled')
    stage_page.set_viewport_size({'width':393,'height':654})
    hp = lambda: stage_page.locator('.stage-card-hp').evaluate_all("els=>els.map(el=>el.getAttribute('aria-valuetext'))")
    skill = lambda id: stage_page.locator(f'.stage-slot[data-unit={id}] .stage-skill')
    stage_start = stage_page.locator('#stageStart')
    stage_time = stage_page.locator('#stageElapsed')
    stage_page.clock.run_for(2500)
    check('RC27 attacks wait for the player to start', stage_time.inner_text()=='0.0秒' and hp()==['245 / 245','120 / 120','136 / 136'])
    stage_start.click()
    check('RC27 heal stays unavailable while all allies are full', skill('c001').is_disabled())
    skill('c002').click()
    check('RC27 iron shield protects every living ally',
          stage_page.locator('.stage-card[data-shielded=true]').count()==3
          and '12秒' in skill('c002').inner_text())
    stage_page.clock.run_for(2600)
    check('RC27 automatic hit targets the first slot and consumes its shield',
          hp()==['244 / 245','120 / 120','136 / 136']
          and stage_page.locator('.stage-slot[data-unit=c002] .stage-front').is_visible())
    skill('c001').click()
    check('RC27 a skill during an attack is queued without spending its cooldown',
          skill('c001').get_attribute('data-queued')=='true' and hp()[0]=='244 / 245')
    skill('c001').click()
    check('RC27 the same button cancels a queued skill', skill('c001').get_attribute('data-queued')=='false')
    skill('c001').click()
    stage_page.clock.run_for(550)
    check('RC27 queued healing restores HP with a cooldown',
          hp()[0]=='245 / 245' and '10秒' in skill('c001').inner_text())
    stage_page.clock.run_for(550)
    skill('c003').click()
    check('RC27 wolf skill uses 250 percent of its trained attack',
          stage_page.locator('.stage-enemy').evaluate("el=>el.style.getPropertyValue('--stage-hp')")=='63%')
    stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-stage-skill.png'), animations='disabled')
    stage_start.click()
    pause_time = stage_time.inner_text()
    pause_hp = hp()
    stage_page.locator('#stageSpeed').click()
    stage_page.clock.fast_forward(5000)
    check('RC27 pause freezes combat and skill cooldowns at either speed',
          stage_time.inner_text()==pause_time and hp()==pause_hp and skill('c003').is_disabled())
    stage_start.click()
    stage_page.clock.fast_forward(2000)
    check('RC27 double speed advances four combat seconds in two seconds',
          abs(float(stage_time.inner_text()[:-1])-float(pause_time[:-1])-4)<0.25)
    stage_page.clock.fast_forward(20000)
    check('RC27 the trained party can finish the stage', stage_page.locator('.stage-app[data-mode=victory]').count()==1)
    stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-stage-victory.png'), animations='disabled')
    stage_page.locator('#stageReset').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC27 reset restores the same party at full HP', stage_time.inner_text()=='0.0秒' and hp()==['245 / 245','120 / 120','136 / 136'])
    # Later skill timings assume normal speed, which persists between battles.
    stage_page.locator('#stageSpeed').click()
    stage_page.locator('#stageBack').click()
    check('RC27 returning from battle preserves formation and save bytes',
          stage_page.locator('#partyScreen.active').count()==1
          and stage_page.locator('#partySlots .party-slot-name').all_inner_texts()==['鉄骸兵','白翼のアルム','冥牙クロウル']
          and stage_page.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==before_stage)
    stage_page.locator('#partySlots [data-party-slot="1"]').click()
    stage_page.locator('#partyRoster [data-party-character=c004]').click()
    check('RC30 a mixed formation can enter the normal stage', stage_page.locator('#partyBattle').inner_text()=='戦闘へ')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC30 Yasha loads its own sprite and trained combat stats',
          stage_page.locator('#stageTrialLabel').is_hidden()
          and stage_page.locator('.stage-level').all_inner_texts()==['Lv10','Lv30','Lv10']
          and stage_page.locator('.stage-slot[data-unit=c004] .stage-stats').inner_text()=='HP 259 · 攻 43'
          and stage_page.locator('.stage-actor[data-unit=c004] img').evaluate('img => img.naturalWidth > 0'))
    stage_start.click()
    skill('c004').click()
    check('RC30 Yasha deals a 280 percent single hit',
          stage_page.locator('.stage-enemy').evaluate("el=>el.style.getPropertyValue('--stage-hp')")=='67%')
    stage_page.locator('#stageBack').click()
    check('RC27 an unsaved formation edit survives the round trip',
          stage_page.locator('#partySlots .party-slot-name').all_inner_texts()==['鉄骸兵','夜叉','冥牙クロウル'])
    stage_page.locator('#partySlots [data-party-slot="1"]').click()
    stage_page.locator('#partyRoster [data-party-character=c010]').click()
    check('RC27 an unsupported party offers an explicitly labeled trial', stage_page.locator('#partyBattle').inner_text()=='お試し戦闘')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC27 trial uses the sample at level 1',
          stage_page.locator('#stageTrialLabel').is_visible()
          and stage_page.locator('.stage-level').all_inner_texts()==['Lv1','Lv1','Lv1'])
    stage_page.locator('#stageBack').click()
    difficulty = stage_page.locator('#partyDifficulty')
    stage_page.set_viewport_size({'width':320,'height':568})
    stage_page.locator('#partyScreen.active').wait_for()
    difficulty.select_option('training')
    check('RC29 difficulty control fits beside the launch buttons',
          difficulty.evaluate("""el => {
            const box = el.getBoundingClientRect();
            const launch = document.querySelector('#partyBattle').getBoundingClientRect();
            return box.height >= 44 && box.right <= launch.left && launch.right <= innerWidth;
          }"""))
    stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-difficulty-preparation.png'), animations='disabled')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC29 selected difficulty is shown on the stage',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 34'
          and stage_page.locator('#battleStageScreen select').count()==0)
    stage_page.locator('#stageStart').click()
    stage_page.clock.fast_forward(34500)
    check('RC29 untrained sample loses on high difficulty without skills',
          stage_page.locator('.stage-app[data-mode=defeat]').count()==1)
    stage_page.locator('#stageStart').click()
    stage_page.locator('.stage-app[data-mode=running]').wait_for()
    check('RC29 rematch preserves the chosen difficulty',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 34')
    stage_page.locator('#stageBack').click()
    check('RC29 going back retains the selected difficulty', difficulty.input_value()=='training')
    difficulty.select_option('normal')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC29 returning to normal restores the original opponent',
          stage_page.locator('#stageEnemyStats').inner_text()=='通常 · 敵HP 360 · 攻 26'
          and stage_page.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==before_stage)
    stage_page.locator('#stageBack').click()
    for slot, member in enumerate(('c006','c005','c004')):
        stage_page.locator(f'#partySlots [data-party-slot="{slot}"]').click()
        stage_page.locator(f'#partyRoster [data-party-character={member}]').click()
    difficulty.select_option('training')
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC30 all three new allies and controls fit in the high-difficulty stage at 320px',
          stage_page.locator('#stageTrialLabel').is_hidden()
          and stage_page.locator('.stage-slot').evaluate_all("slots => slots.map(el => el.dataset.unit)")==['c006','c005','c004']
          and stage_page.locator('.stage-app').evaluate("""root => root.scrollHeight <= root.clientHeight + 1
            && [...root.querySelectorAll('img')].every(img => img.complete && img.naturalWidth > 0)
            && [...root.querySelectorAll('.stage-skill,.stage-name')].every(el => el.scrollWidth <= el.clientWidth + 1)"""))
    stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-stage-new-allies-320.png'), animations='disabled')
    stage_start.click()
    skill('c006').click()
    check('RC30 Swordsman immediately weakens the high-difficulty enemy',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 26 ↓')
    stage_page.clock.run_for(550)
    skill('c005').click()
    check('RC30 Varg deals 44 total skill damage and enters cooldown',
          stage_page.locator('.stage-enemy').evaluate("el=>el.style.getPropertyValue('--stage-hp')")=='92%'
          and '10秒' in skill('c005').inner_text())
    stage_page.clock.run_for(2070)
    check('RC30 weakened enemy deals 26 damage to the front ally', hp()[0]=='134 / 160')
    stage_page.clock.run_for(3500)
    check('RC30 enemy attack returns to 34 after six seconds',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 34')
    stage_page.locator('#stageBack').click()
    check('RC30 testing the new party and both difficulties leaves the save intact',
          stage_page.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==before_stage)
    for slot, member in enumerate(('c007','c008','c009')):
        stage_page.locator(f'#partySlots [data-party-slot="{slot}"]').click()
        stage_page.locator(f'#partyRoster [data-party-character={member}]').click()
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    check('RC31 new allies and battle controls fit at 320px',
          stage_page.locator('#stageTrialLabel').is_hidden()
          and hp()==['144 / 144','202 / 202','130 / 130']
          and stage_page.locator('.stage-app').evaluate("""root => root.scrollHeight <= root.clientHeight + 1
            && [...root.querySelectorAll('img')].every(img => img.complete && img.naturalWidth > 0)
            && [...root.querySelectorAll('.stage-skill,.stage-name')].every(el => el.scrollWidth <= el.clientWidth + 1)"""))
    stage_page.screenshot(path=str(SHOTS/f'{ENGINE}-stage-rc31-320.png'), animations='disabled')
    stage_start.click()
    skill('c009').click()
    check('RC31 Arcadio deals one hit and shows the enemy delay',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 34 · 遅延中'
          and stage_page.locator('.stage-enemy').evaluate("el=>el.style.getPropertyValue('--stage-hp')")=='93%')
    stage_page.clock.run_for(550)
    skill('c007').click()
    check('RC31 Kain reduces the enemy attack by ten percent',
          stage_page.locator('#stageEnemyStats').inner_text()=='高難度 · 敵HP 750 · 攻 31 ↓ · 遅延中')
    stage_page.clock.run_for(550)
    skill('c008').click()
    check('RC31 Siglas shows the four-second burn',
          stage_page.locator('#stageStatus').inner_text()=='煉獄火 · 燃焼ダメージ（4秒）')
    stage_page.clock.run_for(2000)
    check('RC31 the enemy does not attack at its original time', hp()[0]=='144 / 144')
    stage_page.clock.run_for(520)
    check('RC31 the delayed attack lands exactly once and clears the delay',
          hp()[0]=='113 / 144' and '遅延中' not in stage_page.locator('#stageEnemyStats').inner_text())
    check('RC31 burn ticks once per second and weaker debuffs never overwrite stronger ones',
          stage_page.evaluate("""() => {
            const make = ids => TapGachaBattle.createBattle(ids.map(id => ({ id, level: 1 })), 'training');
            const fire = make(['c008']);
            if (fire.requestSkill('c008')[0].amount !== 41) return false;
            const ticks = fire.advanceTo(5000).filter(event => event.periodic);
            const weaken = make(['c006','c007']);
            weaken.requestSkill('c006');
            weaken.advanceTo(1000);
            weaken.requestSkill('c007');
            if (weaken.enemyAttack() !== 26) return false;
            weaken.advanceTo(6000);
            if (weaken.enemyAttack() !== 31) return false;
            weaken.advanceTo(7000);
            return weaken.enemyAttack() === 34 && ticks.length === 4
              && ticks.every((event, index) => event.time === 1000 * (index + 1) && event.amount === 9);
          }"""))
    stage_page.locator('#stageBack').click()
    check('RC31 fighting with the three new allies leaves the save intact',
          stage_page.evaluate('({local:Object.entries(localStorage).sort(),session:Object.entries(sessionStorage).sort()})')==before_stage)
    stage_context.close()

    solo_context = browser.new_context(viewport={'width':320,'height':568}, is_mobile=True, has_touch=True)
    solo_context.add_init_script("""localStorage.setItem('tapgacha_save_v3', JSON.stringify({
      schemaVersion:3, points:0, keys:0, tapPower:1, partyIds:['c003'],
      characters:{c003:{owned:true, level:1, cap:100, shards:0}}
    }));""")
    stage_page = solo_context.new_page()
    stage_page.on('pageerror', lambda error: errors.append('RC27 solo: ' + str(error)))
    stage_page.clock.install(time=datetime(2026,11,11,3,0,tzinfo=timezone.utc))
    stage_page.goto(URL+'?reward-preview=1', wait_until='load')
    stage_page.locator('.kit-transfer').click()
    stage_page.locator('#partyBattle').click()
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    stage_page.clock.pause_at(datetime(2026,11,11,3,0,30,tzinfo=timezone.utc))
    stage_page.locator('#stageStart').click()
    stage_page.clock.fast_forward(10500)
    check('RC27 a solo defeat stops combat at zero HP',
          stage_page.locator('.stage-app[data-mode=defeat]').count()==1
          and stage_page.locator('.stage-card-hp').get_attribute('aria-valuenow')=='0'
          and stage_page.locator('#stageElapsed').inner_text()=='10.0秒')
    stage_page.locator('#stageStart').click()
    stage_page.locator('.stage-app[data-mode=running]').wait_for()
    check('RC27 rematch restores the fallen party', stage_page.locator('.stage-card-hp').get_attribute('aria-valuenow')=='100')
    solo_context.close()

    subprocess.run([sys.executable, str(ROOT/'tools/build_battle_stage.py')], check=True, cwd=ROOT)
    sample_context = browser.new_context(viewport={'width':393,'height':654}, is_mobile=True, has_touch=True)
    stage_page = sample_context.new_page()
    stage_page.on('pageerror', lambda error: errors.append('RC27 standalone: ' + str(error)))
    sample_requests = []
    stage_page.on('request', lambda request: sample_requests.append(request.url)
                  if request.resource_type!='document' and request.url.startswith(('http:', 'https:')) else None)
    stage_page.clock.install(time=datetime(2026,11,11,3,0,tzinfo=timezone.utc))
    stage_page.goto(URL.rsplit('/',1)[0]+'/tapgacha-battle-stage-RC31.html', wait_until='load')
    stage_page.locator('.stage-app[data-mode=ready]').wait_for()
    stage_page.clock.pause_at(datetime(2026,11,11,3,0,30,tzinfo=timezone.utc))
    stage_page.locator('#stageStart').click()
    stage_page.clock.fast_forward(16500)
    check('RC27 standalone runs to victory with all assets embedded',
          stage_page.locator('.stage-app[data-mode=victory]').count()==1
          and stage_page.locator('#stageElapsed').inner_text()=='16.0秒'
          and not sample_requests)
    sample_context.close()

    check('new save safety checks produce no runtime exceptions',not errors)
    (ROOT/f'qa-results-{ENGINE}.json').write_text(json.dumps({'browser':ENGINE,'passed':len(passed),'checks':passed,'runtime_errors':errors,'broken_images':missing,'resource_failures':resource_failures},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ALL {len(passed)} CHECKS PASS',flush=True)
    browser.close()

