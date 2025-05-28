from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mediabot.utils import chunks

class InstagramCollectionKeyboardMarkup:
  @staticmethod
  def build(items: list[dict], id: str) -> InlineKeyboardMarkup:
    # TODO(mhw0): refactor me
    collection_buttons = [[InlineKeyboardButton(f"{'🖼' if post['type'] == 'photo' else '🎞'}",
        callback_data=f"instagram_download_{id}_{col_index+row_index}") for col_index, post in enumerate(row)] \
        for row_index, row in enumerate(chunks(items, 5))]

    return InlineKeyboardMarkup(collection_buttons)