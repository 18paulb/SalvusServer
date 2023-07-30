import json
import os
from models import Trademark, make_trademark_objects


# This function takes in trademark objects and creates a JSON file of them
def make_json_file_of_objects(trademarksList: list):
    file = open("data/json/trademarkObjects.json", "w")

    trademarks = []
    for trademark in trademarksList:
        temp_dict = dict(trademark.__dict__)

        # Removes case_file_descriptions because it is too big for JSON
        temp_dict.pop("case_file_descriptions")
        trademarks.append(temp_dict)

    json.dump(trademarks, file)
    file.close()


# This function takes in trademark objects and creates a JSON file of their mark_identification
def make_json_file_of_mark_identification(trademarksList: list):
    file = open("data/json/mark_identification.json", "w")

    code_dict = dict()

    for trademark in trademarksList:
        for code in trademark.get_codes():
            if code not in code_dict:
                code_dict[code] = []
                code_dict[code].append(trademark.get_mark_identification())
            if code in code_dict:
                code_dict[code].append(trademark.get_mark_identification())

    # See what keys are being produced
    for key in code_dict.keys():
        print(key + "\n")

    json.dump(code_dict, file)
    file.close()


# This function takes in a filepath to a JSON file of trademarks and returns a list of trademark objects
def load_in_json(filepath):
    file = open(filepath, "r")
    data = json.load(file)

    trademarks = []
    for mark in data:
        trademark = Trademark(mark["mark_identification"], mark["serial_number"], mark["codes"],
                              mark["case_file_descriptions"], mark["case_owners"], mark["date_filed"])
        trademarks.append(trademark)

    file.close()
    return trademarks
