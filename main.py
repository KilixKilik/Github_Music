import asyncio
import time
import json
import requests
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

# https://github.com/settings/tokens CREATE CLASSIC TOKEN!!!!!
GITHUB_TOKEN = "твой токен"
GITHUB_USERNAME = "твой ниk"
UPDATE_INTERVAL = 1

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

async def get_media_info():
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        if current_session:
            info = await current_session.try_get_media_properties_async()
            playback_info = current_session.get_playback_info()
            if playback_info.playback_status == 4:  # Playing
                title = info.title.strip()
                artist = info.artist.strip()
                if title and artist:
                    return f"{title} — {artist}"
        return None
    except Exception as e:
        print(f"[Media Error] {e}")
        return None

def update_github_bio(text):
    url = "https://api.github.com/user"
    bio_text = f"🎧 Сейчас слушаю: {text}" if text else "Python dev | Coding to the beat 🎵"
    data = {
        "bio": bio_text
    }
    try:
        r = requests.patch(url, headers=headers, data=json.dumps(data))
        if r.status_code == 200:
            print(f"✅ GitHub bio обновлён: {bio_text}")
        else:
            print(f"[GitHub Error] {r.status_code} — {r.text}")
    except Exception as e:
        print(f"[GitHub Request Error] {e}")

last_status = None

print("🚀 Запущен детектор музыки...")
print("Обновляю bio в GitHub: '🎧 Сейчас слушаю: ...'")
print("Ctrl+C чтобы остановить")

try:
    while True:
        current_track = asyncio.run(get_media_info())
        status_text = current_track if current_track else None

        if status_text != last_status:
            update_github_bio(status_text)
            last_status = status_text

        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\n🛑 Остановка...")
    update_github_bio(None)
