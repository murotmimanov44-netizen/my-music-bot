# --- АДМИН ҮЧҮН ЧЕКСИЗ БАЛАНС ---
def get_user(user_id):
    # Эгер бул сен болсоң, дароо чоң сан кайтарат
    if user_id == ADMIN_ID:
        return 999999999 
    
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0]

@dp.message(F.text == "👤 Профиль")
async def view_profile(message: types.Message):
    user_id = message.from_user.id
    balance = get_user(user_id)
    
    if user_id == ADMIN_ID:
        status = "💎 Админ (Чексиз упай)"
        display_balance = "∞"
    else:
        status = "👤 Колдонуучу"
        display_balance = f"{balance} упай"
        
    await message.answer(
        f"<b>Сенин профилиң:</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"🎭 Статус: {status}\n"
        f"💰 Баланс: {display_balance}",
        parse_mode="HTML"
    )
