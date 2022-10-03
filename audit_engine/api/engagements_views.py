import enum

from django.db.models import Q
from django.core import serializers as dj_serializers
from rest_framework import exceptions, status, generics, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView

from configuration import models as config_models
from audit_engine.api.api_helpers import (SerializeColumn, getUserCompany, getValidatedParams, getEngagementById,
                                          instanceNotFoundResponse, parse_validated_data)
from audit_engine.api import validations


class EngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.Engagement
        fields = ['id', 'start_Date', 'end_Date', 'type', 'compliance_score', 'previous_compliance_score', 'is_active']
        read_only_fields = ['id', 'compliance_score', 'previous_compliance_score']


class ChannelNameSerialzer(serializers.ModelSerializer):
    class Meta:
        model = config_models.ChannelName
        filelds = ['channel_name']


class AllChannelsSerializer(serializers.ModelSerializer):
    channelName = serializers.SerializerMethodField()

    class Meta:
        model = config_models.Channel
        fields = ['id', 'channelName']

    def get_channelName(self, channel):
        return channel.channel_name.channel_name


class AuditSerializer:
    '''Generates a custom serializer to parse audit response.'''

    class Fields(enum.Enum):
        '''Class provides autocompletion in code editors.'''

        CompanyId = 'CompanyId'
        CompanyName = 'CompanyId'
        AuditId = 'AuditId'
        AuditName = 'AuditName'
        AuditType = 'AuditType'
        AuditStatus = 'AuditStatus'
        AuditScore = 'AuditScore'
        ClientType = 'ClientType'
        ClientTypeId = 'ClientTypeId'
        Channels = 'Channels'
        ChannelCount = 'ChannelCount'
        StartTime = 'StartTime'
        EndTime = 'EndTime'

    @classmethod
    def generateSerializer(cls, fields=None, exclude_fields=None):
        # If no field is passed select all fields to send response for.
        if not fields:
            fields = cls.Fields.__members__.values()

        # remove excluded fields.
        if exclude_fields:
            fields = list(filter(lambda x: x not in exclude_fields, fields))

        field_names = list(map(lambda x: x.name, fields))

        class BaseSerializer(serializers.ModelSerializer):
            for field in field_names:
                locals()[field] = serializers.SerializerMethodField()

            class Meta:
                model = config_models.Engagement
                fields = field_names

            def get_CompanyId(self, engagement):
                return engagement.company.id

            def get_CompanyName(self, engagement):
                return engagement.company.name

            def get_AuditName(self, engagement):
                # return f'{engagement.type} Audit'
                return engagement.name

            def get_AuditId(self, engagement):
                return f'{engagement.id}'

            def get_AuditType(self, engagement):
                return engagement.type

            def get_ClientType(self, engagement):
                return engagement.client_type.name

            def get_ClientTypeId(self, engagement):
                return engagement.client_type.id

            def get_AuditStatus(self, engagement):
                # is_open = engagement.end_Date - datetime.datetime.now(datetime.timezone.utc)
                # status = 'Open' if is_open.total_seconds() > 0 else 'Close'
                audit_status = 'Open' if engagement.is_active else 'Closed'
                return audit_status

            def get_Channels(self, engagement):
                # query for all channels present in the audit.
                channels = config_models.Channel.objects.filter(engagement=engagement)
                serializer = AllChannelsSerializer(channels, many=True)
                return serializer.data

            def get_ChannelCount(self, engagement):
                return config_models.ChannelType.objects.filter(engagement=engagement).count()

            def get_AuditScore(self, engagement):
                return engagement.compliance_score

            def get_StartTime(self, engagemet):
                return engagemet.start_Date

            def get_EndTime(self, engagemet):
                return engagemet.end_Date
        return BaseSerializer


@api_view(['GET'])
def getAllAudits(request):
    input_fields = [SerializeColumn(name='CompanyId')]
    validated_data = getValidatedParams(input_fields, request)
    company_id = parse_validated_data(input_fields, validated_data)
    allEngagemnets = config_models.Engagement.objects.filter(Q(company__id=company_id))
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.AuditType,
                                                                    AuditSerializer.Fields.ClientType,
                                                                    AuditSerializer.Fields.ClientTypeId,
                                                                    AuditSerializer.Fields.StartTime,
                                                                    AuditSerializer.Fields.EndTime,
                                                                    ])
    json_response = Serializer(allEngagemnets, many=True).data
    return Response(json_response)


