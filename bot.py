# ============================================
#  NAIRY STARS — МАГАЗИН ЗВЁЗД TELEGRAM
# ============================================

import telebot
from telebot import types
import json
import os
from datetime import datetime

# ============================================
#  НАСТРОЙКИ (ПОМЕНЯЙ ЗДЕСЬ!)
# ============================================

TOKEN = "8860134940:AAE4sN0Gk8U9DS8Q63LmFfLSfKvmPQe8bLA"
ADMIN_ID = 7677873255

MIN_STARS = 15

BANK_CARD = "4400 4302 2119 7087"
BANK_NAME = "Назерке Х."

REVIEW_LINK = "https://t.me/proofnairy/3"

# ============================================
#  БАЗА ДАННЫХ
# ============================================

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        default = {
            "orders": [],
            "users": {},
            "reviews": [],
            "last_order_id": 0,
            "admin_stats": {
                "total_completed": 0,
                "total_cancelled": 0,
                "total_earned": 0
            }
        }
        save_db(default)
        return default
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_order(user_id, username, amount, price_per, total_price, recipient, recipient_username):
    db = load_db()
    db["last_order_id"] += 1
    order = {
        "id": db["last_order_id"],
        "user_id": user_id,
        "username": username,
        "type": "buy",
        "category": "stars",
        "amount": amount,
        "price_per": price_per,
        "total_price": total_price,
        "status": "pending",
        "recipient": recipient,
        "recipient_username": recipient_username,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "completed_at": None
    }
    db["orders"].append(order)
    if str(user_id) not in db["users"]:
        db["users"][str(user_id)] = {"username": username, "total_orders": 0, "total_spent": 0}
    db["users"][str(user_id)]["total_orders"] += 1
    db["users"][str(user_id)]["total_spent"] += total_price
    save_db(db)
    return order

def update_order_status(order_id, status):
    db = load_db()
    for order in db["orders"]:
        if order["id"] == order_id:
            order["status"] = status
            if status == "completed":
                order["completed_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                db["admin_stats"]["total_completed"] += 1
                db["admin_stats"]["total_earned"] += order["total_price"]
            elif status == "cancelled":
                db["admin_stats"]["total_cancelled"] += 1
            save_db(db)
            return order
    return None

def get_pending_orders():
    db = load_db()
    return [o for o in db["orders"] if o["status"] in ["pending", "paid"]]

def get_all_orders(limit=20):
    db = load_db()
    return db["orders"][-limit:]

def get_admin_stats():
    db = load_db()
    return db["admin_stats"]

def get_user_orders(user_id):
    db = load_db()
    return [o for o in db["orders"] if o["user_id"] == user_id]

def add_review(order_id, user_id, username, rating, text):
    db = load_db()
    review = {
        "order_id": order_id,
        "user_id": user_id,
        "username": username,
        "rating": rating,
        "text": text,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }
    db["reviews"].append(review)
    save_db(db)

def get_order_from_db(order_id):
    db = load_db()
    for o in db["orders"]:
        if o["id"] == order_id:
            return o
    return None

# ============================================
#  КНОПКИ
# ============================================

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("⭐ Купить звёзды", callback_data="buy_stars"),
        types.InlineKeyboardButton("📋 Мои заказы", callback_data="my_orders"),
        types.InlineKeyboardButton("ℹ️ О магазине", callback_data="about")
    )
    return kb

def recipient_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Себе", callback_data="recipient_me"),
        types.InlineKeyboardButton("👥 Другу", callback_data="recipient_friend")
    )
    kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu"))
    return kb

def cancel_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action"))
    return kb

def pay_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ Я оплатил", callback_data="paid"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")
    )
    return kb

def order_keyboard(order_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{order_id}"),
        types.InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{order_id}")
    )
    return kb

def stars_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=5)
    kb.add(
        types.InlineKeyboardButton("1", callback_data="rate_1"),
        types.InlineKeyboardButton("2", callback_data="rate_2"),
        types.InlineKeyboardButton("3", callback_data="rate_3"),
        types.InlineKeyboardButton("4", callback_data="rate_4"),
        types.InlineKeyboardButton("5", callback_data="rate_5")
    )
    return kb

def admin_panel_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📋 Активные заказы", callback_data="admin_orders"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("📝 Все заказы", callback_data="admin_all_orders"),
        types.InlineKeyboardButton("⭐ Отзывы", callback_data="admin_reviews"),
        types.InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")
    )
    return kb

# ============================================
#  БОТ
# ============================================

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_data = {}

