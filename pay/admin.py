from django.contrib import admin
from . import models

class UTAdmin(admin.ModelAdmin):
    list_display = ('uuid_id','user','trans_id','factor_number' , 'card_number')

admin.site.register(models.UserTransaction , UTAdmin)


