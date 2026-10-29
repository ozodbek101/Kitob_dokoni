/* Sahifa — kichik interaktivlik. JavaScript o‘chiq bo‘lsa ham sayt ishlaydi. */
(function () {
  const som = (n) => n.toLocaleString("ru-RU").replace(/,/g, " ") + " so‘m";

  // Soni: − / + tugmalari
  document.querySelectorAll("[data-qty]").forEach((box) => {
    const input = box.querySelector("input");
    box.querySelectorAll("[data-step]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const min = Number(input.min || 0);
        const max = Number(input.max || 99);
        const next = Math.min(max, Math.max(min, Number(input.value || 0) + Number(btn.dataset.step)));
        if (next !== Number(input.value)) {
          input.value = next;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
    });
  });

  // O‘zgarganda formani avtomatik yuborish (saralash, savat soni)
  document.querySelectorAll("form[data-autosubmit]").forEach((form) => {
    let t;
    form.addEventListener("change", () => {
      clearTimeout(t);
      t = setTimeout(() => form.submit(), 350);
    });
  });

  // Mobil filtrlar
  const toggle = document.querySelector(".filters-toggle");
  const filters = document.getElementById("filters");
  if (toggle && filters) {
    toggle.addEventListener("click", () => {
      const open = filters.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Buyurtma: yetkazish narxi va manzil maydonlari
  const checkout = document.querySelector("[data-checkout]");
  if (checkout) {
    const subtotal = Number(checkout.dataset.subtotal);
    const prices = JSON.parse(checkout.dataset.prices);
    const priceEl = checkout.querySelector("[data-delivery-price]");
    const totalEl = checkout.querySelector("[data-total]");
    const address = checkout.querySelector("[data-address]");
    const pickupNote = checkout.querySelector("[data-pickup-note]");
    const region = checkout.querySelector("[name=region]");
    const submit = checkout.querySelector("[data-submit-label]");

    const update = () => {
      const method = (checkout.querySelector("[name=delivery_method]:checked") || {}).value || "courier";
      const pay = (checkout.querySelector("[name=payment_method]:checked") || {}).value;
      const price = prices[method] || 0;
      priceEl.textContent = price ? som(price) : "Bepul";
      totalEl.textContent = som(subtotal + price);

      const pickup = method === "pickup";
      pickupNote.hidden = !pickup;
      address.querySelectorAll(".fields").forEach((f) => (f.hidden = pickup));

      // Kuryer faqat Toshkentga — viloyat tanlansa pochtaga o‘tkazamiz
      const inTashkent = ["toshkent_sh", "toshkent_v"].includes(region.value);
      const courier = checkout.querySelector('[data-delivery="courier"]');
      courier.hidden = !inTashkent;
      if (!inTashkent && method === "courier") {
        checkout.querySelector('[name=delivery_method][value="post"]').checked = true;
        update();
        return;
      }
      submit.textContent = pay === "card" ? "To‘lovga o‘tish" : "Buyurtma berish";
    };
    checkout.addEventListener("change", update);
    update();
  }

  // Karta raqamini formatlash va jonli ko‘rinish
  const cardForm = document.querySelector("[data-card-form]");
  if (cardForm) {
    const num = cardForm.querySelector("[name=number]");
    const exp = cardForm.querySelector("[name=expiry]");
    const numOut = document.querySelector("[data-card-num]");
    const expOut = document.querySelector("[data-card-exp]");
    const paintNum = () => {
      const d = num.value.replace(/\D/g, "").slice(0, 16);
      num.value = d.replace(/(.{4})/g, "$1 ").trim();
      numOut.textContent = (d + "•".repeat(16 - d.length)).replace(/(.{4})/g, "$1 ").trim();
    };
    const paintExp = () => {
      let d = exp.value.replace(/\D/g, "").slice(0, 4);
      if (d.length > 2) d = d.slice(0, 2) + "/" + d.slice(2);
      exp.value = d;
      expOut.textContent = d || "OO/YY";
    };
    num.addEventListener("input", paintNum);
    exp.addEventListener("input", paintExp);
    paintNum();
    paintExp();
  }
})();
