import json

from django.http import HttpResponse, JsonResponse

import trademarkSearch.database as db
import trademarkSearch.textSimilarity as ts
from trademarkSearch.datacleaning import download_and_process_files, get_training_data
from trademarkSearch.models import Trademark, make_trademark_objects
import os
from salvusbackend.logger import logger
from authentication.database import compare_token_to_database
from salvusbackend.transformer import classify_code, get_label_decoder


# Create your views here.

def markDatabaseSearch(request):
    try:

        # auth_header = request.META.get('HTTP_AUTHORIZATION', '')  # Fetch the header
        # token = auth_header.split(' ')[1]  # Remove 'Bearer '
        # verify_authtoken(token)

        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')
        companyName = request.GET.get('companyName')
        email = request.GET.get('email')

        infringementList = []

        marks = db.get_trademarks_by_code(typeCode)
        db.save_search_into_table(inputMark, email, companyName, typeCode)

        ts.judge_exact_match(marks, inputMark, infringementList)
        ts.judge_ratio_fuzzy(marks, inputMark, infringementList)
        ts.judge_phonetic_similarity(marks, inputMark, infringementList)

        return JsonResponse([infringement.to_dict() for infringement in infringementList], safe=False,
                            status=200)

    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occurred", status=500)


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
        email = request.GET.get('email')
        return JsonResponse(db.get_search_history(email), safe=False, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)


def verify_authtoken(email, authtoken):
    try:
        # Finds the hashed password in the database
        return compare_token_to_database(email, authtoken)

    except Exception as e:
        logger.error(e)
        return False


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