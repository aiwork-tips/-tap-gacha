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
    }
  };
  const guardian = {
    id: 'guardian', name: '水晶の守護者', maxHp: 360, attack: 26,
    sprite: 'assets/rc25-guardian.webp', color: '#72e4ff'
  };
  const difficulties = Object.freeze({
    normal: Object.freeze({ maxHp: guardian.maxHp, attack: guardian.attack }),
    training: Object.freeze({ maxHp: 750, attack: 34 })
  });
  const allyInterval = 2000;
  const enemyInterval = 2500;
  const animationWindow = 480;

  function supports(id) {
    return typeof id === 'string' && Object.hasOwn(characters, id);
  }

  function sampleParty() {
    return ['c002', 'c001', 'c003'].map(id => ({ id, level: 1 }));
  }

  function createBattle(party, difficulty = "normal") {
    if (!Object.hasOwn(difficulties, difficulty)) throw new RangeError("Unknown battle difficulty.");
    const ids = new Set(party.map(member => member.id));
    if (!party.length || party.length > 3 || ids.size !== party.length || ![...ids].every(supports)) {
      throw new RangeError('A battle needs one to three different supported allies.');
    }
    const allies = party.map(member => {
      const profile = characters[member.id];
      const parsedLevel = Number(member.level);
      const level = Number.isSafeInteger(parsedLevel) && parsedLevel > 0 ? parsedLevel : 1;
      // (level + 24) / 25 is the linear level multiplier. Apply rarity before rounding.
      const multiplier = (level + 24) * (profile.rarity + 4) / 125;
      const maxHp = Math.min(Number.MAX_SAFE_INTEGER, Math.round(profile.baseHp * multiplier));
      const attack = Math.min(Number.MAX_SAFE_INTEGER, Math.round(profile.baseAttack * multiplier));
      return {
        ...profile, id: member.id, level, maxHp, attack, hp: maxHp,
        shield: 0, shieldUntil: 0, skillReadyAt: 0
      };
    });
    const enemy = { ...guardian, ...difficulties[difficulty], hp: difficulties[difficulty].maxHp, shield: 0 };
    const state = { allies, enemy, difficulty, time: 0, result: null, queuedSkill: null };
    let nextAllyAttack = allyInterval;
    let nextEnemyAttack = enemyInterval;
    let animationUntil = 0;

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
      if (ally.skill.kind === 'heal' && !healTarget()) return 'full';
      if (state.queuedSkill) return 'waiting';
      return 'ready';
    }

    function expireShields() {
      for (const ally of allies) {
        if (state.time >= ally.shieldUntil) ally.shield = 0;
      }
    }

    function attack(attacker, target, power, skill, events) {
      const blocked = Math.min(power, target.shield);
      target.shield -= blocked;
      const amount = Math.min(target.hp, power - blocked);
      target.hp -= amount;
      events.push({
        kind: 'hit', from: attacker.id, to: target.id, amount, blocked, skill, time: state.time
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

    function resolveSkill(ally, events) {
      if (skillStatus(ally) !== 'ready') return;
      const skill = ally.skill;
      ally.skillReadyAt = state.time + skill.cooldown;
      if (skill.kind === 'heal') {
        const target = healTarget();
        const amount = Math.min(target.maxHp - target.hp, Math.round(ally.attack * skill.multiplier));
        target.hp += amount;
        events.push({ kind: 'heal', from: ally.id, to: target.id, amount, skill: true, time: state.time });
      } else if (skill.kind === 'shield') {
        const amount = Math.round(ally.maxHp * skill.multiplier);
        for (const target of allies) {
          if (target.hp === 0 || target.shield >= amount) continue;
          target.shield = amount;
          target.shieldUntil = state.time + skill.duration;
          events.push({ kind: 'shield', from: ally.id, to: target.id, amount, skill: true, time: state.time });
        }
      } else {
        attack(ally, enemy, Math.round(ally.attack * skill.multiplier), true, events);
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
        const next = Math.min(nextAllyAttack, nextEnemyAttack, state.queuedSkill?.at ?? Infinity);
        if (next > time) break;
        state.time = next;
        expireShields();
        if (state.queuedSkill?.at === next) {
          const { id } = state.queuedSkill;
          state.queuedSkill = null;
          resolveSkill(allies.find(ally => ally.id === id), events);
        }
        if (!state.result && nextAllyAttack === next) {
          nextAllyAttack += allyInterval;
          for (const ally of allies) {
            if (ally.hp > 0) attack(ally, enemy, ally.attack, false, events);
            if (state.result) break;
          }
          markAnimation();
        }
        if (!state.result && nextEnemyAttack === next) {
          nextEnemyAttack += enemyInterval;
          const front = allies.find(ally => ally.hp > 0);
          attack(enemy, front, enemy.attack, false, events);
          markAnimation();
        }
      }
      if (!state.result) {
        state.time = time;
        expireShields();
      }
      return events;
    }

    return { state, advanceTo, requestSkill, skillStatus };
  }

  globalThis.TapGachaBattle = Object.freeze({ supports, sampleParty, createBattle });
})();
