from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count
from django.urls import path
from django.http import HttpResponseRedirect
from utils.intents_app.handle_prediction import AiTextIntentPredictionModel


from .models import (
    TextIntent, 
    TrainModel,
    OptoutTexts,
    TestTextIntents,
)

from django.db.models import Count

class CustomIntentFilter(admin.SimpleListFilter):
    title = 'Intent'
    parameter_name = 'intent'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        for lang in qs.values_list('intent', flat=True).distinct().order_by():
            count = qs.filter(intent=lang).count()
            if count:
                yield (lang, f'{lang} ({count})')
                
    def queryset(self, request, queryset):
        lang = self.value()
        if lang:
            return queryset.filter(intent=lang)
        
class CustomApprovalFilter(admin.SimpleListFilter):
    title = 'is_approved'
    parameter_name = 'is_approved'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        for lang in qs.values_list('is_approved', flat=True).distinct().order_by():
            count = qs.filter(is_approved=lang).count()
            if count:
                yield (lang, f'{lang} ({count})')
                
    def queryset(self, request, queryset):
        lang = self.value()
        if lang:
            return queryset.filter(is_approved=lang)
          
        
@admin.register(TextIntent)
class TextIntentAdmin(ImportExportModelAdmin):
    change_list_template = "intents_app/admin/textintent_change_list.html"
     
    def changelist_view(self, request, extra_context=None):
        gchart_intent_info = [['', '']]
        intent_infos = self.get_queryset(request).values('intent').annotate(count=Count('id')).order_by()
        for intentinfo in intent_infos:
            gchart_intent_info.append([intentinfo['intent'], intentinfo['count']])

        gchart_approval_info = [['', '']]
        approval_infos = self.get_queryset(request).values('is_approved').annotate(count=Count('id')).order_by()
        for approvalinfo in approval_infos:
            gchart_approval_info.append([f"{approvalinfo['is_approved']}", approvalinfo['count']])

        extra = {
                "gchart_intent_infos": gchart_intent_info,
                "gchart_approval_info": gchart_approval_info
            }
        extra.update(extra_context or {})
        
        return super(TextIntentAdmin, self).changelist_view(request, extra_context=extra)
    
    @admin.action(description='Guess Intent')
    def pre_guess_intent(self, obj):
        if obj.intent == 'not_set':
            guess_intent =  AiTextIntentPredictionModel().getOnlyIntent(str(obj.text))
            return guess_intent
        return obj.intent
    
    list_display = ('short_text', 'intent', 'is_approved', 'created', 'updated', )
    list_filter = (CustomIntentFilter, CustomApprovalFilter,  )
    list_per_page = 100
    search_fields  = ['text', 'clean_text','uid', ]
    readonly_fields = ('uid', 'clean_text', 'pre_guess_intent', 'created', 'updated', )
    date_hierarchy = 'updated'


@admin.register(TrainModel)
class TrainModelAdmin(admin.ModelAdmin):
    change_list_template = "intents_app/admin/trainmodel_change_list.html"

    def changelist_view(self, request, extra_context=None):
        gchart_model_data = [['DateTime', 'SK Accuracy', 'TF Accuracy']] #, 'TF Loss'
        qs =  self.get_queryset(request).filter(model_status='trained').order_by('-created')[:15]
        for obj in qs:
            datetime = obj.updated.strftime('%Y-%m-%d %H:%M')
            sk_accuracy = round(obj.model_info['sk_accuracy'] * 100, 2)
            tf_accuracy = round(obj.model_info['tf_accuracy'] * 100, 2)
            tf_loss = round(obj.model_info['tf_loss'] * 100, 2)
            gchart_model_data.append([datetime, sk_accuracy, tf_accuracy ])

        extra = {
               "gchart_model_data":gchart_model_data
            }
        extra.update(extra_context or {})
        return super(TrainModelAdmin, self).changelist_view(request, extra_context=extra)
    


    list_display = ('uid', 'active', 'model_status', 'train_on', 'created', 'updated', )
    readonly_fields = ('uid', 'model_status', 'created', 'updated', )
    list_filter = ('model_status', 'train_on', 'active', )
    exclude = ('model_info',)


@admin.register(OptoutTexts)
class OptoutTextsAdmin(ImportExportModelAdmin): 
    change_list_template = "intents_app/admin/optouttexts_change_list.html"
    
    def changelist_view(self, request, extra_context=None):
        gchart_intents_labels_count = [['', '']]
        filter_infos = self.get_queryset(request).values('filter_type').annotate(count=Count('id')).order_by()
        for intentinfo in filter_infos:
            gchart_intents_labels_count.append([intentinfo['filter_type'], intentinfo['count'] ])
        extra = {
                "gchart_filter_info": gchart_intents_labels_count,
            }
        extra.update(extra_context or {})
        return super(OptoutTextsAdmin, self).changelist_view(request, extra_context=extra)
    
    list_display = ('text', 'filter_type',  'status', 'clean_text', 'updated', )
    list_filter = ('status', 'filter_type',)
    search_fields = ('text',)
    readonly_fields = ('uid', 'clean_text','created', 'updated',)
    



@admin.register(TestTextIntents)
class TestTextIntentsAdmin(ImportExportModelAdmin):
    change_list_template = "intents_app/admin/testtextintents_change_list.html"
    
    def changelist_view(self, request, extra_context=None):
        match = self.get_queryset(request).filter(intent_match=True).count()
        unmatch = self.get_queryset(request).filter(intent_match=False).count()
        gchart_match_unmatch_data = [['', ''], ['Match', match], ['Un-Match ',unmatch],]
        intents_info = self.get_queryset(request).values('intent').annotate(count=Count('id')).order_by()
        gchart_intents_labels_count = [['', '']]
        for intentinfo in intents_info:
            gchart_intents_labels_count.append([intentinfo['intent'],intentinfo['count'] ])
        extra = {
                "gchart_match_unmatch_data": gchart_match_unmatch_data,
                "gchart_intents_labels_count": gchart_intents_labels_count,
            }
        extra.update(extra_context or {})
        return super(TestTextIntentsAdmin, self).changelist_view(request, extra_context=extra)
    
    
    def update_all_intents(self, request):
        for obj in self.model.objects.all(): obj.save()
        self.message_user(request, "All Guess Intents are updated")
        return HttpResponseRedirect("../")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update-guess-intents/', self.update_all_intents, name="custom_admin_update_guess_intents"),
        ]
        return my_urls + urls
    
    
    list_display = ('short_text', 'intent', 'guess_intent', 'intent_match', 'created', 'updated', )
    list_per_page = 500
    search_fields  = ['text', ]
    readonly_fields = ('guess_intent', 'intent_match', 'created', 'updated', )
