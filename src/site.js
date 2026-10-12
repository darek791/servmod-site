(function () {
  var acct = document.getElementById('acct-link');
  if (acct && window.fetch) fetch('/api/me', { credentials: 'same-origin' }).then(function (r) { if (r.ok) acct.textContent = 'My account'; }).catch(function () {});
  var btn = document.querySelector('.menu'), nav = document.getElementById('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
  });
  // waiting list forms (home page, waiting-list page)
  function wlMsg(el, t, cls) { el.textContent = t; el.className = 'msg show ' + cls; }
  function wlPost(path, body) {
    return fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'servmod' }, body: JSON.stringify(body) });
  }
  document.querySelectorAll('.wl-form').forEach(function (f) {
    var m = f.querySelector('.msg');
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = {}; new FormData(f).forEach(function (v, k) { d[k] = v; });
      if (d.website) return;
      if (!d.email || !/^\S+@\S+\.\S+$/.test(d.email)) { wlMsg(m, 'Enter a valid email address.', 'err'); return; }
      var b = f.querySelector('button'); b.disabled = true; wlMsg(m, 'Sending...', 'ok');
      wlPost('/api/waitlist', d).then(function (r) {
        if (r.ok) { f.reset(); wlMsg(m, 'Almost done: we sent you an email. Click the link in it to confirm your address.', 'ok'); return; }
        if (r.status === 429) { wlMsg(m, 'Too many tries. Please try again later.', 'err'); return; }
        if (r.status === 400) { wlMsg(m, 'Please check the email address.', 'err'); return; }
        throw new Error(r.status);
      }).catch(function () { wlMsg(m, 'Could not save that. Please try again later or write to support@servmod.com.', 'err'); })
        .then(function () { b.disabled = false; });
    });
  });
  var wst = document.getElementById('wl-status');
  var wh = /[#&](confirm|unsub)=([\w-]+)/.exec(location.hash);
  if (wst && wh) {
    history.replaceState(null, '', location.pathname);
    wlPost('/api/waitlist/' + (wh[1] === 'confirm' ? 'confirm' : 'unsubscribe'), { token: wh[2] }).then(function (r) {
      if (r.ok) wlMsg(wst, wh[1] === 'confirm' ? 'Thank you, you are on the list. We will email you when ServMod is released.' : 'You are unsubscribed and your address was removed.', 'ok');
      else wlMsg(wst, 'This link is not valid any more. If you want to join, use the form below.', 'err');
    }).catch(function () { wlMsg(wst, 'Could not complete that. Please try again later.', 'err'); });
  }
  var form = document.getElementById('support-form');
  if (!form) return;
  var msg = document.getElementById('form-msg');
  function show(t, cls) { msg.textContent = t; msg.className = 'msg show ' + cls; }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = {}; new FormData(form).forEach(function (v, k) { d[k] = v; });
    if (d.website) return;
    if (!d.name || !d.email || !/^\S+@\S+\.\S+$/.test(d.email) || !d.message) {
      show('Enter your name, a valid email address and a message.', 'err'); return;
    }
    if (d.message.trim().length < 10) { show('Please write a little more (at least 10 characters).', 'err'); return; }
    var b = form.querySelector('button'); b.disabled = true; show('Sending...', 'ok');
    fetch(form.dataset.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'servmod' }, body: JSON.stringify(d) })
      .then(function (r) {
        if (r.ok) { form.reset(); show('Message sent. We will reply to the email address you gave.', 'ok'); return; }
        if (r.status === 429) { show('Too many messages from this address. Please try again later or write to support@servmod.com.', 'err'); return; }
        if (r.status === 400) { show('Please check your email address and write a message of at least 10 characters.', 'err'); return; }
        throw new Error(r.status);
      })
      .catch(function () { show('The message could not be sent. Please try again later or write to support@servmod.com.', 'err'); })
      .then(function () { b.disabled = false; });
  });
})();