@api_view(["GET"])
def viewAuditSummary(request):
    input_fields = [SerializeColumn(name='CompanyId'),
                    SerializeColumn(name="AuditId"),
                    ]

    validated_data = getValidatedParams(input_fields, request)
    company_id, audit_id = parse_validated_data(input_fields, validated_data)

    audit = config_models.Engagement.objects.filter(
        Q(company__id=company_id) & Q(id=audit_id)).first()
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.AuditType,
                                                                    AuditSerializer.Fields.ClientType,
                                                                    AuditSerializer.Fields.ClientTypeId,
                                                                    AuditSerializer.Fields.StartTime,
                                                                    AuditSerializer.Fields.EndTime,
                                                                    ])
    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(["POST"])
def addAudit(request):
    input_fields = [SerializeColumn('CompanyId', fieldType=serializers.UUIDField, db_column_name='company'),
                    SerializeColumn('AuditName', db_column_name='name'),
                    SerializeColumn('ClientType', db_column_name='client_type'),
                    SerializeColumn('AuditType', db_column_name='type'),
                    SerializeColumn('StartTime', fieldType=serializers.DateField, db_column_name='start_Date'),
                    SerializeColumn('EndTime', fieldType=serializers.DateField, db_column_name='end_Date'),
                    ]
    validated_data = getValidatedParams(input_fields, request)

    # Logical validations before creating a new audit.
    # Also contains code to override validated_data for ForeignKey Records.
    success, response = validations.auditCreationValidation(validated_data)
    if not success:
        return response

    audit = config_models.Engagement.objects.create(**response)
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.CompanyId,
                                                                    AuditSerializer.Fields.CompanyName,
                                                                    AuditSerializer.Fields.AuditScore,
                                                                    AuditSerializer.Fields.Channels,
                                                                    AuditSerializer.Fields.ChannelCount,
                                                                    ])
    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(["POST"])
def editAudit(request):
    input_fields = [SerializeColumn('CompanyId', fieldType=serializers.UUIDField, db_column_name='company'),
                    SerializeColumn('AuditId', fieldType=serializers.UUIDField, db_column_name='id'),
                    SerializeColumn('AuditName', db_column_name='name', required=False),
                    SerializeColumn('ClientType', db_column_name='client_type', required=False),
                    SerializeColumn('AuditType', db_column_name='type', required=False),
                    SerializeColumn('StartTime', fieldType=serializers.DateField,
                                    db_column_name='start_Date', required=False),
                    SerializeColumn('EndTime', fieldType=serializers.DateField,
                                    db_column_name='end_Date', required=False),
                    SerializeColumn('IsActive', fieldType=serializers.BooleanField,
                                    db_column_name='is_active', required=False),
                    ]
    validated_data = getValidatedParams(input_fields, request)

    # Logical validations before creating a new audit.
    # Also contains code to override validated_data for ForeignKey Records.
    success, response = validations.auditUpdateValidation(validated_data)
    if not success:
        return response
    audit = response['audit']

    for keys in ['audit', 'id', 'company']:
        del response[keys]

    if not response:
        return Response('No parameters passed to update', status=status.HTTP_400_BAD_REQUEST)

    for attr, value in response.items():
        setattr(audit, attr, value)
    audit.save()

    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.CompanyId,
                                                                    AuditSerializer.Fields.CompanyName,
                                                                    AuditSerializer.Fields.AuditScore,
                                                                    AuditSerializer.Fields.Channels,
                                                                    AuditSerializer.Fields.ChannelCount,
                                                                    ])
    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(["GET"])
def deleteAudit(request):
    input_fields = [SerializeColumn(name='CompanyId'),
                    SerializeColumn(name="AuditId"),
                    ]

    validated_data = getValidatedParams(input_fields, request)
    company_id, audit_id = parse_validated_data(input_fields, validated_data)
    audit = config_models.Engagement.objects.filter(Q(company__id=company_id) & Q(id=audit_id)).first()
    Serializer = AuditSerializer.generateSerializer()
    audit_info = Serializer(audit).data
    json_response = {'IsDeleted': True, 'AuditDetails': audit_info}
    audit.delete()
    return Response(json_response)


@api_view(["GET"])
def viewAuditInfo(request):
    input_fields = [SerializeColumn(name='CompanyId'),
                    SerializeColumn(name="AuditId"),
                    ]

    validated_data = getValidatedParams(input_fields, request)
    company_id, audit_id = parse_validated_data(input_fields, validated_data)
    audit = config_models.Engagement.objects.filter(Q(company__id=company_id) & Q(id=audit_id)).first()
    Serializer = AuditSerializer.generateSerializer()
    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(["GET"])
