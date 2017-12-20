# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from django_telegrambot.apps import DjangoTelegramBot
from . models import Groups, Subscribers, SubscribersInGroups, WelcomeText, PhotoMessages, TextMessages
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.utils.timezone import localtime, now, timedelta
from .tasks import TIMEOUT
import time
from django.contrib.auth import authenticate
from . tasks import send_message

logger = logging.getLogger(__name__)

BUTTONS_IN_ROW = 2
TEXT_FOR_SUBSCRIBE = 'Выберите группу для подписки, или нажмите Отмена, чтобы завершить процесс'
TEXT_FOR_UNSUBSCRIBE = 'Выберите группу от которой хотите отписаться, или нажмите Отмена, чтобы завершить процесс'
TEXT_NO_MORE_TO_SUBSCRIBE = 'Больше нет групп для подписки'
TEXT_NO_MORE_TO_UNSUBSCRIBE = 'Больше нет групп, от которых Вы можете отписаться'
TEXT_CANCEL_LAST_OPERATION = 'Операция завершена'
TEXT_CANT_FIND_GROUP = 'Не могу найти данную группу'
SAD_EMOJI = '😣'
TEXT_STAFF_LOGIN_SUCCESS = 'Вы успешно вошли, и можете создавать ' \
                           'текстовые рассылки с помощью кнопки "Новая рассылка".'
TEXT_STAFF_LOGIN_ERROR = 'В доступе отказано: введен неверный логин или пароль.'

MAILING_GROUP = {}

main_keyboard = [
    [KeyboardButton("Подписаться"), KeyboardButton("Отписаться")],
    [KeyboardButton("Список групп для подписки")],
    [KeyboardButton("Мои подписки")],
    [KeyboardButton("Расписание занятий")],
    [KeyboardButton("Отменить все подписки и покинуть нас")]
]

staff_keyboard = [
    [KeyboardButton("Новая рассылка")],
    [KeyboardButton("Подписаться"), KeyboardButton("Отписаться")],
    [KeyboardButton("Список групп для подписки")],
    [KeyboardButton("Мои подписки")],
    [KeyboardButton("Расписание занятий")],
    [KeyboardButton("Отменить все подписки и покинуть нас")]
]

main_reply_markup = ReplyKeyboardMarkup(main_keyboard)
staff_reply_markup = ReplyKeyboardMarkup(staff_keyboard)

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
        # Получаем и отправляем подписчику все текущие акции
        current_offers = PhotoMessages.objects.filter(expiration_date__gte=localtime(now()))
        if current_offers:
            for offer in current_offers:
                time.sleep(TIMEOUT)
                update.message.reply_photo(photo=offer.image,
                                           caption=offer.text,
                                           reply_markup=main_reply_markup)
        time.sleep(TIMEOUT)
        bot.sendMessage(472186134, 'Новый подписчик: {}'.format(name))


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


def _is_staff(subscriber):
    return subscriber.exp_date_staff and subscriber.exp_date_staff > localtime(now())


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
            update.message.reply_text(
                TEXT_NO_MORE_TO_SUBSCRIBE,
                reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)


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
            update.message.reply_text(
                TEXT_NO_MORE_TO_UNSUBSCRIBE,
                reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)


