# from fuzzywuzzy import fuzz
import phonetics
from rapidfuzz import fuzz


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


# This judges similarity of text
# - fuzz.ratio() - Helpful for comparing two strings that should be nearly identical
# - fuzz.partial_ratio() - Helpful when dealing with data that might have extra characters or noise
# - fuzz.token_sort_ratio() - Helpful when comparing strings where the order of the words might vary, such as sentence paraphrasing
# - fuzz.token_set_ratio() - Helpful when you need a more robust comparison, including different word orders, duplicate words, and additional words
def score_similar_trademarks(trademarks: list, inputText: str):
    infringementDict = {}

    input_lower = inputText.lower()
    for trademark in trademarks:
        score = 0

        wordmark = trademark[2].lower()

        if inputText.lower() in trademark[2].lower():
            score += 100

        score += fuzz.ratio(wordmark, input_lower)
        score += fuzz.partial_ratio(wordmark, input_lower)
        score += fuzz.token_sort_ratio(wordmark, input_lower)
        score += fuzz.token_set_ratio(wordmark, input_lower)

        infringementDict[trademark] = score

    min_value = min(infringementDict.values())
    max_value = max(infringementDict.values())

    # After all that, normalize each value to be on a scale of 0 to 100
    for key in infringementDict.keys():
        infringementDict[key] = min_max_scale(infringementDict[key], min_value, max_value)

    # Now we sort the dict so that the trademarks with the highest score are first
    sorted_infringementDict = {k: v for k, v in
                               sorted(infringementDict.items(), key=lambda tmpItem: tmpItem[1], reverse=True)}

    list_sorted_infringement = list(sorted_infringementDict.items())

    return list_sorted_infringement


# This is code to standardize all the ratings to be between 0 and 100
def min_max_scale(value, min_value, max_value):
    return 1 + (value - min_value) * 99 / (max_value - min_value)
