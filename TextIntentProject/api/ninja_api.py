# from ninja import NinjaAPI
# from ninja.errors import HttpError
# api = NinjaAPI()

# from django.db.models import Q
# from django.http.response import JsonResponse
# from django.conf import settings

# from intents_app.models import OptoutTexts, TextIntent
# from pdf_app.models import PDFFile

# from utils.utils import is_valid_uuid
# from utils.pdf_app.handle_pdf import AIPDF
# from utils.intents_app.handle_prediction import AiTextIntentPredictionModel
# GLOBAL_TOKEN = settings.GLOBAL_TOKEN


# FAILED_EXCEPTION_MESSAGE = "something went wrong, please check your request data and try again."
# FAILED_AUTHORIZED_MESSAGE = "You are not Authorized."


# @api.get('/pingsite/')
# def ping_site(request):
#     return JsonResponse({}, status=200)

    
# @api.post("/get-intent/")
# def get_intent(request):
#     if GLOBAL_TOKEN != request.headers.get('Authorization'):
#         return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE }, status=400)
#     try:
#         body_data = request.POST.dict()
#         clean_text = body_data['text'] 
#         intent_result = AiTextIntentPredictionModel().getPrediction(clean_text)
#         return JsonResponse({"result": intent_result}, status=200)
#     except:
#         return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)



# @api.post("/train-text/")
# def add_text_for_training(request):
#     if GLOBAL_TOKEN != request.headers.get('Authorization'):
#         return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    
#     try:
#         intent_choices = [_.value for _ in TextIntent.TEXT_INTENT] + ['opt_out']
#         body_data = request.POST.dict()
#         text = body_data['text'].strip().lower()
#         optout_filtertype = body_data['optout_filtertype'].strip().lower()
#         intent_ = body_data['intent'].strip().lower()
#         status = body_data['status']
        
#         if intent_ not in intent_choices:
#             return JsonResponse({"error": f"intent choices are: {intent_choices}"}, status=400)
        
#         if optout_filtertype not in ['exact', 'contains']:
#             return JsonResponse({"error": f"optout_filtertype choices are: {['exact', 'contains']}"}, status=400)
        
#         if intent_ == 'opt_out':
#             obj, created = OptoutTexts.objects.get_or_create(text=text, filter_type=optout_filtertype, status=status)
#             if created:
#                 return JsonResponse({"result": "added successfully!"}, status=200)
#             return JsonResponse({"result": "already exist!"}, status=200)
#         else:
#             obj, created = TextIntent.objects.get_or_create(text=text, intent=intent_, is_approved=status)
#             if created:
#                 return JsonResponse({"result": "added successfully!"}, status=200)
#             return JsonResponse({"result": "already exist!"}, status=200)
#     except:
#         return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)



# @api.post("/render-pdf/")
# def render_pdf(request):
#     if GLOBAL_TOKEN != request.headers.get('Authorization'):
#         return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    
#     try:
#         pdffile = request.FILES['pdffile']
#     except:
#         raise HttpError(400, "Invalid Keyname, keep 'pdffile'")
    
    
#     if not (pdffile.name).endswith('.pdf'): 
#         raise HttpError(400, "'only pdf files are allowed")
    
#     body_data = request.POST.dict()
#     user_email = body_data['email'].strip().lower()
    
#     try:
#         pdf_obj = PDFFile.objects.create(
#             user_email = user_email,
#             pdffile = pdffile,
#             pdffile_name = pdffile.name,
#         )
#         data = AIPDF().returnPDFData(pdf_obj.pdffile.url)
#         data['result_id'] = str(pdf_obj.uid)
#         data['company_fulltitle'] = f"{data['company_title']} {data['company_subtitle']}"
#         pdf_obj.data = data
#         pdf_obj.save() 
#         return data 
#     except:
#         return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)



# @api.post("/get-pdf-data/")
# def get_pdf_data(request):
#     if GLOBAL_TOKEN != request.headers.get('Authorization'):
#         return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    
#     body_data = request.POST.dict()
    
#     try:
#         search = body_data['search'].strip().lower()
        
#         search_query = Q(user_email__iexact=search) | Q(data__emp_identification_number=search)  | Q(pdffile_name__icontains=search)
        
#         if is_valid_uuid(search):
#             search_query = Q(uid=search) | search_query

#         pdf_obj = PDFFile.objects.values('data').filter(search_query).order_by('-updated')
#         if len(pdf_obj) > 0:
#             return pdf_obj[0]['data']
#         else:
#             return JsonResponse({"error": "No Record Found!"}, status=400)
        
#     except:
#         return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)

from ninja import NinjaAPI
from ninja.errors import HttpError
api = NinjaAPI()

from django.db.models import Q
from django.http.response import JsonResponse
from django.conf import settings

from intents_app.models import OptoutTexts, TextIntent
from pdf_app.models import PDFFile

from utils.utils import is_valid_uuid
from utils.pdf_app.handle_pdf import AIPDF
from utils.intents_app.handle_prediction import AiTextIntentPredictionModel
GLOBAL_TOKEN = settings.GLOBAL_TOKEN


FAILED_EXCEPTION_MESSAGE = "something went wrong, please check your request data and try again."
FAILED_AUTHORIZED_MESSAGE = "You are not Authorized."


