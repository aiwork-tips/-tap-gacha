(() => {
  'use strict';

  const characters = {
    c001: {
      name: '白翼のアルム', rarity: 1, baseHp: 120, baseAttack: 14,
      sprite: 'assets/rc25-alum.webp', portrait: 'assets/rc25-icon-c001.webp',
      color: '#ffe4a0', skill: { name: '聖光', kind: 'heal', multiplier: 3, cooldown: 10000 }
    },
    c002: {
      name: '鉄骸兵', rarity: 1, baseHp: 180, baseAttack: 12,
      sprite: 'assets/rc25-iron.webp', portrait: 'assets/rc25-icon-c002.webp',
      color: '#ffae64', skill: { name: '鉄壁', kind: 'shield', multiplier: 0.1, duration: 6000, cooldown: 12000 }
    },
    c003: {
      name: '冥牙クロウル', rarity: 1, baseHp: 100, baseAttack: 22,
      sprite: 'assets/rc25-wolf.webp', portrait: 'assets/rc25-icon-c003.webp',
      color: '#dab1ff', skill: { name: '冥牙', kind: 'hit', multiplier: 2.5, cooldown: 10000 }
    },
    c004: {
      name: '夜叉', rarity: 1, baseHp: 120, baseAttack: 20,
      sprite: 'assets/rc30-yasha.webp', portrait: 'assets/deed14cad6bd683d64ea.webp',
      color: '#ff9b61', skill: { name: '紅刃', kind: 'hit', multiplier: 2.8, cooldown: 12000 }
    },
    c005: {
      name: '黒耀ヴァルグ', rarity: 1, baseHp: 110, baseAttack: 20,
      sprite: 'assets/rc30-varg.webp', portrait: 'assets/a888dd42bddf1a78481f.webp',
      color: '#db9dff', skill: { name: '黒雷', kind: 'combo', multiplier: 2.2, hits: 3, cooldown: 10000 }
    },
    c006: {
      name: '骸の剣士', rarity: 1, baseHp: 160, baseAttack: 14,
      sprite: 'assets/rc30-swordsman.webp', portrait: 'assets/dex-swordsman.webp',
      color: '#8bcaff', skill: { name: '骸の呪刃', kind: 'weaken', multiplier: 1.5, duration: 6000, reduction: 0.25, cooldown: 12000 }
    },
    c007: {
      name: '堕天使カイン', rarity: 2, baseHp: 120, baseAttack: 26,
      sprite: 'assets/rc31-kain.webp', portrait: 'assets/4715d51ddceba9dab7e8.webp',
      color: '#c0a1ef', skill: { name: '堕天の翼', kind: 'weaken', multiplier: 2.6, duration: 6000, reduction: 0.10, cooldown: 12000 }
    },
    c008: {
      name: '煉獄シグラス', rarity: 2, baseHp: 168, baseAttack: 19,
      sprite: 'assets/rc31-siglas.webp', portrait: 'assets/4b7c3e81eac4b21c3344.webp',
      color: '#ff9a4a', skill: { name: '煉獄火', kind: 'burn', multiplier: 1.8, tickMultiplier: 0.4, ticks: 4, cooldown: 12000 }
    },
    c009: {
      name: '紫電アルカディオ', rarity: 2, baseHp: 108, baseAttack: 29,
      sprite: 'assets/rc31-arcadio.webp', portrait: 'assets/55466b3cd275d73074f9.webp',
      color: '#d4a1ff', skill: { name: '紫電連牙', kind: 'delay', multiplier: 1.6, delay: 1000, cooldown: 12000 }
    },
    c010: {
      name: '蒼月レイヴン', rarity: 2, baseHp: 120, baseAttack: 14,
      sprite: 'assets/rc32-raven.webp', portrait: 'assets/8cdeb84e361846857c5b.webp',
      color: '#a6e8ff', skill: { name: '月鏡の雫', kind: 'healAll', multiplier: 1.5, cooldown: 12000 }
    },
    c011: {
      name: '紅蓮の舞姫', rarity: 2, baseHp: 110, baseAttack: 18,
      sprite: 'assets/rc32-dancer.webp', portrait: 'assets/fa9be2f319ee0ca55c0f.webp',
      color: '#ff9b65', skill: { name: '紅蓮の舞', kind: 'rally', multiplier: 1.2, duration: 6000, cooldown: 12000 }
    },
    c012: {
      name: '呪詛の魔女', rarity: 3, baseHp: 100, baseAttack: 22,
      sprite: 'assets/rc32-witch.webp', portrait: 'assets/3cf3761242e4e6737b84.webp',
      color: '#d199ff', skill: { name: '千呪', kind: 'curse', multiplier: 1.6, vulnerability: 1.15, duration: 6000, cooldown: 12000 }
    },
    c013: {
      name: '終焉の天帝', rarity: 3, baseHp: 100, baseAttack: 24,
      sprite: 'assets/rc32-emperor.webp', portrait: 'assets/f25bec3e7f3a03b4622d.webp',
      color: '#ffe59a', skill: { name: '終焉', kind: 'execute', multiplier: 3.2, lowHpMultiplier: 4.5, threshold: 0.3, cooldown: 14000 }
    },
    c014: {
      name: '虚空神・無限', rarity: 3, baseHp: 120, baseAttack: 16,
      sprite: 'assets/rc32-void.webp', portrait: 'assets/41884eba380b57711e4c.webp',
      color: '#cbc8ff', skill: { name: '虚空の帳', kind: 'ward', duration: 4000, cooldown: 14000 }
    },
    c015: {
      name: '白銀の聖騎士', rarity: 3, baseHp: 150, baseAttack: 16,
      sprite: 'assets/rc32-paladin.webp', portrait: 'assets/24dd594f1e189a24c8c8.webp',
      color: '#a8e1ff', skill: { name: '白銀の誓い', kind: 'cover', multiplier: 2, duration: 6000, cooldown: 12000 }
    }
  };
  const guardian = {
    id: 'guardian', name: '水晶の守護者', maxHp: 360, attack: 26,
    sprite: 'assets/rc25-guardian.webp', color: '#72e4ff'
  };
  const armoredGuardian = {
    ...guardian, name: '重装の守護者',
    sprite: 'assets/rc46-armored-guardian.webp', color: '#8ddcfa',
    shieldRatio: 0.3, briefing: '戦闘開始時にシールドを展開'
  };
  const thunderBeast = {
    ...guardian, name: '雷鳴の魔獣',
    sprite: 'assets/rc47-thunder-beast.webp', color: '#ffdc75',
    thunder: { every: 3, warning: 2000, multiplier: 1.7 }, briefing: '3回目の攻撃ごとに強力な雷撃'
  };
  const mirrorDragon = {
    ...guardian, name: '鏡晶竜',
    sprite: 'assets/rc48-mirror-dragon.webp', color: '#e5b3ff',
    enrage: { threshold: 0.5, multiplier: 1.25 }, briefing: '残りHP50%で覚醒し、攻撃力が上昇'
  };
  const stageEnemies = {10: armoredGuardian, 20: thunderBeast, 30: mirrorDragon};
  const difficulties = Object.freeze({
    normal: Object.freeze({ maxHp: guardian.maxHp, attack: guardian.attack }),
    training: Object.freeze({ maxHp: 750, attack: 34 })
  });
  const stagesPerChapter = 30;
  const stageHpGrowth = 1.14;
  const stageAttackGrowth = 1.11;
  const allyInterval = 2000;
  const enemyInterval = 2500;
  const animationWindow = 480;
  const burnInterval = 1000;

  function enemyForStage(stage) {
    const chapterStage = (stage - 1) % stagesPerChapter + 1;
    return stageEnemies[chapterStage] ?? guardian;
  }

  function chapterForStage(stage) {
    return Math.floor((stage - 1) / stagesPerChapter) + 1;
  }

  function stageStat(base, initialGrowth, stage, laterPower) {
    const initial = base * initialGrowth ** (Math.min(stage, stagesPerChapter) - 1);
    const later = 1 + Math.max(0, stage - stagesPerChapter) / 24;
    return Math.min(Number.MAX_SAFE_INTEGER, Math.round(initial * later ** laterPower));
  }

  function campaignEncounter(stage) {
    const { name, briefing } = enemyForStage(stage);
    return { name, boss: Boolean(briefing) };
  }

  function campaignEnemy(stage, difficulty) {
    const profile = enemyForStage(stage);
    const baseline = difficulties[difficulty];
    const maxHp = stageStat(baseline.maxHp, stageHpGrowth, stage, 1.4);
    const attack = stageStat(baseline.attack, stageAttackGrowth, stage, 1.15);
    const openingShield = Math.round(maxHp * (profile.shieldRatio ?? 0));
    return { ...profile, maxHp, attack, openingShield };
  }

  function campaignEnemyPreview(stage, difficulty) {
    const { name, sprite, maxHp, attack, openingShield, thunder, enrage } = campaignEnemy(stage, difficulty);
    let trait = '';
    if (openingShield) {
      trait = '戦闘開始時に耐久 ' + openingShield.toLocaleString('ja-JP') + ' の盾を展開。盾が先にダメージを受ける。';
    } else if (thunder) {
      trait = '攻撃' + thunder.every + '回ごとに、威力' + thunder.multiplier + '倍の雷撃。発動の' + thunder.warning / 1000 + '秒前に予告が出る。';
    } else if (enrage) {
      trait = '残りHPが' + Math.round(enrage.threshold * 100) + '%以下で覚醒し、攻撃力が' + Math.round((enrage.multiplier - 1) * 100) + '%上がる。';
    }
    return { name, sprite, maxHp, attack, trait };
  }

  function supports(id) {
    return typeof id === 'string' && Object.hasOwn(characters, id);
  }

  function characterArt(id) {
    if (!supports(id)) return null;
    const { sprite, color } = characters[id];
    return { sprite, color };
  }

  function sampleParty() {
    return ['c002', 'c001', 'c003'].map(id => ({ id, level: 1 }));
  }

  function characterSkill(id) {
    if (!supports(id)) return null;
    const skill = characters[id].skill;
    const seconds = ms => ms / 1000 + '秒';
    const percent = ratio => Math.round(ratio * 100) + '%';
    const power = '攻撃力×' + skill.multiplier;
    const hit = power + 'のダメージ。';
    const duration = seconds(skill.duration);
    let description;
    switch (skill.kind) {
      case 'heal': description = '残りHPの割合が最も低い味方1体を' + power + '回復。'; break;
      case 'healAll': description = '戦闘不能の味方を除き、味方全体を' + power + '回復。'; break;
      case 'shield': description = duration + '間、味方全体に使用者の最大HPの' + percent(skill.multiplier) + '分の盾を付与。'; break;
      case 'hit': description = hit; break;
      case 'combo': description = '合計' + power + 'のダメージを' + skill.hits + '連撃で与える。'; break;
      case 'weaken': description = hit + duration + '間、敵の攻撃力を' + percent(skill.reduction) + '下げる。'; break;
      case 'burn': description = hit + 'その後、' + seconds(burnInterval) + 'ごとに攻撃力×' + skill.tickMultiplier + 'の燃焼ダメージを' + skill.ticks + '回与える。'; break;
      case 'delay': description = hit + '敵の次の攻撃を' + seconds(skill.delay) + '遅らせる。'; break;
      case 'rally': description = duration + '間、味方全体の通常攻撃を' + percent(skill.multiplier - 1) + '強化。'; break;
      case 'curse': description = hit + duration + '間、敵が受けるスキル・燃焼ダメージを' + percent(skill.vulnerability - 1) + '増やす。'; break;
      case 'execute': description = hit + '敵の残りHPが' + percent(skill.threshold) + '以下なら攻撃力×' + skill.lowHpMultiplier + '。'; break;
      case 'ward': description = duration + '間、味方それぞれの被弾を1回無効にする。'; break;
      case 'cover': description = '自分のHPを' + power + '回復。' + duration + '以内の敵の次の攻撃をかばう。'; break;
    }
    return { name: skill.name, description, cooldown: seconds(skill.cooldown) };
  }

  function characterStats(id, rawLevel) {
    if (!supports(id)) return null;
    const profile = characters[id];
    const parsedLevel = Number(rawLevel);
    const level = Number.isSafeInteger(parsedLevel) && parsedLevel > 0 ? parsedLevel : 1;
    // Apply linear growth and rarity before rounding.
    const multiplier = (level + 24) * (profile.rarity + 4) / 125;
    return {
      level,
      maxHp: Math.min(Number.MAX_SAFE_INTEGER, Math.round(profile.baseHp * multiplier)),
      attack: Math.min(Number.MAX_SAFE_INTEGER, Math.round(profile.baseAttack * multiplier))
    };
  }

  function createBattle(party, difficulty = "normal", stageNumber = 1) {
    if (!Object.hasOwn(difficulties, difficulty)) throw new RangeError("Unknown battle difficulty.");
    if (!Number.isSafeInteger(stageNumber) || stageNumber < 1) {
      throw new RangeError("Unknown campaign stage.");
    }
    const ids = new Set(party.map(member => member.id));
    if (!party.length || party.length > 3 || ids.size !== party.length || ![...ids].every(supports)) {
      throw new RangeError('A battle needs one to three different supported allies.');
    }
    const allies = party.map(member => {
      const profile = characters[member.id];
      const stats = characterStats(member.id, member.level);
      return {
        ...profile, id: member.id, ...stats, hp: stats.maxHp,
        shield: 0, shieldUntil: 0, wardUntil: 0, coverUntil: 0, skillReadyAt: 0
      };
    });
    const enemyProfile = campaignEnemy(stageNumber, difficulty);
    const enemy = {
      ...enemyProfile, hp: enemyProfile.maxHp,
      shield: enemyProfile.openingShield, attackDelayed: false, curseUntil: 0
    };
    const state = { allies, enemy, difficulty, time: 0, result: null, queuedSkill: null, rallyUntil: 0 };
    let nextAllyAttack = allyInterval;
    let nextEnemyAttack = enemyInterval;
    let enemyAttacks = 0;
    let enemyAttackDelay = 0;
    let animationUntil = 0;
    const weakenEffects = new Map();
    let burn = null;
    let rallyMultiplier = 1;
    let curseMultiplier = 1;

    function thunderDue() {
      return enemy.thunder && (enemyAttacks + 1) % enemy.thunder.every === 0;
    }

    function thunderWarning() {
      const remaining = nextEnemyAttack - state.time;
      return !state.result && thunderDue() && remaining <= enemy.thunder.warning + enemyAttackDelay
        ? remaining : null;
    }

    function healTarget() {
      return allies.reduce((target, ally) => {
        if (ally.hp === 0 || ally.hp === ally.maxHp) return target;
        if (!target || ally.hp / ally.maxHp < target.hp / target.maxHp) return ally;
        return target;
      }, null);
    }

    function skillStatus(ally) {
      if (ally.hp === 0) return 'defeated';
      if (state.result) return 'finished';
      if (state.queuedSkill?.id === ally.id) return 'queued';
      if (ally.skillReadyAt > state.time) return 'cooldown';
      if (['heal', 'healAll'].includes(ally.skill.kind) && !healTarget()) return 'full';
      if (state.queuedSkill) return 'waiting';
      return 'ready';
    }

    function expireShields() {
      for (const ally of allies) {
        if (state.time >= ally.shieldUntil) ally.shield = 0;
      }
    }

    function attack(attacker, target, power, skill, events, periodic = false) {
      if (target === enemy && (skill || periodic) && state.time < enemy.curseUntil) {
        power = Math.min(Number.MAX_SAFE_INTEGER, Math.round(power * curseMultiplier));
      }
      const warded = power > 0 && state.time < (target.wardUntil ?? 0);
      const blocked = warded ? power : Math.min(power, target.shield);
      if (warded) target.wardUntil = 0;
      else target.shield -= blocked;
      const amount = Math.min(target.hp, power - blocked);
      target.hp -= amount;
      events.push({
        kind: 'hit', from: attacker.id, to: target.id, amount, blocked, skill, periodic, warded, time: state.time
      });
      if (target.hp === 0 && state.queuedSkill?.id === target.id) state.queuedSkill = null;
      if (enemy.hp === 0) state.result = 'victory';
      else if (allies.every(ally => ally.hp === 0)) state.result = 'defeat';
      if (state.result) state.queuedSkill = null;
    }

    function markAnimation() {
      animationUntil = state.time + animationWindow;
      if (state.queuedSkill) state.queuedSkill.at = animationUntil;
    }

    function heal(caster, target, multiplier, events) {
      const amount = Math.min(target.maxHp - target.hp, Math.round(caster.attack * multiplier));
      target.hp += amount;
      events.push({ kind: 'heal', from: caster.id, to: target.id, amount, skill: true, time: state.time });
    }

    function resolveSkill(ally, events) {
      if (skillStatus(ally) !== 'ready') return;
      const skill = ally.skill;
      ally.skillReadyAt = state.time + skill.cooldown;
      if (skill.kind === 'heal') {
        heal(ally, healTarget(), skill.multiplier, events);
      } else if (skill.kind === 'healAll') {
        for (const target of allies) {
          if (target.hp > 0 && target.hp < target.maxHp) heal(ally, target, skill.multiplier, events);
        }
      } else if (skill.kind === 'rally') {
        state.rallyUntil = state.time + skill.duration;
        rallyMultiplier = skill.multiplier;
        events.push({ kind: 'rally', from: ally.id, to: ally.id, skill: true, time: state.time });
      } else if (skill.kind === 'ward') {
        for (const target of allies) {
          if (target.hp === 0) continue;
          target.wardUntil = state.time + skill.duration;
          events.push({ kind: 'ward', from: ally.id, to: target.id, skill: true, time: state.time });
        }
      } else if (skill.kind === 'cover') {
        ally.coverUntil = state.time + skill.duration;
        events.push({ kind: 'cover', from: ally.id, to: ally.id, skill: true, time: state.time });
        if (ally.hp < ally.maxHp) heal(ally, ally, skill.multiplier, events);
      } else if (skill.kind === 'shield') {
        const amount = Math.round(ally.maxHp * skill.multiplier);
        for (const target of allies) {
          if (target.hp === 0 || target.shield >= amount) continue;
          target.shield = amount;
          target.shieldUntil = state.time + skill.duration;
          events.push({ kind: 'shield', from: ally.id, to: target.id, amount, skill: true, time: state.time });
        }
      } else {
        const multiplier = skill.kind === 'execute' && enemy.hp <= enemy.maxHp * skill.threshold
          ? skill.lowHpMultiplier : skill.multiplier;
        const damage = Math.min(Number.MAX_SAFE_INTEGER, Math.round(ally.attack * multiplier));
        const hits = skill.hits ?? 1;
        const perHit = Math.floor(damage / hits);
        const remainder = damage % hits;
        for (let hit = 0; hit < hits && !state.result; hit += 1) {
          attack(ally, enemy, perHit + (hit < remainder ? 1 : 0), true, events);
        }
        if (!state.result) {
          switch (skill.kind) {
            case 'weaken':
              weakenEffects.set(ally.id, { until: state.time + skill.duration, reduction: skill.reduction });
              break;
            case 'burn':
              burn = {
                caster: ally, amount: Math.round(ally.attack * skill.tickMultiplier),
                next: state.time + burnInterval, remaining: skill.ticks
              };
              break;
            case 'curse':
              enemy.curseUntil = state.time + skill.duration;
              curseMultiplier = skill.vulnerability;
              break;
            case 'delay':
              nextEnemyAttack += skill.delay;
              enemyAttackDelay += skill.delay;
              enemy.attackDelayed = true;
              break;
          }
        }
      }
      markAnimation();
    }

    function requestSkill(id) {
      const ally = allies.find(member => member.id === id);
      const events = [];
      if (!ally || state.result) return events;
      const status = skillStatus(ally);
      if (status === 'queued') {
        state.queuedSkill = null;
      } else if (status === 'ready') {
        if (state.time < animationUntil) state.queuedSkill = { id, at: animationUntil };
        else resolveSkill(ally, events);
      }
      return events;
    }

    function advanceTo(time) {
      const events = [];
      if (!Number.isFinite(time) || time < state.time || state.result) return events;
      while (!state.result) {
        const next = Math.min(nextAllyAttack, nextEnemyAttack, state.queuedSkill?.at ?? Infinity, burn?.next ?? Infinity);
        if (next > time) break;
        state.time = next;
        expireShields();
        if (state.queuedSkill?.at === next) {
          const { id } = state.queuedSkill;
          state.queuedSkill = null;
          resolveSkill(allies.find(ally => ally.id === id), events);
        }
        if (!state.result && burn?.next === next) {
          attack(burn.caster, enemy, burn.amount, false, events, true);
          burn.next += burnInterval;
          if (--burn.remaining === 0) burn = null;
        }
        if (!state.result && nextAllyAttack === next) {
          nextAllyAttack += allyInterval;
          const power = state.time < state.rallyUntil ? rallyMultiplier : 1;
          for (const ally of allies) {
            if (ally.hp > 0) {
              attack(ally, enemy, Math.min(Number.MAX_SAFE_INTEGER, Math.round(ally.attack * power)), false, events);
            }
            if (state.result) break;
          }
          markAnimation();
        }
        if (!state.result && nextEnemyAttack === next) {
          const thunder = thunderDue();
          nextEnemyAttack += enemyInterval;
          enemyAttacks++;
          enemyAttackDelay = 0;
          enemy.attackDelayed = false;
          const front = allies.find(ally => ally.hp > 0);
          const coveringAlly = allies.find(ally => ally.hp > 0 && state.time < ally.coverUntil);
          if (coveringAlly) coveringAlly.coverUntil = 0;
          const damage = thunder ? Math.round(enemyAttack() * enemy.thunder.multiplier) : enemyAttack();
          attack(enemy, coveringAlly ?? front, damage, false, events);
          if (thunder) events.at(-1).thunder = true;
          markAnimation();
        }
      }
      if (!state.result) {
        state.time = time;
        expireShields();
      }
      return events;
    }

    function enemyEnraged() {
      return Boolean(enemy.enrage && enemy.hp > 0 && enemy.hp <= enemy.maxHp * enemy.enrage.threshold);
    }

    function enemyAttackPower() {
      return enemy.attack * (enemyEnraged() ? enemy.enrage.multiplier : 1);
    }

    function enemyAttack() {
      let reduction = 0;
      for (const effect of weakenEffects.values()) {
        if (state.time < effect.until) reduction = Math.max(reduction, effect.reduction);
      }
      return Math.round(enemyAttackPower() * (1 - reduction));
    }

    return { state, advanceTo, requestSkill, skillStatus, enemyAttack, enemyAttackPower, enemyEnraged, thunderWarning };
  }

  globalThis.TapGachaBattle = Object.freeze({ supports, sampleParty, characterArt, characterStats, characterSkill, createBattle, stagesPerChapter, chapterForStage, campaignEncounter, campaignEnemyPreview });
})();
