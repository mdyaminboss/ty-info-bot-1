import requests
import json
import datetime
import html

# আপনার টেলিগ্রাম বটের টোকেন
TOKEN = '8631373804:AAGTF62pXXEZzGEW4FX8y_heLbSgxfXEm3E'

# আপনার এপিআই কি
API_KEY = 'ceH5MEUtBPgqNnWXe2wVKZ8-Nqmfea5poOT5S8fkiPQ'

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def set_bot_commands():
    url = f"{BASE_URL}/setMyCommands"
    commands = {
        "commands": [
            {"command": "info", "description": "Check Free Fire Player Stats & UID Info"},
            {"command": "start", "description": "Start the Tynex Bot"}
        ]
    }
    try:
        requests.post(url, json=commands, timeout=10)
    except Exception as e:
        print(f"Error setting bot commands: {e}")

def send_message(chat_id, text, parse_mode="Markdown", reply_markup=None, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return {}

def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error deleting message: {e}")

def format_date(timestamp):
    if not timestamp:
        return "N/A"
    try:
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%B %d, %Y')
    except:
        return "N/A"

def check_val(val):
    if val is None or val == '':
        return "N/A"
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, list):
        return ", ".join(map(str, val)) if val else "None"
    val_str = str(val)
    if '_' in val_str:
        parts = val_str.split('_')
        return parts[1] if len(parts) > 1 and parts[1] else val_str
    return val_str

def format_number(val):
    try:
        return f"{int(val):,}"
    except:
        return str(val)

