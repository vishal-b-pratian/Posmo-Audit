def getParameterScore(count):
    # if single word is present then 1 else 0.
    # Need to come up with a better approach.
    return int(bool(count))


def convertScoreToPercent(score):
    return int(round(score, 2) * 100)


def getScoreByWeights(payload):
    # payloadFormat = [{'id', 'count', 'weight'},]
    parameter_count = len(payload)
    for parameter in payload:
        parameter['score'] = parameter['weight'] * getParameterScore(parameter['count'])
        parameter['normalized_score'] = convertScoreToPercent(parameter['score'])

    source_score = convertScoreToPercent(sum(map(lambda x: x['normalized_score'])) / parameter_count)
    return {'source_score': source_score, 'parameter': parameter}
