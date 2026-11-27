(function(){
var $=function(i){return document.getElementById(i)}, msg=$('a-msg');
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function say(t,c){msg.textContent=t;msg.className=t?'msg show '+(c||'ok'):'msg'}
function api(method,url,body){return fetch(url,{method:method,credentials:'same-origin',headers:{'Content-Type':'application/json','X-Requested-With':'servmod'},body:body?JSON.stringify(body):undefined})
  .then(function(r){return r.json().catch(function(){return {}}).then(function(j){if(!r.ok){var e=new Error(j.detail||j.error||r.status);e.status=r.status;throw e}return j})})}
function date(t){return new Date(t*1000).toLocaleDateString()}
function show(which){['a-login','a-main'].forEach(function(i){$(i).hidden=(i!==which)})}
var email='';
function dashboard(){ api('GET','/api/me').then(function(me){ show('a-main'); $('a-who').textContent=me.email; say('');
  $('a-ents').innerHTML=me.entitlements.length?me.entitlements.map(function(e){return '<p>'+(e.revoked?'<b>Revoked</b> — ':'')+'Licence #'+e.id+' · '+e.seats+' phone'+(e.seats>1?'s':'')+' ('+e.seats_used+' in use) · device moves left this year: '+e.moves_left+'</p>'}).join('')+(me.entitlements.some(function(e){return !e.revoked&&/(^|,)(PRO|ALL)(,|$)/.test(e.features)})?'<p><a href="/modbox.html">Build your own ServMod Box: wiring drawings and firmware</a></p>':''):'<p>There is no licence on this account yet. <a href="/pricing.html">See pricing</a>. If you bought ServMod, make sure you signed in with the e-mail used for the purchase.</p>';
  var ls=me.licences.filter(function(l){return !l.released});
  $('a-devs').innerHTML=ls.length?ls.map(function(l){return '<div class="mhit"><b>'+esc(l.label||'Phone')+'</b> <span class="hint">'+esc(l.device_id)+' · added '+date(l.created)+'</span><p style="word-break:break-all;font-size:.85rem"><code>'+esc(l.code)+'</code></p><button class="btn ghost" data-rel="'+l.id+'" type="button">Release this phone</button></div>'}).join(''):'<p class="hint">No phone activated yet.</p>';
  if(me.admin) admin(); else $('a-admin').hidden=true;
 }).catch(function(e){ show('a-login'); if(e.status!==401) say('Could not load your account. Try again later.','err') }) }
var lic={grp:'all',q:'',off:0,tmr:null};
function srcl(x){return x==='shop'?'Web shop':x==='play'?'Google Play':String(x).indexOf('admin:')===0?'Granted by '+String(x).slice(6):x}
function featl(f){return String(f||'').split(',').map(function(p){return p==='PRO'?'Pro':p==='ALL'?'Everything':p.indexOf('SUB:')===0?'Subscription to '+p.slice(4,8)+'-'+p.slice(8,10)+'-'+p.slice(10,12):p}).join(' + ')}
var FOLDERS=[['all','All'],['shop','Web shop'],['play','Google Play'],['admin','Granted'],['revoked','Revoked'],['accounts','No licence']];
function licItem(e){
  if(e.kind==='account') return '<div class="mhit"><b>'+esc(e.email)+'</b> <span class="hint">account only · since '+date(e.created)+(e.last_login?' · last sign-in '+date(e.last_login):'')+'</span>'+(e.protected?'<p class="hint">Admin account</p>':'<p class="hint"><a href="#" data-pacc="'+e.id+'">Remove account</a></p>')+'</div>';
  var act=e.devices.filter(function(d){return !d.released});
  var dv=e.devices.length?'<details><summary class="hint">Phones: '+act.length+' of '+e.seats+' in use'+(e.devices.length>act.length?' ('+(e.devices.length-act.length)+' released)':'')+'</summary>'+e.devices.map(function(d){return '<div class="hint" style="margin:4px 0">'+esc(d.device_id)+(d.label?' · '+esc(d.label):'')+' · added '+date(d.created)+(d.released?' · released '+date(d.released):'')+'</div>'}).join('')+'</details>':'<p class="hint">No phone activated yet ('+e.seats+' seat'+(e.seats>1?'s':'')+').</p>';
  var od=(e.orders||[]).length?'<p class="hint">'+e.orders.map(function(o){return esc(o.provider)+' '+esc(o.product)+' £'+(o.pence/100).toFixed(2).replace('.00','')+' · '+date(o.created)}).join('<br>')+'</p>':'';
  return '<div class="mhit"><b style="word-break:break-all">'+esc(e.email)+'</b>'+(e.test?' <span class="hint">[test]</span>':'')+'<p class="hint">#'+e.id+' · '+esc(featl(e.features))+' · '+esc(srcl(e.source))+' · '+date(e.created)+(e.revoked?' · <b>revoked</b>':'')+'</p>'+dv+od
   +'<p class="hint">'+(e.revoked?'<a href="#" data-purge="'+e.id+'">Remove from list</a>':'<a href="#" data-rev="'+e.id+'">Revoke</a>')+'</p></div>'}
function licLoad(more){
  if(!more) lic.off=0;
  api('GET','/api/admin/licences?group='+lic.grp+'&q='+encodeURIComponent(lic.q)+'&offset='+lic.off+'&limit=25').then(function(r){
    var c=r.counts||{};
    $('ad-lf').innerHTML=FOLDERS.map(function(f){var n=f[0]==='all'?c.all:c[f[0]];return '<a href="#" class="chip'+(f[0]===lic.grp?' on':'')+'" data-grp="'+f[0]+'">'+f[1]+' <span>'+(n||0)+'</span></a>'}).join(' ');
    var html=r.items.map(licItem).join('');
    if(more) $('ad-lr').insertAdjacentHTML('beforeend',html); else $('ad-lr').innerHTML=html||'<p class="hint">Nothing found.</p>';
    lic.off+=r.items.length; $('ad-lm').style.display=r.more?'':'none';
  }).catch(function(x){say(x.message,'err')})}
function tabs(name){['lic','vis','req','sup','grant'].forEach(function(t){var p=$('ad-p-'+t), b=document.querySelector('[data-tab="'+t+'"]'); if(p) p.hidden=(t!==name); if(b) b.className='chip'+(t===name?' on':'')})}
function admin(){ $('a-admin').hidden=false; licLoad(false); api('GET','/api/admin/overview').then(function(o){
  (function(){var v=o.visits||{daily:[]};var max=Math.max.apply(null,[1].concat(v.daily.map(function(d){return d.views})));
    function row(n,t){return '<b>'+n+'</b>: '+(t?t.views:0)+' views · '+(t?t.visitors:0)+' visitors · '+(t?t.downloads:0)+' download clicks'}
    $('ad-v').innerHTML='<p>'+row('Today',v.today)+'<br>'+row('7 days',v.d7)+'<br>'+row('30 days',v.d30)+'</p>'
     +'<div style="display:flex;gap:3px;align-items:flex-end;height:70px;margin:8px 0">'+v.daily.map(function(d){return '<div title="'+d.day+': '+d.views+' views, '+d.visitors+' visitors" style="flex:1;background:#eb8a00;min-height:2px;height:'+Math.max(2,Math.round(d.views/max*70))+'px"></div>'}).join('')+'</div>'
     +'<p class="hint">Last 14 days (views). Counted since '+esc(v.since||'today')+'. No cookies, no IP stored; bots and your own logged-in browser are excluded.</p>'
     +'<p><b>Top pages (30 days)</b><br>'+((v.pages||[]).map(function(p){return esc(p.path)+' · '+p.n}).join('<br>')||'none yet')+'</p>'
     +'<p><b>Referrers (30 days)</b><br>'+((v.refs||[]).map(function(p){return esc(p.ref)+' · '+p.n}).join('<br>')||'none yet')+'</p>';
    try{localStorage.setItem('sm_me','1')}catch(e){}})();
  $('ad-r').innerHTML=(o.requests||[]).map(function(r){return '<div class="mhit"><b>#'+r.id+'</b> '+esc(r.status)+' · '+esc(r.kind)+' · '+date(r.created)+(r.email?' · <a href="mailto:'+esc(r.email)+'">'+esc(r.email)+'</a>':'')+'<p><b>'+esc(r.device)+'</b>'+(r.protocol?' · '+esc(r.protocol):'')+(r.connection?' · '+esc(r.connection):'')+'</p>'+(r.details?'<p style="white-space:pre-wrap">'+esc(r.details)+'</p>':'')+'<p class="hint">'+['new','planned','done','declined'].map(function(st){return st===r.status?'<b>'+st+'</b>':'<a href="#" data-rq="'+r.id+':'+st+'">'+st+'</a>'}).join(' · ')+'</p></div>'}).join('')||'<p class="hint">No requests yet.</p>';
  $('ad-t').innerHTML=o.tickets.map(function(t){return '<div class="mhit"><b>#'+t.id+'</b> '+esc(t.status)+' · <a href="mailto:'+esc(t.email)+'">'+esc(t.email)+'</a> · '+date(t.created)+'<p>'+esc(t.subject||'')+'</p><p style="white-space:pre-wrap">'+esc(t.message)+'</p>'+(t.status==='open'?'<button class="btn ghost" data-close="'+t.id+'" type="button">Close</button>':'')+'</div>'}).join('')||'<p class="hint">None.</p>';
  $('ad-r').innerHTML=(o.requests||[]).map(function(r){return '<div class="mhit"><b>#'+r.id+'</b> '+esc(r.status)+' · '+esc(r.kind)+' · '+date(r.created)+(r.email?' · <a href="mailto:'+esc(r.email)+'">'+esc(r.email)+'</a>':'')+'<p><b>'+esc(r.device)+'</b>'+(r.protocol?' · '+esc(r.protocol):'')+(r.connection?' · '+esc(r.connection):'')+'</p>'+(r.details?'<p style="white-space:pre-wrap">'+esc(r.details)+'</p>':'')+'<p class="hint">'+['new','planned','done','declined'].map(function(st){return st===r.status?'<b>'+st+'</b>':'<a href="#" data-rq="'+r.id+':'+st+'">'+st+'</a>'}).join(' · ')+'</p></div>'}).join('')||'<p class="hint">No requests yet.</p>';
  $('ad-t').innerHTML=o.tickets.map(function(t){return '<div class="mhit"><b>#'+t.id+'</b> '+esc(t.status)+' · <a href="mailto:'+esc(t.email)+'">'+esc(t.email)+'</a> · '+date(t.created)+'<p>'+esc(t.subject||'')+'</p><p style="white-space:pre-wrap">'+esc(t.message)+'</p>'+(t.status==='open'?'<button class="btn ghost" data-close="'+t.id+'" type="button">Close</button>':'')+'</div>'}).join('')||'<p class="hint">None.</p>';
  var nr=(o.requests||[]).filter(function(r){return r.status==='new'}).length, nt=o.tickets.filter(function(t){return t.status==='open'}).length;
  document.querySelector('[data-tab="req"]').textContent='Requests'+(nr?' ('+nr+' new)':''); document.querySelector('[data-tab="sup"]').textContent='Support'+(nt?' ('+nt+' open)':'');
}) }
$('a-form1').addEventListener('submit',function(e){e.preventDefault(); email=$('a-email').value.trim();
  if(!/^\S+@\S+\.\S+$/.test(email)){say('Enter a valid e-mail address.','err');return}
  var b=e.target.querySelector('button'); b.disabled=true;
  api('POST','/api/auth/request',{email:email}).then(function(){say('If the address is valid, a sign-in e-mail is on its way.');$('a-form2').hidden=false;$('a-code').focus()})
   .catch(function(x){say(x.status===429?'Too many attempts. Please wait a while.':'Could not send the e-mail. Try again later.','err')}).then(function(){b.disabled=false})});
$('a-form2').addEventListener('submit',function(e){e.preventDefault();
  api('POST','/api/auth/verify',{email:email,code:$('a-code').value.trim()}).then(function(){$('a-code').value='';dashboard()}).catch(function(){say('That code is wrong or has expired.','err')})});
$('a-out').addEventListener('click',function(e){e.preventDefault();api('POST','/api/auth/logout').then(function(){show('a-login');say('Signed out.')})});
$('a-dev').addEventListener('submit',function(e){e.preventDefault();
  api('POST','/api/devices',{device_id:$('a-did').value.trim(),label:$('a-lab').value.trim()}).then(function(r){
    $('a-code-out').innerHTML='<p>Activation code for <b>'+esc(r.device_id)+'</b>. Paste it into ServMod on that phone:</p><p style="word-break:break-all"><code id="a-c">'+esc(r.code)+'</code></p><button class="btn ghost" id="a-copy" type="button">Copy</button>';
    $('a-copy').onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(r.code).then(function(){$('a-copy').textContent='Copied'})};
    $('a-did').value='';dashboard()}).catch(function(x){say(x.message,'err')})});
document.addEventListener('click',function(e){var t=e.target, id; if(t.closest) t=t.closest('[data-grp],[data-tab],[data-purge],[data-pacc],[data-rev],[data-rq],[data-close],[data-rel],#a-del,#ad-lm')||t;
  if((id=t.getAttribute&&t.getAttribute('data-rel'))){ if(confirm('Release this phone? Its code will stop being yours to reuse; you have a limited number of moves per year.')) api('POST','/api/devices/release',{id:+id}).then(dashboard).catch(function(x){say(x.message,'err')}) }
  else if((id=t.getAttribute&&t.getAttribute('data-close'))) api('POST','/api/admin/ticket',{id:+id,status:'closed'}).then(admin);
  else if((id=t.getAttribute&&t.getAttribute('data-rq'))){e.preventDefault(); var pr=id.split(':'); api('POST','/api/admin/request',{id:+pr[0],status:pr[1]}).then(admin)}
  else if((id=t.getAttribute&&t.getAttribute('data-rev'))){e.preventDefault(); if(confirm('Revoke licence #'+id+'? Phones that already hold a code keep working offline.')) api('POST','/api/admin/revoke',{id:+id}).then(function(){licLoad(false)})}
  else if((id=t.getAttribute&&t.getAttribute('data-purge'))){e.preventDefault(); if(confirm('Remove revoked licence #'+id+' and its phones from the list permanently? Orders stay on record.')) api('POST','/api/admin/purge',{id:+id}).then(function(){licLoad(false)}).catch(function(x){say(x.message,'err')})}
  else if((id=t.getAttribute&&t.getAttribute('data-pacc'))){e.preventDefault(); if(confirm('Remove this account (no licence) permanently?')) api('POST','/api/admin/purge',{user_id:+id}).then(function(){licLoad(false)}).catch(function(x){say(x.message,'err')})}
  else if((id=t.getAttribute&&t.getAttribute('data-grp'))){e.preventDefault(); lic.grp=id; licLoad(false)}
  else if((id=t.getAttribute&&t.getAttribute('data-tab'))){e.preventDefault(); tabs(id)}
  else if(t.id==='ad-lm'){licLoad(true)}
  else if(t.id==='a-del'){ if(confirm('Delete your account and licences permanently? This cannot be undone.')) api('DELETE','/api/me').then(function(){show('a-login');say('Your account was deleted.')}) } });
$('ad-q').addEventListener('input',function(){clearTimeout(lic.tmr);lic.tmr=setTimeout(function(){lic.q=$('ad-q').value.trim();licLoad(false)},300)});
$('a-grant').addEventListener('submit',function(e){e.preventDefault();api('POST','/api/admin/grant',{email:$('g-email').value.trim(),seats:+$('g-seats').value||1}).then(function(){say('Licence granted.');$('g-email').value='';licLoad(false);tabs('lic')}).catch(function(x){say(x.message,'err')})});
// magic link: #t=TOKEN (fragment never reaches servers or logs)
var m=/[#&]t=([\w-]+)/.exec(location.hash);
if(m){ history.replaceState(null,'',location.pathname); say('Signing you in…');
  api('POST','/api/auth/verify',{token:m[1]}).then(dashboard).catch(function(){show('a-login');say('This link has expired or was already used. Request a new one.','err')}) }
else dashboard();
})();
