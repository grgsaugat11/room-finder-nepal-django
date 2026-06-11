from django.contrib import admin
from .models import Province, District


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'province')
    list_filter = ('province',)
    search_fields = ('name', 'province__name')