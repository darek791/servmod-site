(function(){
var box=document.getElementById('mq'); if(!box) return;
var sel=document.getElementById('mm'), out=document.getElementById('mres'), data=null;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function norm(s){return String(s||'').toLowerCase().replace(/[\s_-]+/g,'')}
function load(cb){ if(data) return cb(); fetch('/manuals/data.json').then(function(r){return r.json()}).then(function(d){data=d.manuals;
  data.forEach(function(m){var o=document.createElement('option');o.value=m.id;o.textContent=m.title;sel.appendChild(o)});
  var u=new URLSearchParams(location.search); if(u.get('m')) sel.value=u.get('m'); if(u.get('q')) box.value=u.get('q');
  data.forEach(function(m){m.faults.forEach(function(f){f._k=norm(f.code+' '+(f.number||'')+' '+f.name+' '+f.meaning)});
    m.params.forEach(function(p){p._k=norm(p.id+' '+p.name+' '+p.desc)})});
  cb()}).catch(function(){out.textContent='The reference data is not available right now.'}) }
function src(m,pg){return '<a class="mref" href="'+esc(m.doc.url)+'" rel="noopener">'+esc(m.doc.name)+'</a> <span class="hint">(p. '+esc(pg)+' of '+esc(m.doc.number)+')</span>'}
function score(k,q,id){ if(norm(id)===q) return 100; if(norm(id).indexOf(q)===0) return 60; return k.indexOf(q)>-1?10:0 }
function run(){ var q=norm(box.value); out.innerHTML=''; if(q.length<2){out.innerHTML='<p class="hint">Type a fault code (E04, F013, 14), a parameter (P-12, A044, 3-41) or a word such as overcurrent.</p>';return}
  var terms=box.value.trim().toLowerCase().split(/\s+/).map(norm).filter(Boolean), m=sel.value, res=[];
  data.forEach(function(d){ if(m&&d.id!==m) return;
    d.faults.forEach(function(f){var s=terms.every(function(t){return f._k.indexOf(t)>-1}); if(s) res.push({t:'f',d:d,x:f,s:score(f._k,q,f.code)+(f.number!=null&&String(f.number)===q?100:0)+5})});
    d.params.forEach(function(p){var s=terms.every(function(t){return p._k.indexOf(t)>-1}); if(s) res.push({t:'p',d:d,x:p,s:score(p._k,q,p.id)})}) });
  res.sort(function(a,b){return b.s-a.s}); var shown=res.slice(0,30);
  shown.forEach(function(r){var x=r.x,d=r.d,el=document.createElement('div'); el.className='mhit';
    if(r.t==='f'){ el.innerHTML='<div class="mh"><span class="mk">'+esc(d.title)+' · fault</span><b>'+esc(x.code)+'</b> '+esc(x.name)+'</div><p>'+esc(x.meaning)+'</p>'+
      (x.note?'<p class="hint">'+esc(x.note)+'</p>':'')+(x.checks&&x.checks.length?'<ul>'+x.checks.map(function(c){return '<li>'+esc(c)+'</li>'}).join('')+'</ul>':'')+'<p class="hint">Source: '+src(d,x.page)+'</p>'; }
    else { el.innerHTML='<div class="mh"><span class="mk">'+esc(d.title)+' · parameter</span><b>'+esc(x.id)+'</b> '+esc(x.name)+'</div><p>'+esc(x.desc)+'</p><p class="hint">Range: '+esc(x.range)+' · Default: '+esc(x.default)+'</p><p class="hint">Source: '+src(d,x.page)+'</p>'; }
    out.appendChild(el)});
  if(!res.length) out.innerHTML='<p>No matches. Try a shorter term, or check the manufacturer manual.</p>'; else if(res.length>30) out.insertAdjacentHTML('beforeend','<p class="hint">Showing 30 of '+res.length+'. Narrow the search or pick a manual.</p>') }
var t; box.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){load(run)},200)}); sel.addEventListener('change',function(){load(run)});
load(run);
})();
