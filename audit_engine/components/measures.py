import json
from .preprocessor import getProcessedData
from configuration.models import ChannelData, MessageArchitecture


class CalculateScore:
    """
    Calculates the score of a particular field
    and returns it using the calculate function.
    """

    DENSITY_LIMIT = 5  # In percentage

    def __init__(self, channel_data_id, ma_id):

        self.id = channel_data_id
        self.message_architecture = MessageArchitecture.objects.get(id=ma_id)

        try:
            self.channel_data = ChannelData.objects.get(id=channel_data_id)
        except ChannelData.DoesNotExist:
            print("[Error] Channel Data doesn't exist")

        self.words = getProcessedData(self.channel_data.processed_data)

    def __getFrequency(self, keywords: list[str]):

        frequencies = {}
        for keyword in keywords:
            frequencies[keyword] = self.words.count(keyword)

        return frequencies

    def __getDensity(self, keywords: list[str]):

        densities = {}
        raw_text = self.channel_data.scraped_data
        freq = self.__getFrequency(self.words, keywords)
        for keyword, frequency in freq:
            densities[keyword] = frequency / len(raw_text)

        return densities

    def calculate(self, field_name: str):
        fields = self.message_architecture.measure_field.filter(
            field_name__icontains=field_name
        )
        # frequency = 0
        density = 0
        for field in fields:
            keywords = getProcessedData(field.value)
            # frequencies = self.__getFrequency(keywords)
            densities = self.__getDensity(keywords)
            # frequency += sum(frequencies.values()) / len(keywords)
            density += (sum(densities.values()) * field.weightage * 100) / len(
                keywords
            )  # In percentage

        if density >= CalculateScore.DENSITY_LIMIT:
            return 1

        return 0


def getScores(channel_data_id, ma_id):
    """
    Calculates score for each field and
    returns a dictionary containing all
    the scores.
    """
    calculator = CalculateScore(channel_data_id, ma_id)
    json_file = open(r"components\json_files\measuring_fields.json")
    field_names = json.load(json_file)["field_names"]
    scores = {}
    for field_name in field_names:
        scores[field_name] = calculator.calculate(field_name)

    return scores
