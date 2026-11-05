(function(){
function $(i){return document.getElementById(i)}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function mb(n){return (n/1048576).toFixed(2)+' MB'}
function lock(txt,btn,href){$('mb-lock').hidden=false;$('mb-lock-txt').textContent=txt;var b=$('mb-lock-btn');b.textContent=btn;b.href=href}
fetch('/api/box/firmware',{credentials:'same-origin'}).then(function(r){
  if(r.status===401)return lock('Sign in with the e-mail address you used to buy ServMod Pro. After signing in, come back to this page.','Sign in','/account/');
  if(r.status===403)return lock('This section is for ServMod Pro owners. Your account does not have Pro yet.','See pricing','/pricing.html');
  if(r.status===404)return lock('The firmware is being prepared and will appear here soon.','Back to account','/account/');
  if(!r.ok)return lock('Something went wrong. Please try again in a moment.','Account','/account/');
  return r.json().then(function(m){
    $('mb-open').hidden=false;
    $('mb-ver').textContent='version '+m.version+(m.build_date?' ('+m.build_date+')':'');
    $('mb-doc').innerHTML=(m.schematics||[]).filter(function(s){return /\.png$/i.test(s.file)}).map(function(s){
      var title=/mini/i.test(s.file)?'ServMod Box mini (experimental)':'ServMod Box (ESP32-S3 DevKit)';
      var svg=(m.schematics||[]).filter(function(x){return x.file===s.file.replace(/\.png$/i,'.svg')})[0];
      return '<figure class="instshot"><figcaption><b>'+title+'</b>'+(svg?' · <a href="'+esc(svg.url)+'" target="_blank" rel="noopener">SVG</a>':'')+'</figcaption><a href="'+esc(s.url)+'" target="_blank" rel="noopener"><img src="'+esc(s.url)+'" alt="Wiring diagram: '+title+'" loading="lazy" style="width:100%;height:auto"></a></figure>'}).join('');
    var h='';
    Object.keys(m.boxes||{}).forEach(function(k){var b=m.boxes[k];
      h+='<h3 style="margin:22px 0 8px">'+esc(b.title)+'</h3>';
      b.files.forEach(function(f){
        h+='<div class="fwrow" style="border:1px solid #2a2a2a;padding:12px 14px;margin:10px 0"><p style="margin:0"><b>'+esc(f.label)+'</b> · offset <code>'+esc(f.offset)+'</code> · flash '+f.flash_size_mb+' MB · '+mb(f.bytes)+'</p>'
         +'<p class="hint" style="margin:4px 0">'+esc(f.use)+'</p>'
         +'<p class="hint" style="margin:4px 0">'+esc(f.verified||'')+'</p>'
         +'<p style="margin:8px 0 4px"><a class="btn" href="'+esc(f.url)+'" download>Download '+esc(f.file)+'</a></p>'
         +'<p class="hint" style="margin:4px 0;word-break:break-all">SHA-256 '+esc(f.sha256)+'</p></div>'});
    });
    $('mb-fw').innerHTML=h;
  });
}).catch(function(){lock('Could not reach the server. Check your connection and try again.','Account','/account/')});
})();
