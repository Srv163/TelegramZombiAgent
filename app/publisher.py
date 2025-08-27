import asyncio, logging
from aiogram import Bot
from .config import settings

log = logging.getLogger(__name__)
bot = Bot(token=settings.BOT_TOKEN)

async def publish_text(chat_id: str, text: str):
    try:
        msg = await bot.send_message(chat_id, text, disable_web_page_preview=True)
        return msg.message_id
    except Exception as e:
        log.error(f"publish failed: {e}")
        return None