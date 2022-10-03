import json
from .tokenizer import Tokenizer


def getProcessedData(data):
    """
    processed data in the database is stored in
    the form of sentence. This function helps
    covert it into list of words.
    """
    if isinstance(data, list):
        return data

    return data.split(" ")


def convertDataForStorage(data):
    """
    Converting list of processed words to a
    string for storing it in database.
    """
    if isinstance(data, list):
        data = " ".join(data)

    return data


class PreProcessText:
    """
    processes raw scraped data and converts
    it into the required format.
    """

    def __init__(self, language="en"):
        self.language = language
        stopwords_file = open(
            r"C:\Users\jc\pratian\final-project-execution\ContentAnalyser\content_management\components\json_files\stopwords.json"
        )
        punctuations_file = open(
            r"C:\Users\jc\pratian\final-project-execution\ContentAnalyser\content_management\components\json_files\punctuations.json"
        )
        self.stopwords = json.load(stopwords_file)[language]
        self.punctuations = json.load(punctuations_file)[language]

    def _removeStopwords(self, sentence: str):
        sentence = sentence.lower()
        for word in self.stopwords:
            pattern = f" {word} "
            if pattern in sentence:
                sentence = sentence.replace(pattern, " ")
            if sentence == "":
                return None

        return sentence

    def removeStopwords(self, sentences):
        output = []
        for sentence in sentences:
            temp = self._removeStopwords(sentence)
            if temp:
                output.append(temp)

        return output

    def _removePunctuations(self, sentence: str):
        for punctuation in self.punctuations:
            sentence = sentence.replace(punctuation, "")

        return sentence

    def removePunctutaions(self, sentences):
        if isinstance(sentences, str):
            sentences = [sentences]
        output = []
        for sentence in sentences:
            output.append(self._removePunctuations(sentence))

        return output

    # def removeEmojis(self, sentences: list[str]):
    #     if isinstance(sentences, str):
    #         sentences = [sentences]
    #     output = []
    #     for sentence in sentences:
    #         ...

    @staticmethod
    def smallCase(text):

        if isinstance(text, str):
            text = [text]

        text = list(map(str.lower, text))
        return text

    def process(self, text):

        text = self.smallCase(text)
        print(f"\n\n{text}\n\n")
        words = Tokenizer.TokenizeToWords(text)
        print(f"\n\n{words}\n\n")
        sentences = self.removePunctutaions(text)
        sentences = self.removeStopwords(sentences)

        return words


if __name__ == "__main__":
    text = """Me to Mr. Shirt today: \n‘Tum hoti toh kaisa hota….\nTum iss baat pe Ph.D. leti,\nTum iss baat pe kitni hansti…….Tum hoti toh aisa hota..’
     Me also waiting for #Pathaan https://t.co/EnLPXw9csA"""
    text = """Your dedication for the welfare of our country and its people is highly appreciated. May you have the strength and health to achieve all your goals. Take a day off and enjoy your Birthday, sir. Happy Birthday @narendramodi"""
    ppt = PreProcessText()
    x = ppt.process(text)
    print(x)
