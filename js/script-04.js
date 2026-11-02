
(()=>{
 const screen=document.getElementById('characterScreen');
 const toggle=document.getElementById('charRosterToggle');
 const grid=document.getElementById('characterGrid');
 function setExpanded(expanded){
  screen.classList.toggle('roster-expanded',expanded);
  toggle.setAttribute('aria-pressed',String(expanded));
  toggle.setAttribute('aria-label',expanded?'育成パネルに戻る':'キャラ一覧を広く表示する');
  toggle.textContent=expanded?'育成へ戻る ⌃':'一覧を広く見る ⌄';
 }
 toggle.addEventListener('click',()=>setExpanded(!screen.classList.contains('roster-expanded')));
 grid.addEventListener('click',e=>{if(e.target.closest('[data-character-id]'))setExpanded(false)});
})();
