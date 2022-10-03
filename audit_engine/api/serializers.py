import datetime
from rest_framework import serializers
from configuration import models as config_model


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = config_model.CompanyDetails
        fields = ["name", "compliance_score"]


class AllEngagementsSerializer(serializers.ModelSerializer):

    company = CompanySerializer()
    daysRemaining = serializers.SerializerMethodField()
    channelTypeCount = serializers.SerializerMethodField()
    channelCount = serializers.SerializerMethodField()
    sourceCount = serializers.SerializerMethodField()

    class Meta:
        model = config_model.Engagement
        fields = ["id", "company", "daysRemaining", "channelTypeCount", "channelCount", "sourceCount"]

    def get_daysRemaining(self, obj):
        time_diff = obj.end_Date - datetime.datetime.now(datetime.timezone.utc).date()
        if time_diff.total_seconds() < 0:
            return "Ended"
        return f"{time_diff.days} Days to go"

    def get_channelTypeCount(self, engagement):
        channelTypeCount = config_model.ChannelType.objects.filter(engagement = engagement).count()
        return channelTypeCount


    def get_channelCount(self, engagement):
        channel_types = config_model.ChannelType.objects.filter(engagement = engagement)
        channel_type_count = 0
        for channel_type in channel_types:
            channel_type_count += config_model.ChannelName.objects.filter(channel_type_name = channel_type).count()

        return channel_type_count


    def get_sourceCount(self, engagement):
        return config_model.Channel.objects.filter(engagement = engagement).count()



