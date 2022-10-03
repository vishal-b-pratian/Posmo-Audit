from rest_framework import status, serializers
from rest_framework.response import Response
from configuration import models as config_models


class SerializeColumn:
    def __init__(self, name, fieldType=serializers.CharField, db_column_name=None, *args, **kwargs):
        self.key = name
        self.value = fieldType(*args, **kwargs)
        self.db_column_name = db_column_name
        self.__validate()

    def __validate(self):
        assert isinstance(self.key, str) and self.key
        assert isinstance(self.value, serializers.Field)
        if self.db_column_name:
            assert isinstance(self.db_column_name, str) and self.db_column_name

def parse_validated_data(input_fields, validated_data):
    parse_fields =  [validated_data[column.db_column_name or  column.key] for column in input_fields]
    if len(parse_fields) == 1:
        return parse_fields[0]
    return parse_fields
    
def getUserCompany(request, validate=True):
    '''Helps to simulate request even if user is not logged in. As Frontend is angular and auth
    will take place with azure AD, validate=False will return some company instance, if available.'''
    if validate:
        return request.user.company
    return config_models.CompanyDetails.objects.all().first()


def getEngagementById(request):
    _id = request.GET.get('id', None) if request.method == "GET" else request.data.get('id', None)
    if not _id:
        return False, Response('Engagement Id is Required', status=status.HTTP_400_BAD_REQUEST)

    engagement = config_models.Engagement.objects.filter(id=_id).first()
    if not engagement:
        return False, Response('Engagement not found',
                               status=status.HTTP_400_BAD_REQUEST)

    return True, engagement


def instanceNotFoundResponse(class_name, parameter='parameter'):
    return Response(f"Couldn't find a record for the {class_name}. Please ensure correct {parameter} is passed in payload.",
                    status=status.HTTP_400_BAD_REQUEST)


def getValidatedParams(params, request):
    # create serializer class to validate data.
    class InputSerializer(serializers.Serializer):
        has_mapped_columns = False
        for column in params:
            if not isinstance(column, SerializeColumn):
                raise Exception('params should be a list of SerialColumn objects.')

            if column.db_column_name:
                has_mapped_columns = True
            locals()[column.key] = column.value
    data = request.GET if request.method == 'GET' else request.data
    input_serializer = InputSerializer(data=data)
    input_serializer.is_valid(raise_exception=True)

    if InputSerializer.has_mapped_columns:
        for column in params:
            if column.db_column_name:
                try:
                    value = input_serializer.validated_data[column.key]
                except KeyError:
                    continue
                input_serializer.validated_data[column.db_column_name] = value
                del input_serializer.validated_data[column.key]

    return input_serializer.validated_data
