import json

from django.http import HttpResponse, JsonResponse

from DAOs.SearchDao import SearchDao
from DAOs.TrademarkDao import TrademarkDao
from DAOs.UserDao import UserDao
from DAOs.AuthtokenDao import AuthtokenDao
import apps.trademarkSearch.textSimilarity as ts
from salvusbackend.logger import logger
# from salvusbackend.transformer import classify_code, get_label_decoder
from apps.trademarkSearch.datacleaning import download_and_process_files, get_training_data
import os

from apps.trademarkSearch.TrademarkModel import make_trademark_objects


# Create your views here.

def same_mark_search(request):
    try:

        authtokenDao = AuthtokenDao()

        if not authtokenDao.verify_authtoken(request.headers.get('Authorization')):
            return HttpResponse("Unauthorized", status=401)

        userInfo = authtokenDao.find_user_info_by_authtoken(request.headers.get('Authorization'))

        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')

        email = userInfo[0]
        companyName = userInfo[1]

        td = TrademarkDao()
        sd = SearchDao()

        # Get all marks by that code (this will return part of the trademark so that it is faster to query)
        marks = td.search_by_code(typeCode)

        # Save search into database
        sd.insert_search(inputMark, email, companyName, typeCode)

        # Give each trademark a score based on closeness to input mark, return that sorted list of infringements
        infringementList = ts.score_similar_trademarks(marks, inputMark)

        # Now we need to retrieve the rest of the data for the trademarks, in order to make sure the response is as quick as possible
        # Only get the data for some of the trademarks right now, and if the user requests
        returnVals = td.get_trademarks_by_serial_number(infringementList)

        response_data = {
            'data': [{'trademark': infringement[0].to_dict(), 'riskLevel': infringement[1]}
                     for infringement in returnVals],
        }

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occurred", status=500)


def all_mark_search(request):
    pass
    # try:
    #     authtokenDao = AuthtokenDao()
    #
    #     userInfo = authtokenDao.find_user_info_by_authtoken(request.headers.get('Authorization'))
    #     if not authtokenDao.verify_authtoken(userInfo[0], request.headers.get('Authorization')):
    #         return HttpResponse("Unauthorized", status=401)
    #
    #     inputMark = request.GET.get('query')
    #     activeStatus = request.GET.get('activeStatus')
    #     lastEvaluatedKey = request.GET.get('lastEvaluatedKey')
    #
    #     email = userInfo[0]
    #     companyName = userInfo[1]
    #
    #     # This list will contain a list of Tuple(trademarkObject, riskLevel)
    #     infringementList = []
    #
    #     td = TrademarkDao()
    #     sd = SearchDao()
    #
    #     marks, lastEvaluatedKey = td.search_all(activeStatus, lastEvaluatedKey)
    #     sd.insert_search(inputMark, email, companyName, None)
    #
    #     ts.score_similar_trademarks(marks, inputMark, infringementList)
    #
    #     response_data = {
    #         'data': [{'trademark': infringement[0].to_dict(), 'riskLevel': infringement[1]}
    #                  for infringement in infringementList],
    #         'lastEvaluatedKey': lastEvaluatedKey
    #     }
    #
    #     return JsonResponse(response_data, safe=False, status=200)
    #
    # except Exception as e:
    #     logger.error(e)
    #     return HttpResponse("An error has occurred", status=500)


def classifyCode(request):
    pass
    # try:
    #     code = classify_code(request.GET.get('query'), get_label_decoder())
    #
    #     # Read in JSON file and compare the code to get the corresponding classifying string
    #     with open("salvusbackend/info/codes.json", "r") as f:
    #         # Load JSON data from the file
    #         codes_dict = json.load(f)
    #
    #         # Iterate over the "Goods" and "Services" keys in the codes_dict dictionary
    #         for category in codes_dict["codes"]:
    #             # Iterate over the key-value pairs in each category
    #             for key, value in codes_dict["codes"][category].items():
    #                 # Add the key-value pair to the flattened dictionary
    #                 codes_dict[value] = key  # Note that we switched the key and value
    #
    #     return JsonResponse({"classification": codes_dict[code[0]]}, status=200)
    # except Exception as e:
    #     logger.error(e)
    #     return JsonResponse({"message": "An error has occurred"}, status=500)


def getSearchHistory(request):
    try:

        authtokenDao = AuthtokenDao()

        userInfo = authtokenDao.find_user_info_by_authtoken(request.headers.get('Authorization'))
        if not authtokenDao.verify_authtoken(userInfo[0], request.headers.get('Authorization')):
            return HttpResponse("Unauthorized", status=401)

        searchHistory = SearchDao().get_search_history(userInfo[0])

        return JsonResponse(searchHistory, safe=False, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)

# This code does entire process of downloading, cleaning, and inserting into database, uncomment as needed
# download_and_process_files()
#
# td = TrademarkDao()
#
# trademarkObjects = []
# for file in os.listdir():
#     if file.endswith(".xml"):
#         trademarkObjects.extend(make_trademark_objects(file))
#
# print("Inserting ", len(trademarkObjects), " into database")
# td.insert_batch(trademarkObjects)
# print("Inserted around:", len(trademarkObjects), " items")

# This code gets the training data from the xml files and puts it into a json file
# codes = []
# descriptions = []
# for file in os.listdir():
#     if file.endswith(".xml"):
#         for pair in get_training_data(file):
#             codes.append(pair[0])
#             descriptions.append(pair[1])
#
# with open("model_training_data.json", "w") as f:
#     # Take each index at codes and descriptions and make a dictionary
#     json.dump([{"code": code, "description": description} for code, description in zip(codes, descriptions)], f)
#     print("Done writing file")
#     f.close()
