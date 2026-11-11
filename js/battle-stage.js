(() => {
  'use strict';

  const rules = globalThis.TapGachaBattle;
  const positions = {
    1: [[30, 68]],
    2: [[28, 52], [22, 85]],
    3: [[22, 40], [31, 65], [22, 90]]
  };
  const skillLabels = { heal: '回復', shield: '盾', hit: '攻撃' };
  const formatNumber = new Intl.NumberFormat('ja-JP');
  const compactNumber = new Intl.NumberFormat('ja-JP', { notation: 'compact', maximumFractionDigits: 1 });
  const percent = unit => Math.min(100, Math.ceil(100 * unit.hp / unit.maxHp));

  function createController(root, onBack) {
    const get = id => root.querySelector('#' + id);
    const field = get('stageField');
    const actors = get('stageActors');
    const effects = get('stageEffects');
    const partyCards = get('stageParty');
    const cardTemplate = get('stageCardTemplate');
    const status = get('stageStatus');
    const elapsed = get('stageElapsed');
    const startButton = get('stageStart');
    const difficultySelect = get('stageDifficulty');
    const enemyStats = get('stageEnemyStats');
    const resetButton = get('stageReset');
    const speedButton = get('stageSpeed');
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    const runningAnimations = new Set();
    const actorViews = new Map();
    const cardViews = new Map();
    let battle = null;
    let mode = 'closed';
    let trial = false;
    let speed = 1;
    let frame = 0;
    let lastUpdate = 0;
    let loadGeneration = 0;
    let latestSkill = '';

    function cancelFrame() {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
    }

    function clearEffects() {
      runningAnimations.forEach(animation => animation.cancel());
      runningAnimations.clear();
      effects.replaceChildren();
    }

    function actor(unit, x, y, enemy = false) {
      const node = document.createElement('div');
      node.className = 'stage-actor' + (enemy ? ' stage-enemy' : '');
      node.style.left = x + '%';
      node.style.top = y + '%';
      node.dataset.unit = unit.id;
      const sprite = new Image();
      sprite.src = unit.sprite;
      sprite.alt = unit.name;
      sprite.draggable = false;
      const bar = document.createElement('span');
      bar.className = 'stage-field-hp';
      bar.setAttribute('aria-hidden', 'true');
      node.append(sprite, bar);
      if (enemy) {
        const caption = document.createElement('span');
        caption.className = 'stage-enemy-caption';
        caption.textContent = unit.name;
        node.append(caption);
      }
      actors.append(node);
      actorViews.set(unit.id, { node, sprite });
      return sprite;
    }

    function card(ally) {
      const slot = cardTemplate.content.firstElementChild.cloneNode(true);
      slot.dataset.unit = ally.id;
      const image = slot.querySelector('img');
      const tile = slot.querySelector('.stage-card');
      const hp = slot.querySelector('.stage-card-hp');
      const hpText = slot.querySelector('.stage-hp-number');
      const front = slot.querySelector('.stage-front');
      const skill = slot.querySelector('button');
      const skillStatus = slot.querySelector('small');
      image.src = ally.portrait;
      slot.querySelector('.stage-level').textContent = 'Lv' + compactNumber.format(ally.level);
      slot.querySelector('.stage-name').textContent = ally.name;
      slot.querySelector('.stage-stats').textContent =
        'HP ' + compactNumber.format(ally.maxHp) + ' · 攻 ' + compactNumber.format(ally.attack);
      slot.querySelector('.stage-stats').title =
        '最大HP ' + formatNumber.format(ally.maxHp) + ' / 攻撃力 ' + formatNumber.format(ally.attack);
      hp.setAttribute('aria-label', ally.name + 'のHP');
      skill.querySelector('span').textContent = ally.skill.name + '・' + skillLabels[ally.skill.kind];
      skill.addEventListener('click', () => {
        if (mode !== 'running' || skill.disabled) return;
        advanceClock(performance.now());
        if (mode !== 'running') return;
        playEffects(battle.requestSkill(ally.id));
        render();
      });
      partyCards.append(slot);
      cardViews.set(ally.id, { tile, hp, hpText, front, skill, skillStatus });
      return image;
    }

    function setText(node, text) {
      if (node.textContent !== text) node.textContent = text;
    }

    function render() {
      root.dataset.mode = mode;
      startButton.disabled = !battle || mode === 'loading' || mode === 'error' || mode === 'closed';
      difficultySelect.disabled = !['ready', 'victory', 'defeat'].includes(mode);
      resetButton.disabled = startButton.disabled;
      speedButton.disabled = startButton.disabled;
      setText(speedButton, '×' + speed);
      speedButton.setAttribute('aria-label', '戦闘速度 ' + speed + '倍');
      if (!battle) return;
      const state = battle.state;
      difficultySelect.value = state.difficulty;
      setText(enemyStats, '敵HP ' + state.enemy.maxHp + ' · 攻 ' + state.enemy.attack);
      const front = state.allies.find(ally => ally.hp > 0);
      for (const unit of [...state.allies, state.enemy]) {
        const { node } = actorViews.get(unit.id);
        node.style.setProperty('--stage-hp', percent(unit) + '%');
        node.dataset.defeated = String(unit.hp === 0);
        node.dataset.shielded = String(unit.shield > 0 && unit.hp > 0);
      }
      for (const ally of state.allies) {
        const view = cardViews.get(ally.id);
        const remaining = Math.max(0, Math.ceil((ally.skillReadyAt - state.time) / 1000));
        const skillState = battle.skillStatus(ally);
        const labels = {
          defeated: '戦闘不能', finished: '戦闘終了', queued: '予約中 · 取消',
          cooldown: 'あと' + remaining + '秒', full: '味方が全快', waiting: '待機中', ready: '発動可能'
        };
        const label = mode === 'ready' ? '開始後に使用' : mode === 'paused' ? '一時停止' : labels[skillState];
        view.tile.dataset.defeated = String(ally.hp === 0);
        view.tile.dataset.shielded = String(ally.shield > 0 && ally.hp > 0);
        view.front.hidden = front !== ally;
        view.hp.style.setProperty('--stage-hp', percent(ally) + '%');
        view.hp.setAttribute('aria-valuenow', percent(ally));
        view.hp.setAttribute('aria-valuetext', ally.hp + ' / ' + ally.maxHp);
        setText(view.hpText, percent(ally) + '%');
        view.skill.disabled = mode !== 'running' || !['ready', 'queued'].includes(skillState);
        view.skill.dataset.queued = String(skillState === 'queued');
        view.skill.setAttribute('aria-label', ally.name + 'の' + ally.skill.name + ' · ' + label);
        setText(view.skillStatus, label);
      }
      const text = {
        loading: '戦闘の準備中…', ready: '戦闘開始を押してください',
        running: latestSkill || '通常攻撃は自動 · スキルはタップ',
        paused: '一時停止中', error: '画像を読み込めませんでした',
        victory: '勝利 · 生存 ' + state.allies.filter(ally => ally.hp > 0).length + ' / ' + state.allies.length + '体',
        defeat: '敗北 · もう一度挑戦できます'
      };
      const buttons = { running: '一時停止', paused: '再開', victory: '再戦', defeat: '再戦' };
      setText(startButton, buttons[mode] || '戦闘開始');
      setText(status, text[mode] || '');
      setText(elapsed, (Math.floor(state.time / 100) / 10).toFixed(1) + '秒');
      get('stageTrialLabel').hidden = !trial;
    }

    function animate(node, frames, timing, remove = false) {
      const animation = node.animate(frames, timing);
      animation.updatePlaybackRate(speed);
      runningAnimations.add(animation);
      const clean = () => {
        runningAnimations.delete(animation);
        if (remove) node.remove();
      };
      animation.finished.then(clean, clean);
    }

    function playEffects(events) {
      if (!events.length) return;
      const spell = events.findLast(event => event.skill);
      if (spell) {
        const caster = battle.state.allies.find(ally => ally.id === spell.from);
        const messages = { heal: 'HPを回復', shield: 'シールドを付与', hit: '強力な一撃' };
        latestSkill = caster.skill.name + ' · ' + messages[spell.kind];
      }
      if (motion.matches) return;
      const scene = field.getBoundingClientRect();
      const participants = [...battle.state.allies, battle.state.enemy];
      events.filter(event => event.time >= battle.state.time - 550).slice(-6).forEach((event, index) => {
        const attacker = actorViews.get(event.from);
        const target = actorViews.get(event.to).node.getBoundingClientRect();
        const delay = index * 50;
        const popup = document.createElement('span');
        popup.className = 'stage-impact stage-impact-' + event.kind;
        popup.style.left = target.left + target.width / 2 - scene.left + (index % 3 - 1) * 15 + 'px';
        popup.style.top = target.top + target.height * 0.28 - scene.top + 'px';
        popup.style.setProperty('--impact-color', participants.find(unit => unit.id === event.from).color);
        popup.textContent = event.kind === 'shield' ? '盾 +' + event.amount
          : event.kind === 'heal' ? '+' + event.amount
          : event.amount ? '−' + event.amount : '防御';
        effects.append(popup);
        animate(popup, [
          { opacity: 0, transform: 'translate(-50%, 4px) scale(.8)' },
          { opacity: 1, transform: 'translate(-50%, -4px) scale(1.05)', offset: 0.2 },
          { opacity: 1, transform: 'translate(-50%, -15px)', offset: 0.65 },
          { opacity: 0, transform: 'translate(-50%, -29px)' }
        ], { delay, duration: 430, fill: 'both' }, true);

        if (event.kind === 'hit') {
          const distance = event.from === 'guardian' ? -18 : event.from === 'c001' ? 7 : 22;
          animate(attacker.sprite, [
            { transform: 'translate(0, 0)' },
            { transform: 'translate(' + distance + 'px, -4px)', offset: 0.33 },
            { transform: 'translate(0, 0)' }
          ], { delay, duration: 350, easing: 'ease-in-out' });
        }
      });
    }

    function advanceClock(now) {
      const delta = Math.max(0, now - lastUpdate);
      lastUpdate = Math.max(lastUpdate, now);
      const events = battle.advanceTo(battle.state.time + delta * speed);
      playEffects(events);
      if (battle.state.result) mode = battle.state.result;
      render();
    }

    function tick(now) {
      frame = 0;
      if (mode !== 'running') return;
      if (document.hidden) {
        pause(false);
        return;
      }
      advanceClock(now);
      if (mode === 'running') frame = requestAnimationFrame(tick);
    }

    function pause(advance = true) {
      if (mode !== 'running') return;
      if (advance) advanceClock(performance.now());
      if (mode !== 'running') return;
      mode = 'paused';
      cancelFrame();
      runningAnimations.forEach(animation => animation.pause());
      render();
    }

    function start() {
      if (document.hidden || !['ready', 'paused'].includes(mode)) return;
      mode = 'running';
      lastUpdate = performance.now();
      runningAnimations.forEach(animation => animation.play());
      frame = requestAnimationFrame(tick);
      render();
    }

    function load(members, isTrial = false, difficulty = 'normal') {
      const nextBattle = rules.createBattle(members, difficulty);
      const generation = ++loadGeneration;
      cancelFrame();
      clearEffects();
      actors.replaceChildren();
      partyCards.replaceChildren();
      actorViews.clear();
      cardViews.clear();
      battle = nextBattle;
      trial = isTrial;
      latestSkill = '';
      mode = 'loading';
      const images = [];
      battle.state.allies.forEach((ally, index) => {
        const [x, y] = positions[members.length][index];
        images.push(actor(ally, x, y), card(ally));
      });
      images.push(actor(battle.state.enemy, 76, 72, true));
      render();
      return Promise.all(images.map(image => image.decode())).then(() => {
        if (generation !== loadGeneration) return false;
        mode = 'ready';
        render();
        return true;
      }, () => {
        if (generation === loadGeneration) {
          mode = 'error';
          render();
        }
        return false;
      });
    }

    function reset(restart, difficulty = battle?.state.difficulty) {
      if (!battle || resetButton.disabled) return;
      const members = battle.state.allies.map(({ id, level }) => ({ id, level }));
      load(members, trial, difficulty).then(ready => {
        if (ready && restart) start();
      });
    }

    function close() {
      loadGeneration++;
      cancelFrame();
      clearEffects();
      battle = null;
      mode = 'closed';
      render();
    }

    startButton.addEventListener('click', () => {
      if (mode === 'running') pause();
      else if (mode === 'victory' || mode === 'defeat') reset(true);
      else start();
    });
    resetButton.addEventListener('click', () => reset(false));
    difficultySelect.addEventListener('change', () => {
      if (!difficultySelect.disabled) reset(false, difficultySelect.value);
    });
    speedButton.addEventListener('click', () => {
      if (mode === 'running') advanceClock(performance.now());
      speed = speed === 1 ? 2 : 1;
      runningAnimations.forEach(animation => animation.updatePlaybackRate(speed));
      render();
    });
    get('stageBack').addEventListener('click', onBack);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) pause(false);
    });
    window.addEventListener('pagehide', () => pause(false));
    motion.addEventListener('change', () => {
      if (motion.matches) clearEffects();
    });

    return { load, close };
  }

  globalThis.TapGachaBattleStage = Object.freeze({ createController });
})();
