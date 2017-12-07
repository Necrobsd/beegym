# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from django_telegrambot.apps import DjangoTelegramBot
from . models import Groups, Subscribers, SubscribersInGroups, WelcomeText
from django.core.exceptions import ObjectDoesNotExist
import logging
logger = logging.getLogger(__name__)

BUTTONS_IN_ROW = 2
TEXT_FOR_SUBSCRIBE = 'Выберите группу для подписки, или нажмите Отмена, чтобы завершить процесс'
TEXT_FOR_UNSUBSCRIBE = 'Выберите группу от которой хотите отписаться, или нажмите Отмена, чтобы завершить процесс'
TEXT_NO_MORE_TO_SUBSCRIBE = 'Больше нет групп для подписки'
TEXT_NO_MORE_TO_UNSUBSCRIBE = 'Больше нет групп, от которых Вы можете отписаться'
TEXT_CANCEL_LAST_OPERATION = 'Операция завершена'
TEXT_CANT_FIND_GROUP = 'Не могу найти данную группу'

main_keyboard = [
    [KeyboardButton("Подписаться"), KeyboardButton("Отписаться")],
    [KeyboardButton("Список групп для подписки")],
    [KeyboardButton("Мои подписки")],
    [KeyboardButton("Расписание занятий")],
    [KeyboardButton("Отменить все подписки и покинуть нас")]
]

main_reply_markup = ReplyKeyboardMarkup(main_keyboard)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def start(bot, update):
    try:
        subscriber = Subscribers.objects.get(chat_id=update.message.chat_id)
        update.message.reply_text('Рады снова Вас видеть! Выберите действие:', reply_markup=main_reply_markup)
    except ObjectDoesNotExist:
        name = update.effective_user.first_name
        if update.effective_user.last_name:
            name += ' {}'.format(update.effective_user.last_name)
        subscriber = Subscribers.objects.create(chat_id=update.message.chat_id, name=name)
        try:
            default_group = Groups.objects.get(is_default=True)
            subscriber.groups.create(group=default_group)
        except ObjectDoesNotExist:
            pass
        try:
            welcome = WelcomeText.objects.last().text
        except:
            welcome = 'Добро пожаловать!'
        update.message.reply_text(welcome, reply_markup=main_reply_markup)


def stop(bot, update):
    subscriber = Subscribers.objects.get(chat_id=update.message.chat_id)
    subscriber.delete()
    update.message.reply_text('*Спасибо что были с нами!*\n'
                              'Все Ваши подписки удалены.\n'
                              'До новых встреч!', parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())


def _check_subscriber_exists(update):
    try:
        subscriber = Subscribers.objects.get(chat_id=update.message.chat_id)
        return subscriber
    except ObjectDoesNotExist:
        update.message.reply_text('*Вы не подписаны*\n'
                                  'Для начала работы отправьте:\n'
                                  '_/start_',
                                  parse_mode='Markdown')
        return None


def _get_groups_for_subscribe(update):
    subscriber = Subscribers.objects.get(chat_id=update.message.chat_id)
    current_groups_ids = [group.group.id for group in subscriber.groups.all()]
    groups_for_subscribe = [group.name for group in Groups.objects.exclude(id__in=current_groups_ids)]
    return groups_for_subscribe


def _get_groups_for_unsibscribe(update):
    subscriber = Subscribers.objects.get(chat_id=update.message.chat_id)
    current_groups = [group.group.name for group in subscriber.groups.exclude(group__is_default=True)]
    return current_groups


