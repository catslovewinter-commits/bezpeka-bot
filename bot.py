import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot

# ================= НАЛАШТУВАННЯ =================
BOT_TOKEN = "8490519760:AAGKp18gknFhzhaU5MrhLg3sJ9AwGoUu-5A"
CHANNEL_ID = "@BezpekaUkraine"

TARGET_URL = "https://t.me/s/kpszsu"
CHECK_INTERVAL = 15
# =============================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)

last_message_id = None

async def check_telegram_web():
    global last_message_id
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TARGET_URL, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message')
        
        if not messages:
            return

        latest_msg = messages[-1]
        msg_link_element = latest_msg.find('a', class_='tgme_widget_message_date')
        if not msg_link_element:
            return
        
        msg_url = msg_link_element.get('href', '')
        msg_text_element = latest_msg.find('div', class_='tgme_widget_message_text')
        msg_text = msg_text_element.get_text(separator='\n', strip=True) if msg_text_element else ""

        if not msg_url or not msg_text:
            return

        if last_message_id is None:
            last_message_id = msg_url
            print("✅ Моніторинг запущено успішно...")
            return

        if msg_url != last_message_id:
            last_message_id = msg_url
            
            # Визначаємо іконку залежно від тексту
            text_lower = msg_text.lower()
            if "ракет" in text_lower or "балістик" in text_lower or "кх" in text_lower:
                icon = "🚀"
            elif "бпла" in text_lower or "дронов" in text_lower or "безпілотник" in text_lower or "шахед" in text_lower or "ударн" in text_lower:
                icon = "✈️"
            else:
                icon = "⚠️"

            # Чистий формат без зайвих слів
            formatted_text = f"{icon} {msg_text}"

            try:
                await bot.send_message(chat_id=CHANNEL_ID, text=formatted_text, parse_mode="HTML")
                print(f"✅ Надіслано нове сповіщення з іконкою {icon}!")
            except Exception as e:
                print(f"❌ Помилка надсилання: {e}")

    except Exception as e:
        print(f"⚠️ Помилка з'єднання: {e}")

async def main():
    print("🚀 Запуск моніторингу загрози...")
    while True:
        await check_telegram_web()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())