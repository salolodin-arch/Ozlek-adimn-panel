"""
Mijozlar uchun bot.

/start bosilganda — hech qanday salomlashish matni chiqmaydi, to'g'ridan-to'g'ri
admin panelga qo'shilgan DORILAR MENYUSI chiqadi (har biri tugma sifatida).

Dori tanlansa (tugma bosilsa) YOKI nomi yozilsa YOKI ovozli xabar bilan aytilsa —
o'sha dorining admin kiritgan rasmi + nomi + ma'lumoti chiqadi.

Kirill yozuv va kichik xatolar (bir-ikki harf farqi) qidiruvda hisobga olinadi.
Agar hech narsa topilmasa — faqat: "Kechirasiz, bunday dori mavjud emas."

"Oz-Lek haqida" — menyudagi alohida tugma orqali yoki matn/ovoz bilan so'ralsa chiqadi.
"""

import logging
import os
import tempfile

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

import database as db
import text_utils
from config import PUBLIC_BOT_TOKEN

logging.basicConfig(level=logging.INFO)

router = Router()

MENU_HEADER = (
    "✨━━━━━━━━━━━━━━━✨\n"
    "💊 OZ-LEK DORILAR RO'YXATI\n"
    "✨━━━━━━━━━━━━━━━✨\n\n"
    "Kerakli dorini tanlang:"
)

NOT_FOUND_TEXT = "Kechirasiz, bunday dori mavjud emas."


def medicines_menu_keyboard():
    medicines = db.list_medicines()
    buttons = [
        [InlineKeyboardButton(text=f"🔹 {m['name']}", callback_data=f"med_{m['id']}")]
        for m in medicines
    ]
    buttons.append([InlineKeyboardButton(text="ℹ️ Oz-Lek haqida", callback_data="company_info")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_medicine(m: dict) -> str:
    return f"<b>{m['name']}</b>\n\n{m['description']}"


async def send_medicine(message: Message, m: dict):
    caption = format_medicine(m)
    if m["photo_file_id"]:
        await message.answer_photo(m["photo_file_id"], caption=caption, parse_mode="HTML")
    else:
        await message.answer(caption, parse_mode="HTML")


@router.message(Command("start"))
async def cmd_start(message: Message):
    medicines = db.list_medicines()
    if not medicines:
        await message.answer("Hozircha dorilar ro'yxati bo'sh. Birozdan so'ng qayta urinib ko'ring.")
        return
    await message.answer(MENU_HEADER, reply_markup=medicines_menu_keyboard())


# ---------- Kompaniya haqida ----------

@router.callback_query(F.data == "company_info")
async def company_info_callback(call: CallbackQuery):
    await call.answer()
    await call.message.answer(db.get_company_info())


@router.message(F.voice)
async def voice_query(message: Message, bot: Bot):
    """Ovozli xabarni matnga o'giradi va so'rovga mos javob beradi."""
    try:
        import speech_recognition as sr
        from pydub import AudioSegment

        file = await bot.get_file(message.voice.file_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            ogg_path = os.path.join(tmpdir, "voice.ogg")
            wav_path = os.path.join(tmpdir, "voice.wav")
            await bot.download_file(file.file_path, ogg_path)
            AudioSegment.from_file(ogg_path).export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="uz-UZ")
    except Exception as e:
        logging.warning(f"Ovozni tanib bo'lmadi: {e}")
        await message.answer(NOT_FOUND_TEXT)
        return

    await route_text_query(message, text)


# ---------- Dori tanlash (tugma orqali) ----------

@router.callback_query(F.data.startswith("med_"))
async def show_medicine(call: CallbackQuery):
    medicine_id = int(call.data.split("_")[1])
    medicine = db.get_medicine(medicine_id)
    await call.answer()
    if not medicine:
        await call.message.answer(NOT_FOUND_TEXT)
        return
    await send_medicine(call.message, medicine)


# ---------- Dori nomi yozilsa yoki gapirilsa ----------

async def route_text_query(message: Message, text: str):
    if text_utils.is_company_query(text):
        await message.answer(db.get_company_info())
        return

    medicines = db.list_medicines()
    matches = text_utils.find_best_medicine_matches(text, medicines)

    if not matches:
        await message.answer(NOT_FOUND_TEXT)
        return

    if len(matches) == 1:
        await send_medicine(message, matches[0])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🔹 {m['name']}", callback_data=f"med_{m['id']}")] for m in matches[:8]
        ])
        await message.answer("Bir nechta yaqin natija topildi, birini tanlang:", reply_markup=keyboard)


@router.message(F.text)
async def free_text(message: Message):
    await route_text_query(message, message.text)


async def run_public_bot_no_sync():
    """Admin bot bilan bitta jarayonda, bitta faylni bevosita baham ko'rganda ishlatiladi."""
    bot = Bot(token=PUBLIC_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
