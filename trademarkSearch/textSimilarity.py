from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

from fuzzywuzzy import fuzz
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