def get_player_data(uid):
    url = f"https://api.gameskinbo.com/ff-info/get?uid={uid}"
    headers = {'x-api-key': API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # যদি সার্ভার থেকে জেসন ডাটা না আসে
        try:
            data = response.json()
        except ValueError:
            return None, "⚠️ Server is busy or API response is invalid. Please try again later."
            
        if not response.ok or 'error' in data:
            error_text = data.get('error', "Invalid UID or API limit exceeded.")
            return None, f"⚠️ {error_text}"
            
        return data, None
    except requests.exceptions.Timeout:
        return None, "⚠️ Connection timeout! The API server took too long to respond."
    except Exception as e:
        return None, "⚠️ Failed to fetch data. Please check the UID or try again later."

def handle_updates(offset=None):
    url = f"{BASE_URL}/getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    try:
        response = requests.get(url, timeout=110)
        return response.json().get("result", [])
    except Exception as e:
        print(f"Network error in getUpdates: {e}")
        return []

def main():
    set_bot_commands()
    print("🤖 TYNEX INFO CHECKER Bot is running securely with Error Handlers...")
    offset = None
    
    while True:
        updates = handle_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            
            if "callback_query" in update:
                callback = update["callback_query"]
                callback_id = callback["id"]
                data_val = callback["data"]
                try:
                    requests.post(f"{BASE_URL}/answerCallbackQuery", json={
                        "callback_query_id": callback_id,
                        "text": f"Action for: {data_val}",
                        "show_alert": False
                    }, timeout=5)
                except:
                    pass
                continue

            if "message" in update and "text" in update["message"]:
                message = update["message"]
                chat_id = message["chat"]["id"]
                message_id = message["message_id"]
                text = message["text"].strip()
                first_name = message["from"].get("first_name", "Gamer")
                
                parts = text.split()
                command = parts[0].split('@')[0].lower() if parts else ""
                
                uid = ""
                if command == "/info":
                    if len(parts) > 1 and parts[1].isdigit():
                        uid = parts[1]
                    else:
                        send_message(chat_id, "❌ *Incorrect format!*\nPlease use like this: `/info 2287422745`", parse_mode="Markdown", reply_to_message_id=message_id)
                        continue
                elif text.startswith("/start"):
                    welcome_msg = (
                        f"💎 *𝐅𝐑𝐄𝐄 𝐅𝐈𝐑𝐄 — 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐏𝐑𝐎𝐅𝐈𝐋𝐄* 💎\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"Hello *{first_name}*! 👋\n"
                        f"Welcome to the most advanced Free Fire Player Stats & UID Checker Bot.\n\n"
                        f"📌 *How to use?*\n"
                        f"Use command: `/info <UID>`\n"
                        f"Example: `/info 2287422745`\n\n"
                        f"🚀 *𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐓𝐘𝐍𝐄𝐗*"
                    )
                    send_message(chat_id, welcome_msg, parse_mode="Markdown", reply_to_message_id=message_id)
                    continue
                
                if uid:
                    loading_res = send_message(chat_id, "🔍 *Fetching player data from server, please wait...*", parse_mode="Markdown", reply_to_message_id=message_id)
                    loading_msg_id = loading_res.get("result", {}).get("message_id")
                    
                    data, err = get_player_data(uid)
                    
                    if loading_msg_id:
                        delete_message(chat_id, loading_msg_id)
                        
                    if err:
                        # ইউজারকে এখন সরাসরি সুন্দর ও পরিষ্কার এরর মেসেজ দেখাবে
                        send_message(chat_id, f"❌ *Error Occurred*\n{err}", parse_mode="Markdown", reply_to_message_id=message_id)
                        continue
                    
                    acc = data.get("AccountInfo", {})
                    profile = data.get("AccountProfileInfo", {})
                    credit = data.get("CreditScoreInfo", {})
                    if not isinstance(credit, dict):
                        credit = {}
                    social = data.get("SocialInfo", {})
                    guild = data.get("GuildInfo", {})
                    guild_owner = data.get("GuildOwnerInfo", {})
                    pet = data.get("PetInfo", {})
                    items = data.get("EquippedItemsInfo", {})
                    
                    player_name = html.escape(check_val(acc.get("AccountName")))
                    player_level = check_val(acc.get("AccountLevel"))
                    player_region = check_val(acc.get("AccountRegion"))
                    player_likes = format_number(acc.get("AccountLikes"))
                    player_exp = format_number(acc.get("AccountEXP"))
                    created_time = format_date(acc.get("AccountCreateTime"))
                    last_login = format_date(acc.get("AccountLastLogin"))
                    game_version = check_val(data.get("ReleaseVersion"))
                    season_id = check_val(acc.get("AccountSeasonId"))
                    
                    br_max = check_val(profile.get("BrMaxRank"))
                    br_point = format_number(profile.get("BrRankPoint"))
                    cs_max = check_val(profile.get("CsMaxRank"))
                    cs_point = format_number(profile.get("CsRankPoint"))
                    
                    credit_score = check_val(credit.get("creditScore"))
                    language = check_val(social.get("language"))
                    signature = html.escape(check_val(social.get("signature")))
                    time_active = check_val(social.get("timeActive"))
                    mode_prefer = check_val(social.get("modePrefer"))
                    
                    guild_name = html.escape(check_val(guild.get("GuildName")))
                    guild_id = check_val(guild.get("GuildID"))
                    guild_level = check_val(guild.get("GuildLevel"))
                    guild_members = f"{check_val(guild.get('GuildMember'))} / {check_val(guild.get('GuildCapacity'))}"
                    guild_leader = html.escape(check_val(guild_owner.get("nickname")))
                    
                    pet_id = check_val(pet.get("id"))
                    pet_level = check_val(pet.get("level"))
                    bp_badges = format_number(items.get("EquippedBPBadges"))
                    avatar_id = check_val(items.get("EquippedAvatarId"))
                    banner_id = check_val(items.get("EquippedBannerId"))
                    
                    result_msg = (
                        f"💎 *𝐅𝐑𝐄𝐄 𝐅𝐈𝐑𝐄 — 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐏𝐑𝐎𝐅𝐈𝐋𝐄* 💎\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"👑 *𝐏𝐋𝐀𝐘𝐄𝐑 𝐏𝐑𝐎𝐅𝐈𝐋𝐄*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"👤 *𝐍𝐀𝐌𝐄*\n"
                        f"➜ {player_name}\n\n"
                        f"🆔 *𝐔𝐈𝐃*\n"
                        f"➜ `{uid}`\n\n"
                        f"⭐ *𝐋𝐄𝐕𝐄𝐋*\n"
                        f"➜ {player_level}\n\n"
                        f"🌐 *𝐑𝐄𝐆𝐈𝐎𝐍*\n"
                        f"➜ {player_region}\n\n"
                        f"❤️ *𝐋𝐈𝐊𝐄𝐒*\n"
                        f"➜ {player_likes}\n\n"
                        f"🔥 *𝐄𝐗𝐏*\n"
                        f"➜ {player_exp}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"📅 *𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐃𝐄𝐓𝐀𝐈𝐋𝐒*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"📅 *𝐂𝐑𝐄𝐀𝐓𝐄𝐃*\n"
                        f"➜ {created_time}\n\n"
                        f"⏰ *𝐋𝐀𝐒𝐓 𝐋𝐎𝐆𝐈𝐍*\n"
                        f"➜ {last_login}\n\n"
                        f"📱 *𝐕𝐄𝐑𝐒𝐈𝐎𝐍*\n"
                        f"➜ {game_version}\n\n"
                        f"🏆 *𝐒𝐄𝐀𝐒𝐎𝐍*\n"
                        f"➜ {season_id}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"🏆 *𝐑𝐀𝐍𝐊𝐈𝐍𝐆 & 𝐒𝐓𝐀𝐓𝐒*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"🥇 *𝐁𝐑 𝐌𝐀𝐗 𝐑𝐀𝐍𝐊*\n"
                        f"➜ {br_max}\n\n"
                        f"📊 *𝐁𝐑 𝐏𝐎𝐈𝐍𝐓𝐒*\n"
                        f"➜ {br_point}\n\n"
                        f"⚔️ *𝐂𝐒 𝐌𝐀𝐗 𝐑𝐀𝐍𝐊*\n"
                        f"➜ {cs_max}\n\n"
                        f"📊 *𝐂𝐒 𝐏𝐎𝐈𝐍𝐓𝐒*\n"
                        f"➜ {cs_point}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"🛡️ *𝐏𝐑𝐎𝐅𝐈𝐋𝐄 𝐒𝐓𝐀𝐓𝐔𝐒*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"💠 *𝐂𝐑𝐄𝐃𝐈𝐓 𝐒𝐂𝐎𝐑𝐄*\n"
                        f"➜ {credit_score}\n\n"
                        f"🌐 *𝐋𝐀𝐍𝐆𝐔𝐀𝐆𝐄*\n"
                        f"➜ {language}\n\n"
                        f"🌙 *𝐀𝐂𝐓𝐈𝐕𝐄 𝐓𝐈𝐌𝐄*\n"
                        f"➜ {time_active}\n\n"
                        f"🎮 *𝐏𝐑𝐄𝐅𝐄𝐑𝐑𝐄𝐃 𝐌𝐎𝐃𝐄*\n"
                        f"➜ {mode_prefer}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"✍️ *𝐁𝐈𝐎 & 𝐒𝐈𝐆𝐍𝐀𝐓𝐔𝐑𝐄*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"{signature}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"🏰 *𝐆𝐔𝐈𝐋𝐃 𝐏𝐑𝐎𝐅𝐈𝐋𝐄*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"🏷️ *𝐆𝐔𝐈𝐋𝐃 𝐍𝐀𝐌𝐄*\n"
                        f"➜ {guild_name}\n\n"
                        f"🆔 *𝐆𝐔𝐈𝐋𝐃 𝐈𝐃*\n"
                        f"➜ `{guild_id}`\n\n"
                        f"⭐ *𝐆𝐔𝐈𝐋𝐃 𝐋𝐄𝐕𝐄𝐋*\n"
                        f"➜ {guild_level}\n\n"
                        f"👥 *𝐌𝐄𝐌𝐁𝐄𝐑𝐒*\n"
                        f"➜ {guild_members}\n\n"
                        f"👑 *𝐆𝐔𝐈𝐋𝐃 𝐋𝐄𝐀𝐃𝐄𝐑*\n"
                        f"➜ {guild_leader}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
                        f"🐾 *𝐏𝐄𝐓 & 𝐀𝐒𝐒𝐄𝐓𝐒*\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"🐾 *𝐏𝐄𝐓 𝐈𝐃*\n"
                        f"➜ {pet_id}\n\n"
                        f"⭐ *𝐏𝐄𝐓 𝐋𝐄𝐕𝐄𝐋*\n"
                        f"➜ {pet_level}\n\n"
                        f"🎟️ *𝐄𝐋𝐈𝐓𝐄 𝐏𝐀𝐒𝐒 𝐁𝐀𝐃𝐆𝐄𝐒*\n"
                        f"➜ {bp_badges}\n\n"
                        f"🖼️ *𝐀𝐕𝐀𝐓𝐀𝐑 𝐈𝐃*\n"
                        f"➜ {avatar_id}\n\n"
                        f"🎖️ *𝐁𝐀𝐍𝐍𝐄𝐑 𝐈𝐃*\n"
                        f"➜ {banner_id}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"💎 *𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐏𝐑𝐎𝐅𝐈𝐋𝐄*\n"
                        f"🚀 *𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐓𝐘𝐍𝐄𝐗*"
                    )
                    
                    reply_markup = {
                        "inline_keyboard": [
                            [{"text": "🌐 DEVELOPER", "url": "https://t.me/YaminOnFire07"}],
                            [{"text": "📢 OFFICIAL CHANNEL", "url": "https://t.me/MrTripleR_YT0"}]
                        ]
                    }
                    
                    send_message(chat_id, result_msg, parse_mode="Markdown", reply_markup=reply_markup, reply_to_message_id=message_id)

if __name__ == "__main__":
    main()
