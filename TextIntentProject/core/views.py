#django Imports 
from django.shortcuts import redirect, render
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, StreamingHttpResponse, FileResponse, Http404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import F
from django.utils.html import format_html
UserModel = get_user_model()
from django.db.models import Q


from django.shortcuts import render
from django.views.generic import TemplateView

    
from intents_app.models import TextIntent 
from utils.intents_app.handle_prediction import AiTextIntentPredictionModel
from utils.intents_app.handle_google_sheets import add_text

class HomeView(View):
    template_name = "core/home.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class CheckIntent(View):
    template_name = "core/check_intent.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        texts_list = self.request.POST.get('text_intent').split('\n')
        if len(texts_list) < 0 or len(texts_list) > 100:
            messages.info(request, f'List should be greater than 0 and up to 100')
            return redirect('core:text_intent_method_1')
                
        final_data = []
        for text in texts_list:
            text_data = str(text).lower()
            intent_result = AiTextIntentPredictionModel().getPrediction(text_data)
            final_data.append(intent_result)
        context = {
            'show_result' : True,
            'records': final_data, 
        }
        return render(request, self.template_name, context)
    
    
    
class TextTrainData(LoginRequiredMixin, View):
    template_name = "core/train.html"
    def get(self, request, *args, **kwargs):
        print("====")
        pk_ = kwargs.get('pk', None)
        print("pk_",pk_)
        if pk_:
            text_obj = TextIntent.objects.filter(id=pk_).first()
            print(text_obj)
        else:
            text_obj = TextIntent.objects.filter(intent=TextIntent.TEXT_INTENT.NOTSET).order_by('pk').first()
        if text_obj:
            already_trained = False
            if text_obj.intent in [TextIntent.TEXT_INTENT.INTERESTED_GENERAL, TextIntent.TEXT_INTENT.Neutral]:
                already_trained = True
            pre_guess_intent_result =  AiTextIntentPredictionModel().getOnlyIntent(str(text_obj.text).lower())
            context = {
                'text_obj':text_obj,
                'pre_guess_intent_result':pre_guess_intent_result,
                'previous_post_id': text_obj.id - 1,
                'next_post_id': text_obj.id + 1,
                'already_trained': already_trained
            }
            return render(request, self.template_name, context)
        messages.info(request, 'All texts are trained.')
        return redirect('core:check_intent')
    
    
    def post(self, request, *args, **kwargs):
        current_user = request.user
        text = str(self.request.POST.get('text_intent')).strip()
        text_uid = str(self.request.POST.get('text_uid')).strip()
        intent_options = self.request.POST.get('intent_options')
        object_ = TextIntent.objects.get(uid=text_uid)
        object_.text=text
        object_.intent=intent_options
        object_.is_approved=True
        if intent_options == 'opt_out':
            object_.intent = "skiped"
            object_.is_approved = False
            add_text(text)
        # if current_user.is_superuser:
        object_.save()            
        messages.info(request, 'Text has been Trained and saved into Database')
        return redirect('core:text_train_data')
    
    

