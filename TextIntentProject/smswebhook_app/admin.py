from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


from .models import (
    SmsWebhookData,
)
        

    
@admin.register(SmsWebhookData)
class SmsWebhookDataAdmin(ImportExportModelAdmin):
    list_display = ('from_number', 'msg_text',  'carrier', 'added',)
    list_filter = ('carrier',)
    list_per_page = 100
