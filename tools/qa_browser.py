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
    check('seven screens',page.locator('section.screen').count()==7)
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
    check('new save safety checks produce no runtime exceptions',not errors)
    (ROOT/f'qa-results-{ENGINE}.json').write_text(json.dumps({'browser':ENGINE,'passed':len(passed),'checks':passed,'runtime_errors':errors,'broken_images':missing,'resource_failures':resource_failures},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ALL {len(passed)} CHECKS PASS',flush=True)
    browser.close()
