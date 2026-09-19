import os
import asyncio
from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.request import HTTPXRequest

def format_caption_text(caption_data: dict, topic_title: str) -> str:
    """Formats the caption for mobile copy-pasting."""
    takeaways = "\n".join([f"• {item}" for item in caption_data.get("key_takeaways", [])])
    hashtags = " ".join([f"#{tag.strip('#')}" for tag in caption_data.get("hashtags", [])])

    text = (
        f"🚀 {caption_data.get('hook', topic_title)}\n\n"
        f"💡 {caption_data.get('body', '')}\n\n"
        f"📌 Key Engineering Takeaways:\n{takeaways}\n\n"
        f"👇 Discussion:\n{caption_data.get('call_to_action', '')}\n\n"
        f"--- \n{hashtags}"
    )
    return text

def build_topic_selection_keyboard(suggested_topics: list[dict], offset: int = 0) -> InlineKeyboardMarkup:
    """Builds interactive topic selection buttons."""
    keyboard = []
    for t in suggested_topics:
        title = t.get("topic", "Topic")
        btn_text = f"👉 {title[:32]}..." if len(title) > 35 else f"👉 {title}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"sel_{t['id']}")])
        
    keyboard.append([
        InlineKeyboardButton("🔄 Next Suggestions", callback_data=f"page_{offset + 4}"),
        InlineKeyboardButton("🎲 Pick Random", callback_data="sel_random")
    ])
    return InlineKeyboardMarkup(keyboard)

async def send_carousel_to_telegram_async(png_paths: list[str], caption_text: str, bot_token: str, chat_id: str):
    """Sends 5 slides as photo album + full caption + interactive topic picker."""
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    bot = Bot(token=bot_token, request=request)
    
    media_group = []
    for idx, png_path in enumerate(png_paths):
        with open(png_path, 'rb') as f:
            photo_bytes = f.read()
            media_group.append(InputMediaPhoto(media=photo_bytes))

    # 1. Send slide photo album
    print("[*] Uploading 5 photo slides to Telegram...")
    await bot.send_media_group(chat_id=chat_id, media=media_group, write_timeout=90.0, read_timeout=90.0)
    
    # 2. Send ready-to-copy caption text message
    print("[*] Sending caption text message...")
    await bot.send_message(
        chat_id=chat_id,
        text=f"📋 **Ready-to-Post Instagram Caption:**\n\n{caption_text}"
    )

    # 3. Send interactive topic selection panel
    from src.state_manager import get_upcoming_topics
    suggestions = get_upcoming_topics(count=4)
    
    print("[*] Sending topic selection buttons...")
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "🎯 **Choose Next Topic to Generate:**\n\n"
            "Tap any suggestion below, or **reply to this message with any custom topic** (e.g. _Distributed Locks_ or _WebSockets_):"
        ),
        parse_mode="Markdown",
        reply_markup=build_topic_selection_keyboard(suggestions, offset=0)
    )


def send_to_telegram(png_paths: list[str], caption_data_or_text, topic_title: str = "", bot_token: str = None, chat_id: str = None):
    """Synchronous wrapper to send slides and control panel to Telegram."""
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    cid = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not cid:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured.")

    if isinstance(caption_data_or_text, dict):
        caption_text = format_caption_text(caption_data_or_text, topic_title)
    else:
        caption_text = str(caption_data_or_text)
        
    asyncio.run(send_carousel_to_telegram_async(png_paths, caption_text, token, cid))

