import json

from django.http import HttpResponse, JsonResponse

from DAOs.SearchDao import SearchDao
from DAOs.TrademarkDao import TrademarkDao
from DAOs.UserDao import UserDao
from DAOs.AuthtokenDao import AuthtokenDao
import apps.trademarkSearch.textSimilarity as ts
from salvusbackend.logger import logger
from tasks import background_search_by_code
# from salvusbackend.transformer import classify_code, get_label_decoder
from apps.trademarkSearch.datacleaning import download_and_process_files, get_training_data
import os

from apps.trademarkSearch.TrademarkModel import make_trademark_objects

# This initiates the search, and makes a background task, returning the taskID to the client so that it can ping it's status
def same_mark_search(request):
    try:
        authtokenDao = AuthtokenDao()
        sd = SearchDao()

        if not authtokenDao.verify_authtoken(request.headers.get('Authorization')):
            return HttpResponse("Unauthorized", status=401)

        userInfo = authtokenDao.find_user_info_by_authtoken(request.headers.get('Authorization'))

        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')

        email = userInfo[0]
        companyName = userInfo[1]

        sd.insert_search(inputMark, email, companyName, typeCode)
        result = background_search_by_code.delay(typeCode)

        return JsonResponse({'task_id': str(result.id)})

    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occurred", status=500)


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
