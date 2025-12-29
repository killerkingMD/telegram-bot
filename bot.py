
import re
import requests
import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN não definido no ambiente")

if not BACKEND_URL:
    raise Exception("BACKEND_URL não definido no ambiente")

bot = telebot.TeleBot(
    BOT_TOKEN,
    threaded=True,
    skip_pending=True
)

def is_valid_url(url: str) -> bool:
    return (
        url.startswith("http")
        and ("kwai" in url.lower() or "tiktok" in url.lower())
    )

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        "📥 *Downloader Kwai / TikTok*\n\n"
        "Envie o link do vídeo.\n"
        "Sem marca d’água.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    url = msg.text.strip()

    if not is_valid_url(url):
        bot.reply_to(msg, "❌ Envie um link válido do Kwai ou TikTok.")
        return

    status = bot.reply_to(msg, "⏳ Processando vídeo...")

    try:
        response = requests.post(
            BACKEND_URL,
            json={"url": url},
            stream=True,
            timeout=120
        )

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ Falha ao baixar o vídeo.",
                msg.chat.id,
                status.message_id
            )
            return

        title = response.headers.get("X-Video-Title", "video")
        safe_name = re.sub(r'[\\/:*?"<>|]', "", title).strip()[:80]

        bot.send_video(
            msg.chat.id,
            response.raw,
            filename=f"{safe_name}.mp4",
            supports_streaming=True,
            timeout=180
        )

        bot.delete_message(msg.chat.id, status.message_id)

    except Exception:
        bot.edit_message_text(
            "❌ Erro ao processar o vídeo.",
            msg.chat.id,
            status.message_id
        )

print("🤖 Bot Telegram iniciado")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
