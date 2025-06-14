import traceback
import pathlib
from telegram import Update

import mediabot.features.required_join.handlers as required_join_feature
import mediabot.features.track.handlers as track_feature
from mediabot.context import Context
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.exceptions import InstanceQuotaLimitReachedException
from mediabot.features.advertisement.model import Advertisement
from mediabot.features.instagram.buttons import InstagramCollectionKeyboardMarkup
from mediabot.features.instance.model import Instance
# from mediabot.models.request import InstagramLinkRequest, RequestKind
from mediabot.features.instagram.model import Instagram
from mediabot.features.track.model import Track
from mediabot.features.media_downloader.model import MediaService
from mediabot.utils import AsyncFileDownloader
from mediabot.decorators import job_check
from mediabot.cache import redis
from mediabot.features.client_manager.manager import ClientManager



async def _instagram_handle_link(context: Context, link: str, chat_id: int, user_id: int, reply_to_message_id: int = None, use_cache: bool = True):
  try:
    if await ClientManager.is_client_pending(user_id):
      await context.bot.send_message(chat_id, context.l("request.pending"), reply_to_message_id=reply_to_message_id)
      return
    await ClientManager.set_client_pending(user_id)

    processing_message = await context.bot.send_message(chat_id, context.l("request.processing_text"), reply_to_message_id=reply_to_message_id)

    link_info_id = ""

    try:
      instagram_post = await Instagram.get(link)
      link_info_id = await MediaService.save_link_info(instagram_post)
    except Exception:
      await processing_message.delete()

      await context.bot.send_message(chat_id, context.l("request.failed_text"), reply_to_message_id=reply_to_message_id)

      context.logger.error(None, extra=dict(
        action="INSTAGRAM_LINK_FAILED",
        chat_id=chat_id,
        user_id=user_id,
        link=link,
        stack_trace=traceback.format_exc()
      ))

      return

    await Instance.increment_instagram_used(context.instance.id)

    if instagram_post["type"] == "collection":
      await processing_message.delete()

      reply_markup = InstagramCollectionKeyboardMarkup.build(instagram_post["collection"], link_info_id)

      # send the first collection item thumbnail to preview
      await context.bot.send_photo(chat_id, instagram_post["collection"][0]["thumbnail_url"], reply_markup=reply_markup, reply_to_message_id=reply_to_message_id)
    else:
      downloaded_file_path = ""
      try:
        downloaded_file_path = await AsyncFileDownloader.download_file_to_local(instagram_post["download_url"])
        with open(downloaded_file_path, "rb") as fd:

          if instagram_post["type"] == "video":
            reply_markup = InstagramCollectionKeyboardMarkup.get_music_button(link_info_id, user_id)
            await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=fd, thumbnail=instagram_post["thumbnail_url"], supports_streaming=True, reply_markup=reply_markup)
          elif instagram_post["type"] == "photo":
            await advertisement_message_send(context, chat_id, Advertisement.KIND_PHOTO, photo=fd)
      except Exception as e:
        print(f"ERROR INSTAGRAM: {e}")
        await context.bot.send_message(chat_id, context.l("request.failed_text"), reply_to_message_id=reply_to_message_id)

        context.logger.error(None, extra=dict(
          action="INSTAGRAM_LINK_DOWNLOAD_FAILED",
          chat_id=chat_id,
          user_id=user_id,
          link=link,
          stack_trace=traceback.format_exc()
        ))
        return
      finally:
        pathlib.Path(downloaded_file_path).unlink(missing_ok=True)
        await processing_message.delete()


    context.logger.info(None, extra=dict(
      action="INSTAGRAM_LINK",
      chat_id=chat_id,
      user_id=user_id,
      link=link
    ))

    # print(context.instance.instagram_recognize_track_feature_enabled, "CHECK")
    # if context.instance.instagram_recognize_track_feature_enabled and instagram_post["type"] == "video":
    #   try:
    #     recognize_result = await Track.recognize_by_link(instagram_post["download_url"])
    #     if not recognize_result:
    #       return

    #     await track_feature.track_recognize_from_recognize_result(context, chat_id, user_id, recognize_result, reply_to_message_id)

    #     context.logger.error(None, extra=dict(
    #       action="INSTAGRAM_RECOGNIZE_TRACK",
    #       chat_id=chat_id,
    #       user_id=user_id,
    #       link=link
    #     ))
    #   except Exception as ex:
    #     context.logger.error(None, extra=dict(
    #       action="INSTAGRAM_RECOGNIZE_TRACK_FAILED",
    #       chat_id=chat_id,
    #       user_id=user_id,
    #       stack_trace=traceback.format_exc(),
    #       link=link
    #     ))
  finally:
    await ClientManager.delete_client_pending(user_id)
    

