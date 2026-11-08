(() => {
  'use strict';
  const root=document.getElementById('battleApp');
  const field=document.getElementById('battleField');
  const status=document.getElementById('battleStatus');
  const effects=document.getElementById('battleEffects');
  const autoButton=document.getElementById('battleAuto');
  const speedButton=document.getElementById('battleSpeed');
  const resetButton=document.getElementById('battleReset');
  const heroIds=['c001','c002','c003'];
  const units={
    c001:{name:'白翼のアルム',action:'光撃',kind:'holy',color:'#ffde72',damage:14},
    c002:{name:'鉄骸兵',action:'打撃',kind:'metal',color:'#ffb15c',damage:12},
    c003:{name:'冥牙クロウル',action:'突進',kind:'claw',color:'#c38aff',damage:16},
    guardian:{name:'水晶の守護者',action:'水晶の衝撃',kind:'crystal',color:'#68e3ff',damage:18}
  };
  const actors=Object.fromEntries(Object.keys(units).map(id=>[id,document.getElementById('actor-'+id)]));
  const cards=Object.fromEntries(heroIds.map(id=>[id,document.getElementById('card-'+id)]));
  const skillButtons=[...root.querySelectorAll('[data-skill]')];
  const skillNames={c001:'聖光',c002:'重砕撃',c003:'冥牙'};
  const actionButtons=[...root.querySelectorAll('[data-attack]')];
  const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');
  const animations=new Set();
  const state={ready:false,failed:false,hp:{c001:100,c002:100,c003:100,guardian:100},auto:false,paused:false,busy:false,complete:false,speed:1,sequence:0,target:0,active:null,phase:'idle',impacts:0};
  let pending=null;
  state.cooldowns={c001:0,c002:0,c003:0};
  let cooldownStamp=performance.now();
  function advanceCooldowns(){
    const now=performance.now(),elapsed=Math.max(0,now-cooldownStamp);cooldownStamp=now;
    if(!state.ready||state.paused||state.complete||document.hidden)return;
    for(const id of heroIds)state.cooldowns[id]=Math.max(0,state.cooldowns[id]-elapsed*state.speed);
  }
  function setStatus(message){status.textContent=message;}
  function clearTask(){if(pending)clearTimeout(pending.timer);pending=null;}
  function consumeTask(){
    if(!pending||state.paused)return;
    clearTimeout(pending.timer);
    pending.remaining=Math.max(0,pending.remaining-(performance.now()-pending.started)*state.speed);
  }
  function armTask(){
    if(!pending||state.paused)return;
    const task=pending;task.started=performance.now();
    task.timer=setTimeout(()=>{if(pending!==task)return;pending=null;task.fn();},task.remaining/state.speed);
  }
  function schedule(fn,duration){clearTask();pending={fn,remaining:duration,started:performance.now(),timer:null};armTask();}
  function animate(node,frames,duration){
    if(motionPreference.matches)return;
    const animation=node.animate(frames,{duration,easing:'ease-in-out',fill:'none'});
    animation.updatePlaybackRate(state.speed);if(state.paused)animation.pause();
    animations.add(animation);animation.finished.then(()=>animations.delete(animation),()=>animations.delete(animation));
  }
  function clearVisuals(){
    animations.forEach(animation=>animation.cancel());animations.clear();
    effects.replaceChildren();delete effects.dataset.kind;
    root.querySelectorAll('.actor').forEach(actor=>{delete actor.dataset.attacking;delete actor.dataset.hurt;});
  }
  function render(){
    root.dataset.mode=state.failed?'error':!state.ready?'loading':state.complete?'complete':state.paused?'paused':state.auto?'auto':state.busy?'manual':'idle';
    root.dataset.paused=String(state.paused);root.dataset.phase=state.phase;root.style.setProperty('--speed',String(state.speed));
    for(const id of Object.keys(units)){
      const actor=actors[id];actor.style.setProperty('--hp',state.hp[id]+'%');actor.dataset.defeated=String(state.hp[id]===0);actor.dataset.active=String(state.active===id);
      actor.disabled=!state.ready||state.busy||state.auto||state.paused||state.complete||state.hp[id]===0;
      if(cards[id]){
        const card=cards[id];card.style.setProperty('--hp',state.hp[id]+'%');card.dataset.defeated=String(state.hp[id]===0);card.dataset.active=String(state.active===id);card.disabled=actor.disabled;
        card.querySelector('.hero-percent').textContent=state.hp[id]+'%';
        card.setAttribute('aria-label',units[id].name+' HP '+state.hp[id]+'% · 攻撃を確認');
      }
    }
    skillButtons.forEach(button=>{
      const id=button.dataset.skill,remaining=state.cooldowns[id];
      button.disabled=!state.ready||state.busy||state.auto||state.paused||state.complete||state.hp[id]===0||remaining>0;
      button.querySelector('small').textContent=state.hp[id]===0?'戦闘不能':remaining>0?Math.ceil(remaining/1000)+'秒':state.complete?'終了':state.paused?'一時停止':state.auto||state.busy?'待機中':'発動可能';
      button.setAttribute('aria-label',units[id].name+'の'+skillNames[id]+' · '+button.querySelector('small').textContent);
    });
    autoButton.disabled=!state.ready||(!state.auto&&!state.paused&&state.busy);
    autoButton.textContent=state.paused?'再開':state.auto?'一時停止':state.complete?'もう一度':'自動再生';
    autoButton.setAttribute('aria-pressed',String(state.auto&&!state.paused));
    speedButton.disabled=!state.ready;speedButton.textContent='×'+state.speed;speedButton.setAttribute('aria-label','再生速度 '+state.speed+'倍');
    resetButton.disabled=!state.ready;
  }
  function nextLivingHero(){
    for(let offset=0;offset<heroIds.length;offset++){
      const index=(state.target+offset)%heroIds.length;
      if(state.hp[heroIds[index]]>0){state.target=(index+1)%heroIds.length;return heroIds[index];}
    }
    return null;
  }
  function showImpact(attacker,target,amount){
    const scene=field.getBoundingClientRect();
    const source=actors[attacker].getBoundingClientRect(),victim=actors[target].getBoundingClientRect();
    const x1=source.x+source.width*.5-scene.x,y1=source.y+source.height*.55-scene.y;
    const x2=victim.x+victim.width*.5-scene.x,y2=victim.y+victim.height*.53-scene.y;
    effects.dataset.kind=units[attacker].kind;
    for(const [key,value] of Object.entries({'--fx-x':x1+'px','--fx-y':y1+'px','--fx-length':Math.hypot(x2-x1,y2-y1)+'px','--fx-angle':Math.atan2(y2-y1,x2-x1)+'rad','--hit-x':x2+'px','--hit-y':y2+'px','--fx-color':units[attacker].color}))effects.style.setProperty(key,value);
    const ray=document.createElement('span');ray.className='battle-ray';
    const impact=document.createElement('span');impact.className='battle-impact';
    const damage=document.createElement('span');damage.className='battle-damage';damage.textContent='−'+amount+'%';
    effects.replaceChildren(ray,impact,damage);
    const shake=attacker==='guardian'?-5:5;
    animate(actors[target].querySelector('.actor-motion'),[{transform:'translateX(0)'},{transform:`translateX(${shake}px)`},{transform:`translateX(${-shake}px)`},{transform:'translateX(0)'}],360);
  }
  function finishIfNeeded(){
    if(state.hp.guardian>0&&heroIds.some(id=>state.hp[id]>0))return false;
    state.complete=true;state.auto=false;state.paused=false;state.busy=false;state.phase='complete';clearTask();clearVisuals();
    setStatus('演出プレビュー完了 · もう一度再生できます');render();return true;
  }
  function startAction(attacker,skill=false){
    advanceCooldowns();
    if(skill&&(state.auto||!heroIds.includes(attacker)||state.cooldowns[attacker]>0))return;
    if(!state.ready||state.failed||state.busy||state.paused||state.complete||state.hp[attacker]===0)return;
    const target=attacker==='guardian'?nextLivingHero():'guardian';
    if(!target||state.hp[target]===0){finishIfNeeded();return;}
    if(skill)state.cooldowns[attacker]=8000;
    state.busy=true;state.active=attacker;state.phase='windup';
    setStatus((state.auto?'自動再生中 · ':'')+units[attacker].name+'の'+(skill?skillNames[attacker]:units[attacker].action));render();
    const direction=attacker==='guardian'?-1:1;
    const distance=attacker==='c001'?7:field.clientWidth*(attacker==='guardian'?.11:attacker==='c003'?.21:.16);
    animate(actors[attacker].querySelector('.actor-motion'),[{transform:'translate(0,0)',offset:0},{transform:`translate(${distance*direction}px,-3px)`,offset:.4},{transform:'translate(0,0)',offset:1}],760);
    schedule(()=>{
      const amount=Math.min(state.hp[target],units[attacker].damage+(skill?10:0));
      state.hp[target]-=amount;state.impacts++;state.phase='impact';
      showImpact(attacker,target,amount);render();
      schedule(()=>{
        state.busy=false;state.active=null;state.phase='idle';clearVisuals();
        if(finishIfNeeded())return;
        setStatus(state.auto?'自動再生中 · 次の攻撃を準備':'味方・敵をタップで攻撃を確認');render();
        if(state.auto)schedule(nextAutoAction,520);
      },460);
    },300);
  }
  function nextAutoAction(){
    if(!state.auto||state.paused||state.busy||state.complete)return;
    const sequence=[...heroIds,'guardian'];
    for(let tries=0;tries<sequence.length;tries++){
      const id=sequence[state.sequence%sequence.length];state.sequence++;
      if(state.hp[id]>0){startAction(id);return;}
    }
    finishIfNeeded();
  }
  function pause(){
    if(!state.ready||state.paused||state.complete||(!state.auto&&!state.busy))return;
    advanceCooldowns();consumeTask();state.paused=true;animations.forEach(animation=>animation.pause());
    setStatus('一時停止中 · 再開で続きから再生');render();
  }
  function resume(){
    if(!state.paused)return;
    cooldownStamp=performance.now();state.paused=false;animations.forEach(animation=>animation.play());
    setStatus(state.auto?'自動再生を再開しました':'攻撃の確認を再開しました');render();
    if(pending)armTask();else if(state.auto)nextAutoAction();
  }
  function reset(){
    clearTask();clearVisuals();
    state.cooldowns={c001:0,c002:0,c003:0};cooldownStamp=performance.now();
    state.hp={c001:100,c002:100,c003:100,guardian:100};state.auto=false;state.paused=false;state.busy=false;state.complete=false;state.sequence=0;state.target=0;state.active=null;state.phase='idle';state.impacts=0;
    setStatus(state.ready?'味方・敵をタップで攻撃を確認':'画像を読み込んでいます…');render();
  }
  skillButtons.forEach(button=>button.addEventListener('click',()=>{if(!button.disabled)startAction(button.dataset.skill,true);}));
  actionButtons.forEach(button=>button.addEventListener('click',()=>{if(button.disabled||state.auto)return;startAction(button.dataset.attack);}));
  autoButton.addEventListener('click',()=>{
    if(autoButton.disabled)return;
    if(state.paused){resume();return;}
    if(state.auto){pause();return;}
    if(state.complete)reset();
    state.auto=true;render();nextAutoAction();
  });
  speedButton.addEventListener('click',()=>{
    if(speedButton.disabled)return;
    advanceCooldowns();consumeTask();state.speed=state.speed===1?2:1;
    animations.forEach(animation=>animation.updatePlaybackRate(state.speed));
    render();if(pending&&!state.paused)armTask();
  });
  resetButton.addEventListener('click',()=>{if(!resetButton.disabled)reset();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  window.addEventListener('pagehide',()=>{clearInterval(cooldownTicker);cooldownTicker=null;clearTask();clearVisuals();state.busy=false;state.auto=false;state.paused=false;state.phase=state.complete?'complete':'idle';render();});
  motionPreference.addEventListener('change',()=>{if(motionPreference.matches){animations.forEach(animation=>animation.cancel());animations.clear();}});
  const tickCooldowns=()=>{advanceCooldowns();render();};
  let cooldownTicker=setInterval(tickCooldowns,100);
  window.addEventListener('pageshow',()=>{if(cooldownTicker===null){cooldownStamp=performance.now();cooldownTicker=setInterval(tickCooldowns,100);}});
  window.battlePreview=Object.freeze({snapshot:()=>JSON.parse(JSON.stringify(state))});
  render();
  Promise.all([...root.querySelectorAll('img')].map(async img=>{
    await img.decode();if(!img.naturalWidth)throw new Error('Image unavailable');
  })).then(()=>{state.ready=true;setStatus('味方・敵をタップで攻撃を確認');render();},()=>{state.failed=true;setStatus('画像を読み込めませんでした。ページを再読み込みしてください。');render();});
})();
