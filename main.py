import asyncio
import os
import time
from uuid import uuid4
import uuid
from datetime import datetime
import pymongo


import redis
import telethon
import telethon.tl.types
import telethon.tl.types as tl_types
from telethon import events
from telethon.tl import functions, types
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.types import Message, UpdateNewMessage
from telethon import Button


from cansend import CanSend
from config import *
from terabox import get_data
# from stats import (
#     track_message,
#     track_file_type,
#     get_message_count,
#     get_new_user_count_today,
#     get_top_active_users,
#     get_file_type_stats,
# )
from tools import (
    convert_seconds,
    download_file,
    download_image_to_bytesio,
    extract_code_from_url,
    get_formatted_size,
    get_urls_from_string,
    is_user_on_chat,
    get_bot_username,
)

BOT_USERNAME = get_bot_username(BOT_TOKEN)


bot = TelegramClient("tele", API_ID, API_HASH)
# MongoDB Configuration
MONGO_URI = "mongodb+srv://ducexxd:zaxscd123@cluster0.loyreds.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB connection string
MONGO_DATABASE = "Cluster0"  # The name of your database


client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]


spam_records = db["spam_records"] # Collection to store spam related data

# Connect to MongoDB

bot_start_time = time.time()
users = db["users"]  # 'users' should now be defined
user_count = users.count_documents({})  # Initial count
downloads = db["downloads"]
files = db["files"]  # Assuming your collection is named 'files'

MAX_CONCURRENT_DOWNLOADS = 3  # Adjust the concurrency level 
download_queue = asyncio.Queue()  

async def download_worker():
    while True:
        download_task = await download_queue.get()  
        try:
            await process_download(download_task)
        except Exception as e:
            # Handle download errors appropriately
            print(f"Error processing download: {e}")
            message = download_task['message']
            await message.reply(f"Sorry, an error occurred while downloading.") 
        finally:
            download_queue.task_done() 

async def handle_new_user(user_id, first_name):
    if not users.count_documents({"_id": user_id}):
        users.insert_one(
            {"_id": user_id, "first_name": first_name, "joined_at": datetime.now()}
        )
        global user_count
        user_count += 1


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/ban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def ban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    try:
        user_id = int(m.pattern_match.group(1))  # Get user ID to ban
    except ValueError:
        return await m.reply("Invalid user ID format.")

    # Check if user exists in MongoDB
    user_data = users.find_one({"_id": user_id})
    if not user_data:
        return await m.reply("User not found.")

    # Update user data in MongoDB to mark as banned
    users.update_one({"_id": user_id}, {"$set": {"banned": True}})
    await m.reply(f"User ID {user_id} has been banned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/unban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def unban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    try:
        user_id = int(m.pattern_match.group(1))
    except ValueError:
        return await m.reply("Invalid user ID format.")
    # Check if user exists in MongoDB
    user_data = users.find_one({"_id": user_id})
    if not user_data:
        return await m.reply("User not found.")
    # Update user data in MongoDB to remove banned flag
    users.update_one({"_id": user_id}, {"$unset": {"banned": True}})
    await m.reply(f"User ID {user_id} has been unbanned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/stats$", incoming=True, outgoing=False))
