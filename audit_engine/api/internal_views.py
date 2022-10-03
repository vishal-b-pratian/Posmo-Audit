# Contains API used by internal services.
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q

from audit_engine.api import api_helpers
from rest_framework import status
from configuration import models as config_models
from audit_engine import models as audit_models
from content_management import models as content_models


@api_view(['GET'])
def triggerScoreGeneration(request):
    '''Should be trigged by the content service to start score card generation.'''

    channelId = request.GET.get('ChannelId', None)
    # validate channel Id
    if not channelId:
        return Response('ChannelId parameter not found.', status=status.HTTP_400_BAD_REQUEST)

    # get channel from channel Id
    channel = config_models.Channel.objects.filter(id=channelId).first()

    if not channel:
        return api_helpers.instanceNotFoundResponse(class_name='Channel', parameter='channelId')

    # get mapped_keyword in json format
    links = content_models.Links.objects.filter(channel=channel).first()
    if not links:
        return api_helpers.instanceNotFoundResponse(class_name='Link', parameter='channelId')

    content_mapped_keywords = json.loads(links.content.contentfetchinfo.mappedkeywords.mapped_keywords)

    # return Response(mapped_keywords)

    # multiple parameters are available for a single channel. Merging SQL and JSON paramters.
    # >:-( Messy queries as config and content services Models are not compatable with each other.

    source_parameters = config_models.ChannelSourceParameter.objects.filter(channel=channel)
    score_by_parameter = calculateScore(source_parameters, content_mapped_keywords)
    createParameterScoreRecord(score_by_parameter, source_parameters)
    refreshScoreForCompany(channel)
    return Response('OK')


def scoreByParameterWordCount(word):
    '''Customize score by count of word.
    Example can be used to penalise the model if word count is greater than certain number.'''

    word_count = word['word_count']
    return int(bool(word_count))


def calculateParameterScore(parameter_words: list, content_words: dict):
    '''Number of words found in content for the paramter vs total number of words defined for the paramter.
    scoreByParameterWordCount can be used to customize the score by implementing a custom function based on occurrence count.'''

    match_count = 0
    print(parameter_words, content_words)
    for word in parameter_words:
        if word in content_words:
            match_count += scoreByParameterWordCount(content_words[word])
    print(match_count)
    parameter_score = match_count / (len(parameter_words) or 1)  # prevent 0 division error
    return parameter_score


def convertScoreToPercent(score):
    '''Utility method to represent scores better and avoid floatingpoint errors.'''
    return int(round(score, 2) * 100)


def calculateScore(source_parameters, content_mapped_keywords):
    score_by_parameter = []
    for src_parameter in source_parameters:
        parameter_name = src_parameter.parameters.parameter
        parameter_keywords = list(map(lambda x: x.strip(), src_parameter.parameters.keyword.split(',')))
        assert parameter_name in content_mapped_keywords
        content_keyword_map = content_mapped_keywords[parameter_name]['keyword']
        parameter_score = convertScoreToPercent(calculateParameterScore(parameter_keywords, content_keyword_map))
        score_by_parameter.append(parameter_score)
    return score_by_parameter


def createParameterScoreRecord(score_by_parameter, source_parameters):
    for parameter_score, parameter_data in zip(score_by_parameter, source_parameters):
        # update the previous record as mapping is One to One
        source_score_object = audit_models.SourceParameterScore.objects.filter(source=parameter_data).first()
        if source_score_object:
            source_score_object.parameter_score = parameter_score
            source_score_object.save()
        else:
            audit_models.SourceParameterScore.objects.create(source=parameter_data,
                                                             parameter_score=parameter_score)
    #final_score = sum(lambda x: x['weight'] * x['score'], score_by_parameter) / total_weights


def refreshScoreForCompany(channel):
    '''Traverses Up and down the table chain and refreshs parameter scores across all related tables.'''
    # update channel scores based on channelParameters.
    sourceParameters = config_models.ChannelSourceParameter.objects.filter(channel=channel)
    # remove source parameters for which sourceParameterScore has not been generated.
    sourceParameters = list(filter(lambda x: hasattr(x, 'sourceparameterscore'), sourceParameters))
    present_channel_score = channel.compliance_score
    total_weights = sum(map(lambda x: x.weight, sourceParameters))
    new_channel_score = sum(map(lambda x: x.sourceparameterscore.parameter_score *
                            x.weight, sourceParameters)) / (total_weights or 1)
    new_channel_score = round(new_channel_score, 2)
    config_models.Channel.objects.update(compliance_score=new_channel_score,
                                         previous_compliance_score=present_channel_score,
                                         )

    # Refresh score for Audit. Filter channels which already have scores i.e. previous_audit_score !=-1
    channels = config_models.Channel.objects.filter(Q(engagement=channel.engagement) & ~Q(previous_compliance_score=1))
    new_engagement_score = sum(map(lambda x: x.compliance_score, channels)) / \
        (len(channels) or 1)  # prevent 0 division error
    new_engagement_score = round(new_engagement_score, 2)

    present_engagement_score = channel.engagement.compliance_score
    channel.engagement.compliance_score = new_engagement_score
    channel.engagement.previous_compliance_score = present_engagement_score
    channel.engagement.save()

    # Refresh score for company based on Engagement score. Same logic as above.
    engagements = config_models.Engagement.objects.filter(
        Q(company=channel.engagement.company) & ~Q(previous_compliance_score=1))
    new_company_score = sum(map(lambda x: x.compliance_score, engagements)) / \
        (len(engagements) or 1)  # prevent 0 division error
    new_company_score = round(new_company_score, 2)
    
    present_company_score = channel.engagement.company.compliance_score
    channel.engagement.company.compliance_score = new_company_score
    channel.engagement.company.previous_compliance_score = present_company_score
    channel.engagement.company.save()
