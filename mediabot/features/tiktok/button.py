from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mediabot.utils import chunks
import json


class TiktokMusicKeyboardMarkup:
    @staticmethod
    def get_music_button(link: str, user_id):
        payload = json.dumps({"link": link, "user_id": user_id})
        keyboard = [
            [InlineKeyboardButton("🎵 Music", callback_data=f"tiktok_music12:{payload}")]
        ]
        return InlineKeyboardMarkup(keyboard)