async def stats_command(m: UpdateNewMessage):
    # ... your existing checks (channels, permissions) ...

    new_users_today = users.count_documents(
        {
            "joined_at": {
                "$gte": datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            }
        }
    )
    top_active_users = list(
        users.aggregate(
            [
                {
                    "$group": {
                        "_id": "$_id",
                        "total_messages": {"$sum": "$messages_sent"},
                    }
                },
                {"$sort": {"total_messages": -1}},
                {"$limit": 5},  # Show top 5
            ]
        )
    )

    # Calculate uptime
    uptime = convert_seconds(time.time() - bot_start_time)

    stats_message = f"""
**Bot Statistics:**

**Uptime:** {uptime}
**Users:** {user_count} 
@{BOT_USERNAME}
"""

    if m.sender_id == OWNER_ID:
        await m.reply(stats_message)
    else:
        await m.reply("Sorry, this command is restricted to the bot owner.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/start$", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    first_name = m.sender.first_name
    user_id = m.sender.id

    # Check if user exists in MongoDB, if not, create a new entry
    user_data = users.find_one({"_id": user_id})
    if not user_data:
        users.insert_one(
            {
                "_id": user_id,
                "first_name": first_name,
                "joined_at": datetime.now(),
                # ... other fields you want to track ...
            }
        )

    check_if = await is_user_on_chat(bot, f"@{UPCHANNEL}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPCHANNEL} then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@{UPGROUP}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPGROUP} then send me the link again.")

    await bot.send_message(
        USER_CHANNEL,
        f"**New User Joined**\nName: {first_name} \nUser ID: [{user_id}](tg://user?id={user_id})\n@{BOT_USERNAME}",
        parse_mode="markdown",
    )

    reply_text = f"""
**Hello, [{first_name}](tg://user?id={user_id})!** I am a bot to download videos from Terabox.

**Just send me the Terabox link** and I'll start downloading it for you.
"""
    await m.reply(
        reply_text,
        buttons=[
            [
                Button.url("Update Channel", f"https://t.me/{UPCHANNEL}"),
                Button.url("Help", f"https://t.me/{UPGROUP}"),
            ]
        ],
        link_preview=False,
        parse_mode="markdown",
    )


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/broadcast$", incoming=True, outgoing=False))
async def broadcast(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    if m.sender_id != OWNER_ID:  # Check if user is authorized
        await m.reply("Sorry, you don't have permission to broadcast.")
        return
    message_text = await m.get_reply_message()  # Get message to broadcast
    if not message_text:
        return await m.reply("Please reply with the message you want to broadcast.")

    # Get all users from MongoDB
    all_users = users.find({})

    # Broadcast the message
    for user in all_users:
        user_id = user["_id"]
        try:
            await bot.send_message(int(user_id), message_text.message)
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    await m.reply("Broadcast sent successfully!")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/help$", incoming=True, outgoing=False))
async def help_command(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    check_if = await is_user_on_chat(bot, f"@{UPCHANNEL}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPCHANNEL} then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@{UPGROUP}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPGROUP} then send me the link again.")
    help_text = f"""
Available commands:

/start - Start using the bot.
/premium - Get Premium Offer
/help - Show this help message.

@{UPCHANNEL}
"""

    link_preview = (False,)
    await m.reply(
        help_text,
        parse_mode="markdown",
        buttons=[
            [
                Button.url("Updates", f"https://t.me/{UPCHANNEL}"),
                Button.url("Report Bug", f"https://t.me/{UPGROUP}"),
            ]
        ],
    )


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text and get_urls_from_string(message.text),
    )
)
async def get_message(m: Message):
    asyncio.create_task(handle_message(m))


async def handle_message(m: Message):
    if m.is_group or m.is_channel:
        return

    user_id = m.sender_id

    first_name = m.sender.first_name
    user_data = users.find_one({"_id": user_id})
    if not user_data:
        users.insert_one(
            {
                "_id": user_id,
                "first_name": first_name,
                "joined_at": datetime.now(),
                # ... other fields you want to track ...
            }
        )
    
    # if db.sismember("banned_users", user_id):
    #     await m.reply("You are banned from using this bot.")
    #     return
    # Check if banned
    # if user_data.get("banned"):  # Assuming you have a 'banned' field
    #     await m.reply(
    #         "You are banned from using this bot.\nContact @TeamDextiN for unban"
    #     )
    #     return

    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("Please enter a valid url.")

    check_if = await is_user_on_chat(bot, f"@{UPCHANNEL}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPCHANNEL} then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@{UPGROUP}", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @{UPGROUP} then send me the link again.")
    first_name = m.sender.first_name
    username = m.sender.username
    user_id = m.sender_id

    spam_record = spam_records.find_one({"_id": m.sender_id})
    if spam_record and m.sender_id not in [1317173146]: 
        if time.monotonic() - spam_record["last_spam_time"] < 60:  # Check if spammed within 1 minute
            return await m.reply("You are spamming. Please wait a 1 minute and try again.")
        else:
            spam_records.update_one({"_id": m.sender_id}, {"$set": {"last_spam_time": time.monotonic()}})

    count = users.find_one({"_id": m.sender_id}).get("download_count", 0)
    if count > 5:
        return await hm.edit(
            "You are limited now. Please come back after 2 hours or use another account."
        )
    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("Please enter a valid url.")

    download_task = {
        "url": url,
        "message": m  
    }
    await download_queue.put(download_task) 
    hm = await m.reply("Sending you the media, please wait...")
    # Send notification to USER_CHANNEL
    try:
        await bot.send_message(
            USER_CHANNEL,
            f"Name: [{first_name}](tg://user?id={m.sender.id})\nUsername: @{username}\nUser ID: [{user_id}](tg://user?id={user_id})\nLink: {url}\nBot: @{BOT_USERNAME}",
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

    shorturl = extract_code_from_url(url)
    if not shorturl:
        return await hm.edit("Seems like your link is invalid.")
    file_data = files.find_one({"short_code": shorturl})
    if file_data:
        try:
            await hm.delete()
        except:
            pass

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file_data["file_id"]],  # Retrieve the file_id
                to_peer=m.chat.id,
                drop_author=True,
                # noforwards=True,
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        users.update_one({"_id": m.sender_id}, {"$inc": {"download_count": 1}}) 

        return

    user_id = m.sender_id
    user_data = users.find_one({"_id": user_id})
    if not user_data:
        users.insert_one(
            {
                "_id": user_id,
                "first_name": m.sender.first_name,
                "joined_at": datetime.now(),
                # ... other fields you want to track ...
            }
        )

    # track_message(m.sender_id)
    data = get_data(url)
    # print(data)  # Print the API response to your logs
    if not data:
        return await hm.edit("Sorry! Your link is broken or API is dead.")

    # db.set(m.sender_id, time.monotonic(), ex=60)
    if (
        not data["file_name"].endswith(".mp4")
        and not data["file_name"].endswith(".mkv")
        and not data["file_name"].endswith(".Mkv")
        and not data["file_name"].endswith(".webm")
        and not data["file_name"].endswith(".ts")
        and not data["file_name"].endswith(".mov")
        and not data["file_name"].endswith(".hevc")
        and not data["file_name"].endswith(".png")
        and not data["file_name"].endswith(".jpg")
        and not data["file_name"].endswith(".jpeg")
    ):
        return await hm.edit(
            f"Sorry! File is not supported for now. I can download only .mp4, .mkv, .webm, .ts, .mov, .hevc, .png, .jpg, .jpeg files."
        )
    if int(data["sizebytes"]) > 524288000 and m.sender_id not in [6791744215]:
        return await hm.edit(
            f"Sorry! File is too big. I can download only 500MB and this file is of {data['size']} ."
        )

    start_time = time.time()
    cansend = CanSend()

    async def progress_bar(current_downloaded, total_downloaded, state="Sending"):

        if not cansend.can_send():
            return
        bar_length = 20
        percent = current_downloaded / total_downloaded
        arrow = "█" * int(percent * bar_length)
        spaces = "░" * (bar_length - len(arrow))

        elapsed_time = time.time() - start_time

        head_text = f"{state} `{data['file_name']}`"
        progress_bar = f"[{arrow + spaces}] {percent:.2%}"
        upload_speed = current_downloaded / elapsed_time if elapsed_time > 0 else 0
        speed_line = f"Speed: **{get_formatted_size(upload_speed)}/s**"

        time_remaining = (
            (total_downloaded - current_downloaded) / upload_speed
            if upload_speed > 0
            else 0
        )
        time_line = f"Time Remaining: `{convert_seconds(time_remaining)}`"

        size_line = f"Size: **{get_formatted_size(current_downloaded)}** / **{get_formatted_size(total_downloaded)}**"

        await hm.edit(
            f"{head_text}\n{progress_bar}\n{speed_line}\n{time_line}\n{size_line}",
            parse_mode="markdown",
        )

    uuid = str(uuid4())
    thumbnail = download_image_to_bytesio(data["thumb"], "thumbnail.png")

    try:
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            file=data["direct_link"],
            thumb=thumbnail if thumbnail else None,
            progress_callback=progress_bar,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

@{UPCHANNEL}
""",
            supports_streaming=True,
            spoiler=True,
        )
        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file.id],
                to_peer=m.chat.id,
                top_msg_id=m.id,
                drop_author=True,
                # noforwards=True,  # Uncomment if needed
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        users.update_one({"_id": m.sender_id}, {"$inc": {"download_count": 1}}) 

    except telethon.errors.rpcerrorlist.WebpageCurlFailedError:
        download = await download_file(
            data["direct_link"], data["file_name"], progress_bar
        )
        if not download:
            return await hm.edit(
                f"Sorry! Download Failed but you can download it from [here]({data['direct_link']}).",
                parse_mode="markdown",
            )
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            download,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

@{UPCHANNEL}
""",
            # Shareable Link: [Click Here](https://t.me/{BOT_USERNAME}?start={uuid})
            progress_callback=progress_bar,
            thumb=thumbnail if thumbnail else None,
            supports_streaming=True,
            spoiler=True,
        )

        try:
            os.unlink(download)
        except Exception as e:
            print(e)
    except Exception:
        return await hm.edit(
            f"Sorry! Download Failed but you can download it from [here]({data['direct_link']}).",
            parse_mode="markdown",
        )
    try:
        os.unlink(download)
    except Exception as e:
        pass
    try:
        await hm.delete()
    except Exception as e:
        print(e)

async def start_bot():
    await bot.start(bot_token=BOT_TOKEN)  # Start the Telegram bot
    print("Bot started!")
    print(f"This bot is connected to {BOT_USERNAME}.")

    # Create download workers
    # for _ in range(MAX_CONCURRENT_DOWNLOADS):
    #     asyncio.create_task(download_worker())

    await bot.run_until_disconnected()

# asyncio.create_task(download_worker()) 
# for _ in range(MAX_CONCURRENT_DOWNLOADS):
#     asyncio.create_task(download_worker())
# bot.start(bot_token=BOT_TOKEN)
# print("Bot started!")
# print(f"This bot is connected to {BOT_USERNAME}.")
# bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_bot()) 
