import json

from django.http import HttpResponse, JsonResponse

import trademarkSearch.database as db
import trademarkSearch.textSimilarity as ts
from salvusbackend.logger import logger
from authentication.database import find_userInfo_by_authtoken
from salvusbackend.transformer import classify_code, get_label_decoder
from authentication.loginviews import verify_authtoken


# Create your views here.

def same_mark_search(request):
    try:

        userInfo = find_userInfo_by_authtoken(request.headers.get('Authorization'))
        if not verify_authtoken(userInfo[0], request.headers.get('Authorization')):
            return HttpResponse("Unauthorized", status=401)

        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')
        activeStatus = request.GET.get('activeStatus')
        lastEvaluatedKey = request.GET.get('lastEvaluatedKey')

        email = userInfo[0]
        companyName = userInfo[1]

        # This list will contain a list of Tuple(trademarkObject, riskLevel)
        infringementList = []

        marks, lastEvaluatedKey = db.get_trademarks_by_code(typeCode, activeStatus, lastEvaluatedKey)
        db.save_search_into_table(inputMark, email, companyName, typeCode)

        ts.get_similar_trademarks(marks, inputMark, infringementList)

        response_data = {
            'data': [{'trademark': infringement[0].to_dict(), 'riskLevel': infringement[1]}
                     for infringement in infringementList],
            'lastEvaluatedKey': lastEvaluatedKey
        }

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occurred", status=500)


def all_mark_search(request):
    userInfo = find_userInfo_by_authtoken(request.headers.get('Authorization'))
    if not verify_authtoken(userInfo[0], request.headers.get('Authorization')):
        return HttpResponse("Unauthorized", status=401)

    inputMark = request.GET.get('query')
    activeStatus = request.GET.get('activeStatus')
    lastEvaluatedKey = request.GET.get('lastEvaluatedKey')

    email = userInfo[0]
    companyName = userInfo[1]

    # This list will contain a list of Tuple(trademarkObject, riskLevel)
    infringementList = []

    marks, lastEvaluatedKey = db.get_all_trademarks(activeStatus, lastEvaluatedKey)
    db.save_search_into_table(inputMark, email, companyName, None)

    ts.get_similar_trademarks(marks, inputMark, infringementList)

    response_data = {
        'data': [{'trademark': infringement[0].to_dict(), 'riskLevel': infringement[1]}
                 for infringement in infringementList],
        'lastEvaluatedKey': lastEvaluatedKey
    }

    return JsonResponse(response_data, safe=False, status=200)


def classifyCode(request):
    try:
        code = classify_code(request.GET.get('query'), get_label_decoder())

        # Read in JSON file and compare the code to get the corresponding classifying string
        with open("salvusbackend/info/codes.json", "r") as f:
            # Load JSON data from the file
            codes_dict = json.load(f)

            # Iterate over the "Goods" and "Services" keys in the codes_dict dictionary
            for category in codes_dict["codes"]:
                # Iterate over the key-value pairs in each category
                for key, value in codes_dict["codes"][category].items():
                    # Add the key-value pair to the flattened dictionary
                    codes_dict[value] = key  # Note that we switched the key and value

        return JsonResponse({"classification": codes_dict[code[0]]}, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)


def getSearchHistory(request):
    try:
        userInfo = find_userInfo_by_authtoken(request.headers.get('Authorization'))
        if not verify_authtoken(userInfo[0], request.headers.get('Authorization')):
            return HttpResponse("Unauthorized", status=401)

        return JsonResponse(db.get_search_history(userInfo[0]), safe=False, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)

# This code does entire process of downloading, cleaning, and inserting into database, uncomment as needed
# download_and_process_files()
#
# models = []
# for file in os.listdir():
#     if file.endswith(".xml"):
#         models.extend(make_trademark_objects(file))
#
# print("Inserting into database")
# db.insert_into_table(models)
# print("Finished inserting into database")

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
