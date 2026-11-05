
(() => {
  const home = document.getElementById('homeScreen');
  const tap = document.getElementById('tapScreen');
  const gacha = document.getElementById('gachaScreen');
  const characterScreen = document.getElementById('characterScreen');
  const shopScreen = document.getElementById('shopScreen');
  const toast = document.getElementById('toast');
  const tapZone = document.getElementById('tapZone');
  const ptEl = document.getElementById('livePT');
  const powerEl = document.getElementById('tapPower');
  const powerBox = document.getElementById('powerBox');
  const comboEl = document.getElementById('combo');
  const progressNow = document.getElementById('progressNow');
  const progressTarget = document.getElementById('progressTarget');
  const progressBox = document.getElementById('progressBox');
  const progressFill = document.getElementById('progressFill');
  const chestButtons = [...document.querySelectorAll('.chest-button')];

  const gachaPTEl = document.getElementById('gachaPT');
  const gachaResultEl = document.getElementById('gachaResult');
  const gachaFlashEl = document.getElementById('gachaFlash');
  const ownedCountEl = document.getElementById('ownedCount');
  const gachaDrawButtons = [...document.querySelectorAll('.gacha-draw')];

  // 旧プロトタイプから回収した15体。画像・名前・属性・紹介文・設定文を復元。
  // legacyWeight は記録として保持するが、現在の70/25/5抽選には使用しない。
  const GACHA_CHARACTERS = [{"id":"c001","rarity":1,"name":"白翼のアルム","emoji":"🕊️","element":"聖","tagline":"聖なる光をまとう天使見習い","lore":"神殿の最下層で記憶を持たずに目覚めた、天使としては最も小さな存在。羽は一対しかなく、放つ光も弱い。街の守護石に宿ることもあると言われ、人々には「迷い天使」と呼ばれ親しまれている。片方の羽が常に半透明で消えかけているように見えることから「羽なし」とも呼ばれるが、本人はそれを気にしていない。","legacyWeight":13,"image":"assets/19304675598037d22846.webp"},{"id":"c002","rarity":1,"name":"鉄骸兵","emoji":"⚙️","element":"雷","tagline":"廃工場に蘇った機械の亡骸","lore":"廃工場に落雷が続いた夜、解体待ちの機械群に電撃が宿り誕生した。無所属で廃工場跡を根城にし、目的も持たずにさまよい続ける。走るたびに錆びた鉄粉が散ることから「錆走り」「廃鉄」と呼ばれる。錆びるほどに内部の意識が鮮明になるという奇妙な性質を持つ。","legacyWeight":13,"image":"assets/339d1986421cc10d88c7.webp"},{"id":"c003","rarity":1,"name":"冥牙クロウル","emoji":"🐺","element":"闇","tagline":"地を這う怨念の獣","lore":"処刑場の地下に染み込んだ無数の怨念が、長い年月をかけて獣の形をとった存在。冥界の番犬として非公式に認識されているが、誰にも使役されていない。常に地面すれすれを這うように移動するため「地這い」「怨の犬」と呼ばれ、怨念が濃い土地にのみ発生する。","legacyWeight":13,"image":"assets/2ef1b8c6da01c8c39b83.webp"},{"id":"c004","rarity":1,"name":"夜叉","emoji":"👺","element":"炎","tagline":"血に飢えた和風の鬼","lore":"戦場で血に濡れながら絶命した武将の怨念が、炎とともに鬼の形に変じた存在。鬼道衆の末端に属し、激戦地の跡地でたびたび目撃される。全身が返り血のような赤みを帯びていることから「赤鬼」「血塗れ」と呼ばれ、血を浴びるたびに凶暴さを増していく。","legacyWeight":13,"image":"assets/deed14cad6bd683d64ea.webp"},{"id":"c005","rarity":1,"name":"黒耀ヴァルグ","emoji":"🐺","element":"雷","tagline":"漆黒の狼に宿る雷","lore":"嵐の夜に黒い狼の群れへ落雷が直撃し、唯一生き残った個体に雷が宿った。群れを作らず荒野を独走し続ける。黒い毛並みに常に紫電をまとう姿から「黒雷狼」と呼ばれ、かつて群れを持っていたことを知る者はいない。「一匹狼」という呼び名を本人は嫌う。","legacyWeight":14,"image":"assets/a888dd42bddf1a78481f.webp"},{"id":"c006","rarity":1,"name":"骸の剣士","emoji":"💀","element":"闇","tagline":"誓いのために戦い続ける騎士の骸","lore":"誓いを果たせぬまま戦場で朽ちた騎士。誓いへの執念だけが骸を動かし続けており、その誓いの内容を本人は覚えていない。骸騎士団の残存兵として古戦場に眠り、稀に蘇る。何度倒されても立ち上がることから「不死の剣」「誓いの骸」と畏れられる。","legacyWeight":13,"image":"assets/b120306ef7acfe40c1bb.webp"},{"id":"c007","rarity":2,"name":"堕天使カイン","emoji":"🖤","element":"闇","tagline":"神に背いた最初の堕天使","lore":"神が最初に作り、最初に裏切られた天使。全ての堕落の原点とされ、堕天使軍を率いる首領として君臨する。堕落の気配が極めて濃い地にしか現れず、その存在だけで周囲の意志を腐食させる。「原初の罪」「最初の裏切り者」という呼び名を、本人は誇りとして受け入れている。","legacyWeight":4,"image":"assets/4715d51ddceba9dab7e8.webp"},{"id":"c008","rarity":2,"name":"煉獄シグラス","emoji":"🔥","element":"炎","tagline":"炎を愛した煉獄の番人","lore":"煉獄の番人として生まれたが、その炎の美しさに魅了され自らも燃え続けることを選んだ異端者。煉獄守護者の離反派に属し、煉獄の亀裂が地上に現れた時にのみ出現する。自分自身を燃やしながら戦う戦法をとることから「炎喰い」「煉獄の異端者」と呼ばれる。","legacyWeight":3,"image":"assets/4b7c3e81eac4b21c3344.webp"},{"id":"c009","rarity":2,"name":"紫電アルカディオ","emoji":"⚡","element":"雷","tagline":"封印を破った雷の精霊","lore":"古代の雷神殿で封印されていた雷の精霊。封印が緩んだ隙に実体を得て逃亡した唯一の存在。雷神殿の逃亡者として指名手配されているが、捕まえられる者はいない。放つ雷が常に紫色を帯びることから「紫雷」と呼ばれ、「封印破り」という異名を嵐の季節に語り継がれる。","legacyWeight":3,"image":"assets/55466b3cd275d73074f9.webp"},{"id":"c010","rarity":2,"name":"蒼月レイヴン","emoji":"🌙","element":"水","tagline":"月光と水から生まれた女性の霊体","lore":"月光が湖面に反射し続けた千年目の夜、水と月の狭間に生まれた女性の霊体。月詠みの巫女として無所属で存在し、満月の夜に静水の上にのみ姿を現す。その姿が水面に映る月のように揺らいで見えることから「月鏡」「水面の幻」と呼ばれ、触れようとすると消える。","legacyWeight":3,"image":"assets/8cdeb84e361846857c5b.webp"},{"id":"c011","rarity":2,"name":"紅蓮の舞姫","emoji":"💃","element":"炎","tagline":"炎祭りで炎に還った踊り子の化身","lore":"炎祭りの最中、踊り子が炎に巻かれて絶命した瞬間、炎そのものが彼女の意志を宿した。炎舞一座の化身として炎祭りの地に語り継がれる。戦う姿が舞を踊るように美しいことから「炎の化身」と呼ばれるが、触れれば全てを燃やす。「踊る業火」という呼び名を彼女は好む。","legacyWeight":3,"image":"assets/fa9be2f319ee0ca55c0f.webp"},{"id":"c012","rarity":3,"name":"呪詛の魔女","emoji":"🧙","element":"闇","tagline":"千の呪いを受け呪いの化身となった女","lore":"千の呪いを受け続けた末に呪いの化身となった女性。本来の名前は自らの呪いによって消滅しており、誰も知らない。呪縛教団の頂点に立つが、教団員でさえ彼女を恐れる。千の呪いを受けてなお生き続けた伝説から「千呪」と呼ばれ、「名無しの魔女」という呼び名が最も広く知られている。","legacyWeight":2,"image":"assets/3cf3761242e4e6737b84.webp"},{"id":"c013","rarity":3,"name":"終焉の天帝","emoji":"👑","element":"聖","tagline":"宇宙の終わりを司る神格","lore":"宇宙が誕生した瞬間に「終わり」として生まれた存在。始まりと同時に終わりが生まれた証とされ、神格・終末の座に君臨する。世界の終わりが近づく時にのみ姿を現すとされ、その存在を目撃した者は全員が終焉を語り始めると言われる。「終わりの王」「エンドオブオール」と全神話に記される。","legacyWeight":2,"image":"assets/f25bec3e7f3a03b4622d.webp"},{"id":"c014","rarity":3,"name":"虚空神・無限","emoji":"🌀","element":"水","tagline":"存在と無の狭間に生きる超越神格","lore":"存在と無の狭間から来た者。生まれたのか元からいたのかすら不明で、「出現」という概念自体が当てはまらない。超越神格として唯一無二の存在であり、全神話に共通して記されている。始まりも終わりも持たないことから「アルファにしてオメガ」と呼ばれ、「無限」という呼び名が最も端的にその本質を表す。","legacyWeight":1,"image":"assets/41884eba380b57711e4c.webp"},{"id":"c015","rarity":3,"name":"白銀の聖騎士","emoji":"⚔️","element":"水","tagline":"神を捨てた最後の聖騎士","lore":"かつて神に選ばれた聖騎士団の団長。絶対的な信仰を誇ったが、ある瞬間に神への信仰を失い、その瞬間から白銀の鎧が氷と水に覆われた。堕ちた聖騎士団の最後の生き残りとして、信仰が完全に失われた地にのみ現れる。「白き背徳者」「氷の聖女」と語り継がれ、その美しさと悲しさが伝説となっている。","legacyWeight":1,"image":"assets/24dd594f1e189a24c8c8.webp"}];

  const SAVE_KEY = 'tapgacha_save_v3';
  const SAVE_SCHEMA_VERSION = 3;

  function safeJsonParse(raw, fallback=null){
    try{
      const v = JSON.parse(raw);
      return v ?? fallback;
    }catch(e){
      return fallback;
    }
  }

  function normalizeRosterIds(obj){
    const out = {};
    if(!obj || typeof obj !== 'object') return out;

    Object.entries(obj).forEach(([id,val])=>{
      let nid = id;
      const m = /^c(\d{2})$/.exec(id);
      if(m) nid = 'c' + String(Number(m[1])).padStart(3,'0');

      const prev = out[nid] || {};
      const cur = val && typeof val === 'object' ? val : {};

      out[nid] = {
        ...prev,
        ...cur,
        owned: !!(prev.owned || cur.owned),
        shards: Math.max(
          Number(prev.shards || 0),
          Number(cur.shards || 0)
        )
      };
    });
    return out;
  }

  function makeBaseSave(){
    return {
      schemaVersion:SAVE_SCHEMA_VERSION,
      points:12450,
      tapPower:25,
      keys:3,
      characters:{},
      ad:{remaining:3,lastResetDate:''},
      stats:{taps:0,gachaPulls:0,star3Pulls:0},
      migration:{
        createdAt:new Date().toISOString(),
        currentKeysImported:false,
        legacyGV2Detected:false,
        legacyCompatibleImported:false,
        legacyConflictsPreserved:false
      },
      legacyV3:null
    };
  }

  let saveRecoveryBlocked = false;
  let saveWriteError = null;
  function validSaveNumber(v, min){
    return typeof v === 'number' && Number.isFinite(v) && v >= min;
  }
  function buildUnifiedSave(){
    const rawUnified = localStorage.getItem(SAVE_KEY);
    const existing = safeJsonParse(rawUnified);
    if(rawUnified !== null && (!existing || Array.isArray(existing) || typeof existing !== 'object')){
      saveRecoveryBlocked = true; // 破損した原本を絶対に上書きしない
      console.warn('統合セーブの形式が不正です。原本を保護し、保存を停止しました。');
      return makeBaseSave();
    }
    if(existing && typeof existing === 'object'){
      if(!validSaveNumber(existing.points,0) || !validSaveNumber(existing.tapPower,1) ||
         !validSaveNumber(existing.keys,0)){
        saveRecoveryBlocked = true;
        console.warn('統合セーブの数値が不正です。原本を保護し、保存を停止しました。');
        return makeBaseSave();
      }
      const base = makeBaseSave();
      return {
        ...base,
        ...existing,
        schemaVersion:SAVE_SCHEMA_VERSION,
        characters:normalizeRosterIds(existing.characters || {}),
        ad:{...base.ad,...(existing.ad||{})},
        stats:{...base.stats,...(existing.stats||{})},
        migration:{...base.migration,...(existing.migration||{})}
      };
    }

    const save = makeBaseSave();

    // A. 現行UI側の既存キーを最優先で取り込む。
    const newPtRaw = localStorage.getItem('tapgacha_pt');
    const newPowerRaw = localStorage.getItem('tapgacha_power');
    const newCollectionRaw = localStorage.getItem('tapgacha_collection');

    const hasNewPt = newPtRaw !== null;
    const hasNewPower = newPowerRaw !== null;
    const hasNewCollection = newCollectionRaw !== null;

    if(hasNewPt){
      const v = Number(newPtRaw);
      if(Number.isFinite(v)) save.points = Math.max(0,v);
    }
    if(hasNewPower){
      const v = Number(newPowerRaw);
      if(Number.isFinite(v)) save.tapPower = Math.max(1,v);
    }
    if(hasNewCollection){
      save.characters = normalizeRosterIds(
        safeJsonParse(newCollectionRaw,{}) || {}
      );
    }
    save.migration.currentKeysImported =
      hasNewPt || hasNewPower || hasNewCollection;

    // B. 旧v3(gV2)は互換部分のみ取り込む。
    // 現行キーが存在する項目は上書きしない。
    const legacy = safeJsonParse(localStorage.getItem('gV2'));
    if(legacy && typeof legacy === 'object'){
      save.migration.legacyGV2Detected = true;

      if(!hasNewPt && Number.isFinite(Number(legacy.pts))){
        save.points = Math.max(0,Number(legacy.pts));
      }

      const legacyOwned = legacy.oc && typeof legacy.oc === 'object' ? legacy.oc : {};
      const legacyShards = legacy.sh && typeof legacy.sh === 'object' ? legacy.sh : {};

      GACHA_CHARACTERS.forEach(c=>{
        const id = c.id;
        const current = save.characters[id];
        const legacyCount = Math.max(0,Number(legacyOwned[id] || 0));
        const legacyShard = Math.max(0,Number(legacyShards[id] || 0));

        // 二重加算防止：現行collectionにそのキャラの記録が無い時だけ移行。
        if(!current && (legacyCount > 0 || legacyShard > 0)){
          save.characters[id] = {
            owned: legacyCount > 0,
            shards: legacyShard
          };
          save.migration.legacyCompatibleImported = true;
        }
      });

      if(Number.isFinite(Number(legacy.adR))){
        save.ad.remaining = Math.max(0,Math.min(3,Number(legacy.adR)));
      }
      if(typeof legacy.adD === 'string'){
        save.ad.lastResetDate = legacy.adD;
      }

      if(Number.isFinite(Number(legacy.tapC))) save.stats.taps = Math.max(0,Number(legacy.tapC));
      if(Number.isFinite(Number(legacy.gacC))) save.stats.gachaPulls = Math.max(0,Number(legacy.gacC));
      if(Number.isFinite(Number(legacy.s3C))) save.stats.star3Pulls = Math.max(0,Number(legacy.s3C));

      // 現行仕様と衝突する可能性がある旧データは、使用せず丸ごと退避。
      save.legacyV3 = {
        importedAt:new Date().toISOString(),
        pts:legacy.pts ?? null,
        oc:legacy.oc || {},
        sh:legacy.sh || {},
        lv:legacy.lv || {},
        fm:legacy.fm || {},
        adR:legacy.adR ?? null,
        adD:legacy.adD ?? '',
        mCl:legacy.mCl || {},
        daily:legacy.daily || null,
        weekly:legacy.weekly || null,
        logDay:legacy.logDay ?? 0,
        logDate:legacy.logDate ?? '',
        logH:legacy.logH || [],
        tapC:legacy.tapC ?? 0,
        gacC:legacy.gacC ?? 0,
        s3C:legacy.s3C ?? 0,
        tutDone:!!legacy.tutDone,
        party:legacy.party || [],
        savedWave:legacy.savedWave ?? 1,
        awakenStones:legacy.awakenStones ?? 0,
        awakenedIds:legacy.awakenedIds || []
      };
      save.migration.legacyConflictsPreserved = true;
    }

    return save;
  }

  let gameSave = buildUnifiedSave();
  let collection = normalizeRosterIds(gameSave.characters || {});
  let tapPower = Math.max(1,Number(gameSave.tapPower || 25));
  let pt = Math.max(0,Number(gameSave.points ?? 12450));

  // QUEST-RC02: Period-scoped mission baselines. Save object remains schema v3.
  const QUEST_ITEMS = {
    daily: [
      {id:'daily_tap',title:'覚醒核を100回タップ',detail:'毎日のタップで力を蓄えよう',stat:'taps',goal:100,reward:40,art:'crystal'},
      {id:'daily_gacha',title:'ガチャを10回引く',detail:'召喚門から仲間を探そう',stat:'gachaPulls',goal:10,reward:30,art:'scroll'},
      {id:'daily_train',title:'キャラを3回育成する',detail:'レベルアップ3回で達成',stat:'levelUps',goal:3,reward:50,art:'potion'}
    ],
    weekly: [
      {id:'weekly_tap',title:'覚醒核を1,000回タップ',detail:'1週間のタップを積み重ねよう',stat:'taps',goal:1000,reward:200,art:'crystal'},
      {id:'weekly_gacha',title:'ガチャを100回引く',detail:'累計100回の召喚に挑戦',stat:'gachaPulls',goal:100,reward:120,art:'scroll'},
      {id:'weekly_train',title:'キャラを15回育成する',detail:'1週間にレベルアップ15回',stat:'levelUps',goal:15,reward:200,art:'potion'}
    ],
    milestone: [
      {id:'total_tap_1000',title:'累計1,000回タップ',detail:'旅路に刻まれる最初の勲章',stat:'taps',goal:1000,reward:200,art:'crystal'},
      {id:'total_gacha_1000',title:'累計1,000回ガチャ',detail:'仲間との出会いを重ねよう',stat:'gachaPulls',goal:1000,reward:200,art:'scroll'},
      {id:'total_train_50',title:'累計50回レベルアップ',detail:'育成回数の記録は本版から開始',stat:'levelUps',goal:50,reward:250,art:'potion'}
    ],
    limited: []
  };
  const QUEST_STATS=['taps','gachaPulls','levelUps'];
  const QUEST_JST_FORMAT=new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'});
  const safeQuestCounter = v => Number.isSafeInteger(v) && v>=0 ? v : 0;
  function questCounterSnapshot(){
    const stats=gameSave.stats||{};
    return Object.fromEntries(QUEST_STATS.map(key=>[key,safeQuestCounter(stats[key])]));
  }
  function questPeriodKeys(date=new Date()){
    const parts=QUEST_JST_FORMAT.formatToParts(date);
    const p=Object.fromEntries(parts.filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
    const day=`${p.year}-${p.month}-${p.day}`;
    const dateUTC=new Date(Date.UTC(Number(p.year),Number(p.month)-1,Number(p.day)));
    const wd=(dateUTC.getUTCDay()+6)%7;
    dateUTC.setUTCDate(dateUTC.getUTCDate()-wd);
    return {daily:day,weekly:dateUTC.toISOString().slice(0,10)};
  }
  function ensureQuestState(){
    if(!gameSave.stats||typeof gameSave.stats!=='object'||Array.isArray(gameSave.stats))gameSave.stats={};
    if(!Number.isSafeInteger(gameSave.stats.levelUps)||gameSave.stats.levelUps<0)gameSave.stats.levelUps=0;
    if(!gameSave.quests||typeof gameSave.quests!=='object'||Array.isArray(gameSave.quests))gameSave.quests={};
    const keys=questPeriodKeys(), stats=questCounterSnapshot();
    for(const category of ['daily','weekly']){
      const current=gameSave.quests[category];
      if(!current||typeof current!=='object'||current.key!==keys[category]||
         !current.baseline||typeof current.baseline!=='object'){
        gameSave.quests[category]={key:keys[category],baseline:{...stats},claimed:{}};
      }else{
        // Keep existing progress/claims and protect counters from malformed snapshots.
        current.baseline=Object.fromEntries(QUEST_STATS.map(k=>[k,safeQuestCounter(current.baseline[k])]));
        if(!current.claimed||typeof current.claimed!=='object'||Array.isArray(current.claimed))current.claimed={};
      }
    }
    if(!gameSave.quests.milestone||typeof gameSave.quests.milestone!=='object'||Array.isArray(gameSave.quests.milestone))gameSave.quests.milestone={claimed:{}};
    if(!gameSave.quests.milestone.claimed||typeof gameSave.quests.milestone.claimed!=='object'||Array.isArray(gameSave.quests.milestone.claimed))gameSave.quests.milestone.claimed={};
    return keys;
  }
  function questProgress(category,item){
    const current=safeQuestCounter(gameSave.stats?.[item.stat]);
    if(category==='milestone')return current;
    const baseline=safeQuestCounter(gameSave.quests[category].baseline[item.stat]);
    return Math.max(0,current-baseline);
  }
  ensureQuestState();


  function saveUnified(){
    gameSave.schemaVersion = SAVE_SCHEMA_VERSION;
    gameSave.points = Math.max(0,Number(pt || 0));
    gameSave.tapPower = Math.max(1,Number(tapPower || 1));
    gameSave.characters = normalizeRosterIds(collection || {});
    gameSave.keys = Math.max(0,Number(gameSave.keys || 0));

    if(saveRecoveryBlocked){
      console.warn('破損したセーブの保護中につき保存を中止しました。');
      return false;
    }
    try{
      // 正本を先に確定。ミラー書き込み失敗は正本を壊さない。
      localStorage.setItem(SAVE_KEY, JSON.stringify(gameSave));
    }catch(e){
      saveWriteError = e;
      console.error('統合セーブの保存に失敗しました。',e);
      return false;
    }
    try{
      // 移行期間中は現行個別キーにもミラー。旧 gV2 は上書きしない。
      localStorage.setItem('tapgacha_pt', String(gameSave.points));
      localStorage.setItem('tapgacha_power', String(gameSave.tapPower));
      localStorage.setItem('tapgacha_collection', JSON.stringify(gameSave.characters));
    }catch(e){
      console.warn('統合セーブは成功しましたが、互換ミラーの保存に失敗しました。',e);
    }
    saveWriteError = null;
    return true;
  }

  saveUnified();

  // TRAIN-RC07: persistent tap-chest progress (not a per-screen combo counter).
  // Existing saves without this field start at zero once, then carry progress forward.
  const CHEST_THRESHOLDS = [200,500,1000];
  function restoreTapRewards(){
    const record=gameSave.tapRewardProgress;
    if(!record || typeof record!=='object' || Array.isArray(record))
      return {count:0,opened:[]};
    const n=record.count;
    const count=Number.isSafeInteger(n)&&n>=0 ? n : 0;
    const raw=Array.isArray(record.opened)?record.opened:[];
    const opened=CHEST_THRESHOLDS.filter(t=>raw.includes(t)&&count>=t);
    return {count,opened};
  }
  const restoredTapRewards=restoreTapRewards();
  let combo=restoredTapRewards.count;
  let opened=new Set(restoredTapRewards.opened);
  function syncTapRewards(){
    gameSave.tapRewardProgress={count:combo,opened:[...opened].sort((a,b)=>a-b)};
  }
  let toastTimer;
  let floatIndex = 0;

  const slots = [
    [15,30],[84,30],
    [11,41],[89,42],
    [17,53],[83,54],
    [22,64],[78,65],
    [31,69],[69,69],
    [28,48],[73,49]
  ];
  const colors = ['blue','gold','white','blue','gold'];

  const fmt = n => Number(n).toLocaleString('ja-JP');

  function fitText(el,max,min){
    if(!el) return;
    let s = max;
    el.style.fontSize = s + 'px';
    while(s > min && (el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight)){
      s -= 1;
      el.style.fontSize = s + 'px';
    }
  }
  const homeLabel = document.querySelector('.v15-home-label');
  const powerLabel = document.querySelector('.v15-top-label');
  const progressLabel = document.querySelector('.v15-progress-label');
  const bonusBox = document.getElementById('bonusBox');
  const keysEl = document.getElementById('keys');
  if(keysEl) keysEl.textContent = fmt(gameSave.keys || 0);
  // インラインstyleで指定するのでCSSのfont-sizeより優先される
  function fitSvg(el,maxW,base,min){
    if(!el) return;
    el.style.fontSize = base + 'px';
    let w = 0;
    try{ w = el.getComputedTextLength(); }catch(e){ return; }
    if(w > maxW && w > 0){
      const s = Math.max(min, Math.floor(base * maxW / w * 10) / 10);
      el.style.fontSize = s + 'px';
    }
  }
  function fitAll(){
    fitSvg(homeLabel,176,25,16);
    fitSvg(powerLabel,236,25,16);
    fitSvg(powerBox,240,46,22);
    fitSvg(ptEl,172,38,18);
    fitSvg(keysEl,82,30,16);
    fitSvg(comboEl,250,80,30);
    fitSvg(progressLabel,110,24,16);
    let labelW = 96;
    try{ labelW = progressLabel.getComputedTextLength() || 96; }catch(e){}
    fitSvg(progressBox, Math.max(60, 284 - (62 + labelW + 12)), 30, 14);
    fitSvg(bonusBox,230,38,18);
  }

  function showToast(msg){
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(()=>toast.classList.remove('show'),1000);
  }


  // ---------- Character training ----------
  const SHARD_TIERS = [[10,3],[30,5],[50,8],[80,10],[150,12]];
  const limitBreakKeyCost = cap => Number.isSafeInteger(cap) && cap >= 50 && cap % 50 === 0 ? cap / 50 : 0;
  let selectedCharId = null;
  const charEl = id => document.getElementById(id);
  const levelCost = level => {
    if(level <= 10) return 3;
    if(level <= 30) return 5;
    if(level <= 50) return 8;
    if(level <= 80) return 10;
    return 12;
  };
  function currentRecord(id){
    const rec = collection[id] || {owned:false,shards:0};
    if(rec.owned && !Number.isFinite(Number(rec.level))) rec.level=1;
    if(rec.owned && !Number.isFinite(Number(rec.cap))) rec.cap=50;
    return rec;
  }
  function totalLevels(){
    return GACHA_CHARACTERS.reduce((a,c)=>a+(collection[c.id]?.owned ? Math.max(1,Math.floor(Number(collection[c.id].level||1))) : 0),0);
  }
  function computeTapPower(){
    return Math.max(1,1+Math.floor(totalLevels()/25)+Math.max(0,Number(gameSave.awakenCount||0)));
  }
  function refreshTapPower(){
    tapPower=computeTapPower();
    gameSave.tapPower=tapPower;
    powerEl.textContent=fmt(tapPower);
    if(characterScreen.classList.contains('active')) charEl('charTapPower').textContent=fmt(tapPower);
    requestAnimationFrame(fitAll);
  }
  const rosterFilter=charEl('charRosterFilter');
  const rosterSort=charEl('charRosterSort');
  function rosterLevel(id){
    const record=currentRecord(id);
    return record.owned?Number(record.level||1):0;
  }
  function renderCharacters(){
    const owned=GACHA_CHARACTERS.filter(c=>collection[c.id]?.owned).length;
    const ownedCount=`${owned} / ${GACHA_CHARACTERS.length}`;
    charEl('charOwned').textContent=ownedCount;
    charEl('charRosterCount').textContent=ownedCount;
    charEl('charTotalLevels').textContent=fmt(totalLevels());
    charEl('charTapPower').textContent=fmt(tapPower);
    charEl('charPT').textContent=fmt(pt);
    charEl('charKeys').textContent=fmt(gameSave.keys||0);
    if(!selectedCharId || !GACHA_CHARACTERS.some(c=>c.id===selectedCharId)){
      selectedCharId=GACHA_CHARACTERS.find(c=>collection[c.id]?.owned)?.id || GACHA_CHARACTERS[0].id;
    }
    const visible=GACHA_CHARACTERS.filter(c=>rosterFilter.value==='all' ||
      Boolean(collection[c.id]?.owned)===(rosterFilter.value==='owned'));
    if(rosterSort.value==='level')visible.sort((a,b)=>rosterLevel(b.id)-rosterLevel(a.id));
    if(rosterSort.value==='rarity')visible.sort((a,b)=>b.rarity-a.rarity);
    charEl('charRosterEmpty').hidden=visible.length>0;
    charEl('characterGrid').innerHTML=visible.map(c=>{
      const rec=currentRecord(c.id), owned=!!rec.owned;
      return `<button type="button" class="char-tile char-gilt ${owned?'':'locked'} ${c.rarity===3?'r3':''} ${c.id===selectedCharId?'selected':''}" data-character-id="${c.id}" aria-label="${c.name}">
        <img loading="lazy" src="${c.image}" alt=""><em>${'★'.repeat(c.rarity)}</em>
        <small>${owned?'Lv'+(rec.level||1):'未所持'}</small>${owned && gameSave.favoriteCharacterId===c.id?'<i class="fav-pin">♥</i>':''}
      </button>`;
    }).join('');
    renderCharacterDetail();
  }
  [rosterFilter,rosterSort].forEach(control=>control.addEventListener('change',()=>{
    renderCharacters();
    charEl('charRosterScroll').scrollTop=0;
  }));
  // TRAIN-RC07: one-tap MAX is separate, while holding applies the selected 1 / 10 batch repeatedly.
  let trainingTapQuantity = 1;
  let trainingHoldActive = false;
  let trainingHoldCount = 0;
  let trainingHoldTimeout = null;
  let trainingHoldInterval = null;
  let ignoreTrainingClick = false;
  let trainingIgnoreReset = null;
  const trainingButton = charEl('charLevelUp');
  const trainingQuantityButtons = [charEl('charQuantity1'),charEl('charQuantity10')];
  const trainingMaxButton = charEl('charQuantityMax');
  function trainingPlan(rec,limit){
    if(!rec || !rec.owned)return {count:0,cost:0};
    const start=Math.max(1,Math.floor(Number(rec.level||1)));
    const cap=Math.max(start,Math.floor(Number(rec.cap||50)));
    let available=Math.max(0,Math.floor(Number(rec.shards||0)));
    let cost=0,count=0;
    while(count<limit && start+count<cap){
      const need=levelCost(start+count);
      if(available<need)break;
      available-=need;cost+=need;count++;
    }
    return {count,cost};
  }
  // MAX reaches the current unlocked cap only; keys are never consumed or caps auto-unlocked.
  // Capped at the saved cap rather than an arbitrary number of levels.
  function maxTrainingPlan(rec){
    if(!rec || !rec.owned)return {count:0,cost:0};
    const start=Math.max(1,Math.floor(Number(rec.level||1)));
    const cap=Math.max(start,Math.floor(Number(rec.cap||50)));
    return trainingPlan(rec,cap-start);
  }
  function refreshTrainingQuantityButtons(){
    trainingQuantityButtons.forEach((btn,i)=>{
      const chosen=(i===0?1:10)===trainingTapQuantity;
      btn.classList.toggle('is-selected',chosen);
      btn.setAttribute('aria-pressed',String(chosen));
    });
  }
  trainingQuantityButtons.forEach((btn,i)=>btn.addEventListener('click',()=>{
    stopTrainingHold();
    trainingTapQuantity=i===0?1:10;
    refreshTrainingQuantityButtons();
    renderCharacterDetail();
  }));
  // A direct MAX action; keeps 1/10 selected for subsequent taps and holds.
  trainingMaxButton.addEventListener('click',()=>{
    stopTrainingHold();
    const plan=maxTrainingPlan(currentRecord(selectedCharId));
    if(plan.count)levelUpCharacter(plan.count);
  });
  function renderCharacterDetail(){
    const c=GACHA_CHARACTERS.find(x=>x.id===selectedCharId) || GACHA_CHARACTERS[0];
    const rec=currentRecord(c.id),owned=!!rec.owned;
    const lv=owned?Math.max(1,Number(rec.level||1)):0;
    const cap=Math.max(50,Number(rec.cap||50));
    const shards=Math.max(0,Number(rec.shards||0));
    const need=levelCost(lv);
    charEl('selectedPortrait').src=c.image;
    const stars='★'.repeat(c.rarity);
    charEl('selectedRarity').textContent=stars;
    charEl('portraitStars').textContent=stars;
    charEl('selectedName').textContent=c.name;
    charEl('selectedTags').textContent=`${c.element}属性  · ${c.tagline}`;
    charEl('selectedLevel').textContent=owned?`Lv ${lv} / ${cap}`:'未所持';
    charEl('charCapBadge').hidden=!owned||lv<cap;
    charEl('selectedShardCount').textContent=owned?`欠片 ${fmt(shards)} / ${need}`:'ガチャで獲得';
    charEl('charShardFill').style.width=owned?Math.min(100,shards/need*100)+'%':'0%';
    const levelBtn=charEl('charLevelUp'),breakBtn=charEl('charLimitBreak');
    const plan=trainingPlan(rec,trainingTapQuantity);
    levelBtn.disabled=!owned||plan.count===0||saveRecoveryBlocked;
    levelBtn.querySelector('.char-action-note').textContent=lv>=cap?'レベル上限':plan.count
      ? `×${plan.count} ・ 欠片 ${fmt(plan.cost)}` : owned?'欠片が足りません':'ガチャで獲得';
    levelBtn.setAttribute('aria-label',plan.count?`タップで${plan.count}レベル上げる。欠片${plan.cost}個。長押しで${trainingTapQuantity}レベルずつ連続育成`:'レベルアップ不可');
    const maxPlan=maxTrainingPlan(rec);
    trainingMaxButton.disabled=!owned||maxPlan.count===0||saveRecoveryBlocked;
    trainingMaxButton.title=maxPlan.count?`上限Lv${cap}まで、最大${maxPlan.count}レベル（欠片${fmt(maxPlan.cost)}）`:'これ以上育成できません';
    refreshTrainingQuantityButtons();
    const keysNeeded=limitBreakKeyCost(cap);
    breakBtn.disabled=!owned||lv<cap||keysNeeded===0||Number(gameSave.keys||0)<keysNeeded;
    breakBtn.querySelector('.char-action-note').textContent=keysNeeded?`（鍵 ${keysNeeded}個）`:'解放完了';
    charEl('charBuyKey').disabled=pt<5000;
    const fbtn=charEl('charFavoriteButton');
    const isFav=owned && gameSave.favoriteCharacterId===c.id;
    fbtn.disabled=!owned;
    fbtn.classList.toggle('is-favorite',isFav);
    fbtn.querySelector('.char-button-ink').textContent=isFav?'★ お気に入り中':'☆ ホームに設定';
    fbtn.setAttribute('aria-pressed',String(isFav));
  }
  function levelUpCharacter(target=trainingTapQuantity,{quiet=false}={}){
    if(saveRecoveryBlocked){if(!quiet)showToast('セーブ保護中です');return 0;}
    const rec=currentRecord(selectedCharId);
    if(!rec.owned)return 0;
    const lv=Math.floor(Number(rec.level||1));
    const plan=trainingPlan(rec,target);
    if(!plan.count){
      if(!quiet)showToast(lv>=Number(rec.cap||50)?'先に上限解放が必要':'欠片が足りません');
      return 0;
    }
    ensureQuestState();
    const priorRec={...rec};
    const previousLevelUps=safeQuestCounter(gameSave.stats.levelUps);
    rec.shards-=plan.cost;
    rec.level=lv+plan.count;
    gameSave.stats.levelUps=previousLevelUps+plan.count;
    collection[selectedCharId]=rec;
    refreshTapPower();
    if(!saveUnified()){
      collection[selectedCharId]=priorRec;
      gameSave.characters=normalizeRosterIds(collection);
      gameSave.stats.levelUps=previousLevelUps;
      refreshTapPower();
      renderCharacters();
      if(!quiet)showToast('保存に失敗したため育成を取り消しました');
      return 0;
    }
    renderCharacters();
    if(!quiet)showToast(`${GACHA_CHARACTERS.find(c=>c.id===selectedCharId).name} +${plan.count} Lv → Lv${rec.level}！`);
    return plan.count;
  }
  function stopTrainingHold(){
    if(trainingHoldTimeout!==null){clearTimeout(trainingHoldTimeout);trainingHoldTimeout=null;}
    if(trainingHoldInterval!==null){clearInterval(trainingHoldInterval);trainingHoldInterval=null;}
    if(trainingHoldActive && trainingHoldCount>0){
      showToast(`長押し育成 +${trainingHoldCount} Lv`);
      ignoreTrainingClick=true;
      clearTimeout(trainingIgnoreReset);
      trainingIgnoreReset=setTimeout(()=>ignoreTrainingClick=false,650);
    }
    trainingHoldActive=false;
    trainingHoldCount=0;
  }
  function trainHoldTick(){
    if(!characterScreen.classList.contains('active') || trainingButton.disabled){stopTrainingHold();return;}
    const changed=levelUpCharacter(trainingTapQuantity,{quiet:true});
    if(changed){trainingHoldCount+=changed;}
    else stopTrainingHold();
  }
  trainingButton.addEventListener('pointerdown',e=>{
    if(trainingButton.disabled || (e.pointerType==='mouse' && e.button!==0))return;
    stopTrainingHold();
    ignoreTrainingClick=false;
    clearTimeout(trainingIgnoreReset);
    trainingHoldTimeout=setTimeout(()=>{
      trainingHoldTimeout=null;
      if(trainingButton.disabled)return;
      trainingHoldActive=true;
      ignoreTrainingClick=true;
      trainHoldTick();
      if(trainingHoldActive)trainingHoldInterval=setInterval(trainHoldTick,trainingTapQuantity===10?200:130);
    },430);
  });
  trainingButton.addEventListener('click',e=>{
    if(ignoreTrainingClick || trainingHoldActive){
      e.preventDefault();
      ignoreTrainingClick=false;
      return;
    }
    levelUpCharacter(trainingTapQuantity);
  });
  trainingButton.addEventListener('contextmenu',e=>e.preventDefault());
  for(const eventName of ['pointerup','pointercancel'])window.addEventListener(eventName,stopTrainingHold,{passive:true});
  window.addEventListener('blur',stopTrainingHold);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopTrainingHold();});
  trainingButton.addEventListener('pointerleave',e=>{
    if(e.pointerType==='mouse')stopTrainingHold();
  });
  function limitBreakCharacter(){
    const rec=currentRecord(selectedCharId);
    if(!rec.owned)return;
    const cap=Number(rec.cap||50);
    const needed=limitBreakKeyCost(cap);
    if(!needed||Number(rec.level||1)<cap){showToast('上限に到達していません');return;}
    if(Number(gameSave.keys||0)<needed){showToast('鍵が足りません');return;}
    gameSave.keys-=needed;rec.cap=cap+50;
    rec.keysUsed=Number(rec.keysUsed||0)+needed;
    collection[selectedCharId]=rec;
    keysEl.textContent=fmt(gameSave.keys);saveUnified();renderCharacters();
    showToast(`レベル上限 ${rec.cap} 解放！`);
  }
  charEl('charBackHome').addEventListener('click',()=>showScreen('home'));
  // TRAIN-RC07: tap=selected 1/10, hold=repeats selected batch, MAX=direct affordable cap.
  charEl('charLimitBreak').addEventListener('click',limitBreakCharacter);
  // DEV-03: both the training quick-purchase button and the Exchange use one safe transaction.
  const KEY_PRICE = 5000;
  function renderShop(){
    document.getElementById('shopPT').textContent=fmt(pt);
    document.getElementById('shopKeys').textContent=fmt(gameSave.keys||0);
    document.getElementById('shopCardKeys').textContent=fmt(gameSave.keys||0);
    const canBuy=pt>=KEY_PRICE && !saveRecoveryBlocked;
    document.getElementById('shopBuyKey').disabled=!canBuy;
    const notice=document.getElementById('shopNotice');
    if(saveRecoveryBlocked) notice.textContent='セーブ保護中のため購入できません';
    else if(pt<KEY_PRICE) notice.textContent=`購入まであと ${fmt(KEY_PRICE-pt)} PT 必要`;
    else notice.textContent='購入するとPTが減り、鍵が1個増えます';
  }
  function buyLimitKey(){
    if(saveRecoveryBlocked){showToast('セーブ保護中のため購入できません');renderShop();return false;}
    if(pt<KEY_PRICE){showToast('PTが足りません');renderShop();return false;}
    const previousPt=pt;
    const previousKeys=Number(gameSave.keys||0);
    pt=previousPt-KEY_PRICE;
    gameSave.keys=previousKeys+1;
    if(!saveUnified()){
      // On storage failure, revert runtime state; never advertise an unsaved purchase.
      pt=previousPt;
      gameSave.points=previousPt;
      gameSave.keys=previousKeys;
      renderCharacters();renderShop();
      showToast('保存できないため購入を中止しました');
      return false;
    }
    keysEl.textContent=fmt(gameSave.keys);
    ptEl.textContent=fmt(pt);
    renderCharacters();renderShop();renderGachaWallet();updateGachaButtons();refreshHome();
    showToast('上限解放の鍵を獲得！');
    return true;
  }
  charEl('charBuyKey').addEventListener('click',buyLimitKey);
  document.getElementById('shopBuyKey').addEventListener('click',buyLimitKey);
  document.getElementById('shopBackHome').addEventListener('click',()=>showScreen('home'));
  document.getElementById('shopGoCharacter').addEventListener('click',()=>showScreen('character'));
  // SHOP-RC01: filter scrollable product cards; never mutate stored gameplay state.
  const shopFilterButtons=[...document.querySelectorAll('#shopScreen [data-shop-filter]')];
  shopFilterButtons.forEach(button=>button.addEventListener('click',()=>{
    const category=button.dataset.shopFilter;
    shopFilterButtons.forEach(b=>{const selected=b===button;b.classList.toggle('active',selected);b.setAttribute('aria-pressed',String(selected));});
    const products=[...document.querySelectorAll('#shopScreen .shop-product')];
    products.forEach(card=>{card.hidden=category!=='all' && card.dataset.shopCategory!==category;});
    document.getElementById('shopEmpty').hidden=products.some(card=>!card.hidden);
    document.getElementById('shopProductScroll').scrollTop=0;
  }));
  // Reuse the exact shared navigation artwork already used on the home screen.
  const originalShopNav=document.querySelector('#homeScreen nav.home-nav');
  if(originalShopNav){
    const shopNav=originalShopNav.cloneNode(true);
    shopNav.className='shop-bottom-nav kit-shared-nav';
    shopNav.setAttribute('aria-label','ショップ下部メニュー');
    shopNav.querySelectorAll('[data-nav]').forEach(button=>{
      button.classList.remove('kit-selected');
      button.addEventListener('click',()=>{
        const name=button.dataset.nav;
        if(name==='ホーム')showScreen('home');
        else if(name==='キャラ')showScreen('character');
        else if(name==='ガチャ')showScreen('gacha');
        else showToast(name+' は準備中です');
      });
    });
    shopScreen.appendChild(shopNav);
  }

  // Reuse the already embedded character-page illustration as a subdued backdrop.
  document.getElementById('shopBackdrop').src='assets/0e8e898dfb8b2abbc3af.webp';
  charEl('characterGrid').addEventListener('click',e=>{
    const b=e.target.closest('[data-character-id]');if(!b)return;
    selectedCharId=b.dataset.characterId;renderCharacters();
  });
  document.querySelectorAll('[data-character-nav]').forEach(btn=>btn.addEventListener('click',()=>{
    const dest=btn.dataset.characterNav;
    if(dest==='ホーム')showScreen('home');
    else if(dest==='ガチャ')showScreen('gacha');
    else if(dest==='キャラ')showScreen('character');
    else showToast(`${dest} は次工程で接続`);
  }));


  // --- Home favorite + dynamic HUD. Only owned characters can be favorites. ---
  const homeEl = id => document.getElementById(id);
  function ownedCharacterById(id){
    return GACHA_CHARACTERS.find(c=>c.id===id && collection[id]?.owned) || null;
  }
  function shownHomeCharacter(){
    return ownedCharacterById(gameSave.favoriteCharacterId) ||
      GACHA_CHARACTERS.find(c=>collection[c.id]?.owned) || null;
  }
  function refreshHome(){
    homeEl('homePT').textContent=fmt(pt);
    homeEl('homeTapPower').textContent=fmt(tapPower);
    homeEl('homeKeys').textContent=fmt(gameSave.keys||0);
    const rank = Number(gameSave.playerRank);
    homeEl('homeRank').textContent=(Number.isFinite(rank)&&rank>0)?fmt(rank):'—';
    const fav=shownHomeCharacter();
    const picture=homeEl('homeFavoriteImage');
    if(fav){
      picture.hidden=false; picture.src=fav.image; picture.alt=fav.name;
      homeEl('homeRankAvatar').src=fav.image;homeEl('homeRankAvatar').hidden=false;
      homeEl('homeFavoriteEmpty').style.display='none';
      homeEl('homeFavoriteStatus').textContent=(gameSave.favoriteCharacterId===fav.id)?'お気に入りキャラ':'所持キャラを表示中';
      homeEl('homeFavoriteName').textContent=fav.name;
      homeEl('homeFavoriteStars').textContent='★'.repeat(fav.rarity);
      homeEl('homeFavoriteLevel').textContent='Lv '+fmt(collection[fav.id]?.level || 1);
    }else{
      picture.hidden=true;picture.removeAttribute('src');picture.alt='';homeEl('homeRankAvatar').hidden=true;homeEl('homeRankAvatar').removeAttribute('src');
      homeEl('homeFavoriteEmpty').style.display='flex';
      homeEl('homeFavoriteStatus').textContent='仲間を迎えよう';
      homeEl('homeFavoriteName').textContent='キャラ未所持';
      homeEl('homeFavoriteStars').textContent='☆';
      homeEl('homeFavoriteLevel').textContent='';
    }
  }
  function chooseFavorite(id){
    if(!ownedCharacterById(id)){showToast('所持しているキャラだけ設定できます');return;}
    gameSave.favoriteCharacterId=(gameSave.favoriteCharacterId===id) ? null : id;
    saveUnified();
    refreshHome();renderCharacters();
    showToast(gameSave.favoriteCharacterId ? 'ホームのお気に入りに設定！' : 'お気に入り設定を解除');
  }
  homeEl('homeChangeFavorite').addEventListener('click',()=>{
    const fav=shownHomeCharacter();if(fav)selectedCharId=fav.id;
    showScreen('character');
  });
  document.querySelectorAll('[data-home-go]').forEach(btn=>btn.addEventListener('click',()=>showScreen(btn.dataset.homeGo)));
  document.querySelectorAll('[data-home-planned]').forEach(btn=>btn.addEventListener('click',()=>showToast(btn.dataset.homePlanned+' は次工程で接続')));
  charEl('charFavoriteButton').addEventListener('click',()=>chooseFavorite(selectedCharId));


  // Mission board UI is deliberately separate from the shop and the approved home design.
  const questScreen=document.getElementById('questScreen');
  let questTab='daily';
  const questArt={};
  const shopImageNodes=[...document.querySelectorAll('#shopScreen .shop-product .shop-icon img')];
  if(shopImageNodes[0])questArt.scroll=shopImageNodes[0].src;
  if(shopImageNodes[1])questArt.potion=shopImageNodes[1].src;
  if(shopImageNodes[2])questArt.crystal=shopImageNodes[2].src;
  if(!questArt.crystal)questArt.crystal=questArt.scroll;
  if(!questArt.potion)questArt.potion=questArt.scroll;
  const questBackdrop=document.getElementById('questBackdrop');
  document.getElementById('questBackHome').addEventListener('click',()=>showScreen('home'));
  const questNavSource=document.querySelector('#homeScreen nav.home-nav');
  if(questNavSource){
    const questNav=questNavSource.cloneNode(true);
    questNav.className='quest-nav kit-shared-nav';
    questNav.setAttribute('aria-label','依頼掲示板の下部メニュー');
    questNav.querySelectorAll('[data-nav]').forEach(button=>{
      button.classList.remove('kit-selected');
      button.addEventListener('click',()=>{
        const target=button.dataset.nav;
        if(target==='ホーム')showScreen('home');
        else if(target==='キャラ')showScreen('character');
        else if(target==='ガチャ')showScreen('gacha');
        else showToast(target+' は準備中です');
      });
    });
    questScreen.appendChild(questNav);
  }
  function syncQuestArtwork(){
    if(!questBackdrop.src){
      const shopBackdrop=document.getElementById('shopBackdrop');
      if(shopBackdrop?.src)questBackdrop.src=shopBackdrop.src;
    }
    if(!questScreen.style.getPropertyValue('--quest-title-art')){
      const pair=[
        ['--quest-title-art','#shopScreen .shop-head h1'],
        ['--quest-home-art','#shopScreen .shop-back'],
        ['--quest-tab-art','#shopScreen .shop-filter:not(.active)'],
        ['--quest-tab-active-art','#shopScreen .shop-filter.active'],
        ['--quest-buy-art','#shopScreen .shop-to-character'],
        ['--quest-disabled-art','#shopScreen .shop-purchase:disabled']
      ];
      pair.forEach(([key,selector])=>{
        const sample=document.querySelector(selector);
        if(sample){const img=getComputedStyle(sample).backgroundImage;
          if(img&&img!=='none')questScreen.style.setProperty(key,img);}
      });
    }
  }
  function showQuestReward(amount){
    const modal=document.getElementById('questRewardModal');
    document.getElementById('questRewardAmount').textContent=`+${fmt(amount)} PT`;
    modal.classList.add('open');modal.setAttribute('aria-hidden','false');
    document.getElementById('questRewardClose').focus();
  }
  function closeQuestReward(){
    const modal=document.getElementById('questRewardModal');
    modal.classList.remove('open');modal.setAttribute('aria-hidden','true');
  }
  document.getElementById('questRewardClose').addEventListener('click',closeQuestReward);
  document.getElementById('questRewardModal').addEventListener('click',e=>{if(e.target.id==='questRewardModal')closeQuestReward()});
  function claimQuest(id){
    ensureQuestState();
    const item=(QUEST_ITEMS[questTab]||[]).find(it=>it.id===id);
    if(!item)return;
    if(saveRecoveryBlocked){showToast('セーブ保護中のため報酬を受け取れません');return;}
    const record=gameSave.quests[questTab];
    if(!record||record.claimed[id]||questProgress(questTab,item)<item.goal)return;
    const prevPT=pt;
    record.claimed[id]=true;
    pt+=item.reward;
    if(!saveUnified()){
      pt=prevPT;gameSave.points=prevPT;delete record.claimed[id];
      showToast('保存できないため受取を中止しました');renderQuest();return;
    }
    ptEl.textContent=fmt(pt);
    renderGachaWallet();updateGachaButtons();refreshHome();
    renderQuest();showQuestReward(item.reward);
  }
  function renderQuest(){
    syncQuestArtwork();
    ensureQuestState();
    const items=QUEST_ITEMS[questTab]||[];
    document.getElementById('questPT').textContent=fmt(pt);
    document.getElementById('questClaimed').textContent=`${items.filter(it=>gameSave.quests[questTab]?.claimed?.[it.id]).length} / ${items.length}`;
    const captions={daily:'毎日 0:00（日本時間）に更新',weekly:'毎週 月曜 0:00（日本時間）に更新',milestone:'累計記録・受取は各1回まで',limited:'期間限定の依頼は準備中です'};
    document.getElementById('questRefresh').textContent=captions[questTab];
    document.querySelectorAll('#questScreen [data-quest-tab]').forEach(btn=>{
      const on=btn.dataset.questTab===questTab;
      btn.classList.toggle('active',on);btn.setAttribute('aria-pressed',String(on));
    });
    const list=document.getElementById('questList');
    if(questTab==='limited'){
      list.innerHTML='<div class="quest-section-heading">期間限定 <span>準備中</span></div><div class="quest-empty">期間限定の依頼は、イベント機能の実装後に追加する予定です。<br>現時点では報酬や進捗は発生しません。</div>';
      return;
    }
    const title={daily:'デイリー依頼',weekly:'ウィークリー依頼',milestone:'累計実績'}[questTab];
    const readyCount=items.filter(it=>questProgress(questTab,it)>=it.goal&&!gameSave.quests[questTab].claimed[it.id]).length;
    const heading=document.createElement('div');heading.className='quest-section-heading';heading.textContent=title;
    const note=document.createElement('span');note.textContent=readyCount?`受取可能 ${readyCount}件`:'依頼を達成してPTを獲得';heading.appendChild(note);
    list.replaceChildren(heading);
    for(const it of items){
      const prog=questProgress(questTab,it),done=prog>=it.goal,claimed=!!gameSave.quests[questTab].claimed[it.id];
      const card=document.createElement('article');card.className='quest-card'+(claimed?' is-claimed':done?' is-ready':'');
      const icon=document.createElement('img');icon.className='quest-symbol';icon.src=questArt[it.art]||questArt.crystal;icon.alt='';
      const detail=document.createElement('div');detail.className='quest-detail';
      const h=document.createElement('h2');h.className='quest-name';h.textContent=it.title;
      const desc=document.createElement('p');desc.className='quest-explain';desc.textContent=it.detail;
      const meterRow=document.createElement('div');meterRow.className='quest-progress-line';
      const meter=document.createElement('div');meter.className='quest-meter';meter.setAttribute('role','progressbar');meter.setAttribute('aria-label',it.title);meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax',String(it.goal));meter.setAttribute('aria-valuenow',String(Math.min(it.goal,prog)));
      const fill=document.createElement('span');fill.style.width=(100*Math.min(it.goal,prog)/it.goal)+'%';meter.appendChild(fill);
      const num=document.createElement('span');num.className='quest-fraction';num.textContent=`${fmt(Math.min(it.goal,prog))} / ${fmt(it.goal)}`;meterRow.append(meter,num);
      const footer=document.createElement('div');footer.className='quest-card-foot';
      const bounty=document.createElement('span');bounty.className='quest-bounty';bounty.textContent=`💎 ${fmt(it.reward)} PT`;
      const btn=document.createElement('button');btn.type='button';btn.className='quest-claim';btn.textContent=claimed?'受取済':done?'受け取る':'挑戦中';
      btn.disabled=claimed||!done;btn.addEventListener('click',()=>claimQuest(it.id));
      footer.append(bounty,btn);detail.append(h,desc,meterRow,footer);card.append(icon,detail);list.appendChild(card);
    }
  }
  document.querySelectorAll('#questScreen [data-quest-tab]').forEach(button=>button.addEventListener('click',()=>{
    questTab=button.dataset.questTab;document.getElementById('questList').scrollTop=0;renderQuest();
  }));

  function showScreen(which){
    const toHome = which === 'home';
    const toTap = which === 'tap';
    const toGacha = which === 'gacha';
    const toCharacter = which === 'character';
    const toShop = which === 'shop';
    const toQuest = which === 'quest';

    home.classList.toggle('active',toHome);
    tap.classList.toggle('active',toTap);
    gacha.classList.toggle('active',toGacha);
    characterScreen.classList.toggle('active',toCharacter);
    shopScreen.classList.toggle('active',toShop);
    questScreen.classList.toggle('active',toQuest);
    if(!toQuest)closeQuestReward();
    document.getElementById('devBuildLabel').style.display=toQuest?'none':'';
    if(toQuest)renderQuest();
    if(toShop) renderShop();
    if(toCharacter) renderCharacters();
    if(toHome) refreshHome();

    if(toTap){
      // Do not erase the next-chest progress when revisiting the tap screen.
      comboEl.textContent = fmt(combo);
      ptEl.textContent = fmt(pt);
      powerEl.textContent = fmt(tapPower);
      updateProgress();
      updateChests();
      requestAnimationFrame(fitAll);
    }

    if(toGacha){
      renderGachaWallet();
      renderOwnedCount();
      updateGachaButtons();
    }
  }

  function updateProgress(){
    const targets = [200,500,1000];
    const target = targets.find(t=>combo<t) || 1000;
    const prev = target===200 ? 0 : (target===500 ? 200 : 500);
    const within = Math.max(0,combo-prev);
    const span = target-prev;
    const percent = (target===1000 && combo>=1000) ? 100 : Math.min(100,(within/span)*100);

    progressNow.textContent = fmt(combo);
    progressTarget.textContent = fmt(target);
    progressFill.setAttribute('width', String(226 * percent / 100));
    requestAnimationFrame(fitAll);
  }

  function updateChests(){
    chestButtons.forEach(btn=>{
      const threshold = Number(btn.dataset.threshold);
      btn.classList.remove('locked','ready','opened');
      if(opened.has(threshold)){
        btn.classList.add('opened');
        btn.style.pointerEvents = 'auto';
      }else if(combo >= threshold){
        btn.classList.add('ready');
        btn.style.pointerEvents = 'auto';
      }else{
        btn.classList.add('locked');
        btn.style.pointerEvents = 'none';
      }
    });
  }

  function spawnPT(){
    const base = slots[floatIndex % slots.length];
    floatIndex++;
    const x = base[0] + (Math.random()*4 - 2);
    const y = base[1] + (Math.random()*3 - 1.5);
    const tone = colors[Math.floor(Math.random()*colors.length)];

    const node = document.createElement('div');
    node.className = 'pt-float ' + tone;
    node.textContent = '+' + fmt(tapPower) + ' PT';
    node.style.left = x + '%';
    node.style.top = y + '%';
    tap.appendChild(node);
    node.addEventListener('animationend',()=>node.remove(),{once:true});

    for(let i=0;i<2;i++){
      const sp = document.createElement('i');
      sp.className = 'pt-spark';
      sp.style.left = (x + (Math.random()*8 - 4)) + '%';
      sp.style.top = (y + (Math.random()*5 - 2.5)) + '%';
      sp.style.color = tone==='gold' ? '#ffd56a' : (tone==='white' ? '#e8fbff' : '#67d7ff');
      tap.appendChild(sp);
      sp.addEventListener('animationend',()=>sp.remove(),{once:true});
    }
  }


  function saveCollection(){
    saveUnified();
  }

  function renderGachaWallet(){
    if(gachaPTEl) gachaPTEl.textContent = fmt(pt);
  }

  function renderOwnedCount(){
    const owned = GACHA_CHARACTERS.filter(c => collection[c.id]?.owned).length;
    if(ownedCountEl) ownedCountEl.textContent = String(owned);
  }

  function updateGachaButtons(){
    gachaDrawButtons.forEach(btn => {
      const pulls = Number(btn.dataset.pulls);
      btn.disabled = pt < pulls;
    });
  }

  function rollRarity(){
    const r = Math.random() * 100;
    if(r < 5) return 3;
    if(r < 30) return 2;
    return 1;
  }

  function randomCharacterOfRarity(rarity){
    const pool = GACHA_CHARACTERS.filter(c => c.rarity === rarity);
    return pool[Math.floor(Math.random() * pool.length)];
  }

  function createRawDraws(pulls){
    const draws = [];
    for(let i=0;i<pulls;i++){
      const rarity = rollRarity();
      draws.push(randomCharacterOfRarity(rarity));
    }

    // 10連：★2以上が0体なら10枠目を★2以上抽選へ置換。
    if(pulls === 10 && !draws.some(c => c.rarity >= 2)){
      // 通常率25:5を条件付きで再正規化。
      const guaranteedRarity = Math.random() < (5 / (25 + 5)) ? 3 : 2;
      draws[9] = randomCharacterOfRarity(guaranteedRarity);
    }

    // 100連：★3が0体なら100枠目を★3へ置換。
    if(pulls === 100 && !draws.some(c => c.rarity === 3)){
      draws[99] = randomCharacterOfRarity(3);
    }

    // 1000連：★3最低10体保証。
    if(pulls === 1000){
      let star3 = draws.filter(c => c.rarity === 3).length;
      if(star3 < 10){
        let need = 10 - star3;
        for(let i=draws.length-1; i>=0 && need>0; i--){
          if(draws[i].rarity !== 3){
            draws[i] = randomCharacterOfRarity(3);
            need--;
          }
        }
      }
    }
    return draws;
  }

  function applyCollection(draws){
    const results = [];
    draws.forEach(c => {
      const prev = collection[c.id] || {owned:false, shards:0};
      const isNew = !prev.owned;
      const priorCount = Math.max(0, Number(prev.count || (prev.owned ? 1 : 0)));
      const nextCount = priorCount + 1;
      const nextShards = Math.max(0, Number(prev.shards || 0)) + (isNew ? 0 : 1);
      collection[c.id] = {...prev, owned:true, count:nextCount, shards:nextShards};
      results.push({...c, isNew, shardGain:isNew ? 0 : 1,
        ownedCount:nextCount, shardTotal:nextShards});
    });
    saveCollection();
    return results;
  }

  function stars(n){
    return '★'.repeat(n);
  }

  function resultCardHtml(r){
    return `
      <div class="gacha-card star${r.rarity}${r.rarity === 3 ? ' just-drawn' : ''}${r.isNew ? ' is-new' : ''}">
        <img class="char-thumb" src="${r.image}" alt="">
        <div class="char-copy">
          <span class="rarity">${stars(r.rarity)}</span>
          <span class="name">${r.name}</span>
          <span class="element">${r.element}</span>
          <span class="tagline">${r.tagline}</span>
          <span class="gain">${r.isNew ? 'NEW・所持 ×1' : `欠片 +1（計${fmt(r.shardTotal)}）`}<span class="owned-total"> · 所持 ×${fmt(r.ownedCount)}</span></span>
        </div>
      </div>`;
  }

  function renderSmallResults(results){
    const single = results.length === 1 ? ' single' : '';
    gachaResultEl.innerHTML = `<div class="gacha-card-grid${single}">${results.map(resultCardHtml).join('')}</div>`;
    gachaResultEl.scrollTop = 0;
  }

  function renderSummary(results, pulls){
    const rarityCounts = {1:0,2:0,3:0};
    const charCounts = {};
    results.forEach(r => {
      rarityCounts[r.rarity]++;
      charCounts[r.id] = (charCounts[r.id] || 0) + 1;
    });

    const rows = GACHA_CHARACTERS
      .filter(c => charCounts[c.id])
      .sort((a,b) => b.rarity-a.rarity || a.id.localeCompare(b.id))
      .map(c => `
        <div class="summary-row ${c.rarity===3?'star3':''}">
          <img class="summary-thumb" src="${c.image}" alt="">
          <span class="s-name">${stars(c.rarity)} ${c.name}</span>
          <span class="s-count">×${fmt(charCounts[c.id])}<small style="display:block;font:8px sans-serif;color:#d4f4ff">欠片 ${fmt(collection[c.id]?.shards || 0)} · 所持 ${fmt(collection[c.id]?.count || 1)}</small></span>
        </div>`).join('');

    const note =
      pulls === 1000 ? '1000連：★3最低10体保証' :
      pulls === 100 ? '100連：★3 1体保証' :
      `${pulls}回召喚・集計結果`;
    gachaResultEl.innerHTML = `
      <div class="gacha-summary">
        <div class="summary-head">
          <div class="summary-rarity"><span>★1</span><b>${fmt(rarityCounts[1])}</b></div>
          <div class="summary-rarity"><span>★2</span><b>${fmt(rarityCounts[2])}</b></div>
          <div class="summary-rarity"><span>★3</span><b>${fmt(rarityCounts[3])}</b></div>
        </div>
        <div class="summary-list">${rows}</div>
        <div class="summary-note">${note}</div>
      </div>`;
    gachaResultEl.scrollTop = 0;
  }

  function flashGacha(hasStar3){
    gachaFlashEl.classList.remove('go','star3go');
    void gachaFlashEl.offsetWidth;
    gachaFlashEl.classList.add('go');
  }

  function performGacha(pulls){
    const cost = pulls; // v1: 1回=1PT
    if(pt < cost){
      showToast('PTが足りません');
      return;
    }

    ensureQuestState();
    pt -= cost;
    saveUnified();
    ptEl.textContent = fmt(pt);
    renderGachaWallet();

    const raw = createRawDraws(pulls);
    const results = applyCollection(raw);
    refreshTapPower();
    saveUnified();
    const star3Count = results.filter(r => r.rarity === 3).length;
    const hasStar3 = star3Count > 0;

    gameSave.stats.gachaPulls = Math.max(0,Number(gameSave.stats.gachaPulls||0)) + pulls;
    gameSave.stats.star3Pulls = Math.max(0,Number(gameSave.stats.star3Pulls||0)) + star3Count;
    saveUnified();

    if(pulls <= 10) renderSmallResults(results);
    else renderSummary(results,pulls);

    renderOwnedCount();
    updateGachaButtons();
    flashGacha(hasStar3);

    if(hasStar3 && navigator.vibrate) navigator.vibrate([20,35,28]);
  }

  function openChest(btn){
    const threshold = Number(btn.dataset.threshold);
    if(combo < threshold || opened.has(threshold)) return;

    opened.add(threshold);
    syncTapRewards();
    if(!saveUnified()){
      opened.delete(threshold);
      syncTapRewards();
      updateChests();
      showToast('保存できなかったため、宝箱の受取を確定できませんでした');
      return;
    }
    updateChests();

    const r = btn.getBoundingClientRect();
    const tr = tap.getBoundingClientRect();
    const burst = document.createElement('div');
    burst.className = 'chest-burst';
    burst.style.left = (r.left-tr.left+r.width/2) + 'px';
    burst.style.top = (r.top-tr.top+r.height/2) + 'px';
    tap.appendChild(burst);
    burst.addEventListener('animationend',()=>burst.remove(),{once:true});

    if(navigator.vibrate) navigator.vibrate(22);
    showToast(threshold + '回 宝箱を開封！　報酬内容は未設定');
  }

  document.getElementById('goTap').addEventListener('click',()=>showScreen('tap'));
  document.getElementById('backHome').addEventListener('click',()=>showScreen('home'));

  const growHit = document.querySelector('.home-hit.train');
  if(growHit) growHit.addEventListener('click',()=>showScreen('character'));
  const summonHit = document.querySelector('.home-hit.summon');
  if(summonHit) summonHit.addEventListener('click',()=>showScreen('gacha'));

  document.querySelectorAll('.home-nav [data-nav]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const dest = btn.dataset.nav;
      if(dest === 'ホーム') showScreen('home');
      else if(dest === 'ガチャ') showScreen('gacha');
      else if(dest === 'キャラ') showScreen('character');
      else showToast(dest + ' は次工程で接続');
    });
  });

  document.getElementById('gachaBackHome').addEventListener('click',()=>showScreen('home'));

  document.querySelectorAll('[data-gacha-nav]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const dest = btn.dataset.gachaNav;
      if(dest === 'ホーム') showScreen('home');
      else if(dest === 'ガチャ') showScreen('gacha');
      else if(dest === 'キャラ') showScreen('character');
      else showToast(dest + ' は次工程で接続');
    });
  });

  gachaDrawButtons.forEach(btn=>{
    btn.addEventListener('click',()=>{
      performGacha(Number(btn.dataset.pulls));
    });
  });

  chestButtons.forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.stopPropagation();
      openChest(btn);
    });
  });

  tapZone.addEventListener('pointerdown',e=>{
    e.preventDefault();

    if(saveRecoveryBlocked){showToast('セーブ保護中のためタップを保存できません');return;}
    ensureQuestState();
    const prevPT=pt,prevCombo=combo;
    const prevTaps=Number(gameSave.stats.taps||0);
    pt += tapPower;
    combo += 1;
    gameSave.stats.taps = Math.max(0,prevTaps) + 1;
    syncTapRewards();
    if(!saveUnified()){
      pt=prevPT; combo=prevCombo; gameSave.stats.taps=prevTaps;
      syncTapRewards();
      showToast('保存に失敗したためタップを確定できませんでした');
      return;
    }
    ptEl.textContent = fmt(pt);
    comboEl.textContent = fmt(combo);

    spawnPT();
    updateProgress();
    updateChests();
    requestAnimationFrame(fitAll);

    if(combo % 10 === 0 && navigator.vibrate) navigator.vibrate(16);
  });

  window.addEventListener('resize',()=>requestAnimationFrame(fitAll));
  window.addEventListener('pagehide',()=>saveUnified());
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')saveUnified();});

  window.tapGacha = {
    getPT:()=>pt,
    setPT(v){
      pt = Math.max(0,Number(v)||0);
      saveUnified();
      ptEl.textContent = fmt(pt);
      renderGachaWallet();
      updateGachaButtons();
      requestAnimationFrame(fitAll);
    },
    getTapPower:()=>tapPower,
    setTapPower(v){
      tapPower = Math.max(1,Number(v)||1);
      saveUnified();
      powerEl.textContent = fmt(tapPower);
      requestAnimationFrame(fitAll);
    },
    getCombo:()=>combo,
    setCombo(v){
      combo = Math.max(0,Math.floor(Number(v)||0));
      comboEl.textContent = fmt(combo);
      updateProgress();
      updateChests();
      requestAnimationFrame(fitAll);
    },
    getChestStates(){
      return chestButtons.map(btn=>({
        threshold:Number(btn.dataset.threshold),
        state:btn.classList.contains('opened')?'opened':btn.classList.contains('ready')?'ready':'locked'
      }));
    },
    getSave(){
      return JSON.parse(JSON.stringify(gameSave));
    },
    getMigrationInfo(){
      return JSON.parse(JSON.stringify(gameSave.migration || {}));
    },
    exportSave(){
      return JSON.stringify(gameSave,null,2);
    },
    forceSave(){
      saveUnified();
      return true;
    }
  };

  if(!gameSave.tapPowerFormulaV1){gameSave.tapPowerFormulaV1=true;}
  refreshTapPower();
  saveUnified();
  renderGachaWallet();
  renderOwnedCount();
  updateGachaButtons();
  refreshHome();
  requestAnimationFrame(fitAll);
})();