# ========== СТАРТ ==========
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    user_data.pop(message.from_user.id, None)

    if message.from_user.id == ADMIN_ID:
        show_admin_panel(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        photo="https://i.ibb.co/q3V6PQx0/1782466395871.png",
        caption=(
            "🌟 <b>Добро пожаловать в Nairy Stars!</b> 🌟\n\n"
            "✨ <i>Ваш надёжный магазин Telegram Stars</i>\n\n"
            "🚀 Мгновенная доставка\n"
            "💎 Лучшие цены на рынке\n"
            "🛡️ Безопасная сделка\n"
            "⭐ Более 1100 довольных клиентов\n\n"
            "Выберите действие:"
        ),
        reply_markup=main_menu()
    )

# ========== АДМИН-ПАНЕЛЬ ==========
def show_admin_panel(chat_id):
    stats = get_admin_stats()
    pending = get_pending_orders()

    text = (
        "🔐 <b>Админ-панель Nairy Stars</b>\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "📊 <b>Статистика:</b>\n"
        f"✅ Выполнено: {stats['total_completed']}\n"
        f"❌ Отменено: {stats['total_cancelled']}\n"
        f"💰 Заработано: {stats['total_earned']} ₸\n"
        f"⏳ В ожидании: {len(pending)}\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Выберите действие:"
    )

    bot.send_message(chat_id, text, reply_markup=admin_panel_keyboard())

# ========== ФУНКЦИИ АДМИНА ==========

def show_pending_orders(chat_id):
    pending = get_pending_orders()
    if not pending:
        bot.send_message(chat_id, "✅ Нет активных заказов", reply_markup=admin_panel_keyboard())
        return

    for o in pending:
        recipient = "себе" if o.get("recipient") == "me" else f"другу @{o.get('recipient_username', '?')}"
        status_emoji = {"pending": "⏳", "paid": "💰"}
        text = (
            f"📋 <b>Заказ #{o['id']}</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 Клиент: @{o['username']}\n"
            f"⭐ Количество: {o['amount']} звёзд\n"
            f"💰 Сумма: {o['total_price']} ₸\n"
            f"📤 Кому: {recipient}\n"
            f"🕐 Создан: {o['created_at']}\n"
            f"📌 Статус: {status_emoji.get(o['status'], '❓')} {o['status']}"
        )
        bot.send_message(chat_id, text, reply_markup=order_keyboard(o["id"]))

def show_all_orders(chat_id):
    orders = get_all_orders(30)
    if not orders:
        bot.send_message(chat_id, "📝 История пуста", reply_markup=admin_panel_keyboard())
        return

    text = "📝 <b>История заказов:</b>\n\n"
    for o in reversed(orders):
        status_emoji = {"pending": "⏳", "paid": "💰", "completed": "✅", "cancelled": "❌"}
        recipient = "себе" if o.get("recipient") == "me" else f"@{o.get('recipient_username', '?')}"
        text += f"{status_emoji.get(o['status'], '❓')} #{o['id']} | @{o['username']} | {o['amount']}⭐ | {o['total_price']}₸\n"

    bot.send_message(chat_id, text, reply_markup=admin_panel_keyboard())

def show_stats(chat_id):
    stats = get_admin_stats()
    pending = get_pending_orders()

    text = (
        "📊 <b>Статистика Nairy Stars</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        f"✅ Выполнено заказов: <b>{stats['total_completed']}</b>\n"
        f"❌ Отменено заказов: <b>{stats['total_cancelled']}</b>\n"
        f"💰 Заработано: <b>{stats['total_earned']} ₸</b>\n"
        f"⏳ Активных: <b>{len(pending)}</b>\n"
        f"📦 Всего в базе: <b>{len(load_db()['orders'])}</b>"
    )

    bot.send_message(chat_id, text, reply_markup=admin_panel_keyboard())

def show_reviews(chat_id):
    db = load_db()
    if not db["reviews"]:
        bot.send_message(chat_id, "⭐ Пока нет отзывов", reply_markup=admin_panel_keyboard())
        return

    text = "⭐ <b>Отзывы клиентов:</b>\n\n"
    for r in db["reviews"][-15:]:
        stars = "⭐" * r["rating"]
        text += f"{stars} | @{r['username']}\n💬 {r['text']}\n🕐 {r['date']}\n\n"

    bot.send_message(chat_id, text, reply_markup=admin_panel_keyboard())

