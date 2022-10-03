import re


class Tokenizer:
    """
    class to help tokenize text into
    sentences or words.
    """

    alphabets = "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|co)"

    @classmethod
    def tokenizeToSentences(cls, text: str):
        if isinstance(text, list):
            text = " ".join(text)
        text = " " + text + "  "
        text = text.replace("\n", "<stop>")
        text = text.replace("\u2018", "")
        text = text.replace("\u2019", "")
        # ^^^ this is a brute force method to get rid of the apostrophes to help with apostrophe searches.
        # it is not a good method.
        text = re.sub(cls.prefixes, "\\1<prd>", text)
        text = re.sub(cls.websites, "<prd>\\1", text)
        if "Ph.D" in text:
            text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        text = re.sub("\s" + cls.alphabets + "[.] ", " \\1<prd> ", text)
        text = re.sub(cls.acronyms + " " + cls.starters, "\\1<stop> \\2", text)
        text = re.sub(
            cls.alphabets + "[.]" + cls.alphabets + "[.]" + cls.alphabets + "[.]",
            "\\1<prd>\\2<prd>\\3<prd>",
            text,
        )
        text = re.sub(
            cls.alphabets + "[.]" + cls.alphabets + "[.]",
            "\\1<prd>\\2<prd>",
            text,
        )
        text = re.sub(
            " " + cls.suffixes + "[.] " + cls.starters,
            " \\1<stop> \\2",
            text,
        )
        text = re.sub(" " + cls.suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + cls.alphabets + "[.]", " \\1<prd>", text)
        if "”" in text:
            text = text.replace(".”", "”.")
        if '"' in text:
            text = text.replace('."', '".')
        if "!" in text:
            text = text.replace('!"', '"!')
        if "?" in text:
            text = text.replace('?"', '"?')
        text = text.replace(". ", ".<stop>")
        text = text.replace("? ", "?<stop>")
        text = text.replace("! ", "!<stop>")
        text = text.replace("<prd>", ".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences if s != ""]
        return sentences

    @classmethod
    def TokenizeToWords(cls, text: str):
        if isinstance(text, list):
            text = " ".join(text)
        sentences = cls.tokenizeToSentences(text)
        words = []
        for sentence in sentences:
            try:
                words += sentence.split(" ")
            except ValueError:
                pass

        return words


if __name__ == "__main__":
    text = """Me to Mr. Shirt today: \n‘Tum hoti toh kaisa hota….\nTum iss baat pe Ph.D. leti,\nTum iss baat pe kitni hansti…….Tum hoti toh aisa hota..’
     Me also waiting for #Pathaan https://t.co/EnLPXw9csA"""
    t = Tokenizer.tokenizeToSentences(text)
    print("\n", t)
