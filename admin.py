from pyrogram import Client, filters
import sqlite3

def init_db():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            username TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

@Client.on_message(filters.command("addadmin"))
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

@Client.on_message(filters.command("remadmin"))
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

# Inizializza il database
init_db()
