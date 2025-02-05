import logging
from telegram import InputMediaAnimation, InputMediaPhoto, Update
from telegram.ext import ContextTypes

async def media_handler(update: Update,  context:ContextTypes.DEFAULT_TYPE, text, query=None, reply_markup=None, file_id=None):
    try:
        
        if file_id:
            info = await context.bot.getFile(file_id)
            if info.file_path.__contains__('animation') == True:
                file = 'animation'
            elif info.file_path.__contains__('photo') == True:
                file = 'photo'

            if file == 'animation':
                if query:
                    media = InputMediaAnimation(
                            media=file_id,  
                            caption=text,
                            parse_mode="MarkdownV2"
                    )
                    if reply_markup:
                        await query.edit_message_media(
                                media=media,
                                reply_markup=reply_markup,
                            )
                    else:
                        await query.edit_message_media(
                                media=media,
                            )
                    await query.answer()
                    return
                else:
                    if reply_markup:
                        await context.bot.sendAnimation(
                            chat_id=update.effective_chat.id,
                            animation=file_id,
                            caption=text,
                            reply_markup=reply_markup,
                            parse_mode="MarkdownV2"
                            )
                    else:
                        await context.bot.sendAnimation(
                        chat_id=update.effective_chat.id,
                        animation=file_id,
                        caption=text,
                        parse_mode="MarkdownV2"
                        )
            elif file == 'photo':
                if query:
                    media=InputMediaPhoto(
                            media=file_id,
                            caption=text,
                            parse_mode="MarkdownV2"
                    )
                    if reply_markup:
                        await query.edit_message_media(
                            media=media,
                            reply_markup=reply_markup
                        )
                    else:
                        await query.edit_message_media(
                            media=media
                        )
                    await query.answer()
                    return
                else:
                    if reply_markup:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=file_id,
                            caption=text,
                            reply_markup=reply_markup,
                            parse_mode="MarkdownV2"
                            )
                    else:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=file_id,
                            caption=text,
                            parse_mode="MarkdownV2"
                            )
        else:
            if query:
                if reply_markup:
                    await query.edit_message_text(
                            text=text,
                            reply_markup=reply_markup,
                        )
                else:
                    await query.edit_message_text(
                            text=text,
                        )
                await query.answer()
                return
            else:
                if reply_markup:
                    await context.bot.sendMessage(
                        chat_id=update.effective_chat.id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode="MarkdownV2"
                        )
                else:
                    await context.bot.sendMessage(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode="MarkdownV2"
                    )
    except Exception as e:
        logging.error(f"Error handling media: {e}")


async def get_profile_file_id(update):
    photos = await update.effective_user.get_profile_photos()
    return photos['photos'][0][1]['file_id']