from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from django.db.models import JSONField 
from django.forms import widgets
from import_export.admin import ImportExportModelAdmin

from pdf_app.models import PDFFile


    
class PrettyJSONWidget(widgets.Textarea):
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=4, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            return super(PrettyJSONWidget, self).format_value(value)


class CustomDataFilter(admin.SimpleListFilter):
    title = 'Data Generated'
    parameter_name = 'data'
    
    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),('no', 'No'),)
        
    def queryset(self, request, queryset):
        if self.value() == 'yes': return queryset.exclude(data={})
        elif self.value() == 'no': return queryset.filter(data={})
        return queryset

    
@admin.register(PDFFile)
class PDFFileAdmin(ImportExportModelAdmin):
    
    @admin.display(description='Data Generated', boolean=True)
    def data_generated(self, obj):
        if obj.data:
            return True
        return False
    
    @admin.action(description='PDF File')
    def handle_pdffile(self, obj):
        download_url = obj.pdffile.url
        return mark_safe(f"<a target='_blank' href='{download_url}'>Preview/Download</a>")
    
    
    list_display = ('uid', 'user_email', 'pdffile_name', 'data_generated', 'updated', 'handle_pdffile',)
    list_per_page = 100
    search_fields  = ['user_email', 'uid', 'pdffile_name', ]
    readonly_fields = ('created', 'updated',)
    empty_value_display  = '-'
    list_filter = (CustomDataFilter, )


#     formfield_overrides = {
#         JSONField: {'widget': PrettyJSONWidget}
#     }