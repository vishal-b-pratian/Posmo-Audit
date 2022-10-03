from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.CompanyDetails)
# admin.site.register(models.DNAElement)
admin.site.register(models.MessageArchitecture)
admin.site.register(models.Engagement)
admin.site.register(models.ChannelName)
# admin.site.register(models.Measure)
admin.site.register(models.ChannelType)
#admin.site.register(models.Source)
admin.site.register(models.Channel)
admin.site.register(models.ClientType)
admin.site.register(models.AuditParameter)
admin.site.register(models.ChannelTypeParameter)
admin.site.register(models.ChannelParameter)
admin.site.register(models.ChannelSourceParameter)
# admin.site.register(models.AuditParameterType)