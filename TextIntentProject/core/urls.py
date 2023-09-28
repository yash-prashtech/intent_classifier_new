from django.urls import path, include
from .views import (
    HomeView, 
    CheckIntent, 
    TextTrainData, 
    )
app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('check-intent/', CheckIntent.as_view(), name='check_intent'),

    path('train-data/', TextTrainData.as_view(), name='text_train_data'),
    path('train-data/<pk>/', TextTrainData.as_view(), name='single_text_train_data'),
]



