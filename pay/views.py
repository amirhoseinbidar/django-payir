from django.shortcuts import render, redirect, Http404
from django.views import generic
from django.utils.translation import gettext_lazy as _
from .forms import PayForm
from . import settings
from .settings import cache
from .models import UserTransaction
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError

import requests
import importlib

def get_error_render(request, errorMessage, errorCode, state):
    return render(
        request=request,
        template_name='pay/service_error.html',
        context={
            'errorMessage': errorMessage,
            'errorCode': errorCode,
            'state': state,
        }
    )

def get_signal_method(method_name):
    method = settings.PAY_SIGNAL_METHODS.get(method_name, None)
    if isinstance(method,str):
        mod_name, func_name = method.rsplit('.',1)
        mod = importlib.import_module(mod_name)
        return getattr(mod, func_name)
    return method        

def get_signal_from_value(value , kwargs):
    method_name = value.split(settings.METHOD_FIELD_PREFIX)[1]
    method = get_signal_method(method_name)
    if not method:
        raise ImproperlyConfigured(
            'method with name "%s" does not exist in PAY_SIGNAL_METHODS' % (
                method_name)
        )
    else:
        return method(**kwargs)  

def data_adapter(request, user, form_name, data: dict):
    for key, value in data.items():
        if key in PayForm.after_callback_handel:
            data[key] = value
            continue
        # if field is for a field method fireup a signal
        if value.startswith(settings.METHOD_FIELD_PREFIX):
            data[key] = get_signal_from_value(value , 
                            kwargs ={'request': request, 'user': user, 'form_name': form_name}  )            
    
    return data

def call_or_redirect(method,kwargs):
    if method.startswith(settings.METHOD_FIELD_PREFIX):
        return get_signal_from_value(method,kwargs)
    else:
        return redirect(method)



class FormProcessorView(generic.View):
    def post(self, request):
        request_data = self.get_form_data()
        request_data['user'] = -1
        if request.user.is_authenticated:
            request_data['user'] = request.user.id

        service_data = {  # it is better dont cache this data
            'api': settings.PAY_API_KEY,
            'redirect': settings.PAY_CALLBACK_URL,
        }
        service_data.update(request_data)

        pay_request = requests.post(
            settings.PAY_REQUEST_TOKEN_URL, json=service_data)
        data = pay_request.json()

        if str(data['status']) in settings.OK_STATUS:
            cache[data['token']] = request_data
            return redirect(settings.PAY_REDIRECT_USER_URL+data['token'])
        else:
            return get_error_render(request, data['errorMessage'], data['errorCode'], 'send')

    def get_form_data(self):
        data = data_adapter(
            request=self.request,
            user=self.request.user,
            form_name=self.request.POST.get('form_name', None),
            data=self.request.POST.copy()
        )
        form = PayForm(data=data, change_methodable_fileds=False)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise ImproperlyConfigured('invalid PayForm , check inputs \n '+str(form.errors.as_text()))


class CallBackView(generic.View):
    def get(self, request):
        status = request.GET.get('status', None)
        token = request.GET.get('token', None)
        if not status or not token:
            raise Http404
        
        data = cache.pop(token, None)
        if not data:  # if not data mean data is outdate or token is uncorrect
            raise Http404
 
        cached_user = data.pop('user')
        cancel_url = data.pop('cancel_url')
        return_url = data.pop('return_url')
        data['request'] = request

        if not (status in settings.OK_STATUS):
            return call_or_redirect(cancel_url , kwargs = data)
            
        # if one of data sender or giver is authenticated check their id
        # if both are anonymous ignore check
        if not (cached_user == -1 and not request.user.is_authenticated):
            if not request.user.id == cached_user:
                return render(request,'pay/user_auth_error.html')
        
        data.update(self.verify_callback(token))

        if UserTransaction.objects.filter(trans_id = data['transId']).exists():
            return render(request,'pay/duplicate_trans_id.html')
        
        self.save_to_db(data)
        return call_or_redirect(return_url,data)


    def verify_callback(self, token):
        ''' verify a callback if every thing ok path it else send a error page '''
        pay_request = requests.post(settings.PAY_VARIFY_URL, json={
            'api': settings.PAY_API_KEY,
            'token': token,
        })
        data = pay_request.json()
        if str(data['status']) in settings.OK_STATUS:
            return data

        return get_error_render(self.request, data['errorMessage'], data['errorCode'], 'varify')

    def save_to_db(self, data):
        user = self.request.user
        if not self.request.user.is_authenticated:
            user = None

        ut = UserTransaction(
            user=user,
            trans_id=data['transId'],
            factor_number=data['factorNumber'] or '',
            card_number=data['cardNumber'] or '',
        )
        ut.save()
        return ut
