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
