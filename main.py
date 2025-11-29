import asyncio
import time
import json
import os
import requests
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

# Get token at https://github.com/settings/tokens → Generate new token (classic) → scope "user"
token_nahui = "пошел нахуй"
uzername = "KilixKilik"
neeby = 3
camfig = "bio_config.json"

headers = {
    "Authorization": f"Bearer {token_nahui}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}
media_sessions = None

# Initialize config file if missing
if not os.path.exists(camfig):
    default_config = {
        "active_template": "Сейчас слушаю\\смотрю: {track}",
        "default_bio": "ы"
    }
    with open(camfig, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    print(f"[Config] Created default configuration at {camfig}")

# Load bio templates
with open(camfig, "r", encoding="utf-8") as f:
    config = json.load(f)

async def musica_palucheniao():
    global media_sessions
    try:
        if media_sessions is None:
            media_sessions = await MediaManager.request_async()
        
        session = media_sessions.get_current_session()
        if not session:
            return None
        
        props = await session.try_get_media_properties_async()
        playback = session.get_playback_info()
        
        # PlaybackStatus.Playing = 4
        if playback.playback_status == 4 and props.title and props.artist:
            return f"{props.title.strip()} — {props.artist.strip()}"
        return None
    except Exception as e:
        print(f"[Media Error] {str(e)}")
        media_sessions = None
        return None

def obnovastatusa(track_text):
    bio_content = config["active_template"].format(track=track_text) if track_text else config["default_bio"]
    payload = {"bio": bio_content[:256]}  # GitHub bio max length is 256 chars
    
    try:
        resp = requests.patch(
            "https://api.github.com/user",
            headers=headers,
            data=json.dumps(payload)
        )
        status = "✅" if resp.status_code == 200 else f"❌ [{resp.status_code}]"
        print(f"{status} Updated bio: {bio_content}")
    except Exception as e:
        print(f"[GitHub API Error] {str(e)}")

# Main execution loop
last_track = None
print("🚀 GitHub Media Status Updater initialized")
print(f"Using config: {camfig}")
print("Monitoring system media sessions (Spotify/Yandex.Music/Browsers)")
print("Press Ctrl+C to terminate")

try:
    while True:
        current_track = asyncio.run(musica_palucheniao())
        
        if current_track != last_track:
            obnovastatusa(current_track)
            last_track = current_track
        
        time.sleep(neeby)

except KeyboardInterrupt:
    print("\n🛑 Graceful shutdown initiated")
    obnovastatusa(None)
    print("Bio reset to default state")