def inactiveateAuditInfo(request):
    input_fields = [SerializeColumn(name='CompanyId'),
                    SerializeColumn(name="AuditId"),
                    ]

    validated_data = getValidatedParams(input_fields, request)
    company_id, audit_id = parse_validated_data(input_fields, validated_data)
    audit = config_models.Engagement.objects.filter(Q(company__id=company_id) & Q(id=audit_id)).first()
    audit.is_active = False
    audit.save()
    Serializer = AuditSerializer.generateSerializer()
    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(["GET"])
def getAuditScore(request):
    input_fields = [SerializeColumn('AuditId', fieldType=serializers.UUIDField)]
    validated_data = getValidatedParams(input_fields, request)
    audit_id = parse_validated_data(input_fields, validated_data)
    audit = config_models.Engagement.objects.filter(Q(id=audit_id)).first()
    Serializer = AuditSerializer.generateSerializer(fields=[AuditSerializer.Fields.AuditId,
                                                            AuditSerializer.Fields.AuditScore,
                                                            ])

    json_response = Serializer(audit).data
    return Response(json_response)


@api_view(['GET'])
def companyAuditStatusSummary(request):
    input_fields = [SerializeColumn('CompanyId', fieldType=serializers.UUIDField)]
    validated_data = getValidatedParams(input_fields, request)
    company_id = parse_validated_data(input_fields, validated_data)
    company = config_models.CompanyDetails.objects.filter(id=company_id).first()
    if not company:
        return instanceNotFoundResponse('Company', 'CompanyId')

    audits = config_models.Engagement.objects.filter(Q(company=company))
    in_progress = audits.filter(is_active=True).count()
    closed = audits.count() - in_progress
    company_complience = company.compliance_score
    json_response = {
        'InProgress': in_progress,
        'Closed': closed,
        'Complience': company_complience,
    }
    return Response(json_response)


@api_view(['GET'])
def companyAuditSummary(request):
    input_fields = [SerializeColumn('CompanyId', fieldType=serializers.UUIDField)]
    validated_data = getValidatedParams(input_fields, request)
    company_id = parse_validated_data(input_fields, validated_data)
    company = config_models.CompanyDetails.objects.filter(id=company_id).first()
    if not company:
        return instanceNotFoundResponse('Company', 'CompanyId')
    audits = config_models.Engagement.objects.filter(Q(company=company))

    # creating json object mannually as increasing fields in Audit serializer will increase generateSerializer exclude fields.
    json_response = []
    for audit in audits:
        source_count = config_models.Channel.objects.filter(engagement=audit).count()
        channel_types = config_models.ChannelType.objects.filter(engagement=audit)
        channel_count = channel_types.count()
        channel_type_count = 0
        for channel_type in channel_types:
            channel_type_count += config_models.ChannelName.objects.filter(channel_type_name=channel_type).count()
        days_remaining = (audit.end_Date - audit.start_Date).days

        audit_info = {
            'ComapanyName': audit.company.name,
            'ClientType': audit.client_type.name,
            'DaysRemaining': days_remaining,
            'ComplianceScore': audit.compliance_score,
            'ChannelTypeCount': channel_type_count,
            'ChannelCount': channel_count,
            'SourceCount': source_count,
        }
        json_response.append(audit_info)
    return Response(json_response)


@api_view(["GET"])
def filterAudit(request):
    input_fields = [SerializeColumn('AuditType', fieldType=serializers.CharField)]
    validated_data = getValidatedParams(input_fields, request)
    audit_type = parse_validated_data(input_fields, validated_data)

    audit_type_values = list(map(lambda x: x[1], config_models.PREDEFINED_AUDIT_TYPES))
    if audit_type not in audit_type_values:
        return instanceNotFoundResponse('AuditType', 'AuditType')

    audit = config_models.Engagement.objects.filter(Q(type=audit_type))
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.AuditType,
                                                                    AuditSerializer.Fields.ClientType,
                                                                    AuditSerializer.Fields.ClientTypeId,
                                                                    AuditSerializer.Fields.StartTime,
                                                                    AuditSerializer.Fields.EndTime,
                                                                    ])
    json_response = Serializer(audit, many=True).data
    return Response(json_response)


