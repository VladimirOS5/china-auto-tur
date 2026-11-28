// бургер
var burger = document.getElementById('burger'), mob = document.getElementById('mobmenu');
if (burger) burger.onclick = function () { mob.classList.toggle('open'); };

// модалки
function openM(id) { var m = document.getElementById('modal-' + id); if (m) m.classList.add('open'); }
function closeM(m) { m.classList.remove('open'); }
document.querySelectorAll('[data-open]').forEach(function (b) { b.onclick = function () { openM(b.dataset.open); }; });
document.querySelectorAll('.modal').forEach(function (m) {
  m.addEventListener('click', function (e) { if (e.target === m) closeM(m); });
  m.querySelectorAll('[data-close]').forEach(function (b) { b.onclick = function () { closeM(m); }; });
});
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') document.querySelectorAll('.modal.open').forEach(closeM); });

// заявка из модалки
var rf = document.getElementById('reqform');
if (rf) rf.onsubmit = function (e) {
  e.preventDefault();
  var token = rf.querySelector('[name=csrfmiddlewaretoken]').value;
  fetch(rf.action, { method: 'POST', body: new FormData(rf), headers: { 'X-CSRFToken': token } })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      closeM(document.getElementById('modal-req'));
      if (d.ok) { rf.reset(); openM('ok'); }
      else { document.getElementById('errtext').textContent = d.error; openM('err'); }
    })
    .catch(function () { closeM(document.getElementById('modal-req')); openM('err'); });
};

// итог на странице заказа
var trim = document.getElementById('trim');
if (trim) {
  var total = document.getElementById('total');
  var recount = function () {
    var sum = parseFloat(trim.dataset.base) + parseFloat(trim.selectedOptions[0].dataset.extra || 0);
    document.querySelectorAll('input[name=options]:checked').forEach(function (c) { sum += parseFloat(c.dataset.price); });
    total.textContent = Math.round(sum).toLocaleString('ru-RU') + ' ¥';
  };
  document.querySelectorAll('#trim, input[name=options]').forEach(function (el) { el.onchange = recount; });
  recount();
}

// живой калькулятор
var cf = document.getElementById('cf');
if (cf) {
  var fmt = function (v) { return Math.round(parseFloat(v)).toLocaleString('ru-RU'); };
  var t = null;
  var run = function () {
    var p = new URLSearchParams(new FormData(cf));
    fetch('/calc/api/?' + p).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) return;
      document.getElementById('r_total').textContent = fmt(d.r.total) + ' ₽';
      ['price', 'duty', 'excise', 'vat', 'util', 'extra'].forEach(function (k) {
        document.getElementById('r_' + k).textContent = fmt(d.r[k]);
      });
      document.getElementById('c_pay').textContent = fmt(d.c.pay) + ' ₽';
      document.getElementById('c_down').textContent = fmt(d.c.down) + ' ₽';
      document.getElementById('c_over').textContent = fmt(d.c.over) + ' ₽';
      document.getElementById('sbody').innerHTML = d.c.rows.map(function (r) {
        return '<tr><td>' + r[0] + '</td><td>' + fmt(r[1]) + '</td><td>' + fmt(r[2]) + '</td><td>' + fmt(r[3]) + '</td><td>' + fmt(r[4]) + '</td></tr>';
      }).join('');
    });
  };
  cf.addEventListener('input', function (e) {
    if (e.target.name === 'down') document.getElementById('dl').textContent = e.target.value + '%';
    if (e.target.name === 'months') document.getElementById('ml').textContent = e.target.value + ' мес';
    if (e.target.name === 'annual') document.getElementById('al').textContent = e.target.value + '%';
    clearTimeout(t); t = setTimeout(run, 200);
  });
  var pick = document.getElementById('pick');
  pick.onchange = function () {
    var o = pick.selectedOptions[0];
    if (!o.dataset.price) return;
    document.getElementById('price').value = Math.round(parseFloat(o.dataset.price));
    document.getElementById('power').value = o.dataset.power;
    document.getElementById('engine').value = o.dataset.engine;
    run();
  };
  var st = document.getElementById('stoggle'), sc = document.getElementById('sched');
  st.onclick = function () { sc.hidden = !sc.hidden; st.textContent = sc.hidden ? 'Показать график платежей' : 'Скрыть график платежей'; };
  run();
}

// битая картинка -> заглушка
document.addEventListener('error', function (e) {
  var i = e.target;
  if (!i || i.tagName !== 'IMG' || i.dataset.fb) return;
  i.dataset.fb = 1;
  i.src = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="384" height="220"><rect width="384" height="220" fill="#1d1d25"/><path d="M96 140h192l-24-38c-6-9-15-14-26-14h-92c-11 0-20 5-26 14z" fill="#2a2a33"/><circle cx="140" cy="146" r="14" fill="#4d7cfe"/><circle cx="244" cy="146" r="14" fill="#ff6a00"/></svg>');
}, true);
