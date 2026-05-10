import requests
import time
import sys
from pathlib import Path

# ======================== تنظیمات ========================
API_URL = "https://hub.ytconvert.org/api/download"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://media.ytmp3.gg/",
    "Content-Type": "application/json",
    "Origin": "https://media.ytmp3.gg"
}

# ======================== توابع ========================
def download_video(video_url: str, output_type: str = "video", quality: str = "720", bitrate: str = "192"):
    """
    دانلود ویدیو یا صدا از YouTube با استفاده از API
    
    Args:
        video_url: لینک ویدیوی YouTube
        output_type: "video" یا "audio"
        quality: برای ویدیو: 144, 360, 480, 720, 1080
        bitrate: برای صدا: 128, 192, 320 (بر حسب kbps)
    
    Returns:
        مسیر فایل دانلود شده یا None در صورت خطا
    """
    
    # ساخت payload بر اساس نوع خروجی
    if output_type == "audio":
        payload = {
            "url": video_url,
            "os": "linux",
            "output": {
                "type": "audio",
                "format": "mp3"
            },
            "audio": {
                "bitrate": f"{bitrate}k"
            }
        }
        file_ext = "mp3"
    else:  # video
        payload = {
            "url": video_url,
            "os": "linux",
            "output": {
                "type": "video",
                "format": "mp4",
                "quality": f"{quality}p"
            }
        }
        file_ext = "mp4"
    
    # 1. ارسال درخواست اولیه
    print(f"[1] ارسال درخواست به API...")
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"خطا در پاسخ سرور: {response.status_code}")
            return None
        data = response.json()
        status_url = data.get("statusUrl")
        if not status_url:
            print("خطا: statusUrl دریافت نشد")
            return None
        print(f"    وضعیت چک در: {status_url}")
    except Exception as e:
        print(f"خطا در اتصال به API: {e}")
        return None
    
    # 2. Polling برای بررسی وضعیت تبدیل
    print("[2] در انتظار تبدیل ویدیو...")
    max_attempts = 60  # حدود 2 دقیقه (هر 2 ثانیه)
    for attempt in range(max_attempts):
        time.sleep(2)
        try:
            status_response = requests.get(status_url, headers=HEADERS, timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get("status", "")
                
                if state == "completed":
                    download_url = status_data.get("downloadUrl")
                    if not download_url:
                        print("    خطا: downloadUrl وجود ندارد")
                        return None
                    print("    تبدیل با موفقیت انجام شد!")
                    
                    # 3. دانلود فایل نهایی
                    print("[3] در حال دانلود فایل...")
                    return download_file(download_url, file_ext)
                
                elif state in ("failed", "error"):
                    print("    تبدیل با خطا مواجه شد")
                    return None
                else:
                    # هنوز در حال پردازش
                    print(f"    وضعیت: {state} ...")
            else:
                print(f"    پاسخ غیرمنتظره: {status_response.status_code}")
        except Exception as e:
            print(f"    خطا در polling: {e}")
    
    print("زمان انتظار به پایان رسید، تبدیل کامل نشد")
    return None


def download_file(url: str, extension: str) -> Path | None:
    """دانلود فایل از downloadUrl و ذخیره در دایرکتوری current"""
    try:
        # نام فایل: از URL نمی‌شه استخراج کرد، پس یه اسم پیش‌فرض با timestamp
        filename = f"youtube_{int(time.time())}.{extension}"
        filepath = Path(filename)
        
        response = requests.get(url, headers=HEADERS, stream=True, timeout=600)
        if response.status_code != 200:
            print(f"   خطا در دانلود: کد {response.status_code}")
            return None
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r   دانلود: {percent:.1f}%", end="")
        
        print(f"\n   فایل ذخیره شد: {filepath.name} ({downloaded / 1e6:.1f} MB)")
        return filepath
    
    except Exception as e:
        print(f"\n   خطا در دانلود فایل: {e}")
        return None
