import datetime
from rest_framework.response import Response
from rest_framework import status, exceptions
from configuration import models as config_models
from audit_engine.api.api_helpers import instanceNotFoundResponse


def auditCreationValidation(data):
    company_id = data['company']
    audit_name = data['name'].strip()  # remove starting and trailing spaces.
    client_type = data['client_type']
    audit_type = data['type']  # take care of audit type case.
    start_date = data['start_Date']
    end_date = data['end_Date']

    audit_type_values = list(map(lambda x: x[1], config_models.PREDEFINED_AUDIT_TYPES))
    company_object = config_models.CompanyDetails.objects.filter(id=company_id).first()

    # company should exists
    if not company_object:
        return False, instanceNotFoundResponse('Company', 'CompanyId')
    data['company'] = company_object

    # AuditName should not be empty.
    if not audit_name:
        return False, Response("AuditName can't be empty.")

    # Client Type should already exist in the table
    client_type_object = config_models.ClientType.objects.filter(name=client_type).first()
    if not client_type:
        return False, instanceNotFoundResponse('ClientType')
    data['client_type'] = client_type_object

    # AuditType should already be defined
    # Directly validating from code as no seperate table is being used.
    if audit_type not in audit_type_values:
        return False, instanceNotFoundResponse('AuditType', 'AuditType')

    # Same company should not have multiple similar audit type
    company_audits_count = config_models.Engagement.objects.filter(company=company_object, type=audit_type).count()
    if company_audits_count:
        return False, Response("Cannot create multiple audits with same audit type within a company.", status=status.HTTP_400_BAD_REQUEST)

    if datetime.datetime.now().date() > start_date:
        return False, Response("StartDate can't be less than today's date.", status=status.HTTP_400_BAD_REQUEST)

    if datetime.datetime.now().date() > end_date:
        return False, Response("StartDate can't be less than today's date.", status=status.HTTP_400_BAD_REQUEST)

    if start_date > end_date:
        return False, Response('StartTime should be less than EndTime')

    return True, data


def auditUpdateValidation(data):
    company_id = data['company']
    aduit_id = data['id']
    client_type = data.get('client_type', None)
    audit_type = data.get('type', None)  # take care of audit type case.
    start_date = data.get('start_Date', None)
    end_date = data.get('end_Date', None)
    is_active = data.get('IsActive', None)

    audit_type_values = list(map(lambda x: x[1], config_models.PREDEFINED_AUDIT_TYPES))
    company_object = config_models.CompanyDetails.objects.filter(id=company_id).first()
    audit_object = config_models.Engagement.objects.filter(id=aduit_id).first()

    # audit should exist
    if not audit_object:
        return False, instanceNotFoundResponse('Audit', 'AuditId')
    data['audit'] = audit_object

    # company should exist
    if not company_object:
        return False, instanceNotFoundResponse('Company', 'CompanyId')

    # Client Type should already exist in the table
    if client_type:
        client_type_object = config_models.ClientType.objects.filter(name=client_type).first()
        if not client_type:
            return False, instanceNotFoundResponse('ClientType')
        data['client_type'] = client_type_object

    # AuditType should already be defined
    # Directly validating from code as no seperate table is being used.
    if audit_type and audit_type not in audit_type_values:
        return False, instanceNotFoundResponse('AuditType', 'AuditType')

    # Same company should not have multiple similar audit type
    company_audits_count = config_models.Engagement.objects.filter(company=company_object, type=audit_type).count()
    if company_audits_count:
        return False, Response("Cannot create multiple audits with same audit type within a company.", status=status.HTTP_400_BAD_REQUEST)

    # Skipping start and end date validation for being >= Today's date in update. Need further info.

    # if datetime.datetime.now().date() > start_date:
    #     return False, Response("StartDate can't be less than today's date.", status=status.HTTP_400_BAD_REQUEST)

    # if datetime.datetime.now().date() > end_date:
    #     return False, Response("StartDate can't be less than today's date.", status=status.HTTP_400_BAD_REQUEST)
    
    # If startDate is not passed by the user take audit start date.
    if (start_date or audit_object.start_Date) > (end_date or audit_object.end_Date):
        return False, Response('StartTime should be less than EndTime')

    return True, data


def validateChoice(field_name, choices, value):
    '''Simulates django choice field. If tupple is passed for choice, first parameter will be returned as value.'''
    # choices = (('start_Date', 'AuditDate'), ('compliance_score', 'AuditScore'))
    # choices = ('start_Date', ('compliance_score', 'AuditScore'))

    acceptable_values = []

    for choice in choices:
        multivalued = (isinstance(choice, tuple) or isinstance(choice, list)) and len(choice) > 1
        choice_value = choice[1] if multivalued else choice[0]
        acceptable_values.append(choice_value)  # populate acceptable to throw better error.

        mapped_value = choice[0] if multivalued else None
        match = choice_value == value
        if match:
            if multivalued:
                return mapped_value
            return value

    raise exceptions.ValidationError({field_name: [f'Field value could be only among {acceptable_values}']})