@api_view(["GET"])
def searchAudit(request):
    input_fields = [SerializeColumn('AuditName', fieldType=serializers.CharField)]
    validated_data = getValidatedParams(input_fields, request)
    audit_name = parse_validated_data(input_fields, validated_data)
    audit = config_models.Engagement.objects.filter(Q(name__icontains=audit_name))
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.AuditType,
                                                                    AuditSerializer.Fields.ClientType,
                                                                    AuditSerializer.Fields.ClientTypeId,
                                                                    AuditSerializer.Fields.StartTime,
                                                                    AuditSerializer.Fields.EndTime,
                                                                    ])
    json_response = Serializer(audit, many=True).data
    return Response(json_response)


@api_view(["GET"])
def sortAudit(request):
    input_fields = [SerializeColumn('CompanyId', fieldType=serializers.UUIDField),
                    SerializeColumn('SortBy', fieldType=serializers.CharField),
                    SerializeColumn('Ascending', fieldType=serializers.BooleanField, default=True)]

    validated_data = getValidatedParams(input_fields, request)
    company_id, sort_parameter, ascending = parse_validated_data(input_fields, validated_data)

    # choices are mapped with database column names.
    sort_choices = (('start_Date', 'AuditDate'), ('compliance_score', 'AuditScore'))
    sort_parameter = validations.validateChoice('SortBy', sort_choices, sort_parameter)
    sort_parameter = sort_parameter if ascending else f'-{sort_parameter}'  # add -FieldName for descending sort

    audit = config_models.Engagement.objects.order_by(sort_parameter).filter(Q(company__id=company_id))
    Serializer = AuditSerializer.generateSerializer(exclude_fields=[AuditSerializer.Fields.AuditType,
                                                                    AuditSerializer.Fields.ClientType,
                                                                    AuditSerializer.Fields.ClientTypeId,
                                                                    AuditSerializer.Fields.StartTime,
                                                                    AuditSerializer.Fields.EndTime,
                                                                    ])
    json_response = Serializer(audit, many=True).data
    return Response(json_response)


# class createEngagement(CreateAPIView):
#     serializer_class = EngagementSerializer

#     def create(self, request):
#         if not request.user.is_authenticated:
#             raise exceptions.NotAuthenticated

#         company = getUserCompany(request)
#         if not company:
#             raise Exception('Developer Error!!! All user should contain company')

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(company=company)
#         return Response(serializer.data)


# @ api_view(["POST"])
# def deleteEngagement(request):
#     fetched, result = getEngagementById(request)
#     if not fetched:
#         return result
#     result.delete()
#     return Response('Engagement Deleted')


# @ api_view(["POST"])
# def editEngagement(request):
#     serializer = EngagementSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     fetched, result = getEngagementById(request)
#     if not fetched:
#         return result
#     new_engagement = result.update(**serializer.validated_data)
#     return dj_serializers.serialize('json', new_engagement)


# @ api_view(['GET'])
# def companyEngagements(request):
#     if not request.user.is_authenticated:
#         raise exceptions.NotAuthenticated
#     company = getUserCompany(request)

#     if not company:
#         raise Exception('Developer Error!!! All user should contain company')

#     allEngagemnets = config_models.Engagement.objects.filter(company=company)
#     serializer = AuditResponseSerializer(allEngagemnets, many=True)
#     return Response(serializer.data)


# class Engagements(RetrieveUpdateDestroyAPIView):
#     serializer_class = serializers.EngagementSerializer
#     queryset = config_model.Engagement.objects.all()

#     def get(self, request):
#         _id = request.GET.get('id')
#         if not _id:
#             return Response('Engagement Id is Required')
#         # _id = uuid.UUID(_id)
#         engagement = config_model.Engagement.objects.filter(id=_id)
#         serializer = self.serializer_class(engagement, many=True)
#         return Response(serializer.data)

#     def put(self, request):
#         if not request.user.is_authenticated:
#             raise exceptions.NotAuthenticated

#         if not request.user.company:
#             raise Exception('Developer Error!!! All user should contain company')

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(company=request.user.company)
#         return Response(serializer.data)

#     def patch(self, request):
#         self.serializer_class(data=request.data)
#         self.serializer_class.is_valid(raise_exception=True)
#         _id = request.data['id']
#         serializer = self.get_serializer(data=request.data)

#         serializer.is_valid(raise_exception=True)

#     def delete(self, request):
#         _id = request.data.get('id')
#         if not _id:
#             return Response('Engagement Id is Required')

#         _id = request.data['id']
#         x = config_model.Engagement.objects.delete(id=_id)
#         print(x)
#         return Response('Engagement Deleted')


# @api_view(["GET"])
# def getEngagementAudits(request):
#     serializer_class = serializers
#     serializer = get_serializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save(clinc=request.user.clinic)
