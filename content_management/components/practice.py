"""
Class to process scraped data and map with audit parrameter keywords
"""
import re
import json
import string
import nltk
from nltk.corpus import brown
from nltk.stem import WordNetLemmatizer
from nltk.data import find
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import gensim

# nltk.download()

class ContentAnalyser():

    def __init__(self,text_data,parameters):
        self.text_data = text_data
        self.parameters = parameters
        self.lemmatized_words_list = []
        self.final_dict = []
        self.model = gensim.models.Word2Vec(brown.sents())
        self.WORD_TWO_VEC_SAMPLE = str(find('models/word2vec_sample/pruned.word2vec.txt'))
        self.model = gensim.models.KeyedVectors.load_word2vec_format(self.WORD_TWO_VEC_SAMPLE, binary=False)
        # FILE_PATH_SCRAPPED_DATA = r"C:\\Users\\ammittal\\Desktop\\fer.txt"
        self.FILE_PATH_STOPWORDS = r"content_management\components\json_files\stop_words.json"
        self.ENCODING_EXTNS = 'utf-8'
        self.pos_dict = {"JJ": "a", "JJR": "a", "JJS": "a",
                "NN": "n", "NNS": "n", "NNP": "n",
                "NNPS": "n", "PRP": "n", "PRP$": "n",
                "WP": "n", "WP$": 'n',"RB": "v",
                "RBR": "v", "RBS": "v", "VB": "v",
                "VBD": "v", "VBG": "v",
                "VBN": "v", "VBP": "v", "VBZ": "v",
                "WRB": 'n' }


    def remove_emoji(self,string_text):
        """
        Removes the emojis if present in the text
        used interanly for processing
        """
        emoji_pattern = re.compile("["
                            u"U0001F600-U0001F64F"
                            u"U0001F300-U0001F5FF"
                            u"U0001F680-U0001F6FF"
                            u"U0001F1E0-U0001F1FF"
                            u"U00002702-U000027B0"
                            u"U000024C2-U0001F251"
                            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string_text)

    def decontracted(self,phrase):
        """
        Decontracting the text
        used interanly for processing
        """
        phrase = re.sub(r"won\'t", "will not", phrase)
        phrase = re.sub(r"can\'t", "can not", phrase)
        phrase = re.sub(r"n\'t", " not", phrase)
        phrase = re.sub(r"\'re", " are", phrase)
        phrase = re.sub(r"\'s", " is", phrase)
        phrase = re.sub(r"\'d", " would", phrase)
        phrase = re.sub(r"\'ll", " will", phrase)
        phrase = re.sub(r"\'t", " not", phrase)
        phrase = re.sub(r"\'ve", " have", phrase)
        phrase = re.sub(r"\'m", " am", phrase)
        return phrase

    # def extracted_keywords_from_audit_parameters(self,posmotag):
    #     """
    #     Extract the list of keywords from audit parameters
    #     used interanly for processing
    #     """
    #     keywords=np.unique(np.array(posmotag).flatten())
    #     string_keywords=' '.join(keywords)
    #     return np.unique(self.preprocessing(string_keywords,self.pos_dict))


    def preprocessing(self):
        """
        Removing and cleaning of unwanted data
        """
        text = self.text_data
        position_dict = self.pos_dict
        lower_text=text.lower()
        lower_text=lower_text.replace("\u200d"," ")
        puncts_to_remove=string.punctuation
        punct_list=[]
        for i in puncts_to_remove:
            punct_list.append(i)
        punct_list.append("'")
        punct_list.append("\n")
        punct_removed=''.join([i for i in lower_text if i not in punct_list])
        digits_removed=''.join([i for i in punct_removed if not i.isdigit()])
        space_removed=" ".join(digits_removed.split())
        replace_rep=re.sub(r'(!|.)1+', '', space_removed)
        remove_emojis=self.remove_emoji(replace_rep)
        decontracted_text=self.decontracted(remove_emojis)
        tokenized_words=decontracted_text.split(" ")
        with open(self.FILE_PATH_STOPWORDS,encoding=self.ENCODING_EXTNS) as stop_words_file:
            data=json.load(stop_words_file)
        stop_words_file.close()
        stop_words=data['en']
        filtered_words = [w for w in tokenized_words if not w.lower() in stop_words]
        lemmatizer = WordNetLemmatizer()
        lemmatized_words=[lemmatizer.lemmatize(i) for i in filtered_words]
        lemmatized_words_final=[]
        for i in lemmatized_words:
            try:
                lemmatized_words_final.append(lemmatizer.lemmatize(i,
                pos=position_dict[nltk.pos_tag([i])[0][1]]))
            except KeyError:
                lemmatized_words_final.append(i)
        self.lemmatized_words_list = lemmatized_words_final
        return lemmatized_words_final
    # lemmatized_words_list=preprocessing(text_data,pos_dict)
    # print("Lemmatized Words:-",lemmatized_words_list)



    def find_similar_keywords(self,audit_keywords,unmapped_list):
        """
        Finds similarity score and filter the
        similar words to add them to the final frequencies
        used interanly for processing
        """
        extracted_keywords=audit_keywords
        threshold = 0.25
        similiar_words={}
        key_words_dict = {}
        key_word_nd_count_dict = {}
        for i in extracted_keywords:
            similiar_words[i]=[]
        count=0
        for i in extracted_keywords:
            similar_word_dict = {}
            for j in self.lemmatized_words_list:
                try:
                    if self.model.similarity(i,j)>threshold:
                        if j not in similiar_words[i]:
                            similiar_words[i].append(j)
                            count=count+1
                    else:
                        unmapped_list.append(j)
                except KeyError:
                    pass
            similar_word_dict['similar'] = similiar_words[i]
            similar_word_dict['word_count'] = len(similiar_words[i])
            key_words_dict[i] = similar_word_dict
        
        key_word_nd_count_dict['keywords'] = key_words_dict
        key_word_nd_count_dict['count'] = count
        return key_word_nd_count_dict,unmapped_list

    def audit_frequency(self):
        """
        Calculates the average frquencies
        for corresponding audit parameters

        """
        parameters = self.parameters
        uniques_keys=list(parameters.keys())
        dict_frequency={}
        unmapped_word_list = []
        for i in uniques_keys:
            unmapped_list=[]
            dict_frequency[i],unmapped_list2 = self.find_similar_keywords(parameters[i],unmapped_list)
            unmapped_word_list+=unmapped_list2
        unmapped_word_list = set(unmapped_word_list)
        unmapped_word_list = list(unmapped_word_list)
        self.final_dict = dict_frequency
        # return dict_frequency,unmapped_word_list
        return json.dumps(dict_frequency)

    # dict_frequency,unmapped_word_list = audit_frequency(FILE_PATH_LOCATION)
    # dict_frequency = audit_frequency(FILE_PATH_LOCATION)
    # print('Dict_Frequency:', dict_frequency)
    # with open("sample.json", "w+") as outfile:
    #     json.dump(dict_frequency, outfile)
    # print('Unmapped Words: ',unmapped_word_list)
    # print('unmapped words count:', len(unmapped_word_list))
    def count_mapped_keywords(self):
        mapped_count = 0
        uniques_keys=list(self.final_dict.keys())
        for i in uniques_keys:
            mapped_count+=self.final_dict[i]['count']
        return mapped_count

    def final_unmapped(self):
        uniques_keys=list(self.final_dict.keys())
        unmapped_words = []
        for i in uniques_keys:
            for key,value in self.final_dict[i]['keywords'].items():
                if self.final_dict[i]['keywords'][key]['word_count']==0:
                    unmapped_words.append(key)
                    unmapped_words = set(unmapped_words)
                    unmapped_words = list(unmapped_words)
        return unmapped_words

    # unmapped_words = final_unmapped(FILE_PATH_LOCATION)
    # mapped_count = count_mapped_keywords(FILE_PATH_LOCATION)
    # print('Unmapped Words: ',unmapped_words)
    # print('unmapped words count:', len(unmapped_words))
    # print('mapped words count:', mapped_count)
    # print('Total words:', len(unmapped_words)+mapped_count)


