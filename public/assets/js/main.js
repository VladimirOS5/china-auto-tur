/* ==========================================================
   main.js — общая логика всех страниц.
   Сейчас: открытие и закрытие мобильного меню.
   ========================================================== */

"use strict";

/* Ищем бургер и меню на странице */
const burger = document.getElementById("burger");
const nav = document.getElementById("main-nav");

/* Работаем только если оба элемента найдены */
if (burger && nav) {
  burger.addEventListener("click", function () {
    /* toggle возвращает true, если класс добавлен, и false, если убран */
    const isOpen = nav.classList.toggle("is-open");

    /* Сообщаем скринридерам текущее состояние меню */
    burger.setAttribute("aria-expanded", isOpen);
  });
}
