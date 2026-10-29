"""Yetkazib berish narxlari va muddatlari bir joyda."""

FREE_COURIER_FROM = 300_000  # shu summadan boshlab kuryer bepul

OPTIONS = {
    "courier": {"price": 25_000, "eta": "Ertaga, 10:00–21:00", "note": "Toshkent shahri va viloyati"},
    "post": {"price": 35_000, "eta": "2–4 kun", "note": "Barcha viloyatlarga"},
    "pickup": {"price": 0, "eta": "Bugundan, 9:00–20:00", "note": "Chilonzor, Bunyodkor ko‘chasi 1"},
}


def delivery_price(method, subtotal):
    option = OPTIONS.get(method, OPTIONS["courier"])
    if method == "courier" and subtotal >= FREE_COURIER_FROM:
        return 0
    return option["price"]
