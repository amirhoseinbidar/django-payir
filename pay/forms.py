from django import forms
from .settings import PAY_DESCRIPTION_MAX_LENGTH, PAY_FORM_PROCESSOR, METHOD_FIELD_PREFIX

import copy

# method field do nothing it just add a prefix to name of a signal method for identifiction purpose


class MethodField(forms.CharField):
    def __init__(self, signal_method_name, *args, **kwargs):
        assert isinstance(signal_method_name,
                          str), 'signal_method_name must be a str'
        super().__init__(
            # "methodfield||__" is method fileds default identifier
            #  but it can change in setting 
            initial=METHOD_FIELD_PREFIX+signal_method_name,
            widget=forms.HiddenInput,
            *args, **kwargs
        )


class PayForm(forms.Form):
    # this use for form action
    pay_form_processor = PAY_FORM_PROCESSOR
    
    # extadData won't send to pay.ir api 
    # it is just for programmer pass another data he/she want  
    extraData = forms.CharField(widget=forms.HiddenInput, required=False)  
    amount = forms.IntegerField(widget=forms.HiddenInput)
    mobile = forms.IntegerField(widget=forms.HiddenInput, required=False)
    factorNumber = forms.IntegerField(
        widget=forms.HiddenInput, required=False)
    description = forms.CharField(
        max_length=PAY_DESCRIPTION_MAX_LENGTH, widget=forms.HiddenInput, required=False)
    
    return_url = forms.CharField(widget=forms.HiddenInput)
    cancel_url = forms.CharField(widget=forms.HiddenInput)

    methodable_fileds = ['extraData','amount', 'factorNumber','mobile',
                         'description', 'return_url', 'cancel_url' , '' ]
    after_callback_handel = [
        'return_url', 'cancel_url'
    ] 

    def __init__(self, initial=None, change_methodable_fileds=True, *args, **kwargs):
        # think all initial data are none methodable
        non_methodfiled_data = copy.deepcopy(initial)
        methodfiled_data = {}
        # then pop intial data that are isnstance of MethodField
        # and replace them with thair methodfield 
        # methodfields will handel in FormProcessorView
        if change_methodable_fileds:
            for key in initial:
                if key in self.methodable_fileds and isinstance(initial[key], MethodField):
                    methodfiled_data[key] = non_methodfiled_data.pop(key)
        
        super().__init__(initial=non_methodfiled_data, *args, **kwargs)

        for key, value in methodfiled_data.items():
            self.fields[key] = value
