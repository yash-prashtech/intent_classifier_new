from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, StreamingHttpResponse, FileResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from pdf_app.models import PDFFile

class PDFMediaSecureView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        fileuid = str(kwargs['file']).split('.pdf')[0]
        # print(fileuid,  user.is_authenticated, user.is_superuser)
        try:
            if user.is_authenticated and user.is_superuser:
                # pdffile = PDFFile.objects.get(uid=fileuid)
                return FileResponse(pdffile.pdffile)
        except:
            pass
        raise Http404()

