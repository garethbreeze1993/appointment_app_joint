from django.urls import path
from appointment_app.views import appointment_list, appointment_detail
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('appointments/', appointment_list),
    path('appointments/<int:pk>/', appointment_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
