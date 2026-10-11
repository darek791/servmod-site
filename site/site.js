(function () {
  var acct = document.getElementById('acct-link');
  if (acct && window.fetch) fetch('/api/me', { credentials: 'same-origin' }).then(function (r) { if (r.ok) acct.textContent = 'My account'; }).catch(function () {});
  var btn = document.querySelector('.menu'), nav = document.getElementById('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
  });
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