@api.get('/pingsite/')
def ping_site(request):
    return JsonResponse({}, status=200)

from utils.intents_app.handle_new_model import loadNewModel

@api.post("/get-intent/") 
def get_intent(request):
    
    # if GLOBAL_TOKEN != request.headers.get('Authorization'):
    #     return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE }, status=400)
    # try:
    body_data = request.POST.dict()
    print("body_data",body_data)
    clean_text = body_data['text']
    print("clean_text",clean_text)
    intent_result = AiTextIntentPredictionModel().getPrediction(clean_text)
    print('intent_result',intent_result)
    return JsonResponse({"result": intent_result}, status=200)
    #     return JsonResponse({"result": intent_result}, status=200)
    # except: 
    #     return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)
    
    
@api.post("/train-text/")
def add_text_for_training(request):
    # if GLOBAL_TOKEN != request.headers.get('Authorization'):
    #      return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    try:
        intent_choices = [_.value for _ in TextIntent.TEXT_INTENT] + ['opt_out']
        print("intent_choices ",intent_choices)
        body_data = request.POST.dict()
        print("body_data",body_data)
        text = body_data['text'].strip().lower()    
        print("text ",text)
        optout_filtertype = body_data['optout_filtertype'].strip().lower()
        print('optout_filtertype ',optout_filtertype)
        intent_ = body_data['intent'].strip().lower()
        print('intent_ ',intent_)
        status = body_data['status']
        print("status ",status)
        
        if intent_ not in intent_choices:
            return JsonResponse({"error": f"intent choices are: {intent_choices}"}, status=400)
        
        if optout_filtertype not in ['exact', 'contains']:
            return JsonResponse({"error": f"optout_filtertype choices are: {['exact', 'contains']}"}, status=400)
        
        if intent_ == 'opt_out':
            obj, created = OptoutTexts.objects.get_or_create(text=text, filter_type=optout_filtertype, status=status)
            if created:
                return JsonResponse({"result": "added successfully!"}, status=200)
            return JsonResponse({"result": "already exist!"}, status=200)
        else:
            
            obj, created = TextIntent.objects.get_or_create(text=text, intent=intent_, is_approved=status)
            if created:
                print("Created")
                return JsonResponse({"result": "added successfully!"}, status=200)
            return JsonResponse({"result": "already exist!"}, status=200)
    except:
        return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)


@api.post("/render-pdf/")
def render_pdf(request):
    # if GLOBAL_TOKEN != request.headers.get('Authorization'):
    #     return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    
    try:
        pdffile = request.FILES['pdffile']
    except:
        raise HttpError(400, "Invalid Keyname, keep 'pdffile'")
    
    
    if not (pdffile.name).endswith('.pdf'): 
        raise HttpError(400, "'only pdf files are allowed")
    
    body_data = request.POST.dict()
    user_email = body_data['email'].strip().lower()
    print("BODY DATA", body_data)
    try:
        
        pdf_obj = PDFFile.objects.create(
            user_email = user_email,
            pdffile = pdffile,
            pdffile_name = pdffile.name,
        )
        print("PDF OBJ", pdf_obj.pdffile.url)
        data = AIPDF().returnPDFData(pdf_obj.pdffile.url)
        print("DATA", data)
        data['result_id'] = str(pdf_obj.uid)
        data['company_fulltitle'] = f"{data['company_title']} {data['company_subtitle']}"
        pdf_obj.data = data
        pdf_obj.save() 
        print("DATA===", pdf_obj)
        return data 
    except:
        return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)




@api.post("/get-pdf-data/")
def get_pdf_data(request):
    # if GLOBAL_TOKEN != request.headers.get('Authorization'):
    #     return JsonResponse({"error": FAILED_AUTHORIZED_MESSAGE}, status=400)
    try:
        body_data = request.POST.dict()
        print("body_data",body_data)
        search = body_data['search'].strip().lower()
        print('search',search)
        
        search_query = Q(user_email__iexact=search) | Q(data__emp_identification_number=search)  | Q(pdffile_name__icontains=search)
        print('search_query',search_query)
        if is_valid_uuid(search):
            search_query = Q(uid=search) | search_query
            print("search_query",search_query)

        pdf_obj = PDFFile.objects.values('data').filter(search_query).order_by('-updated')
        print("pdf_obj",pdf_obj)
        if len(pdf_obj) > 0:
            print("3")
            return pdf_obj[0]['data']
        else:
            return JsonResponse({"error": "No Record Found!"}, status=400)
    except:
        return JsonResponse({"error": FAILED_EXCEPTION_MESSAGE}, status=400)
    

from utils.pdf_app.pdf_to_text import returnPdfOCRData
import tempfile

@api.post("/get_pdf_ocr_data/")
def get_pdf_data_new(request):
    print("API CALLED")
    try:
        pdffile = request.FILES['pdffile']
        print("FILE NAME: ===>>>", pdffile)
    except:
        print("FILE NAME: ===>>> ERROR")
        raise HttpError(400, "Invalid Keyname, keep 'pdffile'")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdffile.file.read())
        file_path = temp_file.name
        
    text = returnPdfOCRData(file_path)
    
    return text
