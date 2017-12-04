from django.contrib import admin
from . models import Groups, TextMessages, PhotoMessages, WelcomeText
from django.utils.html import format_html
from . tasks import send_message
from django.contrib import messages

import logging
logger = logging.getLogger(__name__)


@admin.register(WelcomeText)
class WelcomeTextAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        perm = super().has_add_permission(request)
        return True if perm and not len(self.get_queryset(request)) else False


@admin.register(Groups)
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


@admin.register(PhotoMessages)
class PhotoMessagesAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'group', 'image_tag', 'text', 'created', 'status')
    fields = ('group', ('image', 'image_tag'), 'text')
    readonly_fields = ('image_tag',)
    actions = ['send_messages']
    list_display_links = ('get_id', 'group')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />'.format(obj.image.url))
    image_tag.short_description = 'Картинка'

    def get_id(self, obj):
        return obj.id
    get_id.short_description = '№'

    def send_messages(self, request, queryset):
        for message in queryset:
            if not message.status:
                self.message_user(request, '{} отправлено в очередь на рассылку'.format(message))
                send_message.delay(photo_message=message)
            else:
                self.message_user(request, '{} уже было отправлено ранее'.format(message),
                                  level=messages.WARNING)
    send_messages.short_description = 'Отправить сообщения'


@admin.register(TextMessages)
class TextMessagesAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'group', 'text', 'created', 'status')
    fields = ('group', 'text')
    actions = ['send_messages']
    list_display_links = ('get_id', 'group')

    def get_id(self, obj):
        return obj.id
    get_id.short_description = '№'

    def send_messages(self, request, queryset):
        for message in queryset:
            if not message.status:
                self.message_user(request, '{} отправлено в очередь на рассылку'.format(message))
                send_message.delay(photo_message=message)
            else:
                self.message_user(request, '{} уже было отправлено ранее'.format(message),
                                  level=messages.WARNING)
    send_messages.short_description = 'Отправить сообщения'