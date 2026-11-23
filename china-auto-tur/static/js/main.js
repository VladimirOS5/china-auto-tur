// табы на странице машины: кнопка показывает свою панель и прячет остальные
document.querySelectorAll(".car-tabs__btn").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".car-tabs__btn").forEach(function (b) {
      b.classList.remove("car-tabs__btn--active");
    });
    document.querySelectorAll(".car-tabs__panel").forEach(function (p) {
      p.classList.remove("car-tabs__panel--active");
    });
    btn.classList.add("car-tabs__btn--active");
    document
      .getElementById("tab-" + btn.dataset.tab)
      .classList.add("car-tabs__panel--active");
  });
});

// итог на странице заказа: база плюс комплектация плюс опции.
// это только показ для человека: сервер пересчитает сам и своему числу не поверит
(function () {
  var totalEl = document.getElementById("order-total");
  if (!totalEl) return;
  var base = parseFloat(totalEl.dataset.base);

  function recalc() {
    var sum = base;
    var trim = document.querySelector('select[name="trim"]');
    if (trim && trim.selectedOptions[0]) {
      sum += parseFloat(trim.selectedOptions[0].dataset.delta || 0);
    }
    document
      .querySelectorAll('input[name="options"]:checked')
      .forEach(function (cb) {
        sum += parseFloat(cb.dataset.price || 0);
      });
    totalEl.textContent = Math.round(sum).toLocaleString("ru-RU") + " ¥";
  }

  document
    .querySelectorAll('select[name="trim"], input[name="options"]')
    .forEach(function (el) {
      el.addEventListener("change", recalc);
    });
  recalc();
})();

// глаз на странице входа: показываем и прячем пароль
(function () {
  var btn = document.getElementById("toggle-password");
  var input = document.getElementById("password");
  if (!btn || !input) return;
  btn.addEventListener("click", function () {
    var show = input.type === "password";
    input.type = show ? "text" : "password";
    btn.querySelector(".icon").textContent = show
      ? "visibility_off"
      : "visibility";
  });
})();

// тень у липкой шапки после прокрутки: класс вешаем один раз на скролле
(function () {
  var header = document.querySelector(".header");
  if (!header) return;
  function onScroll() {
    header.classList.toggle("scrolled", window.scrollY > 10);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();

// мобильное меню: бургер открывает, крестик и переход по ссылке закрывают
(function () {
  var burger = document.getElementById("burger");
  var menu = document.getElementById("mobile-menu");
  if (!burger || !menu) return;
  function setMenu(open) {
    menu.classList.toggle("open", open);
    burger.classList.toggle("open", open);
    document.body.classList.toggle("no-scroll", open);
  }
  burger.addEventListener("click", function () {
    setMenu(!menu.classList.contains("open"));
  });
  document.getElementById("menu-close").addEventListener("click", function () {
    setMenu(false);
  });
  menu.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () {
      setMenu(false);
    });
  });
})();

// модалки: открытие по data-modal-open, закрытие по крестику, фону и Escape
(function () {
  function open(id) {
    var m = document.getElementById("modal-" + id);
    if (!m) return;
    m.classList.add("open");
    document.body.classList.add("no-scroll");
    var first = m.querySelector("input, button.btn--primary");
    if (first) first.focus();
  }
  function close(m) {
    m.classList.remove("open");
    if (!document.querySelector(".modal.open"))
      document.body.classList.remove("no-scroll");
  }
  document.querySelectorAll("[data-modal-open]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var menu = document.getElementById("mobile-menu");
      if (menu) menu.classList.remove("open");
      open(btn.dataset.modalOpen);
    });
  });
  document.querySelectorAll(".modal").forEach(function (m) {
    m.addEventListener("click", function (e) {
      if (e.target === m) close(m);
    });
    m.querySelectorAll("[data-modal-close]").forEach(function (b) {
      b.addEventListener("click", function () {
        close(m);
      });
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape")
      document.querySelectorAll(".modal.open").forEach(close);
  });
  var retry = document.getElementById("error-retry");
  if (retry)
    retry.addEventListener("click", function () {
      close(document.getElementById("modal-error"));
      open("request");
    });

  // заявка из модалки: отправляем fetch, успех и ошибка — своими модалками
  var form = document.getElementById("request-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var err = document.getElementById("request-error");
    err.hidden = true;
    var token = form.querySelector("[name=csrfmiddlewaretoken]").value;
    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { "X-CSRFToken": token, "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.ok) {
          close(document.getElementById("modal-request"));
          form.reset();
          open("success");
        } else {
          document.getElementById("error-text").textContent =
            data.error || "Проверьте поля формы";
          close(document.getElementById("modal-request"));
          open("error");
        }
      })
      .catch(function () {
        document.getElementById("error-text").textContent =
          "Сервер не ответил. Попробуйте ещё раз.";
        close(document.getElementById("modal-request"));
        open("error");
      });
  });
})();

