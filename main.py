from rubka.asynco import Robot, filters
from rubka.context import Message
import asyncio
from pytube import YouTube
import os, re
from downloader import download_video

# Base variables
DOWNLOAD_LOCATION = "./temp/"
is_yt_sent = False
token = os.getenv(BOT_TOKEN)
bot = Robot(token)

# Send welcome message to new users
@bot.on_message(filters.is_command.start)
async def start(bot:Robot, message:Message):
    await message.reply("به ربات آپارات دانلودر من خوش اومدی!")

# Download video from youtube and send to user
@bot.on_message()
async def download(bot:Robot, message:Message):
    
    user_id = message.chat_id
    # Check if user message is a valid youtube video link
    link = message.text
    pattern = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌[\w\?‌=]*)?"
    result = re.match(pattern, link)
    if result and message.is_user or result and message.is_group:
        try:
            # ارسال وضعیت در حال پردازش
            status_msg = await message.answer("در حال دانلود ویدیو... لطفاً صبر کنید ⏳")
        # Download video from youtube
            video = download_video(
                video_url=link.strip(),
                output_type="video",
                quality="720"
            )
            with open(file_path, 'rb') as video_file:
                await bot.send_file(
                user_id,           
                video=video_file,                                        caption="فایل آپلود شد!"
                )
        # Delete video from disk after sending to user
            os.remove(video)
            
            # حذف پیام وضعیت
            await status_msg.delete()
            
        except Exception as e:
            await message.reply(f"❌ خطا در دانلود: {str(e)}")
            
    elif result == False:
        await message.reply("لینک نامعتبر!")

bot.run()
