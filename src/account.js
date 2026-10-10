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
  $('a-ents').innerHTML=me.entitlements.length?me.entitlements.map(function(e){return '<p>'+(e.revoked?'<b>Revoked</b> — ':'')+'Licence #'+e.id+' · '+e.seats+' phone'+(e.seats>1?'s':'')+' ('+e.seats_used+' in use) · device moves left this year: '+e.moves_left+'</p>'}).join(''):'<p>There is no licence on this account yet. <a href="/pricing.html">See pricing</a>. If you bought ServMod, make sure you signed in with the e-mail used for the purchase.</p>';
  var ls=me.licences.filter(function(l){return !l.released});
  $('a-devs').innerHTML=ls.length?ls.map(function(l){return '<div class="mhit"><b>'+esc(l.label||'Phone')+'</b> <span class="hint">'+esc(l.device_id)+' · added '+date(l.created)+'</span><p style="word-break:break-all;font-size:.85rem"><code>'+esc(l.code)+'</code></p><button class="btn ghost" data-rel="'+l.id+'" type="button">Release this phone</button></div>'}).join(''):'<p class="hint">No phone activated yet.</p>';
  if(me.admin) admin(); else $('a-admin').hidden=true;
 }).catch(function(e){ show('a-login'); if(e.status!==401) say('Could not load your account. Try again later.','err') }) }
function admin(){ $('a-admin').hidden=false; api('GET','/api/admin/overview').then(function(o){
  $('ad-t').innerHTML=o.tickets.map(function(t){return '<div class="mhit"><b>#'+t.id+'</b> '+esc(t.status)+' · <a href="mailto:'+esc(t.email)+'">'+esc(t.email)+'</a> · '+date(t.created)+'<p>'+esc(t.subject||'')+'</p><p style="white-space:pre-wrap">'+esc(t.message)+'</p>'+(t.status==='open'?'<button class="btn ghost" data-close="'+t.id+'" type="button">Close</button>':'')+'</div>'}).join('')||'<p class="hint">None.</p>';
  $('ad-u').innerHTML=o.users.map(function(u){return '<p>'+esc(u.email)+' <span class="hint">since '+date(u.created)+'</span></p>'}).join('')+o.entitlements.map(function(e){return '<p class="hint">Licence #'+e.id+' · '+esc(e.email)+' · '+e.seats+' seat(s) · '+esc(e.source)+(e.revoked?' · revoked':' · <a href="#" data-rev="'+e.id+'">revoke</a>')+'</p>'}).join('')}) }
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
document.addEventListener('click',function(e){var t=e.target, id;
  if((id=t.getAttribute&&t.getAttribute('data-rel'))){ if(confirm('Release this phone? Its code will stop being yours to reuse; you have a limited number of moves per year.')) api('POST','/api/devices/release',{id:+id}).then(dashboard).catch(function(x){say(x.message,'err')}) }
  else if((id=t.getAttribute&&t.getAttribute('data-close'))) api('POST','/api/admin/ticket',{id:+id,status:'closed'}).then(admin);
  else if((id=t.getAttribute&&t.getAttribute('data-rev'))){e.preventDefault(); if(confirm('Revoke licence #'+id+'?')) api('POST','/api/admin/revoke',{id:+id}).then(dashboard)}
  else if(t.id==='a-del'){ if(confirm('Delete your account and licences permanently? This cannot be undone.')) api('DELETE','/api/me').then(function(){show('a-login');say('Your account was deleted.')}) } });
$('a-grant').addEventListener('submit',function(e){e.preventDefault();api('POST','/api/admin/grant',{email:$('g-email').value.trim(),seats:+$('g-seats').value||1}).then(function(){say('Licence granted.');$('g-email').value='';admin()}).catch(function(x){say(x.message,'err')})});
// magic link: #t=TOKEN (fragment never reaches servers or logs)
var m=/[#&]t=([\w-]+)/.exec(location.hash);
if(m){ history.replaceState(null,'',location.pathname); say('Signing you in…');
  api('POST','/api/auth/verify',{token:m[1]}).then(dashboard).catch(function(){show('a-login');say('This link has expired or was already used. Request a new one.','err')}) }
else dashboard();
})();