async def _instagram_handle_collection_item_download(context: Context, chat_id: int, user_id: int, info_id: str, index: int):
  processing_message = await context.bot.send_message(chat_id, context.l("request.processing_text"))

  info = await MediaService.get_link_info(info_id)
  downloaded_file_path = ""

  try:
    collection_item = info["collection"][index]
    downloaded_file_path = await AsyncFileDownloader.download_file_to_local(collection_item["download_url"])

    with open(downloaded_file_path, "rb") as fd:
      if collection_item["type"] == "video":
        await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=fd)
      elif collection_item["type"] == "photo":
        await advertisement_message_send(context, chat_id, Advertisement.KIND_PHOTO, photo=fd)
  except Exception as ex:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="INSTAGRAM_COLLECTION_ITEM_DOWNLOAD_FAILED",
      chat_id=chat_id,
      user_id=user_id,
      id=info_id,
      stack_trace=traceback.format_exc()
    ))
  finally:
    pathlib.Path(downloaded_file_path).unlink(missing_ok=True)
    await processing_message.delete()


async def instagram_handle_music_button(update: Update, context: Context):
  processing_message = await context.bot.send_message(update.effective_chat.id, context.l("request.processing_text"))

  try:
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")[-1]
    link_info_id, user_id = data.split("-")

    info = await MediaService.get_link_info(link_info_id)
    download_url = info.get("download_url")


    recognize_result = await Track.recognize_by_link(download_url)
    if not recognize_result:
        await context.bot.send_message(update.effective_chat.id, context.l("request.failed_text"))

        # await query.edit_message_caption("🎵 Musiqa topilmadi.")
        return

  
    await track_feature.track_recognize_from_recognize_result(
        context=context,
        chat_id=update.effective_chat.id,
        user_id=int(user_id),
        recognize_result=recognize_result,
        reply_to_message_id=query.message.message_id
    )
  except Exception as e:
    print("INSTAGRAM MUSIC CALLBACK ERROR:", e)
    traceback.print_exc()
    await context.bot.send_message(update.effective_chat.id, context.l("request.failed_text"))

    # await update.effective_message.reply_text("❌ Xatolik yuz berdi.")
  finally:
    await processing_message.delete()



async def instagram_handle_link_message(update: Update, context: Context):
  assert update.effective_message and context.matches and update.effective_chat

  instagram_link = context.matches[0][0]

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, required_join_feature.RequiredJoinKind.MEDIA_QUERY)

  if (context.instance.instagram_quota != -1) and context.instance.instagram_quota <= context.instance.instagram_used:
    raise InstanceQuotaLimitReachedException()

  await _instagram_handle_link(context, instagram_link, update.effective_chat.id, update.effective_chat.id)

async def instagram_handle_collection_item_download_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and update.effective_chat

  await update.callback_query.answer()

  info_id = str(context.matches[0].groups(0)[0])
  index = int(context.matches[0].groups(0)[1])

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, required_join_feature.RequiredJoinKind.MEDIA_DOWNLOAD)

  if (context.instance.instagram_quota != -1) and context.instance.instagram_quota <= context.instance.instagram_used:
    raise InstanceQuotaLimitReachedException()

  await _instagram_handle_collection_item_download(context, update.effective_chat.id, update.effective_user.id, info_id, index)

async def instagram_handle_link_chat_member(update: Update, context: Context, instagram_link: str):
  assert update.chat_member

  await _instagram_handle_link(context, instagram_link, update.chat_member.from_user.id, update.chat_member.from_user.id)

async def instagram_handle_download_collection_item_chat_member(update: Update, context: Context, post_id: str, collection_item: int, advertisement_kind: int):
  assert update.chat_member

  await _instagram_handle_collection_item_download(context, update.chat_member.from_user.id, \
      update.chat_member.from_user.id, post_id, collection_item, advertisement_kind)

async def instagram_handle_username_stories_message(update: Update, context: Context):
  assert update.message and update.message.text and update.effective_chat and update.effective_user

  username = update.message.text.replace("@", "")
  instagram_link = f"https://instagram.com/stories/{username}"

  await _instagram_handle_link(context, instagram_link, update.effective_chat.id, update.effective_user)
