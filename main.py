import os
import time
import telebot
import logging
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = str(os.getenv('CHAT_ID'))
VAULT_KEY = os.getenv('VAULT_KEY')

if not all([BOT_TOKEN, CHAT_ID, VAULT_KEY]):
    raise ValueError("CRITICAL ERROR: Missing credentials in .env file.")

bot = telebot.TeleBot(BOT_TOKEN)
cipher = Fernet(VAULT_KEY.encode()) 

TARGET_FOLDER = os.path.expanduser('~/Desktop/confidential')
if not os.path.exists(TARGET_FOLDER):
    raise FileNotFoundError("CRITICAL ERROR: Target folder missing.")

logging.basicConfig(
    filename='Vault_Audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VaultHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        filename = os.path.basename(event.src_path)

        if filename.startswith('.') or filename.endswith('.enc'):
            return

        logging.info(f"New file detected: {filename}")
        
        msg = f"📁 **New File Detected:** `{filename}`\n\nTake your time to view or edit it. When you are ready to secure it, reply with:\n`/lock {filename}`"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")



@bot.message_handler(commands=['lock'])
def lock_file(message):
    if str(message.chat.id) != CHAT_ID: return

    try:
        command_parts = message.text.split(' ', 1)
        if len(command_parts) < 2:
            bot.reply_to(message, "⚠️ Please specify a file.\nExample: `/lock passports.jpg`", parse_mode="Markdown")
            return

        target_filename = command_parts[1]
        filepath = os.path.join(TARGET_FOLDER, target_filename)

        if not os.path.exists(filepath):
            bot.reply_to(message, "❌ File not found. Make sure you typed the exact name and extension.")
            return

        if target_filename.endswith('.enc'):
            bot.reply_to(message, "⚠️ This file is already encrypted.")
            return

        bot.reply_to(message, "🔒 Encrypting... please wait.")

        with open(filepath, 'rb') as f:
            raw_data = f.read()

        encrypted_data = cipher.encrypt(raw_data)

        encrypted_filepath = filepath + '.enc'
        with open(encrypted_filepath, 'wb') as f:
            f.write(encrypted_data)

        os.remove(filepath)

        logging.info(f"Manually Locked: {target_filename}")
        bot.send_message(CHAT_ID, f"✅ **SUCCESS!**\n`{target_filename}` is now secured via AES-128.\n\nTo view it later, use:\n`/unlock {target_filename}.enc`", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Manual encryption failed: {e}")
        bot.reply_to(message, "❌ Critical failure during encryption. Check the audit logs.")


@bot.message_handler(commands=['unlock'])
def unlock_file(message):
    if str(message.chat.id) != CHAT_ID: return

    try:
        command_parts = message.text.split(' ', 1)
        if len(command_parts) < 2:
            bot.reply_to(message, "⚠️ Please specify a file.\nExample: `/unlock passports.jpg.enc`", parse_mode="Markdown")
            return

        target_filename = command_parts[1]
        encrypted_filepath = os.path.join(TARGET_FOLDER, target_filename)

        if not os.path.exists(encrypted_filepath):
            bot.reply_to(message, "❌ File not found in the vault.")
            return

        with open(encrypted_filepath, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        original_filepath = encrypted_filepath[:-4]

        with open(original_filepath, 'wb') as f:
            f.write(decrypted_data)

        os.remove(encrypted_filepath)

        logging.info(f"Manually Unlocked: {target_filename}")
        bot.reply_to(message, f"🔓 **Unlocked:** `{os.path.basename(original_filepath)}`\nThe file is now visible on your Mac.", parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ Decryption failed. The file may be corrupt or altered.")
        logging.error(f"Decryption error: {e}")

@bot.message_handler(commands=['list'])
def list_vault(message):
    if str(message.chat.id) != CHAT_ID: return

    files = [f for f in os.listdir(TARGET_FOLDER) if f.endswith('.enc')]
    if not files:
        bot.reply_to(message, "📭 The vault has no encrypted files.")
        return

    msg = "📁 **Encrypted Files in Vault:**\n\n"
    for f in files:
        msg += f"- `{f}`\n"
    bot.reply_to(message, msg + "\nType `/unlock <filename>` to decrypt.", parse_mode="Markdown")

if __name__ == '__main__':
    event_handler = VaultHandler()
    observer = Observer()
    observer.schedule(event_handler, TARGET_FOLDER, recursive=False)
    observer.start()
    
    print(f"[+] Cipher Vault C2 Online. Guarding: {TARGET_FOLDER}")
    bot.send_message(CHAT_ID, "🟢 **Cipher Vault C2 Online.**\nSend `/list` to view secured files.\nDrop a new file in the folder to begin.", parse_mode="Markdown")

    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        observer.stop()
        print("\n[!] Vault shutting down.")
    observer.join()