from django import forms
from .settings import PAY_DESCRIPTION_MAX_LENGTH, PAY_FORM_PROCESSOR ,METHOD_FIELD_PREFIX

import copy

# method field do nothing it just add a prefix to name of a signal method for identifiction purpose  
class MethodField(forms.CharField):
    def __init__(self,signal_method_name, *args,**kwargs):
        assert isinstance(signal_method_name , str) , 'signal_method_name must be a str'
        super().__init__(
            # "methodfield||__" is method fileds identifier
            initial= METHOD_FIELD_PREFIX+signal_method_name ,
            widget=forms.HiddenInput ,
            *args,**kwargs
        )


class PayForm(forms.Form):
    # this use for form action
    pay_form_processor = PAY_FORM_PROCESSOR

    form_name = forms.CharField(widget=forms.HiddenInput,required=False)
    amount = forms.IntegerField(widget=forms.HiddenInput , initial = 10450)
    mobile = forms.IntegerField(widget=forms.HiddenInput, required=False)
    factor_number = forms.IntegerField(
        widget=forms.HiddenInput, required=False)
    description = forms.CharField(
        max_length=PAY_DESCRIPTION_MAX_LENGTH, widget=forms.HiddenInput, required=False)
    return_url = forms.CharField(widget=forms.HiddenInput)
    cancel_url = forms.CharField(widget=forms.HiddenInput)
    
    methodable_fileds = ['amount', 'factor_number',
                         'mobile', 'description' ]
    
    def __init__(self,initial=None,change_methodable_fileds=True,*args,**kwargs):
        non_methodfiled_data = copy.deepcopy(initial)
        methodfiled_data = {}
        if change_methodable_fileds:
            for key in initial:
                if key in self.methodable_fileds and isinstance(initial[key],MethodField):
                    methodfiled_data[key] = non_methodfiled_data.pop(key)
        super().__init__(initial=non_methodfiled_data , *args,**kwargs)
        
        for key ,value in methodfiled_data.items():
            self.fields[key] = value 


