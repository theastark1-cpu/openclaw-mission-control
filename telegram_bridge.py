# telegram_bridge.py
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import base64
from datetime import datetime

# CONFIGURATION
TELEGRAM_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
GITHUB_TOKEN = "github_pat_YOUR_TOKEN_HERE"  # Your existing token
REPO = "theastark1-cpu/openclaw-mission-control"
TARGET_FILE = "openclaw_mission_control_enhanced.py"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 *OpenClaw Mission Control*\n\n"
        "*Commands:*\n"
        "📤 /update \\- Push new code to GitHub\n"
        "📊 /status \\- Check repo status\n"
        "🎨 /style \\- Get UI template\n\n"
        "To deploy: Send /update, then paste your code in the next message",
        parse_mode='MarkdownV2'
    )

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Ready for code. Paste your Python code now (as text):")
    context.user_data['awaiting_code'] = True

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{REPO}/commits/main"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        last_commit = resp.json()
        msg = f"✅ *Last Commit:*\n{last_commit['commit']['message']}\nBy: {last_commit['commit']['author']['name']}"
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Could not fetch status")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_code'):
        return
        
    code = update.message.text
    await update.message.reply_text("🚀 Pushing to GitHub...")
    
    # Push to GitHub
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current SHA
    url = f"https://api.github.com/repos/{REPO}/contents/{TARGET_FILE}"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        await update.message.reply_text(f"❌ Error fetching file: {resp.json()}")
        return
    
    sha = resp.json()['sha']
    
    # Commit new code
    data = {
        "message": f"Telegram Update @ {datetime.now().strftime('%H:%M')}",
        "content": base64.b64encode(code.encode()).decode(),
        "sha": sha
    }
    
    put_resp = requests.put(url, headers=headers, json=data)
    
    if put_resp.status_code == 200:
        await update.message.reply_text(
            "✅ *Success!*\\n\n"
            "GitHub updated\\.\n"
            "Streamlit will redeploy in 60\\-90 seconds\\.\n"
            f"View: https://share\\.streamlit\\.io/{REPO}",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text(f"❌ Error: {put_resp.json().get('message', 'Unknown')}")
    
    context.user_data['awaiting_code'] = False

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    
    print("🤖 Bot is running... Send /start in Telegram")
    app.run_polling()

if __name__ == "__main__":
    main()
