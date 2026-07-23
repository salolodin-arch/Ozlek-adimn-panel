"""
Rasmni catbox.moe xizmatiga yuklab, ochiq (public) linkini qaytaradi.
Bu xizmat uchun HECH QANDAY ro'yxatdan o'tish yoki API kalit kerak emas.
"""

import logging
import aiohttp


async def upload_image_to_imgbb(image_bytes: bytes) -> str | None:
    """Rasm baytlarini catbox.moe'ga yuboradi, muvaffaqiyatli bo'lsa ochiq URL qaytaradi, bo'lmasa None.
    (Funksiya nomi eski koddagi chaqiruvlar bilan mos bo'lishi uchun shunday qoldirildi.)"""
    try:
        form = aiohttp.FormData()
        form.add_field("reqtype", "fileupload")
        form.add_field("fileToUpload", image_bytes, filename="photo.jpg", content_type="image/jpeg")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://catbox.moe/user/api.php",
                data=form,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                text = (await resp.text()).strip()
                if resp.status == 200 and text.startswith("https://"):
                    return text
                logging.warning(f"catbox.moe xato qaytardi: {text}")
                return None
    except Exception as e:
        logging.warning(f"catbox.moe'ga yuklashda xatolik: {e}")
        return None
