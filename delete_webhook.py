import asyncio
from aiogram import Bot

API_TOKEN = "8336860008:AAHUQX3MXo-6u07KpfPi_2Gm1AgbKzMkcJo"  # ← bu yerga bot tokeningizni yozing

async def main():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook()
    print("✅ Webhook o‘chirildi")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
