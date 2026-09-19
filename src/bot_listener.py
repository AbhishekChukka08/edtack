import os
import asyncio
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
    mark_topic_completed,
    get_curriculum_status
)
from src.ai_scriptwriter import generate_carousel_content
from src.renderer import generate_carousel_images_async
from src.telegram_bot import send_carousel_to_telegram_async, format_caption_text, build_topic_selection_keyboard

def build_curriculum_view(page: int = 1) -> tuple[str, InlineKeyboardMarkup]:
    """Builds a paginated visual curriculum display with selection buttons."""
    items, total_items, total_pages, current_page = get_curriculum_status(page=page, page_size=5)
    
    text_lines = [
        f"📚 *Generative AI & LLM Systems Curriculum*",
        f"_Track Overview: Page {current_page} of {total_pages} ({total_items} Topics total)_\n"
    ]
    
    keyboard = []
    for item in items:
        status_icon = "✅" if item["completed"] else "⏳"
        status_text = "Done" if item["completed"] else "Pending"
        text_lines.append(f"{status_icon} *Day {item['index']}:* {item['topic']}\n   _Category: {item['category']} • {status_text}_")
        
        btn_label = f"{status_icon} Day {item['index']}: {item['topic'][:24]}..." if len(item['topic']) > 26 else f"{status_icon} Day {item['index']}: {item['topic']}"
        keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"sel_{item['id']}")])
        
    text_lines.append("\n👉 *Tap any topic button to generate its 5-slide visual carousel now:*")
    
    # Navigation row
    nav_row = []
    if current_page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"cur_page_{current_page - 1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="noop"))
    if current_page < total_pages:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"cur_page_{current_page + 1}"))
    keyboard.append(nav_row)
    
    # Action row
    keyboard.append([
        InlineKeyboardButton("🚀 Generate Next in Track", callback_data="sel_next"),
        InlineKeyboardButton("🎲 Pick Random", callback_data="sel_random")
    ])
    
    return "\n".join(text_lines), InlineKeyboardMarkup(keyboard)


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
        output_dir = os.path.join(os.getcwd(), "output")
        png_paths = []
        caption_text = ""

        # Primary: 5-Slide Infographic Image Generation (gemini-3.1-flash-lite-image)
        try:
            from src.infographic_generator import generate_infographic_carousel
            await status_msg.edit_text(
                f"🚀 *Generating:* `{topic_title}`\n\n_1/2: Generating 5 visual infographic cheat sheets with gemini-3.1-flash-lite-image..._",
                parse_mode="Markdown"
            )
            png_paths, caption_text = await asyncio.to_thread(generate_infographic_carousel, topic_info, output_dir)
        except Exception as img_err:
            logger.warning(f"Image model fallback triggered: {img_err}")
            await status_msg.edit_text(
                f"🚀 *Generating:* `{topic_title}`\n\n_1/2: Writing engineering script & rendering 5x Mermaid infographics..._",
                parse_mode="Markdown"
            )
            carousel_data = await asyncio.to_thread(generate_carousel_content, topic_info)
            png_paths = await generate_carousel_images_async(carousel_data, output_dir, theme="theme-notebook")
            caption_text = format_caption_text(carousel_data['caption'], topic_title)

        await status_msg.edit_text(
            f"🚀 *Generating:* `{topic_title}`\n\n_2/2: Uploading 5 slides, ready-to-post caption & next topic buttons to chat..._",
            parse_mode="Markdown"
        )
        
        # Deliver to Telegram
        await send_carousel_to_telegram_async(png_paths, caption_text, token, str(chat_id))
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

    if data == "noop":
        await query.answer()
        return

    elif data.startswith("cur_page_"):
        try:
            page_num = int(data[9:])
        except ValueError:
            page_num = 1
        text, markup = build_curriculum_view(page=page_num)
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("sel_"):
        topic_key = data[4:]
        
        if topic_key == "random":
            topics = get_upcoming_topics(count=10)
            topic_info = random.choice(topics) if topics else get_next_topic()
        elif topic_key == "next":
            topic_info = get_next_topic()
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
        "👋 **Welcome to your Digital Engineering Notebook Assistant (@edtack_edu)!**\n\n"
        "Commands:\n"
        "• `/generate` - Generate next topic in the curriculum track\n"
        "• `/curriculum` - View full 30-day curriculum & select any topic to generate\n"
        "• Or **reply directly with any custom topic** (e.g. _GraphRAG_ or _vLLM_)\n\n"
        "🎯 **Upcoming suggestions:**",
        parse_mode="Markdown",
        reply_markup=build_topic_selection_keyboard(suggestions, offset=0)
    )


async def cmd_curriculum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /curriculum or /topics handler to list and pick from full curriculum."""
    text, markup = build_curriculum_view(page=1)
    await update.message.reply_text(text=text, parse_mode="Markdown", reply_markup=markup)


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /generate or /next handler."""
    topic_info = get_next_topic()
    await run_pipeline_for_topic(update, context, topic_info)


def start_bot():
    """Starts the interactive polling bot listener."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment.")

    print("[*] Starting Interactive Telegram Bot Listener for 'edtack' (@edtack_edu)...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("next", cmd_next))
    app.add_handler(CommandHandler("generate", cmd_next))
    app.add_handler(CommandHandler("curriculum", cmd_curriculum))
    app.add_handler(CommandHandler("topics", cmd_curriculum))
    app.add_handler(CommandHandler("list", cmd_curriculum))
    app.add_handler(CommandHandler("track", cmd_curriculum))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    print("[+] Bot listener is polling for button clicks and messages! (Ctrl+C to stop)")
    app.run_polling()

if __name__ == "__main__":
    start_bot()
