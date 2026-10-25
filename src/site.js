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
  var shop = document.getElementById('shop');
  if (shop) {
    if (location.hash === '#paid=1') {
      history.replaceState(null, '', location.pathname);
      shop.hidden = false; shop.innerHTML = '<h2>Thank you</h2><p>Your payment went through. We are sending an email with your licence details; it usually arrives within a minute. Check the spam folder if you do not see it, or write to support@servmod.com.</p>';
    } else {
      fetch('/api/shop/config').then(function (r) { return r.json(); }).then(function (c) {
        if (!c.open) return;
        var rows = [['pro', 'Pro', 'one-time', 'Write parameters, restore, manual control, fault and factory reset.'], ['sub', 'Subscription', 'per year', 'Modules and drive brands released after you buy, and updated parameter lists.']];
        var h = '<h2>Buy</h2><p class="fine">Pay by card or PayPal on a secure page of our payment provider. We never see your card. If you know your Device ID (app: Settings, Subscription) you can enter it there and the code is emailed at once.</p><div class="actions">';
        rows.forEach(function (x) { var p = c.products[x[0]]; h += '<button class="btn" type="button" data-product="' + x[0] + '">' + x[1] + ' ' + p.price + ' ' + x[2] + '</button>'; });
        shop.innerHTML = h + '</div><p class="fine" id="shop-msg"></p>'; shop.hidden = false;
        shop.addEventListener('click', function (e) {
          var b = e.target.closest('button[data-product]'); if (!b) return;
          var m = document.getElementById('shop-msg'); b.disabled = true; m.textContent = 'Opening the payment page...';
          fetch('/api/shop/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'servmod' }, body: JSON.stringify({ product: b.dataset.product }) })
            .then(function (r) { return r.json(); }).then(function (d) { if (d.url) location.href = d.url; else throw 0; })
            .catch(function () { m.textContent = 'Could not open the payment page. Please try again later.'; b.disabled = false; });
        });
      }).catch(function () {});
    }
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