def card(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        update.message.reply_text(
            '*Ваша карта действительна до:*\n'
            '_31 января 2018г._',
            parse_mode='Markdown',
            reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)


def groups_list(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        groups = Groups.objects.exclude(is_default=True)
        groups_text = '*Список групп для подписки:*\n'
        for count, group in enumerate(groups, 1):
            groups_text += '_{}. {} - {}_\n'.format(count, group.name, group.description)
        update.message.reply_text(
            groups_text,
            parse_mode='Markdown',
            reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)


def get_my_subscribes(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        subscribes_list = [group.group.name for group in subscriber.groups.all()]
        subscribes_list_text = ''
        for group_name in subscribes_list:
            subscribes_list_text += '- {}\n'.format(group_name)
        update.message.reply_text(
            '*Вы подписаны на рассылки:*\n'
            '_{}_'.format(subscribes_list_text),
            parse_mode='Markdown',
            reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup
        )


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')
    bot.sendMessage()


def timetable(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        timetable_text = ''
        for group in Groups.objects.exclude(is_default=True):
            if group.timetable:
                timetable_text += '*{}*\n_{}_\n'.format(group.name, group.timetable)
        if timetable_text:
            update.message.reply_text(
                timetable_text,
                parse_mode='Markdown',
                reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)
        else:
            update.message.reply_text(
                'На данный момент расписание недоступно.',
                parse_mode='Markdown',
                reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)


def login(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        if _is_staff(subscriber):
            update.message.reply_text(TEXT_STAFF_LOGIN_SUCCESS,
                                      reply_markup=staff_reply_markup)
        else:
            subscriber.subscribing_status = 'login'
            subscriber.save()
            update.message.reply_text('Введите Ваш логин и пароль через пробел')


def get_mailing_group(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        if _is_staff(subscriber):
            groups = [group.name for group in Groups.objects.all()]
            buttons = [KeyboardButton(group_name) for group_name in groups]
            keyboard = [buttons[d:d + BUTTONS_IN_ROW] for d in range(0, len(buttons), BUTTONS_IN_ROW)]
            keyboard.append([KeyboardButton('Отмена')])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text('Выберите группу для рассылки:', reply_markup=reply_markup)
            subscriber.subscribing_status = 'get_mailing_group'
            subscriber.save()
        else:
            update.message.reply_text(
                'У Вас нет доступа. Пожалуйста, авторизуйтесь, используя команду: _/login_',
                parse_mode='Markdown',
                reply_markup=main_reply_markup)


def get_mailing_text(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        if _is_staff(subscriber):
            MAILING_GROUP[update.message.chat_id] = update.message.text
            keyboard = [
                [KeyboardButton("Отмена")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            update.message.reply_text(
                'Наберите текст рассылки и отправьте, '
                'или нажмите "Отмена"',
                reply_markup=reply_markup, resize_keyboard=True)
            subscriber.subscribing_status = 'get_mailing_text'
            subscriber.save()
        else:
            update.message.reply_text(
                'У Вас нет доступа. Пожалуйста, авторизуйтесь, используя команду: /login',
                reply_markup=main_reply_markup)


def send_mailing(bot, update):
    subscriber = _check_subscriber_exists(update)
    if subscriber:
        subscriber.subscribing_status = None
        subscriber.save()
        if _is_staff(subscriber):
            group_name = MAILING_GROUP.get(update.message.chat_id, None)
            if group_name:
                try:
                    group = Groups.objects.get(name=group_name)
                    if update.message.text:
                        message = TextMessages.objects.create(group=group, text=update.message.text)
                        update.message.reply_text(
                            'Сообщение отправлено в очередь на рассылку',
                            reply_markup=staff_reply_markup)
                        send_message.delay(text_message=message.id)
                    else:
                        del MAILING_GROUP[update.message.chat_id]
                        update.message.reply_text(
                            TEXT_CANCEL_LAST_OPERATION,
                            reply_markup=staff_reply_markup)
                except ObjectDoesNotExist:
                    update.message.reply_text(
                        'Ошибка: группа не существует, возможно ее удалили',
                        reply_markup=staff_reply_markup)
            else:
                update.message.reply_text(
                    'Ошибка: группа не была выбрана',
                    reply_markup=staff_reply_markup)


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
            elif update.message.text == 'Новая рассылка':
                get_mailing_group(bot, update)
            else:
                update.message.reply_text(
                    'Извините, я не знаю такой команды: "{}"\n{}'.format(update.message.text,
                                                                         SAD_EMOJI))
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
                    update.message.reply_text(
                        TEXT_CANCEL_LAST_OPERATION,
                        reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)
                else:
                    update.message.reply_text(TEXT_CANT_FIND_GROUP + ': ' + update.message.text)
                    add(bot, update)
            elif subscriber.subscribing_status == 'unsub':
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
                    update.message.reply_text(
                        TEXT_CANCEL_LAST_OPERATION,
                        reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)
                else:
                    update.message.reply_text(TEXT_CANT_FIND_GROUP + ': ' + update.message.text)
                    delete(bot, update)
            elif subscriber.subscribing_status == 'login':
                user_login, user_pass = update.message.text.split(' ')
                staff_user = authenticate(username=user_login, password=user_pass)
                subscriber.subscribing_status = None
                if not staff_user:
                    update.message.reply_text(TEXT_STAFF_LOGIN_ERROR, reply_markup=main_reply_markup)
                else:
                    subscriber.exp_date_staff = localtime(now() + timedelta(1))
                    update.message.reply_text(TEXT_STAFF_LOGIN_SUCCESS, reply_markup=staff_reply_markup)
                subscriber.save()
            elif subscriber.subscribing_status == 'get_mailing_group':
                if update.message.text in [group.name for group in Groups.objects.all()]:
                    get_mailing_text(bot, update)
                elif update.message.text == 'Отмена':
                    subscriber.subscribing_status = None
                    subscriber.save()
                    update.message.reply_text(
                        TEXT_CANCEL_LAST_OPERATION,
                        reply_markup=staff_reply_markup if _is_staff(subscriber) else main_reply_markup)
                else:
                    update.message.reply_text(TEXT_CANT_FIND_GROUP + ': ' + update.message.text)
                    get_mailing_group(bot, update)
            elif subscriber.subscribing_status == 'get_mailing_text':
                send_mailing(bot, update)



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
    dp.add_handler(CommandHandler("login", login))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text))

    # log all errors
    dp.add_error_handler(error)