def complete_order(order_id, admin_chat_id):
    order = update_order_status(order_id, "completed")
    if not order:
        bot.send_message(admin_chat_id, f"❌ Заказ #{order_id} не найден!")
        return

    bot.send_message(admin_chat_id, f"✅ Заказ #{order_id} выполнен!")

    recipient_text = "Вам" if order.get("recipient") == "me" else f"другу @{order.get('recipient_username', 'Неизвестно')}"

    bot.send_message(
        order["user_id"],
        f"🌟 <b>Заказ #{order_id} выполнен!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Товар: {order['amount']} звёзд Telegram\n"
        f"👤 Отправлено: {recipient_text}\n"
        f"💰 Сумма: {order['total_price']} ₸\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"🤍 <i>Спасибо, что выбрали Nairy Stars!</i>\n"
        f"<i>Будем рады видеть вас снова!</i>\n\n"
        f"📝 <b>Пожалуйста, оставьте отзыв:</b>\n"
        f"Напишите: @naiiryy1\n\n"
        f"⚠️ <i>Не оставите отзыв — блок!</i>",
        reply_markup=main_menu()
    )

def cancel_order(order_id, admin_chat_id):
    order = update_order_status(order_id, "cancelled")
    if not order:
        bot.send_message(admin_chat_id, f"❌ Заказ #{order_id} не найден!")
        return

    bot.send_message(admin_chat_id, f"❌ Заказ #{order_id} отменён!")
    bot.send_message(
        order["user_id"],
        f"❌ <b>Заказ #{order_id} отменён</b>\n\n"
        f"Свяжитесь с нами: @naiiryy1"
    )