// калькулятор: любой контрол меняет расчёт сразу, без перезагрузки страницы
(function () {
  var form = document.getElementById("calc-form");
  if (!form) return;
  var timer = null;
  var fmt = function (v) {
    return Math.round(parseFloat(v)).toLocaleString("ru-RU") + " ₽";
  };

  function render(d) {
    document.getElementById("r-total").textContent = fmt(d.total);
    document.getElementById("r-price").textContent = fmt(d.price_rub);
    document.getElementById("r-duty").textContent = fmt(d.duty);
    document.getElementById("r-excise").textContent = fmt(d.excise);
    document.getElementById("r-vat").textContent = fmt(d.vat);
    document.getElementById("r-util").textContent = fmt(d.util);
    document.getElementById("r-fees").textContent = fmt(d.fees_total);
    document.getElementById("r-payment").textContent = fmt(d.payment);
    document.getElementById("r-down").textContent = fmt(d.down);
    document.getElementById("r-overpay").textContent = fmt(d.overpay);

    // график: столбик на месяц, снизу тело кредита синим, сверху проценты огненным
    var svg = document.getElementById("calc-chart");
    var n = d.schedule.length;
    var bw = 600 / n;
    var max = parseFloat(d.schedule[0][1]);
    var bars = "";
    for (var i = 0; i < n; i++) {
      var pay = parseFloat(d.schedule[i][1]);
      var intr = parseFloat(d.schedule[i][2]);
      var h = (pay / max) * 140;
      var hi = (intr / max) * 140;
      var x = (i * bw + 1).toFixed(2);
      var w = Math.max(bw - 2, 1).toFixed(2);
      bars +=
        '<rect x="' +
        x +
        '" y="' +
        (150 - h).toFixed(2) +
        '" width="' +
        w +
        '" height="' +
        h.toFixed(2) +
        '" fill="#ff6a00" rx="1"></rect>';
      bars +=
        '<rect x="' +
        x +
        '" y="' +
        (150 - h + hi).toFixed(2) +
        '" width="' +
        w +
        '" height="' +
        (h - hi).toFixed(2) +
        '" fill="#4d7cfe" rx="1"></rect>';
    }
    svg.innerHTML = bars;

    var body = document.getElementById("calc-schedule-body");
    body.innerHTML = d.schedule
      .map(function (s) {
        return (
          "<tr><td>" +
          s[0] +
          "</td><td>" +
          fmt(s[1]) +
          "</td><td>" +
          fmt(s[2]) +
          "</td><td>" +
          fmt(s[3]) +
          "</td><td>" +
          fmt(s[4]) +
          "</td></tr>"
        );
      })
      .join("");
  }

  function recalc() {
    var params = new URLSearchParams();
    [
      "price_cny",
      "power_hp",
      "engine",
      "age",
      "down_percent",
      "months",
      "annual_percent",
    ].forEach(function (name) {
      var el = form.querySelector("[name=" + name + "]");
      if (el) params.set(name, el.value);
    });
    fetch("/calc/api/?" + params.toString())
      .then(function (r) {
        return r.json();
      })
      .then(function (d) {
        if (d.ok) render(d);
      });
  }

  form.addEventListener("input", function (e) {
    if (e.target.id === "calc-down")
      document.getElementById("down-label").textContent = e.target.value + "%";
    if (e.target.id === "calc-months")
      document.getElementById("months-label").textContent =
        e.target.value + " мес";
    if (e.target.id === "calc-annual")
      document.getElementById("annual-label").textContent =
        e.target.value + "%";
    clearTimeout(timer);
    timer = setTimeout(recalc, 200);
  });

  // выбор машины из каталога подставляет цену, мощность и двигатель
  var carSelect = document.getElementById("calc-car");
  carSelect.addEventListener("change", function () {
    var opt = carSelect.selectedOptions[0];
    if (!opt || !opt.dataset.price) return;
    document.getElementById("calc-price").value = Math.round(
      parseFloat(opt.dataset.price),
    );
    var digits = (opt.dataset.power || "").replace(/\D/g, "");
    if (digits) document.getElementById("calc-power").value = digits;
    document.getElementById("calc-engine").value =
      opt.dataset.engine || "electric";
    recalc();
  });

  var toggle = document.getElementById("schedule-toggle");
  var table = document.getElementById("calc-schedule");
  toggle.addEventListener("click", function () {
    table.hidden = !table.hidden;
    toggle.textContent = table.hidden
      ? "Показать график платежей"
      : "Скрыть график платежей";
  });

  recalc();
})();
