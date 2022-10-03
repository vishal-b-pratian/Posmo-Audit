from django.core import serializers as dj_serializers
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView

from audit_engine.api import api_helpers
from rest_framework import serializers
from configuration import models as config_models
from audit_engine import models as audit_models

# class AuditGridSerializer(serializers.Serializer):
#     ChannelType = serializers.SerializerMethodField()
    

#     def get_ChannelType(self, audit):
        

@api_view(['GET'])
def getAuditDetails(request):
    audit_id = request.GET.get('AuditId', None)
    if not audit_id:
        return Response('Audit Id not passed in parameter', status=status.HTTP_400_BAD_REQUEST)

    engagement = config_models.Engagement.objects.filter(id =  audit_id).first()
    if not engagement:
        return api_helpers.instanceNotFoundResponse('Audit', 'AuditId')
    
    channel_types = config_models.ChannelType.objects.filter(engagement=engagement)
    channel_type_data = []
    
    for channel_type in channel_types:
        channel_data = {'channel_type_id': channel_type.id,
                        'channel_type_name': channel_type.channel_type, 'channels': []}
        channel_names = config_models.ChannelName.objects.filter(channel_type_name=channel_type)
        for channel_name in channel_names:
            channel = config_models.Channel.objects.filter(channel_name=channel_name,
                                                           type_name=channel_type,
                                                           engagement=engagement).first()
            if not channel:
                continue

            source_parameter_data = []
            source_parameters = config_models.ChannelSourceParameter.objects.filter(channel=channel)

            for source_parameter in source_parameters:
                parameter_score = audit_models.SourceParameterScore.objects.filter(
                    source=source_parameter).first()

                if not parameter_score:
                    continue

                source_parameter_data.append({'parameter_id': source_parameter.id,
                                              'audit_parameter_id': source_parameter.parameters.id,
                                              'src_parameter_weight': source_parameter.parameters.audit_weightage,
                                              'src_parameter_score': parameter_score.parameter_score})

            channel_data['channels'].append({
                'channel_id': channel.id,
                'url': channel.url,
                'channel_name': channel.channel_name.channel_name,
                'parameters': source_parameter_data
            })

        if not channel_names:
            continue

        channel_type_data.append(channel_data)

    all_audit_parameters = config_models.AuditParameter.objects.filter(engagement=engagement)
    all_audit_parameters = [{'parameter_id': audit_parameter.id,
                             'parameter_name': audit_parameter.parameter} for audit_parameter in all_audit_parameters]

    channel_type_data = {'channel_data': channel_type_data,
                         'audit_parameter': all_audit_parameters}
    return Response(channel_type_data)

@api_view(['GET'])
def calculateScore():
    pass