# ========== CALLBACK-ОБРАБОТЧИК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    username = call.from_user.username or "NoName"
    message_id = call.message.message_id

    # ===== АДМИН-КНОПКИ =====
    if user_id == ADMIN_ID:
        if call.data == "admin_orders":
            bot.answer_callback_query(call.id)
            show_pending_orders(chat_id)
            return

        if call.data == "admin_stats":
            bot.answer_callback_query(call.id)
            show_stats(chat_id)
            return

        if call.data == "admin_all_orders":
            bot.answer_callback_query(call.id)
            show_all_orders(chat_id)
            return

        if call.data == "admin_reviews":
            bot.answer_callback_query(call.id)
            show_reviews(chat_id)
            return

        if call.data == "admin_refresh":
            bot.answer_callback_query(call.id, "Обновлено!")
            show_admin_panel(chat_id)
            return

        if call.data.startswith("done_"):
            order_id = int(call.data.split("_")[1])
            bot.answer_callback_query(call.id, "Выполнено!")
            complete_order(order_id, chat_id)
            return

        if call.data.startswith("cancel_"):
            order_id = int(call.data.split("_")[1])
            bot.answer_callback_query(call.id, "Отменено!")
            cancel_order(order_id, chat_id)
            return

    # ===== ОБЫЧНЫЕ КНОПКИ =====

    if call.data == "back_to_menu":
        user_data.pop(user_id, None)
        try:
            bot.edit_message_caption(
                caption="Выберите действие:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=main_menu()
            )
        except:
            bot.edit_message_text(
                "Выберите действие:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=main_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data == "about":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "🌟 <b>Nairy Stars</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Магазин по продаже Telegram Stars.\n"
            "Быстрые, качественные и выгодные цены.\n\n"
            "🎯 <i>Наша цель — простота, удобство и надёжность.</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "⭐ Более 1100 отзывов\n\n"
            "📢 Канал:\n"
            "https://t.me/naiiiryyyy\n\n"
            "📞 По вопросам:\n"
            "@naiiryy1",
            reply_markup=main_menu(),
            disable_web_page_preview=True
        )
        return

    if call.data == "buy_stars":
        user_data[user_id] = {"step": "ask_recipient"}
        try:
            bot.edit_message_caption(
                caption="⭐ <b>Покупка звёзд Telegram</b>\n\nКому отправляем звёзды?",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=recipient_menu()
            )
        except:
            bot.edit_message_text(
                "⭐ <b>Покупка звёзд Telegram</b>\n\nКому отправляем звёзды?",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=recipient_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data == "my_orders":
        user_orders = get_user_orders(user_id)
        if not user_orders:
            try:
                bot.edit_message_caption(
                    caption="📋 У вас пока нет заказов",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=main_menu()
                )
            except:
                bot.edit_message_text(
                    "📋 У вас пока нет заказов",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=main_menu()
                )
            bot.answer_callback_query(call.id)
            return

        text = "📋 <b>Ваши заказы:</b>\n\n"
        for o in user_orders[-5:]:
            status_emoji = {"pending": "⏳", "paid": "💰", "completed": "✅", "cancelled": "❌"}
            recipient = "Себе" if o.get("recipient") == "me" else f"Другу @{o.get('recipient_username', '?')}"
            text += f"{status_emoji.get(o['status'], '❓')} <b>Заказ #{o['id']}</b>\n"
            text += f"   {o['amount']} ⭐ → {recipient}\n"
            text += f"   {o['total_price']} ₸\n\n"

        try:
            bot.edit_message_caption(caption=text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu())
        except:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return

    if call.data == "recipient_me":
        user_data[user_id] = {"step": "ask_amount", "recipient": "me", "recipient_username": username}
        try:
            bot.edit_message_caption(
                caption=f"✅ Звёзды будут отправлены <b>Вам</b> (@{username})\n\n✏️ Введите количество звёзд:\n<i>Минимум: {MIN_STARS} шт.</i>",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        except:
            bot.edit_message_text(
                f"✅ Звёзды будут отправлены <b>Вам</b> (@{username})\n\n✏️ Введите количество звёзд:\n<i>Минимум: {MIN_STARS} шт.</i>",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data == "recipient_friend":
        user_data[user_id] = {"step": "ask_friend_username", "recipient": "friend"}
        try:
            bot.edit_message_caption(
                caption="👤 Введите юзернейм друга:\n\n<i>Например: @username</i>",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        except:
            bot.edit_message_text(
                "👤 Введите юзернейм друга:\n\n<i>Например: @username</i>",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data == "cancel_action":
        user_data.pop(user_id, None)
        try:
            bot.edit_message_caption(
                caption="❌ Действие отменено\n\nВыберите действие:",
                chat_id=chat_id, message_id=message_id, reply_markup=main_menu()
            )
        except:
            bot.edit_message_text(
                "❌ Действие отменено\n\nВыберите действие:",
                chat_id=chat_id, message_id=message_id, reply_markup=main_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data == "paid":
        if user_id not in user_data or "order_id" not in user_data[user_id]:
            bot.answer_callback_query(call.id, "Нет активного заказа!")
            return
        user_data[user_id]["step"] = "waiting_cheque"
        try:
            bot.edit_message_caption(
                caption="📸 <b>Отправьте чек оплаты</b>\n\nПрикрепите скриншот или фото чека к сообщению и отправьте.",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        except:
            bot.edit_message_text(
                "📸 <b>Отправьте чек оплаты</b>\n\nПрикрепите скриншот или фото чека к сообщению и отправьте.",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("review_"):
        order_id = int(call.data.split("_")[1])
        user_data[user_id] = {"step": "ask_rating", "order_id": order_id}
        try:
            bot.edit_message_caption(
                caption="⭐ Оцените заказ от 1 до 5:",
                chat_id=chat_id, message_id=message_id, reply_markup=stars_keyboard()
            )
        except:
            bot.edit_message_text(
                "⭐ Оцените заказ от 1 до 5:",
                chat_id=chat_id, message_id=message_id, reply_markup=stars_keyboard()
            )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("rate_"):
        rating = int(call.data.split("_")[1])
        if user_id not in user_data:
            bot.answer_callback_query(call.id, "Ошибка!")
            return
        user_data[user_id]["rating"] = rating
        user_data[user_id]["step"] = "ask_review_text"
        try:
            bot.edit_message_caption(
                caption=f"⭐ Оценка: {rating}/5\n\n✏️ Напишите текст отзыва:",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        except:
            bot.edit_message_text(
                f"⭐ Оценка: {rating}/5\n\n✏️ Напишите текст отзыва:",
                chat_id=chat_id, message_id=message_id, reply_markup=cancel_menu()
            )
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)

# ========== ОБРАБОТЧИК ФОТО (ЧЕК) ==========
@bot.message_handler(content_types=['photo'])
def handle_cheque(message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    if not data or data.get("step") != "waiting_cheque":
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu())
        return

    order_id = data["order_id"]
    update_order_status(order_id, "paid")
    data["step"] = "done"

    bot.send_message(message.chat.id, "✅ Чек получен! Ожидайте выполнения заказа.", reply_markup=main_menu())

    order = get_order_from_db(order_id)
    if order:
        recipient = "себе" if order.get("recipient") == "me" else f"другу @{order.get('recipient_username', '?')}"

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=(
                f"💰 <b>Заказ #{order_id} оплачен!</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 Клиент: @{message.from_user.username or 'NoName'}\n"
                f"⭐ Звёзд: {order['amount']}\n"
                f"💰 Сумма: {order['total_price']} ₸\n"
                f"📤 Кому: {recipient}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📸 Чек прикреплён выше. Проверь и выполни заказ!"
            ),
            reply_markup=order_keyboard(order_id)
        )


# ========== ВВОД ТЕКСТА ==========
@bot.message_handler(func=lambda m: m.from_user.id in user_data)
def process_text_input(message):
    user_id = message.from_user.id
    text = message.text.strip()
    data = user_data.get(user_id, {})

    if not data:
        return

    step = data.get("step", "")

    if step == "ask_friend_username":
        friend_username = text.replace("@", "")
        data["recipient_username"] = friend_username
        data["step"] = "ask_amount"
        bot.send_message(message.chat.id,
            f"✅ Звёзды будут отправлены другу <b>@{friend_username}</b>\n\n✏️ Введите количество звёзд:\n<i>Минимум: {MIN_STARS} шт.</i>",
            reply_markup=cancel_menu())
        return

    if step == "ask_amount":
        if not text.isdigit():
            bot.send_message(message.chat.id, "❌ Введите число!")
            return

        amount = int(text)
        if amount < MIN_STARS:
            bot.send_message(message.chat.id, f"❌ Минимальный заказ: {MIN_STARS} звёзд!")
            return

        price_per = 7 if amount <= 49 else 6.9
        total = int(amount * price_per)

        data["amount"] = amount
        data["price_per"] = price_per
        data["total"] = total
        data["step"] = "waiting_payment"

        recipient = data.get("recipient", "me")
        recipient_username = data.get("recipient_username", message.from_user.username or "NoName")

        order = create_order(user_id, message.from_user.username or "NoName", amount, price_per, total, recipient, recipient_username)
        data["order_id"] = order["id"]

        recipient_line = "👤 Получатель: <b>Вы</b>" if recipient == "me" else f"👤 Получатель: <b>Друг</b> (@{recipient_username})"

        bot.send_message(message.chat.id,
            f"📋 <b>Заказ #{order['id']}</b>\n━━━━━━━━━━━━━━━━\n"
            f"⭐ Товар: <b>{amount} звёзд Telegram</b>\n💰 Итого к оплате: <b>{total} ₸</b>\n\n"
            f"{recipient_line}\n━━━━━━━━━━━━━━━━\n\n"
            f"💳 <b>Реквизиты для оплаты:</b>\n\n🏦 Kaspi Bank\n"
            f"💳 Номер карты: <code>{BANK_CARD}</code>\n👤 Получатель: {BANK_NAME}\n\n"
            f"⚠️ <i>В сообщении при переводе укажите ваш юзернейм:</i>\n<b>@{message.from_user.username or 'ваш_юзернейм'}</b>\n\n"
            f"✅ После оплаты нажмите кнопку ниже:",
            reply_markup=pay_keyboard())
        return

    if step == "ask_review_text":
        rating = data.get("rating", 5)
        order_id = data.get("order_id", 0)
        add_review(order_id, user_id, message.from_user.username or "NoName", rating, text)
        user_data.pop(user_id, None)
        bot.send_message(message.chat.id, f"🌟 Спасибо за отзыв! {'⭐' * rating}", reply_markup=main_menu())
        return

# ========== ТЕКСТОВЫЕ КОМАНДЫ ==========
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    show_admin_panel(message.chat.id)

@bot.message_handler(commands=['orders'])
def list_orders_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    show_pending_orders(message.chat.id)

@bot.message_handler(commands=['complete'])
def complete_order_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    try:
        parts = message.text.split()
        order_id = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Формат: /complete НОМЕР_ЗАКАЗА")
        return
    complete_order(order_id, message.chat.id)

@bot.message_handler(commands=['cancel'])
def cancel_order_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    try:
        parts = message.text.split()
        order_id = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Формат: /cancel НОМЕР_ЗАКАЗА")
        return
    cancel_order(order_id, message.chat.id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    show_stats(message.chat.id)

@bot.message_handler(commands=['reviews'])
def reviews_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа!")
        return
    show_reviews(message.chat.id)

# ========== НЕИЗВЕСТНЫЙ ТЕКСТ ==========
@bot.message_handler(func=lambda m: True)
def unknown(message):
    if message.from_user.id in user_data:
        process_text_input(message)
        return
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu())

# ============================================
#  ЗАПУСК
# ============================================
# ... весь остальной код ...
print("🌟 Nairy Stars — бот запущен!")

# Анти-сон
import threading
import time
import requests

def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get("https://nairy-stars.onrender.com", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

bot.infinity_polling()
