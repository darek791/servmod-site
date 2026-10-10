(function () {
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
    var b = form.querySelector('button'); b.disabled = true; show('Sending...', 'ok');
    fetch(form.dataset.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); show('Message sent. We will reply to the email address you gave.', 'ok'); })
      .catch(function () { show('The message could not be sent because the support service is not live yet. Please write to support@servmod.com instead.', 'err'); })
      .then(function () { b.disabled = false; });
  });
})();
