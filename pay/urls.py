from django.conf.urls import include, url
from . import views

app_name = 'pay'
urlpatterns = [
    url(r'^form/processor/$',views.FormProcessorView.as_view() ,name = 'form_processor'),
    url(r'^callback/$',views.CallBackView.as_view() , name = 'callback'),
] 