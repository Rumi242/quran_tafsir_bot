import os
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

with open("tafsir_data.json", "r", encoding="utf-8") as f:
    tafsir_data = json.load(f)

BOT_TOKEN = os.getenv("BOT_TOKEN")
user_query_cache = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🕌 Welcome to *Qur’an Insight AI*!\n"
        "Use `/tafsir Surah Al-Fatiha Ayah 1` to get tafsir.\n"
        "You'll get to choose a scholar.",
        parse_mode='Markdown'
    )

def tafsir(update: Update, context: CallbackContext):
    if len(context.args) < 4:
        update.message.reply_text("⚠️ Usage: /tafsir Surah <Surah_Name> Ayah <Number>")
        return

    surah_name = context.args[1]
    ayah_number = context.args[3]
    user_query_cache[update.effective_chat.id] = (surah_name, ayah_number)

    buttons = [
        [InlineKeyboardButton("📘 Ibn Kathir", callback_data="Ibn Kathir")],
        [InlineKeyboardButton("🎙 Nouman Ali Khan", callback_data="Nouman Ali Khan")]
    ]
    update.message.reply_text(
        f"🔍 Choose a scholar for *{surah_name}* Ayah *{ayah_number}*:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )

def scholar_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    scholar = query.data
    chat_id = query.message.chat.id
    surah, ayah = user_query_cache.get(chat_id, (None, None))

    if not surah or not ayah:
        query.answer()
        query.edit_message_text("❌ No query found. Please use /tafsir first.")
        return

    text = tafsir_data.get(surah, {}).get(ayah, {}).get(scholar, "⚠️ Tafsir not found.")
    query.answer()
    query.edit_message_text(f"*{scholar}* on *{surah}*, Ayah *{ayah}*:\n\n{text}", parse_mode='Markdown')

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set.")
        return

    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tafsir", tafsir))
    dp.add_handler(CallbackQueryHandler(scholar_selected))

    print("✅ Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
