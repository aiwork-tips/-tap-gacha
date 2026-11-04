
(()=>{
  const trainingBtn=document.getElementById('charLevelUp');
  if(trainingBtn){
    // CSS touch-action:manipulation is the primary iOS Safari safeguard.
    // Suppress the default double-click zoom while allowing both click handlers.
    trainingBtn.addEventListener('dblclick', e=>e.preventDefault(), {passive:false});
  }
})();
