"""
Admin bot — faqat ADMIN_CHAT_ID ga tegishli odam ishlata oladi.
Imkoniyatlari:
  /start        - menyu
  Dori qo'shish  - nomi -> tavsifi -> rasm (bosqichma-bosqich so'raydi)
  Dorilar ro'yxati - barcha dorilarni ko'rsatadi, har birida "Tahrirlash" / "O'chirish" tugmasi
  Kompaniya haqida - "Oz-Lek haqida" matnini yangilash
"""

import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

import database as db
from config import ADMIN_BOT_TOKEN, ADMIN_CHAT_ID

logging.basicConfig(level=logging.INFO)

router = Router()


def admin_only(message_or_call) -> bool:
    return message_or_call.from_user.id == ADMIN_CHAT_ID


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Dori qo'shish")],
        [KeyboardButton(text="📋 Dorilar ro'yxati")],
        [KeyboardButton(text="🏢 Kompaniya ma'lumotini yangilash")],
    ],
    resize_keyboard=True,
)


class AddMedicine(StatesGroup):
    name = State()
    description = State()
    photo = State()


class EditMedicine(StatesGroup):
    field = State()
    value = State()


class EditCompany(StatesGroup):
    text = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    if not admin_only(message):
        await message.answer("Bu bot faqat admin uchun.")
        return
    await message.answer(
        "Assalomu alaykum! Oz-Lek admin panelga xush kelibsiz.\n"
        "Quyidagi menyudan birini tanlang:",
        reply_markup=MAIN_MENU,
    )


# ---------- Dori qo'shish ----------

@router.message(F.text == "➕ Dori qo'shish")
async def add_medicine_start(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AddMedicine.name)
    await message.answer("Dorining nomini yozing:", reply_markup=ReplyKeyboardRemove())


@router.message(AddMedicine.name)
async def add_medicine_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddMedicine.description)
    await message.answer("Endi dori haqida tavsif (ta'siri, dozasi va h.k.) yozing:")


@router.message(AddMedicine.description)
async def add_medicine_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddMedicine.photo)
    await message.answer("Endi shu dorining rasmini yuboring (rasm sifatida, fayl emas):")


@router.message(AddMedicine.photo, F.photo)
async def add_medicine_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id
    medicine_id = db.add_medicine(
        name=data["name"],
        description=data["description"],
        photo_file_id=photo_file_id,
    )
    await state.clear()
    await message.answer(
        f"✅ Dori qo'shildi! (ID: {medicine_id})\n\n"
        f"Nomi: {data['name']}",
        reply_markup=MAIN_MENU,
    )


@router.message(AddMedicine.photo)
async def add_medicine_photo_invalid(message: Message):
    await message.answer("Iltimos, rasm yuboring (matn emas).")


# ---------- Dorilar ro'yxati / tahrirlash / o'chirish ----------

@router.message(F.text == "📋 Dorilar ro'yxati")
async def list_medicines_handler(message: Message):
    if not admin_only(message):
        return
    medicines = db.list_medicines()
    if not medicines:
        await message.answer("Hozircha dorilar yo'q.")
        return
    for m in medicines:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_{m['id']}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{m['id']}"),
        ]])
        caption = f"<b>{m['name']}</b>\n{m['description']}"
        if m["photo_file_id"]:
            await message.answer_photo(m["photo_file_id"], caption=caption, reply_markup=keyboard, parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("delete_"))
async def delete_medicine_handler(call: CallbackQuery):
    if call.from_user.id != ADMIN_CHAT_ID:
        return
    medicine_id = int(call.data.split("_")[1])
    db.delete_medicine(medicine_id)
    await call.answer("O'chirildi ✅")
    await call.message.answer(f"Dori (ID: {medicine_id}) o'chirildi.")


@router.callback_query(F.data.startswith("edit_"))
async def edit_medicine_handler(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_CHAT_ID:
        return
    medicine_id = int(call.data.split("_")[1])
    await state.update_data(medicine_id=medicine_id)
    await state.set_state(EditMedicine.field)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Nomini", callback_data="field_name")],
        [InlineKeyboardButton(text="Tavsifini", callback_data="field_description")],
        [InlineKeyboardButton(text="Rasmini", callback_data="field_photo")],
    ])
    await call.answer()
    await call.message.answer("Nimasini o'zgartirmoqchisiz?", reply_markup=keyboard)


@router.callback_query(EditMedicine.field, F.data.startswith("field_"))
async def edit_medicine_field(call: CallbackQuery, state: FSMContext):
    field = call.data.split("_")[1]
    await state.update_data(field=field)
    await state.set_state(EditMedicine.value)
    await call.answer()
    prompt = {
        "name": "Yangi nomini yozing:",
        "description": "Yangi tavsifni yozing:",
        "photo": "Yangi rasmni yuboring:",
    }[field]
    await call.message.answer(prompt)


@router.message(EditMedicine.value)
async def edit_medicine_value(message: Message, state: FSMContext):
    data = await state.get_data()
    medicine_id = data["medicine_id"]
    field = data["field"]

    if field == "photo":
        if not message.photo:
            await message.answer("Iltimos, rasm yuboring.")
            return
        db.update_medicine(medicine_id, photo_file_id=message.photo[-1].file_id)
    elif field == "name":
        db.update_medicine(medicine_id, name=message.text)
    elif field == "description":
        db.update_medicine(medicine_id, description=message.text)

    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=MAIN_MENU)


# ---------- Kompaniya ma'lumotini yangilash ----------

@router.message(F.text == "🏢 Kompaniya ma'lumotini yangilash")
async def edit_company_start(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    current = db.get_company_info()
    await state.set_state(EditCompany.text)
    await message.answer(
        f"Hozirgi matn:\n\n{current}\n\n---\nYangi matnni to'liq yozib yuboring:",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(EditCompany.text)
async def edit_company_save(message: Message, state: FSMContext):
    db.set_company_info(message.text)
    await state.clear()
    await message.answer("✅ Kompaniya ma'lumoti yangilandi!", reply_markup=MAIN_MENU)


async def run_admin_bot():
    db.init_db()
    bot = Bot(token=ADMIN_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)
