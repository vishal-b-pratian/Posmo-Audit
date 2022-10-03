from . import models
from django.contrib import admin

# Register your models here.
admin.site.register(models.ContentFetchInfo)
admin.site.register(models.Content)
admin.site.register(models.MappedKeyWords)
admin.site.register(models.UnmappedKeywords)
admin.site.register(models.Links)


