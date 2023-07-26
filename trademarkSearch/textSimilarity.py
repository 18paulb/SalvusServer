from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from jsonify import load_in_json
from fuzzywuzzy import fuzz
from models import Trademark

#Test
from sklearn.feature_extraction.text import TfidfVectorizer

class BertTextSimilarity:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

    def get_sentence_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        outputs = self.model(**inputs)
        # We use the average of the last hidden state as sentence embedding
        sentence_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return sentence_embedding

    def compute_similarity(self, text1, text2):
        embedding1 = self.get_sentence_embedding(text1)
        embedding2 = self.get_sentence_embedding(text2)
        similarity = cosine_similarity(embedding1, embedding2)
        return similarity


def judge_mark_identification(trademarks: list, inputText: str, code: str):
    wordList = inputText.lower().split(" ")

    for trademark in trademarks:
        # Currently removes one letter word marks
        if trademark.mark_identification in wordList and code in trademark.codes:
            print("Possible Infringement Found: \n")
            print(str(trademark) + "\n\n")



def judge_exact_match(trademarks: list, inputText: str, infringementList: list):

    for trademark in trademarks:
        if trademark.mark_identification == inputText:
            # print("Possible Infringement Found: \n")
            # print(mark + "\n\n")
            infringementList.append(trademark)
            trademarks.remove(trademark)

# This judges similarity of text
# TODO: Decide which is best case (or use all)
# - fuzz.ratio()
# - fuzz.partial_ratio()
# - fuzz.token_sort_ratio()
# - fuzz.token_set_ratio()

def judge_ratio_fuzzy(trademarks: list, inputText: str, infringementList: list):

    for trademark in trademarks:
    
        if fuzz.token_set_ratio(trademark.mark_identification, inputText) > 75:
            infringementList.append(trademark)
            trademarks.remove(trademark)

# def compute_cosine_similarity(mark_identification: list, text: str, possible_infringement_list: list):

#     vectorizer = TfidfVectorizer()

#     for mark in mark_identification:
#         matrix = vectorizer.fit_transform([mark, text])
#         score = cosine_similarity(matrix)
#         if score > .5:
#             print("Possible Infringement Found: \n")
#             print(mark + "\n\n")
#             possible_infringement_list.append(mark)
#             mark_identification.remove(mark)


def compare_text_to_marklist(text: str, wordMarks: list):

    similar_words = []

    comparater = BertTextSimilarity()

    i = 0
    for mark in wordMarks:
        i = i + 1
        if comparater.compute_similarity(mark.lower(), text.lower()) > .5:
            print(i)
            similar_words.append(mark)

        if i == 500:
            break

    return similar_words

