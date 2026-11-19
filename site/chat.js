(function () {
  var box, log, input, hist = [], busy = false;
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x) e.textContent = x; return e; }
  function add(role, text) { var m = el("div", "cm " + role, text); log.appendChild(m); log.scrollTop = log.scrollHeight; return m; }
  function send() {
    var q = input.value.trim(); if (!q || busy) return;
    input.value = ""; add("user", q); hist.push({ role: "user", content: q }); busy = true;
    var wait = add("bot", "Thinking...");
    fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json", "X-Requested-With": "servmod" }, body: JSON.stringify({ messages: hist.slice(-6) }) })
      .then(function (r) { return r.json(); })
      .then(function (d) { wait.textContent = d.reply || "No answer."; hist.push({ role: "assistant", content: d.reply || "" }); })
      .catch(function () { wait.textContent = "The assistant is offline. Please use the Support page."; })
      .then(function () { busy = false; log.scrollTop = log.scrollHeight; });
  }
  function build() {
    var btn = el("button", "chatbtn", "Ask ServMod"); btn.type = "button"; btn.setAttribute("aria-expanded", "false");
    box = el("div", "chatbox"); box.hidden = true; box.setAttribute("role", "dialog"); box.setAttribute("aria-label", "ServMod assistant");
    var head = el("div", "chathead"); head.appendChild(el("b", "", "ServMod assistant"));
    var x = el("button", "chatx", "×"); x.type = "button"; x.setAttribute("aria-label", "Close"); head.appendChild(x);
    log = el("div", "chatlog"); log.setAttribute("aria-live", "polite");
    var note = el("p", "chatnote", "AI assistant. It can be wrong: check the manufacturer manual before touching equipment. Questions are processed on our own server and not stored.");
    var row = el("div", "chatrow"); input = el("input"); input.type = "text"; input.maxLength = 600; input.placeholder = "Ask about drives, fault codes, pricing..."; input.setAttribute("aria-label", "Your question");
    var go = el("button", "chatgo", "Send"); go.type = "button"; row.appendChild(input); row.appendChild(go);
    box.appendChild(head); box.appendChild(log); box.appendChild(note); box.appendChild(row);
    document.body.appendChild(btn); document.body.appendChild(box);
    add("bot", "Hi! Ask me about supported drives, wiring, fault codes, the free version or Pro.");
    function toggle(o) { box.hidden = !o; btn.setAttribute("aria-expanded", o); btn.style.display = o ? "none" : ""; if (o) input.focus(); }
    function fit() { var v = window.visualViewport; if (!v || window.innerWidth > 600 || box.hidden) { box.style.top = box.style.height = ""; return; }
      box.style.top = (v.offsetTop + 8) + "px"; box.style.height = (v.height - 16) + "px"; }
    if (window.visualViewport) { visualViewport.addEventListener("resize", fit); visualViewport.addEventListener("scroll", fit); }
    var t0 = toggle; toggle = function (o) { t0(o); fit(); if (o) setTimeout(fit, 300); };
    btn.onclick = function () { toggle(true); }; x.onclick = function () { toggle(false); };
    go.onclick = send; input.onkeydown = function (e) { if (e.key === "Enter") send(); };
  }
  build();
})();
