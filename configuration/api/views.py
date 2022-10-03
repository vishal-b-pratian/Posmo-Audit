from random import sample
from symbol import parameters
from urllib import response
from configuration.models import Engagement
from django.core import serializers
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import dateutil.parser as dateTimeparser
from itertools import chain
from . import serializers as config_serializers
from configuration import models as config_models
from django.contrib.auth import models as auth_models


@api_view(["GET"])
def getRoutes(request):

    routes = [
        {"GET", "/api/users/"},
        {"GET", "/api/users/<int:id>/"},
        {"GET", "/api/company-details/"},
        {"GET", "/api/company-details/<uuid:id>/"},
        {"GET / POST", "/api/create-channel/"},
        {"GET / POST", "/api/create-channel-data/"},
        {"GET", "/api/engagement-details/"}
    ]

    return Response(routes)


@api_view(["GET"])
def getUsersData(request):

    users = auth_models.User.objects.all()
    serializer = config_serializers.UserSerializer(users, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def getCompanyDetailsData(request):
    sample_data = request.data.get('sample')
    print(sample_data)
    company_details = config_models.CompanyDetails.objects.all()
    serializer = config_serializers.CompanyDetailsSerializer(company_details, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def getEngagementDetails(request,company_id):
    response = {}
    company = config_models.CompanyDetails.objects.get(id = company_id)
    engagement_details = config_models.Engagement.objects.filter(company = company)
    for engagement in engagement_details:
        channel_types_list=[]
        response['engagement'] = engagement.type
        channel_types = config_models.ChannelType.objects.filter(engagement=engagement)
        for channel_type in channel_types.values():
            channel_types_list.append(channel_type['channel_type'])
            response['channel-types'] = channel_types_list
        response['channel_type_count'] = len(response['channel-types'])
        for channelType in channel_types:
            channels = config_models.Channel.objects.filter(type_name = channelType)
            channel_list = []
            parameters_list = []
            for channel in channels.values():
                parameters = config_models.ChannelSourceParameter.objects.filter(channel=channel['id'])
                
                for parameter in parameters.values():
                    audit_parameter = config_models.AuditParameter.objects.get(id = parameter['parameters_id'])
                    print(audit_parameter)
                    parameters_list.append([audit_parameter.parameter,parameter['weight']])
                   
                channel_list.append([channel['id'],channel['channel_title'],channel['is_active'],parameters_list])
                response[str(channelType)]= {str(channel['channel_name_id']):channel_list}



    return Response(response)



@api_view(["GET"])
def getUrlDetailsChannelType(request,company_name, engagement_type, channel_type):
  
    company_details = config_models.CompanyDetails.objects.get(name = company_name)
    channel_type_object = config_models.ChannelType.objects.get(channel_type= channel_type)
    engagement_details = config_models.Engagement.objects.filter(company = company_details,type = engagement_type)
    for engagement in engagement_details:
        url_details = config_models.Channel.objects.filter(engagement = engagement, type_name = channel_type_object)
    serializer = config_serializers.UrlDetailsChannelTypeSerializer(url_details, many=True)
    print(serializer.data)
    return Response(serializer.data)
  

@api_view(["GET"])
def getUrlDetailsChannel(request,company_name, engagement_type, channel_name):

    channel_name_object = config_models.ChannelName.objects.get(channel_name= channel_name)
    company_details = config_models.CompanyDetails.objects.get(name = company_name)
    
    engagement_details = config_models.Engagement.objects.filter(company = company_details,type = engagement_type)
    for engagement in engagement_details:
        url_details = config_models.Channel.objects.filter(engagement = engagement, channel_name = channel_name_object)
    serializer = config_serializers.UrlDetailsChannelSerializer(url_details, many=True)
    print(serializer.data)
    return Response(serializer.data)

@api_view(["GET"])
def getChannelsData(request,company_name):
    company_details = config_models.CompanyDetails.objects.get(name = company_name)
    engagement_details = config_models.Engagement.objects.filter(company = company_details)
    channels = []
    for engagement in engagement_details:
        if engagement.is_active:
            channels.append(config_models.Channel.objects.filter(engagement = engagement)) 
    serializer_data = []
    for channel in channels:
       
        serializer_data.append(config_serializers.ChannelSerializer(channel, many=True).data) 
                 
    return Response(serializer_data)

@api_view(["POST"])
def addChannel(request):
    channel = request.data.get('channel')
    engagement_id = channel['engagement_id']
    channel_type_id = channel['channel_type_id']
    channel_title = channel['channel_title']
    parameters = channel['parameters']
    url = channel['url']
    engagement = config_models.Engagement.objects.get(id = engagement_id)
    channel_type = config_models.ChannelType.objects.get(id = channel_type_id) 
    print(parameters.items())
    channel = config_models.Channel(engagement=engagement,type_name = channel_type,channel_title=channel_title,url =url)
    for parameter_it,weight_it in parameters.items():
        parameter_instance = config_models.AuditParameter.objects.get(engagement= engagement, parameter = parameter_it)
        channelSourceParameter = config_models.ChannelSourceParameter(parameters = parameter_instance,weight= float(weight_it),engagement=engagement)

    response={'channel':channel,
    'channelSourceParameter':channelSourceParameter}


    return Response(response)

@api_view(["GET"])
def viewAllSources(request, company_id):

    response = {}
    company_details = config_models.CompanyDetails.objects.get(id = company_id)
    if company_details:
        response['company_id'] = company_id
    engagement_details = config_models.Engagement.objects.filter(company = company_details)
    sources = []
    source_id = []
    channel_type_id = []
    channel_type_name = []
    source_status = []
    
    for engagement in engagement_details:
        url = config_models.Channel.objects.filter(engagement = engagement)
        for i in url:
            if i.url:
                source_id.append(str(i.id))
                sources.append(i.url)
                channel_type_id.append(i.type_name.id)
                channel_type_name.append(i.type_name.channel_type)
                source_status.append(i.is_active)

    for i in range(len(source_id)):
        response[source_id[i]] = {}
        response[source_id[i]]["url"] = sources[i]
        response[source_id[i]]["channel_type_id"] = channel_type_id[i]
        response[source_id[i]]["channel_type"] = channel_type_name[i]
        response[source_id[i]]["status"] = source_status[i]

    return Response(response)


@api_view(["GET"])
def viewSourcebyID(request, company_id, source_id):

    response = {}
    company_details = config_models.CompanyDetails.objects.get(id = company_id)
    if company_details:
        response['company_id'] = company_id
    url = config_models.Channel.objects.get(id = source_id)

    if url:
        sources = url.url
        channel_type_id = url.type_name.id
        channel_type_name = url.type_name.channel_type
        source_status = url.is_active
    response[source_id] = {}
    response[source_id]["url"] = sources
    response[source_id]["channel_type_id"] = channel_type_id
    response[source_id]["channel_type"] = channel_type_name
    response[source_id]["status"] = source_status
    
    return Response(response)


@api_view(["POST"])
def addSource(request):
    company_id = request.data.get("company_id")
    engagement_id = request.data.get("engagement_id")
    channel_name = request.data.get("channel_name")
    channel_type = request.data.get("channel_type")
    url = request.data.get("link")

    company = config_models.CompanyDetails.objects.get(id=company_id)
    engagement = config_models.Engagement.objects.get(id=engagement_id)

    config_models.ChannelType.objects.update_or_create(
        channel_type=channel_type,
        engagement=engagement,
    )

    channel_type_object = config_models.ChannelType.objects.get(
        channel_type=channel_type, 
        engagement=engagement
    )

    config_models.ChannelName.objects.update_or_create(
        channel_type_name=channel_type_object,
        channel_name=channel_name,
    )

    channel_name_object = config_models.ChannelName.objects.get(
        channel_name=channel_name,
        channel_type_name=channel_type_object
    )

    config_models.Channel.objects.create(
        channel_name=channel_name_object,
        type_name=channel_type_object,
        engagement=engagement,
        url=url,
    ).save()

    return Response("hii")


@api_view(["PUT"])
def editSource(request):
    company_id = request.data.get("company_id")
    engagement_id = request.data.get("engagement_id")
    channel_name = request.data.get("channel_name")
    channel_type = request.data.get("channel_type")
    url_id = request.data.get("link_id") 
    url = request.data.get("link")

    company = config_models.CompanyDetails.objects.get(id=company_id)
    engagement = config_models.Engagement.objects.get(id=engagement_id)

    config_models.ChannelType.objects.update_or_create(
        channel_type=channel_type,
        engagement=engagement,
    )

    channel_type_object = config_models.ChannelType.objects.get(
        channel_type=channel_type, 
        engagement=engagement
    )

    config_models.ChannelName.objects.update_or_create(
        channel_type_name=channel_type_object,
        channel_name=channel_name,
    )

    channel_name_object = config_models.ChannelName.objects.get(
        channel_name=channel_name,
        channel_type_name=channel_type_object
    )


    config_models.Channel.objects.filter(
        id = url_id
    ).update(
        channel_name=channel_name_object,
        type_name=channel_type_object,
        engagement=engagement,
        url=url,
    )

    return Response("hii") 
    
@api_view(["POST"])
def add_channel_type(request,engagement_id):
    channel_type = request.data.get('channel_type')
    response = {}

    channel_type_name = channel_type['channel_type_name']
    channel_type_weightage = channel_type['channel_type_weightage']
    engagement = config_models.Engagement.objects.get(id=engagement_id)
    channel_type_object = config_models.ChannelType.objects.create(
    channel_type=channel_type_name,
    engagement=engagement,
    channel_type_weightage= float(channel_type_weightage)
    ).save()
    response['channel_type'] = channel_type_object
    return Response(response)
       # print(Engagement)
    # end_date = dateTimeparser.parse(Engagement.get('end_Date'))
    # type = Engagement['type']
    # company_details = config_models.CompanyDetails.objects.get(name = Engagement.get('company'))
    # # print(Engagement)
    # engagement = config_models.Engagement.objects.create(company = company_details,type = type, end_Date = end_date)
    # x = {}
    # x['company'] = engagement.company.id
    # x['start_Date'] = engagement.start_Date
    # return Response(x)
    
# def addChannel(request):
#     if request.method == "GET":

#     else:
#         serializer = config_serializers.ChannelSerializer(data = request.data.get('channel'))
#         serializer .is_valid(raise_exception = True)
#         serializer.save()
#         return Response(serializer.validated_data)