def add(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        groups_for_subscribe = _get_groups_for_subscribe(update)
        if groups_for_subscribe:
            buttons = [KeyboardButton(group_name) for group_name in groups_for_subscribe]
            keyboard = [buttons[d:d + BUTTONS_IN_ROW] for d in range(0, len(buttons), BUTTONS_IN_ROW)]
            keyboard.append([KeyboardButton('Отмена')])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text(TEXT_FOR_SUBSCRIBE, reply_markup=reply_markup)
            subscriber.subscribing_status = 'sub'
            subscriber.save()
        else:
            subscriber.subscribing_status = None
            subscriber.save()
            update.message.reply_text(TEXT_NO_MORE_TO_SUBSCRIBE, reply_markup=main_reply_markup)


def delete(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        current_groups = _get_groups_for_unsibscribe(update)
        if current_groups:
            buttons = [KeyboardButton(group_name) for group_name in current_groups]
            keyboard = [buttons[d:d+BUTTONS_IN_ROW] for d in range(0, len(buttons), BUTTONS_IN_ROW)]
            keyboard.append([KeyboardButton('Отмена')])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text(TEXT_FOR_UNSUBSCRIBE, reply_markup=reply_markup)
            subscriber.subscribing_status = 'unsub'
            subscriber.save()
        else:
            subscriber.subscribing_status = None
            subscriber.save()
            update.message.reply_text(TEXT_NO_MORE_TO_UNSUBSCRIBE, reply_markup=main_reply_markup)


def card(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        update.message.reply_text('*Ваша карта действительна до:*\n'
                                  '_31 января 2018г._',
                                  parse_mode='Markdown',
                                  reply_markup=main_reply_markup)


def groups_list(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        groups = Groups.objects.exclude(is_default=True)
        groups_text = '*Список групп для подписки:*\n'
        for count, group in enumerate(groups, 1):
            groups_text += '_{}. {} - {}_\n'.format(count, group.name, group.description)
        update.message.reply_text(groups_text,
                                  parse_mode='Markdown',
                                  reply_markup=main_reply_markup)


def get_my_subscribes(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        subscribes_list = [group.group.name for group in subscriber.groups.all()]
        subscribes_list_text = ''
        for group_name in subscribes_list:
            subscribes_list_text += '- {}\n'.format(group_name)
        bot.sendMessage(update.message.chat_id,
                        text='*Вы подписаны на рассылки:*\n'
                             '_{}_'.format(subscribes_list_text),
                        parse_mode='Markdown')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')
    bot.sendMessage()


def timetable(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        timetable_text = ''
        for group in subscriber.groups.all():
            if not group.group.is_default and group.group.timetable:
                timetable_text += '*{}*\n_{}_\n'.format(group.group.name, group.group.timetable)
        update.message.reply_text(timetable_text,
                                  parse_mode='Markdown',
                                  reply_markup=main_reply_markup)


def text(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        if not subscriber.subscribing_status:
            if update.message.text == 'Подписаться':
                add(bot, update)
            elif update.message.text == 'Отписаться':
                delete(bot, update)
            elif update.message.text == 'Список групп для подписки':
                groups_list(bot, update)
            elif update.message.text == 'Мои подписки':
                get_my_subscribes(bot, update)
            elif update.message.text == 'Срок действия карты':
                card(bot, update)
            elif update.message.text == 'Расписание занятий':
                timetable(bot, update)
            elif update.message.text == 'Отменить все подписки и покинуть нас':
                stop(bot, update)
            else:
                update.message.reply_text(':confused: Извините, я не знаю такой команды: ' + update.message.text)
                update.message.reply_text('Выберите действие:', reply_markup=main_reply_markup)
        else:
            if subscriber.subscribing_status == 'sub':
                if update.message.text in _get_groups_for_subscribe(update):
                    SubscribersInGroups.objects.create(subscriber=subscriber,
                                                       group=Groups.objects.get(name=update.message.text))
                    update.message.reply_text('Вы успешно подписались на группу *{}*'.format(update.message.text),
                                              parse_mode='Markdown')
                    add(bot, update)

                elif update.message.text in _get_groups_for_unsibscribe(update):
                    update.message.reply_text('*Ошибка при подписке*\n'
                                              '_Вы уже подписаны на группу {}_'.format(update.message.text),
                                              parse_mode='Markdown', reply_markup=main_reply_markup)
                    add(bot, update)
                elif update.message.text == 'Отмена':
                    subscriber.subscribing_status = None
                    subscriber.save()
                    update.message.reply_text(TEXT_CANCEL_LAST_OPERATION, reply_markup=main_reply_markup)
                else:
                    update.message.reply_text(TEXT_CANT_FIND_GROUP + ': ' + update.message.text)
                    add(bot, update)
            if subscriber.subscribing_status == 'unsub':
                if update.message.text in _get_groups_for_unsibscribe(update):
                    obj = SubscribersInGroups.objects.get(subscriber=subscriber,
                                                          group=Groups.objects.get(name=update.message.text))
                    obj.delete()
                    update.message.reply_text('Вы успешно отписались от группы *{}*'.format(update.message.text),
                                              parse_mode='Markdown')
                    delete(bot, update)
                elif update.message.text in _get_groups_for_subscribe(update):
                    update.message.reply_text('*Ошибка при отписке:*\n'
                                              '_Вы не подписаны на группу {}_'.format(update.message.text),
                                              parse_mode='Markdown')
                    delete(bot, update)
                elif update.message.text == 'Отмена':
                    subscriber.subscribing_status = None
                    subscriber.save()
                    update.message.reply_text(TEXT_CANCEL_LAST_OPERATION, reply_markup=main_reply_markup)
                else:
                    update.message.reply_text(TEXT_CANT_FIND_GROUP + ': ' + update.message.text)
                    delete(bot, update)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.TELEGRAM_BOT_TOKENS)
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("card", card))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("me", get_my_subscribes))
    dp.add_handler(CommandHandler("list", groups_list))
    dp.add_handler(CommandHandler("timetable", timetable))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text))

    # log all errors
    dp.add_error_handler(error)
