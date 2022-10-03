from pyexpat import model
from attr import fields
from rest_framework import serializers
from configuration import models as config_models
from django.contrib.auth import models as auth_models



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "is_staff", "date_joined"]


class CompanyDetailsSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = config_models.CompanyDetails
        fields = ["id", "user", "name", "created", "updated", "is_active"]
        read_only_fields = ["id", "user", "created", "updated"]

class EngagementSerializer(serializers.Serializer):
    company = serializers.CharField()
    type = serializers.CharField()
    end_Date = serializers.DateTimeField()
    
    
    def create(self, validated_data):
        company_details = config_models.CompanyDetails.objects.get(name = validated_data.get('company'))
        validated_data['company'] = company_details
        return config_models.Engagement.objects.create(**validated_data)


# class ChannelDetailsSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     company = CompanyDetailsSerializer()

#     class Meta:
#         model = config_models.Channel
#         fields = ["url", "channel_name", "type_name","engagement"]
class ChannelSourceParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.ChannelSourceParameter
        fields = ["parameters","weight"]
class ChannelSerializer(serializers.Serializer):
    parameter_weightage = ChannelSourceParameterSerializer(many=True)
    class Meta:
        model = config_models.Channel
        fields = ["channel_name","channel_title","url","is_active","parameter_weightage"]



class EngagementDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.Engagement
        fields = ('id','company','type','end_Date')

class ChannelTypeSerializer(serializers.ModelSerializer):
    engagement = EngagementDetailsSerializer(many = True)
    
    class Meta:
        model = config_models.ChannelType
        fields = ('id','channel_type','channel_type_weightage','engagement')
class UrlDetailsChannelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.Channel
        fields = ["id","type_name","channel_name","url"]
class UrlDetailsChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.Channel
        fields = ("id","channel_name","url")
class ChannelSerializer(serializers.Serializer):
    channel_name = serializers.CharField()
    type_name = serializers.CharField()
    url = serializers.URLField()
   
   