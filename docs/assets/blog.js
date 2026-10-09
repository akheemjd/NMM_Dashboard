/* Northern Mile blog: wordmark, hero layout and the live "This week" sign (reads assets/now.json). 2026-10-08. */
document.addEventListener('DOMContentLoaded',function(){
  var logo=document.querySelector('.gh-navigation-logo');
  if(logo&&!logo.querySelector('.nm-word')){var w=document.createElement('span');w.className='nm-word';w.textContent='Northern Mile';logo.appendChild(w);}
  /* Post pages: hide the old feature cards that repeat the headline as an image. Photos stay. */
  var fi=document.querySelector('.post-template .gh-feature-image');
  if(fi&&/-hero(-\d+)?\.(png|jpe?g|webp)/i.test(fi.currentSrc||fi.src)){var f=fi.closest('figure');if(f)f.classList.add('nm-hide-hero');}
  if(!document.body.classList.contains('home-template'))return;
  var inner=document.querySelector('.gh-header-inner'); if(!inner)return;
  var title=inner.querySelector('.gh-header-title'), form=inner.querySelector('.gh-form');
  var left=document.createElement('div'); left.className='gh-header-left';
  var dek=document.createElement('p'); dek.className='nm-dek'; dek.textContent='Diesel, the border and the dollar on both sides, read for the people who pay for them. One email every Wednesday morning.';
  if(title)left.appendChild(title); left.appendChild(dek); if(form)left.appendChild(form);
  var btn=form&&form.querySelector('.gh-button span span'); if(btn)btn.textContent='Get the Brief';
  var input=form&&form.querySelector('.gh-form-input'); if(input)input.placeholder='Your email';
  inner.insertBefore(left,inner.firstChild);
  var sign=document.createElement('div'); sign.className='nm-sign'; sign.setAttribute('aria-live','polite');
  sign.innerHTML='<h2>This week</h2><div class="nm-row"><span>US diesel</span><span>…</span></div><div class="nm-row"><span>Canadian diesel</span><span>…</span></div><a href="https://dashboard.northernmilemedia.com/">Open the live dashboard</a>';
  inner.appendChild(sign);
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  fetch('https://dashboard.northernmilemedia.com/assets/now.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(d){
    var rows=[];
    if(d.us!=null)rows.push(['US diesel','$'+Number(d.us).toFixed(3)+'/gal']);
    if(d.ca!=null)rows.push(['Canadian diesel',Number(d.ca).toFixed(1)+'¢/L']);
    if(d.gap!=null)rows.push([(/US higher/.test(d.gap_word||'')?'US over Canada':'Canada over US'),d.gap+'¢/L']);
    var h='<h2>This week</h2>';
    rows.forEach(function(r){h+='<div class="nm-row"><span>'+esc(r[0])+'</span><span>'+esc(r[1])+'</span></div>';});
    if(d.slowest&&d.slowest.mins>=10){h+='<div class="nm-row"><span>'+esc(d.slowest.name)+'<small>'+esc(d.slowest.dir)+'</small></span><span class="nm-hot">'+esc(d.slowest.mins)+' min</span></div>';}
    h+='<a href="https://dashboard.northernmilemedia.com/">Open the live dashboard</a>';
    sign.innerHTML=h;
  }).catch(function(){sign.innerHTML='<h2>This week</h2><div class="nm-row"><span>Live diesel, border and dollar</span></div><a href="https://dashboard.northernmilemedia.com/">Open the live dashboard</a>';});
});
