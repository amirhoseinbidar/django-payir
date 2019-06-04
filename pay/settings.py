# Django library.
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

# Extra library 
from cachetools import TTLCache

# CONTENT ----------------------------------------------------------

# https://pay.ir/docs/gateway/

PAY_DESCRIPTION_MAX_LENGTH = 255
PAY_REQUEST_TOKEN_URL = 'https://pay.ir/pg/send'
PAY_REDIRECT_USER_URL = 'https://pay.ir/pg/'
PAY_VARIFY_URL = 'https://pay.ir/pg/verify'
OK_STATUS = ('1' , 'OK',)
ERROR_STATUS = '0'


# ------------------------------------------------------------------

def _pay(var, default):
    """
    Adds "pay_" to the requested variable and retrieves its value
    from settings or returns the default.

    :param var: Variable to be retrieved.
    :type var: str
    :param default: Default value if the variable is not defined.
    :return: Value corresponding to 'var'.
    """
    try:
        return getattr(settings, 'PAY_' + var, default)
    except ImproperlyConfigured:
        # To handle the auto-generation of documentations.
        return default


PAY_USED_DOMAIN = 'http://localhost:8000/'
PAY_API_KEY = _pay('API_KEY', 'test')
PAY_CALLBACK_URL = _pay('CALLBACK_URL', PAY_USED_DOMAIN+'pay/callback/')
PAY_FORM_PROCESSOR = _pay('FORM_PROCESSOR','/pay/form/processor/' )
PAY_SIGNAL_METHODS = _pay('SIGNAL_METHODS' , {})

# EXTRA --------------------------------------------------------------

METHOD_FIELD_PREFIX =  "methodfield||__"
# simple cacheClass for cache data that need for callback 
cache = TTLCache(2**20,1800) #1800s = 30min