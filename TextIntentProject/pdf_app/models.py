from django.db import models
import uuid
import os

def pdffile_upload_path_with_uid(instance, filename):
    path = "pdf_files/"
    extension = "." + filename.split('.')[-1]
    filename_reformat = f"{instance.uid}{extension}"
    return os.path.join(path, filename_reformat)


class PDFFile(models.Model):
    user_email = models.CharField(max_length=255, null=True, blank=True)
    uid = models.UUIDField(auto_created=True, default = uuid.uuid4, editable = False, unique=True)
    pdffile = models.FileField(upload_to=pdffile_upload_path_with_uid,  null=True, blank=True)
    pdffile_name = models.TextField(null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uid}"

    class Meta:
        verbose_name = verbose_name_plural ="PDF File Data"