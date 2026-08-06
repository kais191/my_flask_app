/* Nested Blooms — progressive enhancement only.
   Every interaction below has a working no-JS fallback: menus are real links,
   the accordion panels start open, and add-to-basket is a normal form post. */

(function () {
  'use strict';

  var on = function (el, type, fn) { if (el) el.addEventListener(type, fn); };
  var all = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };

  /* ---------------------------------------------------- mobile drawer -- */

  var drawer = document.querySelector('[data-menu-panel]');
  var scrim = document.querySelector('.drawer__scrim');

  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle('is-open', open);
    if (scrim) scrim.classList.toggle('is-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    all('[data-menu-toggle]').forEach(function (btn) {
      if (btn.hasAttribute('aria-expanded')) {
        btn.setAttribute('aria-expanded', String(open));
      }
    });
  }

  all('[data-menu-toggle]').forEach(function (btn) {
    on(btn, 'click', function () {
      setDrawer(!drawer.classList.contains('is-open'));
    });
  });

  /* ----------------------------------------------------- search panel -- */

  var searchPanel = document.querySelector('[data-search-panel]');
  all('[data-search-toggle]').forEach(function (btn) {
    on(btn, 'click', function () {
      if (!searchPanel) return;
      var hidden = searchPanel.hasAttribute('hidden');
      if (hidden) {
        searchPanel.removeAttribute('hidden');
        var input = searchPanel.querySelector('input');
        if (input) input.focus();
      } else {
        searchPanel.setAttribute('hidden', '');
      }
    });
  });

  on(document, 'keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (searchPanel && !searchPanel.hasAttribute('hidden')) {
      searchPanel.setAttribute('hidden', '');
    }
    if (drawer && drawer.classList.contains('is-open')) setDrawer(false);
  });

  /* --------------------------------------------------------- flashes -- */

  all('.flash__close').forEach(function (btn) {
    on(btn, 'click', function () {
      var flash = btn.closest('.flash');
      if (flash) flash.remove();
    });
  });

  /* ------------------------------------------------------- accordions -- */
  // Panels are rendered open so they work without JS; collapse them on load.
  all('.accordion__trigger').forEach(function (trigger, index) {
    var panel = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!panel) return;
    var open = index === 0;
    trigger.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;

    on(trigger, 'click', function () {
      var expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      panel.hidden = expanded;
    });
  });

  /* ------------------------------------------------ product page maths -- */

  var priceForm = document.querySelector('[data-price-form]');
  if (priceForm) {
    var priceOut = document.querySelector('[data-price-out]');
    var basePrice = parseInt(priceForm.dataset.basePrice, 10) || 0;

    var formatEuro = function (cents) {
      return '€' + (cents / 100).toFixed(2);
    };

    var recalc = function () {
      var total = basePrice;
      var size = priceForm.querySelector('input[name="size"]:checked');
      if (size) total += parseInt(size.dataset.delta, 10) || 0;
      all('input[name="addons"]:checked', priceForm).forEach(function (input) {
        total += parseInt(input.dataset.price, 10) || 0;
      });
      var qty = parseInt(priceForm.querySelector('input[name="quantity"]').value, 10) || 1;
      if (priceOut) priceOut.textContent = formatEuro(total * qty);
    };

    all('input[name="size"], input[name="addons"]', priceForm).forEach(function (input) {
      on(input, 'change', recalc);
    });

    /* quantity stepper */
    var qtyInput = priceForm.querySelector('input[name="quantity"]');
    all('[data-qty]', priceForm).forEach(function (btn) {
      on(btn, 'click', function () {
        var step = btn.dataset.qty === 'up' ? 1 : -1;
        var next = (parseInt(qtyInput.value, 10) || 1) + step;
        qtyInput.value = Math.max(1, Math.min(99, next));
        recalc();
      });
    });
    on(qtyInput, 'change', recalc);
    recalc();
  }

  /* ----------------------------------------------- card message counter */

  all('[data-counter]').forEach(function (textarea) {
    var output = document.querySelector(textarea.dataset.counter);
    if (!output) return;
    var max = parseInt(textarea.getAttribute('maxlength'), 10) || 450;
    var update = function () {
      output.textContent = textarea.value.length + ' / ' + max + ' characters';
    };
    on(textarea, 'input', update);
    update();
  });

  /* ------------------------------------- delivery option ↔ date coupling */
  // Same-day cannot be scheduled ahead, and next-day cannot be booked for
  // today, so keep the date input's bounds honest as the option changes.
  var dateInput = document.querySelector('[data-delivery-date]');
  if (dateInput) {
    var applyBounds = function () {
      var option = document.querySelector('input[name="delivery_option"]:checked');
      if (!option) return;
      var min = option.dataset.earliest;
      if (!min) return;
      dateInput.min = min;
      if (!dateInput.value || dateInput.value < min) dateInput.value = min;
      if (option.value === 'sameday') {
        dateInput.max = min;
      } else {
        dateInput.max = dateInput.dataset.maxDate || '';
      }
    };
    all('input[name="delivery_option"]').forEach(function (input) {
      on(input, 'change', applyBounds);
    });
    applyBounds();
  }

  /* ---------------------------------------------------- sort dropdown -- */

  var sortSelect = document.querySelector('[data-sort]');
  on(sortSelect, 'change', function () {
    if (sortSelect.form) sortSelect.form.submit();
  });

  /* ------------------------------------------- card number formatting -- */

  var cardNumber = document.querySelector('[data-card-number]');
  on(cardNumber, 'input', function () {
    var digits = cardNumber.value.replace(/\D/g, '').slice(0, 19);
    cardNumber.value = digits.replace(/(.{4})/g, '$1 ').trim();
  });

  var cardExpiry = document.querySelector('[data-card-expiry]');
  on(cardExpiry, 'input', function () {
    var digits = cardExpiry.value.replace(/\D/g, '').slice(0, 4);
    cardExpiry.value = digits.length > 2
      ? digits.slice(0, 2) + '/' + digits.slice(2)
      : digits;
  });
})();
