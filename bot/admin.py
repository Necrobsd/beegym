from django.contrib import admin
from . models import Groups, Messages
from django.utils.html import format_html
from django_telegrambot.apps import DjangoTelegramBot
from django.conf import settings
from django.contrib import messages
from telegram.error import TelegramError
import time
import logging
logger = logging.getLogger(__name__)


class GroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subscribers_number', 'is_default')
    su_list_editable = ('is_default', )
    non_su_readonly_fields = ('is_default', )

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            self.list_editable = self.su_list_editable
            self.readonly_fields = []
        else:
            self.list_editable = []
            self.readonly_fields = self.non_su_readonly_fields
        return super(GroupsAdmin, self).get_form(request, obj=None, **kwargs)

    def subscribers_number(self, obj):
        return len(obj.subscribers.all())

    subscribers_number.short_description = 'Количество подписчиков'

admin.site.register(Groups, GroupsAdmin)


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'group', 'image_tag', 'text', 'created', 'status')
    fields = ('group', ('image', 'image_tag'), 'text')
    readonly_fields = ('image_tag',)
    actions = ['send_messages']
    list_display_links = ('get_id', 'group')

    def has_add_permission(self, request):
        perm = super().has_add_permission(request)
        return True if perm and len(self.get_queryset(request)) < 5 else False

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />'.format(obj.image.url))
    image_tag.short_description = 'Картинка'

    def get_id(self, obj):
        return obj.id
    get_id.short_description = '№'

    def send_messages(self, request, queryset):
        dp = DjangoTelegramBot.dispatcher
        for message in queryset:
            if not message.status:
                self.message_user(request, '{} отправлено в очередь на рассылку'.format(message))
                if message.image:
                    image_url = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_SITE') + message.image.url
                    print('IMAGE_URL=', image_url)
                    for counter, subscriber in enumerate(message.group.subscribers.all()):
                        time.sleep(1/30)
                        if not counter:
                            try:
                                response = dp.bot.sendPhoto(
                                    subscriber.subscriber.chat_id,
                                    # 472186134,
                                    photo=image_url,
                                    caption=message.text)
                                print(response)
                                file_id = response.photo[-1].file_id
                            except TelegramError as error:
                                print(error.message)
                        else:
                            dp.bot.sendPhoto(
                                subscriber.subscriber.chat_id,
                                # 472186134,
                                photo=file_id if file_id else image_url,
                                caption=message.text)
                else:
                    for subscriber in message.group.subscribers.all():
                        time.sleep(1/30)
                        try:
                            response = dp.bot.sendMessage(
                                subscriber.subscriber.chat_id,
                                # 472186134,
                                message.text)
                            print(response)
                        except TelegramError as error:
                            print(error.message)
                message.status = True
                message.save()
            else:
                self.message_user(request, '{} уже было отправлено ранее'.format(message),
                                  level=messages.WARNING)
    send_messages.short_description = 'Отправить сообщения'


admin.site.register(Messages, MessagesAdmin)
