
/* v10: fit long live numbers within three independent frames without changing save data. */
(()=>{
  const ids=['homePT','homeKeys','homeTapPower','homeRank'];
  const nodes=ids.map(id=>document.getElementById(id)).filter(Boolean);
  const fit=()=>{
    for(const el of nodes){
      el.style.removeProperty('font-size');
      const cs=getComputedStyle(el), width=el.clientWidth-5;
      if(width<=0) continue;
      const current=parseFloat(cs.fontSize)||18;
      const canvas=document.createElement('canvas');
      const ctx=canvas.getContext('2d');
      if(!ctx) continue;
      ctx.font=`${cs.fontWeight} ${current}px ${cs.fontFamily}`;
      const measured=ctx.measureText(el.textContent||'').width;
      if(measured>width) el.style.setProperty('font-size',Math.max(9,Math.floor(current*width/measured))+'px','important');
    }
  };
  let queued=false;
  const schedule=()=>{
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>{queued=false;fit()});
  };
  const obs=new MutationObserver(schedule);
  nodes.forEach(n=>obs.observe(n,{childList:true,characterData:true,subtree:true}));
  window.addEventListener('resize',schedule,{passive:true});
  schedule();
})();
