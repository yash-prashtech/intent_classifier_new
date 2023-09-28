from django.db import models
from django.template.defaultfilters import truncatechars  # or truncatewords
from uuid import uuid4
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


from utils.intents_app.handle_cleantext import CLEANTEXT
from utils.intents_app.helpling_function import data_preprocessing


class OptoutTexts(models.Model):
    class FilterType(models.TextChoices):
        EXACT = "exact", "Exact Match"
        CONTAINS = "contains", "Contains"
    
    uid = models.UUIDField(auto_created=True, default = uuid4, editable = False, unique=True)
    text = models.CharField(verbose_name="Text", max_length=255, unique=True)
    clean_text = models.TextField(blank=True, null=True) 
    filter_type = models.CharField(max_length=10, choices=FilterType.choices, default=FilterType.CONTAINS)
    status = models.BooleanField(verbose_name="Status/Active", default=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        self.text = self.text.strip().lower()

    def __str__(self) -> str:
        return f"{self.text}"
    
    def save(self, *args, **kwargs):
        # self.clean_text = CLEANTEXT().getCleanText(self.text)
        self.clean_text = data_preprocessing(self.text)
        super(OptoutTexts, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = verbose_name_plural = "Optout Texts"
        indexes = [
            models.Index(fields=['text', 'clean_text'], name='optout_model_indexes'),
        ]
         
    

class TextIntent(models.Model):
    class TEXT_INTENT(models.TextChoices):
        INTERESTED_GENERAL = 'interested_general', 'Interested General'
        Neutral = 'neutral', 'Neutral'
        NOTSET = 'not_set', 'Not Set'
        SKIPPED = 'skiped', 'Skiped'
        
    uid = models.UUIDField(auto_created=True, default = uuid4, editable = False, unique=True)
    text = models.TextField() 
    clean_text = models.TextField(blank=True, null=True) 
    intent = models.CharField(max_length=30, choices=TEXT_INTENT.choices, default=TEXT_INTENT.NOTSET)
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_intent_display()} - {self.text}"
    
    class Meta:
        ordering = ["-pk"]
        verbose_name = verbose_name_plural = "Text Intents (Interested General | Neutral)"
        indexes = [
            models.Index(fields=['text', 'clean_text'], name='textintent_model_indexes'),
        ]

    def save(self, *args, **kwargs):
        text_ = str(self.text).strip().lower()
        self.text = text_
        # self.clean_text = CLEANTEXT().getCleanText(text_)
        self.clean_text = data_preprocessing(self.text)
        super(TextIntent, self).save(*args, **kwargs)

    @property
    def short_text(self):
        return truncatechars(self.text, 40)
    
    
class TrainModel(models.Model):
    class TrainOn(models.TextChoices):
        FULL = 'full', 'All Data'
        MINIMUM = 'minimum', 'Minimum Limit'

    class ModelStatus(models.TextChoices):
        TRAINING = 'training', 'Training'
        TRAINED = 'trained', 'Trained'

    uid = models.UUIDField(auto_created=True, default = uuid4, editable = False, unique=True)
    train_on = models.CharField(verbose_name="Trained On", max_length=30, choices=TrainOn.choices, default=TrainOn.FULL)
    model_status = models.CharField(max_length=30, choices=ModelStatus.choices, default=ModelStatus.TRAINING)
    model_info = models.JSONField(default=dict)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.uid}"
    
    class Meta:
        ordering = ["-pk"]
        verbose_name = verbose_name_plural = "Train Model"


@receiver(pre_save, sender=TrainModel)
def train_model_signal(sender, instance, **kwargs):
    if instance.id is not None:
        if instance.active and instance.model_status == 'trained':
            TrainModel.objects.update(active=False, updated=timezone.now())
        else:
            instance.active = False
            
            
from utils.intents_app.handle_train_model import IntentTrainModel
@receiver(post_save, sender=TrainModel)
def train_model_signal1(sender, instance, **kwargs):
    if instance.id is not None and instance.model_status != 'trained':
        IntentTrainModel(instance.uid).train_model()          
            
            
# keep this import here 
from utils.intents_app.handle_prediction import AiTextIntentPredictionModel

class TestTextIntents(models.Model):
    class TEXT_INTENT(models.TextChoices):
        INTERESTED_GENERAL = 'interested_general', 'Interested General'
        OPT_OUT = 'opt_out', 'Opt Out'
        Neutral = 'neutral', 'Neutral'
        NOTSET = 'not_set', 'Not Set'

    text = models.TextField() 
    intent = models.CharField(max_length=30, choices=TEXT_INTENT.choices, default=TEXT_INTENT.NOTSET)
    guess_intent = models.CharField(max_length=30)
    intent_match = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_intent_display()} - {self.text}"
    
    class Meta:
        ordering = ["-pk"]
        verbose_name = verbose_name_plural = "Test Intents"

    def save(self, *args, **kwargs):
        text_ = str(self.text).strip().lower()
        self.text = text_
        self.guess_intent =  AiTextIntentPredictionModel().getOnlyIntent(text_)
        if self.intent == self.guess_intent:
            self.intent_match = True
        else:
            self.intent_match = False
        super(TestTextIntents, self).save(*args, **kwargs)

    @property
    def short_text(self):
        return truncatechars(self.text, 60)
    
