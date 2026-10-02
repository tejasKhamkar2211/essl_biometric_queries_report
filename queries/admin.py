from django.contrib import admin
from .models import Query

@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('fc_id_name', 'date', 'related_system')  # removed new_functionality
    list_filter = ('related_system', 'date')                 # removed new_functionality
    search_fields = ('fc_id_name', 'description')


from .models import Functionality

@admin.register(Functionality)
class FunctionalityAdmin(admin.ModelAdmin):
    list_display = ('fc_id_name', 'date')
    list_filter = ('date',)
    search_fields = ('fc_id_name', 'description')
