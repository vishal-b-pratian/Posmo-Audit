import uuid
from django.db import models
from django.contrib.auth.models import User
from content_management import models as content_models
from configuration import models as config_models
from django.core.validators import MinValueValidator, MaxValueValidator

# class AuditInformation(models.Model):
#     channel_name = models.ForeignKey(
#         config_models.ChannelName,
#         on_delete=models.CASCADE,
#         related_name="audit_info",
#     )
#     start_date = models.DateField(verbose_name="Start Date")
#     end_date = models.DateField(verbose_name="End Date")
#     overall_compliance_score = models.FloatField(
#         verbose_name="Overall Compliance Score",
#         default=0.0,
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#     )
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Audit info <{self.channel_name}>"


# class ClientTypes(models.Model):
#     id = models.UUIDField(default = uuid.uuid4, verbose_name = "Id", primary_key = True)
#     type_name = models.CharField(max_length = 50, unique = True, verbose_name = "Client Type")


# class AuditType(models.Model):
#     # !!!!! Important add prevention for multiple same audits.
#     id = models.UUIDField(default = uuid.uuid4, verbose_name = "Id", primary_key = True)
#     parameters = models.ForeignKey(to = config_models.AuditParameter, on_delete = models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()

# class Audit(models.Model):
#     Engagements = models.ForeignKey()
#     audit_name = models.CharField(max_length = 500, nullable = False)
#     ClientTypes = models.ForeignKey(to = ClientTypes, on_delete = models.PROTECT)


class SourceParameterScore(models.Model):
    source = models.OneToOneField(
        config_models.ChannelSourceParameter, on_delete=models.CASCADE, primary_key = True
    )

    # id = models.UUIDField(
    #     default=uuid.uuid4,
    #     verbose_name="Source Parameter Id",
    #     primary_key=True,
    #     editable=True,
    # )
    # keyword_count = models.IntegerField(verbose_name = 'Mapped Keyword Count', default = 0)
    # keyword_frequencies  = JSONField(default = '[]')
    parameter_score = models.FloatField(verbose_name="Parameter Score", default=0.0)


class ChannelParameterScore(models.Model):
    channel = models.OneToOneField(
        config_models.ChannelParameter, on_delete=models.CASCADE, related_name="parameter"
    )
    # id = models.UUIDField(
    #     default=uuid.uuid4,
    #     verbose_name="Channel Parameter Id",
    #     primary_key=True,
    #     editable=True,
    # )
    parameter_score = models.FloatField(verbose_name="Parameter scores", default=0.0)


class ChannelTypeParameterScore(models.Model):
    channel_type = models.OneToOneField(
        config_models.ChannelTypeParameter, on_delete=models.CASCADE, related_name="parameter"
    )
    # id = models.UUIDField(
    #     default=uuid.uuid4,
    #     verbose_name="ChannelType Parameter Id",
    #     primary_key=True,
    #     editable=True,
    # )
    parameter_score = models.FloatField(
        verbose_name="Parameter Score", default=0.0
    )

# class ScoreCardParameter(models.Model):
#     """
#     Table is used to store scores for each
#     parameter.
#     """

#     id = models.UUIDField(
#         default=uuid.uuid4, verbose_name="Score Id", primary_key=True, editable=True
#     )
#     dna_alignment = models.FloatField(verbose_name="DNA Alignment", default=0.0)
#     posmo_tag = models.FloatField(verbose_name="Posmo Tag", default=0.0)
#     differentiator = models.FloatField(verbose_name="Differentiator", default=0.0)
#     value_proposition = models.FloatField(verbose_name="Value Proposition", default=0.0)
#     tagline = models.FloatField(verbose_name="Tagline", default=0.0)
#     total_score = models.FloatField(verbose_name="Total Score", default=0.0)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.id}"
