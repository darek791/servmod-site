(function(){
var box=document.getElementById('mq'); if(!box) return;
var sel=document.getElementById('mm'), out=document.getElementById('mres'), list=document.getElementById('mlist'), data=null;
function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(cb){ if(data) return cb(); fetch('/manuals/index.json').then(function(r){return r.json()}).then(function(d){data=d.manuals;
  data.forEach(function(m){var o=document.createElement('option');o.value=m.id;o.textContent=m.title;sel.appendChild(o);
    var li=document.createElement('li');li.innerHTML='<a href="'+esc(m.url)+'">'+esc(m.title)+'</a> <span class="hint">'+esc(m.maker||'')+' · '+m.pages.length+' pages</span>';list.appendChild(li)});
  var u=new URLSearchParams(location.search); if(u.get('m')) sel.value=u.get('m'); if(u.get('q')) box.value=u.get('q'); cb()})
  .catch(function(){out.textContent='Manuals are not published yet.'}) }
function run(){ var q=box.value.trim().toLowerCase(); out.innerHTML=''; if(q.length<2){out.innerHTML='<p class="hint">Type a fault code (E04, F013), parameter (P-12, A044) or any word.</p>';return}
  var terms=q.split(/\s+/), n=0, m=sel.value, res=[];
  data.forEach(function(d){ if(m&&d.id!==m) return;
    d.pages.forEach(function(t,i){ var l=t.toLowerCase(), ok=terms.every(function(w){return l.indexOf(w)>-1}); if(!ok) return;
      var at=l.indexOf(terms[0]), s=Math.max(0,at-90), sn=esc(t.slice(s,at+170)); terms.forEach(function(w){sn=sn.replace(new RegExp('('+w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')});
      res.push({d:d,p:i+1,sn:(s?'… ':'')+sn+' …',score:(l.split(terms[0]).length-1)}) }) });
  res.sort(function(a,b){return b.score-a.score}); res.slice(0,40).forEach(function(r){
    var el=document.createElement('div'); el.className='mhit'; el.innerHTML='<a href="'+esc(r.d.url)+'#page='+r.p+'"><b>'+esc(r.d.title)+'</b> — page '+r.p+'</a><p>'+r.sn+'</p>'; out.appendChild(el)});
  if(!res.length) out.innerHTML='<p>No matches. Try a shorter term.</p>'; else if(res.length>40) out.insertAdjacentHTML('beforeend','<p class="hint">Showing 40 of '+res.length+' pages. Narrow the search.</p>') }
var t; box.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){load(run)},200)}); sel.addEventListener('change',function(){load(run)});
load(run);
})();
