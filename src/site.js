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
    var ph = location.hash;
    if (ph === '#paid=problem' || ph === '#paid=1' || ph === '#paid=app') {
      history.replaceState(null, '', location.pathname);
      var mainEl = document.getElementById('main'), T;
      if (ph === '#paid=app') T = ['ok', 'Thank you!', 'Your licence is being activated.', 'Go back to the ServMod app. It activates by itself in a few seconds, you do not need to do anything else.', 'A receipt is also on its way to your email.', '<a class="btn ghost" href="/">Back to servmod.com</a>'];
      else if (ph === '#paid=1') T = ['ok', 'Thank you!', 'Your payment went through.', 'To activate the app: open Settings, Subscription, copy your Device ID and paste it on your account page. Your code appears there and is sent to your email.', 'A receipt is also on its way to your email.', '<a class="btn" href="/account/">Open my account</a>'];
      else T = ['warn', 'One moment', 'We could not confirm your payment automatically.', 'If money left your account, write to support@servmod.com and we will sort it out by hand.', '', '<a class="btn" href="/support.html">Contact support</a>'];
      var card = '<div class="wrap page"><div class="thanks ' + T[0] + '"><div class="mark" aria-hidden="true">' + (T[0] === 'ok' ? '&#10003;' : '!') + '</div><h1>' + T[1] + '</h1><p class="lead2">' + T[2] + '</p><p>' + T[3] + '</p>' + (T[4] ? '<p class="fine">' + T[4] + '</p>' : '') + '<div class="actions" style="justify-content:center">' + T[5] + '</div></div></div>';
      if (mainEl) mainEl.innerHTML = card;
      document.title = T[1] + ' - ServMod'; window.scrollTo(0, 0);
    } else {
      fetch('/api/shop/config').then(function (r) { return r.json(); }).then(function (c) {
        if (!c.open) return;
        var rows = [['pro', 'Pro', 'one-time', 'Write parameters, restore, manual control, fault and factory reset.'], ['sub', 'Subscription', 'per year', 'Modules and drive brands released after you buy, and updated parameter lists.']];
        var h = '<h2>Buy</h2><p class="fine">Pay by card' + (c.stripe && c.paypal ? ' or PayPal' : '') + ' on a secure page of our payment provider. We never see your card. With a card you can enter your Device ID (app: Settings, Subscription) and the code is emailed at once; with PayPal, or if you leave it empty, you get the code on your account page.</p><div class="actions">';
        var provs = []; if (c.stripe) provs.push(['stripe', 'card']); if (c.paypal) provs.push(['paypal', 'PayPal']);
        rows.forEach(function (x) { var p = c.products[x[0]]; provs.forEach(function (v) { h += '<button class="btn' + (v[0] === 'paypal' ? ' ghost' : '') + '" type="button" data-product="' + x[0] + '" data-provider="' + v[0] + '">' + x[1] + ' ' + p.price + ' ' + x[2] + ' (' + v[1] + ')</button> '; }); });
        shop.innerHTML = h + '</div><p class="fine">By buying you accept the <a href="/terms.html">Terms</a> and <a href="/refunds.html">Refunds policy</a>. You ask us to deliver your activation code at once and you accept that you then lose the 14-day right to cancel.</p><p class="fine" id="shop-msg"></p>'; shop.hidden = false;
        ['shop-closed', 'shop-closed2'].forEach(function (id) { var el = document.getElementById(id); if (el) el.hidden = true; });
        shop.addEventListener('click', function (e) {
          var b = e.target.closest('button[data-product]'); if (!b) return;
          var m = document.getElementById('shop-msg'); b.disabled = true; m.textContent = 'Opening the payment page...';
          fetch('/api/shop/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'servmod' }, body: JSON.stringify({ product: b.dataset.product, provider: b.dataset.provider }) })
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
