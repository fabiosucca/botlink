from pyrogram import Client, filters
import re
import base64
import json
import sqlite3
# avvio spegnimento bot
import signal
import sys

# Gestione spegnimento
def signal_handler(sig, frame):
    print("\n⛔️ Bot Link Spento!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Load config
with open("config.json") as f:
    config = json.load(f)

# Initialize bot
app = Client(
    "LinkConverterBot",
    api_id=config["api_id"],
    api_hash=config["api_hash"],
    bot_token=config["bot_token"]
)

# Messaggio di avvio
print("✅ Bot Link Avviato!")

# fine parte avvio spegnimento 

# Load config
with open("config.json") as f:
    config = json.load(f)

# Initialize bot
app = Client(
    "LinkConverterBot",
    api_id=config["api_id"],
    api_hash=config["api_hash"],
    bot_token=config["bot_token"]
)

def is_admin(user_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT id FROM admins WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    db.close()
    return bool(result) or user_id == config["owner_id"]

@app.on_message(filters.command("start"))
async def start_command(client, message):
    try:
        if len(message.command) > 1 and message.command[1].startswith("gen_"):
            encoded_link = message.command[1].replace("gen_", "")
            original_link = base64.b64decode(encoded_link.encode()).decode()
            
            match = re.match(r'https://t\.me/(?:c/)?([^/]+)/(\d+)', original_link)
            if match:
                chat_id = match.group(1)
                message_id = int(match.group(2))
                
                if chat_id.isdigit():
                    chat_id = int('-100' + chat_id)
                else:
                    chat = await client.get_chat(chat_id)
                    chat_id = chat.id
                
                forwarded_msg = await client.get_messages(chat_id, message_id)
                if forwarded_msg:
                    await forwarded_msg.copy(
                        chat_id=message.chat.id,
                        caption=forwarded_msg.caption
                    )
                    return
            
        await message.reply_text("Benvenuto! Usa /gen seguito da un link Telegram per iniziare.")
        
    except Exception as e:
        await message.reply_text(f"🔄 Riprova con un nuovo link: {str(e)}")

@app.on_message(filters.command("gen"))
async def comando_gen(client, message):
    if not is_admin(message.from_user.id):
        await message.reply_text("🚫 Comando riservato ad admin e owner")
        return

    try:
        if len(message.command) < 2:
            await message.reply_text("Usa: /gen link1 link2 link3...")
            return
            
        text = " ".join(message.command[1:])
        links = re.findall(r'https://t\.me/(?:c/)?[^/]+/\d+', text)
        
        if not links:
            await message.reply_text("Nessun link valido trovato")
            return
            
        for link in links:
            match = re.match(r'https://t\.me/(?:c/)?([^/]+)/(\d+)', link)
            
            if not match:
                await message.reply_text(f"Link non valido: {link}")
                continue
                
            chat_id = match.group(1)
            message_id = int(match.group(2))
            
            if chat_id.isdigit():
                chat_id = int('-100' + chat_id)
            else:
                chat = await client.get_chat(chat_id)
                chat_id = chat.id
                
            msg = await client.get_messages(chat_id, message_id)
            if msg:
                await msg.copy(
                    chat_id=message.chat.id,
                    caption=msg.caption if msg.caption else None
                )
                
                bot_username = (await client.get_me()).username
                encoded_link = base64.b64encode(link.encode()).decode()
                direct_link = f"https://t.me/{bot_username}?start=gen_{encoded_link}"
                await message.reply_text(f"🔗 Link diretto:\n`{direct_link}`", quote=True)
            
    except Exception as e:
        await message.reply_text(f"❌ Errore: {str(e)}")

@app.on_message(filters.command("addadmin"))
async def add_admin(client, message):
    if message.from_user.id != config["owner_id"]:
        await message.reply_text("🚫 Solo l'owner può aggiungere admin")
        return
        
    if len(message.command) != 2:
        await message.reply_text("Uso: /addadmin [user_id]")
        return
        
    try:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute("INSERT OR IGNORE INTO admins (id, username) VALUES (?, ?)",
                      (user_id, user.username))
        db.commit()
        db.close()
        
        await message.reply_text(f"✅ Admin aggiunto: {user.mention}")
        
    except Exception as e:
        await message.reply_text(f"❌ Errore: {str(e)}")

@app.on_message(filters.command("remadmin"))
async def remove_admin(client, message):
    if message.from_user.id != config["owner_id"]:
        await message.reply_text("🚫 Solo l'owner può rimuovere admin")
        return
        
    if len(message.command) != 2:
        await message.reply_text("Uso: /remadmin [user_id]")
        return
        
    try:
        user_id = int(message.command[1])
        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute("DELETE FROM admins WHERE id = ?", (user_id,))
        db.commit()
        db.close()
        
        await message.reply_text(f"✅ Admin rimosso: {user_id}")
        
    except Exception as e:
        await message.reply_text(f"❌ Errore: {str(e)}")

app.run()
