from aportalsmp import update_auth, giftsFloors, search, PortalsGift, buy
from telebot import TeleBot, types
import asyncio
from time import sleep
import threading
from avg_colors import color_similarity

# === CONFIG ===
bot_token = "" # токен бота
api_id = 0 # твой api_id 
api_hash = "" # api_hash
chat_id = 0 # твой чат айди, куда присылаются уведомления
margin_threshold = 0.09
market_fee = 0.05

# === INIT ===
bot = TeleBot(bot_token)
token = asyncio.run(update_auth(api_id, api_hash))
floors = {}
seen_ids = set()
gift_cache = {}  # gift.id -> (owner_id, price)

# === UTILS ===
def shortname(gift_name):
    return gift_name.lower().replace(' ', '').replace('-', '').replace("'", "")

# === FLOOR PRICE UPDATER ===
def update_floors():
    global floors
    while True:
        try:
            floors = giftsFloors(authData=token)
            print('[✓] Updated floors')
        except Exception as e:
            print('[X] update_floors error:', e)
        sleep(60)

def floor_model(gift_name, model):
    return float(PortalsGift(search(gift_name=gift_name, model=model, limit=1, authData=token, sort="price_asc")[1]).price)

# === CALLBACK HANDLER ===
@bot.callback_query_handler(func=lambda call: True)
def buy_gift(call):
    nft_id = call.data
    price = gift_cache.get(nft_id)
    if price is None:
        bot.answer_callback_query(call.id, "Gift info not found. Try again later.")
        return
    try:
        print(buy(nft_id, price, authData=token))
        bot.answer_callback_query(call.id, "🎉 Gift bought successfully!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error buying gift: {e}")

# === GIFT WATCHER ===
def latest_gifts():
    global seen_ids, gift_cache
    while True:
        try:
            if not floors:
                print('[!] Waiting for floor data...')
                sleep(5)
                continue

            gifts = search(sort="latest", limit=20, authData=token)
            for gift_data in gifts:
                gift = PortalsGift(gift_data)
                gift_short = shortname(gift.name)

                if gift.id in seen_ids:
                    continue
                if gift_short not in floors:
                    continue

                floor_price = float(floors[gift_short])
                gift_price = float(gift.price)
                url = gift.animation_url
                similarity = asyncio.run(color_similarity(url))['similarity']

                if similarity >= 70.0:
                    try:
                        model_floor = PortalsGift(search(gift_name=gift.name, model=gift.model, sort="price_asc", limit=1, authData=token)[0]).price
                        model_text = f'📉 Model Floor: {model_floor} TON\n\n'
                    except:
                        model_text = "\n"
                    seen_ids.add(gift.id)
                    gift_cache[gift.id] = gift_price
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton("One-click Buy", callback_data=gift.id)
                    )
                    bot.send_message(chat_id,
                        f'🛎️ <a href="https://t.me/nft/{gift_short}-{gift.tg_id}">New Gift Found!</a>\n\n'
                        f'<b>{gift.name}</b>\n'
                        f'Model: {gift.model} ({gift.model_rarity}%)\n'
                        f'Backdrop: {gift.backdrop} ({gift.backdrop_rarity}%)\n'
                        f'Symbol: {gift.symbol} ({gift.symbol_rarity}%)\n\n'
                        f'💰 Price: <b>{gift_price} TON</b>\n'
                        f'📉 Floor: {floor_price} TON\n'
                        f'{model_text}'
                        f'Similarity: {similarity}%\n\n'
                        f'<a href="https://t.me/portals/market?startapp=gift_{gift.id}">Buy on Portals</a>',
                        parse_mode='HTML',
                        reply_markup=markup
                    )
        except Exception as e:
            print('[X] latest_gifts error:', e)

        print('[✓] Checked latest gifts')
        sleep(10)

# === THREAD START ===
threading.Thread(target=update_floors, daemon=True).start()
threading.Thread(target=latest_gifts, daemon=True).start()

# === START BOT POLLING ===
bot.infinity_polling()
