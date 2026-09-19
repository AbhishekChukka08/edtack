import os
import random
import logging
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from src.state_manager import (
    get_next_topic,
    get_upcoming_topics,
    get_topic_by_id,
    create_custom_topic,
    mark_topic_completed
)
from src.ai_scriptwriter import generate_carousel_content
from src.renderer import generate_carousel_images_async
from src.telegram_bot import send_carousel_to_telegram_async, format_caption_text, build_topic_selection_keyboard

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def run_pipeline_for_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic_info: dict):
    """Executes the full generation and delivery pipeline for a selected topic."""
    chat_id = update.effective_chat.id
    topic_title = topic_info['topic']
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    status_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"🚀 *Starting Generation for:* `{topic_title}`\n\n_1/3: Writing engineering notebook script with Gemini 3.1 Flash Lite..._",
        parse_mode="Markdown"
    )

    try:
        # Step 1: Script & Mermaid diagrams (non-blocking thread)
        carousel_data = await asyncio.to_thread(generate_carousel_content, topic_info)
        
        await status_msg.edit_text(
            f"🚀 *Generating:* `{topic_title}`\n\n_2/3: Rendering 5x 1080x1350 Mermaid infographics with Playwright..._",
            parse_mode="Markdown"
        )
        
        # Step 2: Render slides to PNG (async)
        output_dir = os.path.join(os.getcwd(), "output")
        png_paths = await generate_carousel_images_async(carousel_data, output_dir, theme="theme-notebook")
        
        await status_msg.edit_text(
            f"🚀 *Generating:* `{topic_title}`\n\n_3/3: Uploading slides, caption & next suggestions to chat..._",
            parse_mode="Markdown"
        )
        
        # Step 3: Deliver to Telegram (async)
        caption_text = format_caption_text(carousel_data['caption'], topic_title)
        await send_carousel_to_telegram_async(png_paths, caption_text, token, str(chat_id))
        
        # Mark completed
        mark_topic_completed(topic_info['id'])
        
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error generating carousel: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ *Error generating carousel:*\n`{str(e)}`", parse_mode="Markdown")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button taps from inline keyboards."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("sel_"):
        topic_key = data[4:]
        
        if topic_key == "random":
            topics = get_upcoming_topics(count=10)
            topic_info = random.choice(topics) if topics else get_next_topic()
        else:
            topic_info = get_topic_by_id(topic_key)
            if not topic_info:
                topic_info = create_custom_topic(topic_key)

        await query.edit_message_reply_markup(reply_markup=None)
        await run_pipeline_for_topic(update, context, topic_info)

    elif data.startswith("page_"):
        try:
            offset = int(data[5:])
        except ValueError:
            offset = 0
            
        suggestions = get_upcoming_topics(count=4, offset=offset)
        new_keyboard = build_topic_selection_keyboard(suggestions, offset=offset)
        
        await query.edit_message_text(
            text="🎯 **Choose Next Topic to Generate:**\n\nTap any suggestion below, or **reply with any custom topic**:",
            parse_mode="Markdown",
            reply_markup=new_keyboard
        )

    elif data == "approve":
        await query.edit_message_text(
            text="🎉 **Post Approved!** Copy the caption above and post the 5 slides directly to Instagram/LinkedIn."
        )


async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles direct text messages from user as custom topics."""
    text = update.message.text.strip()
    if not text:
        return
        
    topic_info = create_custom_topic(text)
    await run_pipeline_for_topic(update, context, topic_info)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start handler."""
    suggestions = get_upcoming_topics(count=4)
    await update.message.reply_text(
        "👋 **Welcome to your Digital Engineering Notebook Assistant!**\n\n"
        "Every day, I turn complex system design concepts into 5-slide visual cheat sheets with Mermaid diagrams.\n\n"
        "🎯 **Pick a topic to generate right now, or type any topic directly:**",
        parse_mode="Markdown",
        reply_markup=build_topic_selection_keyboard(suggestions, offset=0)
    )


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /generate or /next handler."""
    topic_info = get_next_topic()
    await run_pipeline_for_topic(update, context, topic_info)


def start_bot():
    """Starts the interactive polling bot listener."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment.")

    print("[*] Starting Interactive Telegram Bot Listener for 'edtack'...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("next", cmd_next))
    app.add_handler(CommandHandler("generate", cmd_next))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    print("[+] Bot listener is polling for button clicks and messages! (Ctrl+C to stop)")
    app.run_polling()

if __name__ == "__main__":
    start_bot()
