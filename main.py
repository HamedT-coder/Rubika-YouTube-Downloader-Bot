# Import libraries - به روش صحیح
from rubka.asynco import Robot, filters
from rubka.context import Message
import asyncio
from pytube import YouTube
import os, re

token = os.getenv(BOT_TOKEN)
bot = Robot(token)

# Base variables
DOWNLOAD_LOCATION = "./temp/"
is_yt_sent = False

# Send welcome message to new users
@bot.on_message(filters.is_command.start)
async def start(bot:Robot, message:Message):
    await message.reply("به ربات آپارات دانلودر من خوش اومدی!")

# Handle /yt command
@bot.on_message()
async def yt_command(bot:Robot, message:Message):
    text = message.text
    if text == "/yt":
        global is_yt_sent
        await message.reply("یه لینک برام بفرست تا دانلودش کنم!")
        is_yt_sent = True

# Download video from youtube and send to user
@bot.on_message()
async def download(bot:Robot, message:Message):
    
    user_id = message.chat_id
    # Check if user message is a valid youtube video link
    link = message.text
    pattern = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌[\w\?‌=]*)?"
    result = re.match(pattern, link)
    if result and message.is_user and is_yt_sent or result and message.is_group:
        try:
            # ارسال وضعیت در حال پردازش
            status_msg = await message.answer("در حال دانلود ویدیو... لطفاً صبر کنید ⏳")
        # Download video from youtube
            youtube = YouTube(link)
            youtube_stream = youtube.streams.get_highest_resolution()
            file_path = youtube_stream.download(DOWNLOAD_LOCATION)
        # Send video to user
            file_name = youtube.streams.get_highest_resolution().default_filename
            #file_dir = f"{DOWNLOAD_LOCATION}{file_name}"
            with open(file_path, 'rb') as video_file:
                await bot.send_file(
                user_id,           
                video=video_file,                                        caption="فایل آپلود شد!"
                )
        # Delete video from disk after sending to user
            os.remove(file_path)
            
            # حذف پیام وضعیت
            await status_msg.delete()
            
        except Exception as e:
            await message.reply(f"❌ خطا در دانلود: {str(e)}")
            
    elif result == False and is_yt_sent == True:
        await message.reply("لینک نامعتبر!")

bot.run()
