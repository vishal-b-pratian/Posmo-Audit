import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CompanyDetails(models.Model):
    """
    This table stores the basic details of the company
    """
    id = models.UUIDField(
        default=uuid.uuid4, verbose_name="Company Id", primary_key=True, editable=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    name = models.CharField(verbose_name="Company Name", null=True, max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)
    compliance_score = models.FloatField(verbose_name="Compliance Score", default=0)
    previous_compliance_score = models.FloatField(
        verbose_name="Compliance Score", default=0
    )

    def __str__(self):
        return self.name


class Engagement(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, verbose_name="Company Id", primary_key=True, editable=True
    )
    company = models.ForeignKey("CompanyDetails", on_delete=models.CASCADE)
    start_Date = models.DateTimeField(auto_now_add=True)
    end_Date = models.DateTimeField()
    type = models.CharField(
        max_length=70,
        choices = (
        ("branding", "branding"),
        ("positioning", "positioning"),
        ("both", "both")
        )
    )

    def __str__(self):
        return f"{self.company.name} - {self.type}"


class MessageArchitecture(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, verbose_name="MA Id", primary_key=True, editable=True
    )
    engagement = models.ForeignKey(to = "Engagement",on_delete=models.CASCADE)
    parameter = models.CharField(verbose_name="Parameter Name", max_length=200)
    keyword = models.CharField(verbose_name="Keyword", max_length=200)

    def __str__(self):
        return f"MA for {self.company}"


class AuditParameter(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, 
        verbose_name="Audit Parameter Id", 
        primary_key=True, 
        editable=True
    )
    engagement = models.ForeignKey(
        to = "Engagement",
        verbose_name = "Engagement Details",
        on_delete = models.DO_NOTHING
    )
    parameter = models.CharField(verbose_name="Parameter Name", max_length=200)
    audit_weightage = models.FloatField(
        verbose_name="Audit Weightage", 
        null=True, 
        default=1.0
    )
    keyword = models.CharField(
        verbose_name="Keyword", 
        max_length=200
    )

    def __str__(self) -> str:
        return f"{self.parameter}"


class ChannelType(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, 
        verbose_name="Channel Type Id", 
        primary_key=True, 
        editable=True
    )
    channel_type = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Channel Type",
        choices = (
            ("social_media", "Social Media"),
            ("owned_press_release", "Owned Press Release"),
            ("company_website", "Company Website")
        )
    )
    engagement = models.ForeignKey(
        to = "Engagement",
        on_delete=models.CASCADE,
        related_name="engagement_details",
    )
    channel_type_weightage = models.FloatField(
        verbose_name="Weightage", 
        null=True, 
        default=1.0
        )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        verbose_name="Is Active", 
        default=True
        )

    def __str__(self):
        return f"{self.engagement.company.name} - {self.channel_type}"

class Channel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, 
        verbose_name="Channel Id", 
        primary_key=True, 
        editable=True
    )
    channel_name = models.ForeignKey(
        to = "ChannelName", 
        on_delete=models.CASCADE, 
    )
    type_name = models.ForeignKey(
        to = "ChannelType", 
        on_delete=models.CASCADE, 
    )
    engagement = models.ForeignKey(
        to = "Engagement", 
        on_delete=models.DO_NOTHING,
    )
    is_active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f" {self.url.url}"

class ChannelSource(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, 
        verbose_name="Channel Source Id", 
        primary_key=True, 
        editable=True
    )
    channel = models.ForeignKey("Channel", on_delete = models.CASCADE)
    url = models.URLField(
        verbose_name="Channel Url", 
        max_length=200
    )

class ChannelName(models.Model):
    channel_type_name = models.ForeignKey(
        to ="ChannelType",
        on_delete = models.DO_NOTHING)
    channel_name = models.CharField(
        verbose_name="Channel Name", 
        max_length=70
    )
    def __str__(self):
        return f" {self.channel_name}"

class ChannelTypeParameter(models.Model):
    type_name = models.ForeignKey(
        to = "ChannelType", 
        on_delete=models.CASCADE
    )
    parameters = models.ForeignKey(
        to="AuditParameter",
        on_delete=models.DO_NOTHING
    )
    weight = models.FloatField()



class ChannelParameter(models.Model):
    channel= models.ForeignKey(
        to = "Channel", on_delete=models.CASCADE, related_name="channel"
    )
    parameters = models.ForeignKey(
        to="AuditParameter",
        on_delete=models.DO_NOTHING
    )
    weight = models.FloatField()


class ChannelSourceParameter(models.Model):
    url =  models.ForeignKey(
        to = "Channel", 
        verbose_name="Channel Url",  
        max_length=200,
        on_delete = models.DO_NOTHING
    )
    parameters = models.ForeignKey(
        to="AuditParameter",
        on_delete=models.DO_NOTHING
    )
    weight = models.FloatField()
