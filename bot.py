import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_data = {}

def download_media(url, audio_only=False):
    opts = {
        'format': 'bestaudio/best' if audio_only else 'best',
        'outtmpl': 'media/%(title).70s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4' if not audio_only else 'mp3',
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 🔘 /start buyrug‘i
@router.message(F.text == "/start")
async def start_handler(msg: Message):
    await msg.answer(
        text=(
            "<b>👋 Salom!</b>\n\n"
            "Men <b>GoodBot</b>, sizga YouTube, TikTok, Instagram va boshqa saytlardan video yoki qo‘shiq yuklab beraman.\n\n"
            "🔗 Linkni yuboring – men darhol yuklayman!"
        )
    )

# 🔘 Link yuborilganda
@router.message(F.text.regexp(r'https?://'))
async def link_handler(message: Message):
    url = message.text.strip()

    if not any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com"]):
        await message.answer("❌ Hozircha faqat YouTube, TikTok va Instagram linklarini qabul qilaman.")
        return

    loading_msg = await message.answer("⏳ Yuklab olinmoqda...")

    user_data[message.from_user.id] = url

    try:
        video_path = download_media(url, audio_only=False)
        video_file = FSInputFile(video_path)

        audio_button = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🎵 Qo‘shiqni yuklab olish", callback_data=f"download_audio|{message.from_user.id}")
        ]])

        await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)

        await message.answer_video(
            video=video_file,
            caption="📥 Goodbot orqali yuklab olindi",
            reply_markup=audio_button
        )

        os.remove(video_path)

    except Exception as e:
        await bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        await message.answer(f"❌ Xatolik yuz berdi: {e}")

# 🔘 Audio yuklab beruvchi tugma
@router.callback_query(F.data.startswith("download_audio"))
async def audio_download(call: types.CallbackQuery):
    user_id = int(call.data.split("|")[1])
    url = user_data.get(user_id)
    if not url:
        await call.message.answer("❗ Link topilmadi.")
        return

    downloading_msg = await call.message.answer("🎧 Audio yuklab olinmoqda...")

    try:
        audio_path = download_media(url, audio_only=True)
        audio_file = FSInputFile(audio_path)

        await call.message.answer_audio(
            audio=audio_file,
            caption="📥 Goodbot orqali yuklab olindi"
        )

        await bot.delete_message(chat_id=call.message.chat.id, message_id=downloading_msg.message_id)

        os.remove(audio_path)

    except Exception as e:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=downloading_msg.message_id)
        await call.message.answer(f"❌ Audio yuklab olishda xatolik: {e}")

# 🔘 Botni ishga tushirish
async def main():
    os.makedirs("media", exist_ok=True)
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
