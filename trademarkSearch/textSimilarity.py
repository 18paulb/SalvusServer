from fuzzywuzzy import fuzz
import phonetics


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


# This judges similarity of text
# - fuzz.ratio() - Helpful for comparing two strings that should be nearly identical
# - fuzz.partial_ratio() - Helpful when dealing with data that might have extra characters or noise
# - fuzz.token_sort_ratio() - Helpful when comparing strings where the order of the words might vary, such as sentence paraphrasing
# - fuzz.token_set_ratio() - Helpful when you need a more robust comparison, including different word orders, duplicate words, and additional words
def judge_ratio_fuzzy(trademarks: list, inputText: str, infringementList: list):
    # We are starting the threshold at 50 for multiple reasons
    # 1. It will reduce the number of false negative (ie saying it is not an infringement even though it is)
    # - However this will also cause false positives, but we are not worried about that right now

    for trademark in trademarks:
        if fuzz.ratio(trademark.mark_identification, inputText) > 90:
            pair = (trademark, "red")
            infringementList.append(pair)
            trademarks.remove(trademark)
            continue

        if fuzz.partial_ratio(trademark.mark_identification, inputText) > 80:
            pair = (trademark, "yellow")
            infringementList.append(pair)
            trademarks.remove(trademark)
            continue

        if fuzz.token_sort_ratio(trademark.mark_identification, inputText) > 80:
            pair = (trademark, "yellow")
            infringementList.append(pair)
            trademarks.remove(trademark)
            continue

        if fuzz.token_set_ratio(trademark.mark_identification, inputText) > 75:
            pair = (trademark, "green")
            infringementList.append(pair)
            trademarks.remove(trademark)
            continue


def get_similar_trademarks(trademarks: list, inputText: str, infringementList: list):
    judge_exact_match(trademarks, inputText, infringementList)
    judge_ratio_fuzzy(trademarks, inputText, infringementList)
    judge_phonetic_similarity(trademarks, inputText, infringementList)
