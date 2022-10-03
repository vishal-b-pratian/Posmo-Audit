from . import models
from django.contrib import admin
from . import models as audit_model

# Register your models here.

admin.site.register(audit_model.ChannelParameterScore)
admin.site.register(audit_model.ChannelTypeParameterScore)
admin.site.register(audit_model.SourceParameterScore)
# admin.site.register(audit_model.AuditInformation) 