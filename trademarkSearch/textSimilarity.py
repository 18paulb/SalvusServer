from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

from fuzzywuzzy import fuzz
import phonetics
from trademarkSearch.models import Trademark


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


def judge_exact_match(trademarks: list, inputText: str, infringementList: list):
    for trademark in trademarks:
        if trademark.mark_identification == inputText:
            pair = (trademark, "red")
            infringementList.append(pair)
            trademarks.remove(trademark)


# Consider using Metaphone double metaphone
def judge_phonetic_similarity(trademarks: list, inputText: str, infringementList: list):
    for trademark in trademarks:
        if phonetics.dmetaphone(trademark.mark_identification) == phonetics.dmetaphone(inputText):
            pair = (trademark, "red")
            infringementList.append(pair)
            trademarks.remove(trademark)


# Eventually do language similarity
def judge_language_similarity(trademarks: list, inputText: str, infringementList: list):
    pass


# This is not good, consider just scrapping this
def judge_BERT(trademarks: list, inputText: str, infringementList: list):
    bert = BertTextSimilarity()
    for trademark in trademarks:
        if bert.compute_similarity(trademark.mark_identification, inputText) > 0.75:
            infringementList.append(trademark)
            trademarks.remove(trademark)


# This judges similarity of text
# - fuzz.ratio() - Helpful for comparing two strings that should be nearly identical
# - fuzz.partial_ratio() - Helpful when dealing with data that might have extra characters or noise
# - fuzz.token_sort_ratio() - Helpful when comparing strings where the order of the words might vary, such as sentence paraphrasing
# - fuzz.token_set_ratio() - Helpful when you need a more robust comparison, including different word orders, duplicate words, and additional words
def judge_ratio_fuzzy(trademarks: list, inputText: str, infringementList: list):
    for trademark in trademarks:
        if fuzz.token_set_ratio(trademark.mark_identification, inputText) > 75:
            pair = (trademark, "yellow")
            infringementList.append(pair)
            trademarks.remove(trademark)
