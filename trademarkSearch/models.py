from django.db import models
import xml.etree.ElementTree as ET
import json


# This is not a django model, but it is a model for the trademark object
class Trademark:

    def __init__(self, mark_identification=None, serial_number=None, codes=None, case_file_descriptions=None,
                 case_owners=None, date_filed=None, activeStatus=None):
        self.mark_identification = mark_identification if mark_identification is not None else ""
        self.serial_number = serial_number if serial_number is not None else ""
        self.codes = codes if codes is not None else []
        self.case_file_descriptions = case_file_descriptions if case_file_descriptions is not None else []
        self.case_owners = case_owners if case_owners is not None else []
        self.date_filed = date_filed if date_filed is not None else ""
        self.activeStatus = activeStatus if activeStatus is not None else ""

    def __str__(self):
        return "Case Owners: " + "\n".join(
            self.case_owners) + "\nDate Filed: " + self.date_filed + "\nactiveStatus: " + self.activeStatus + "\nSerial Number: " + self.serial_number + "\nMark Identification: " + self.mark_identification + "\nCodes: " + " ".join(
            self.codes) + "\nDescriptions: " + "\n".join(self.case_file_descriptions) + "\n\n"

    def to_dict(self):

        # Get rid of duplicates in lists (includes case sensitivity)
        case_owners = list(set([s.lower() for s in self.case_owners]))
        case_file_descriptions = list(set([s.lower() for s in self.case_file_descriptions]))
        codes = list(set([s.lower() for s in self.codes]))

        return {
            'mark_identification': self.mark_identification,
            'serial_number': self.serial_number,
            'codes': codes,
            'case_file_descriptions': case_file_descriptions,
            'case_owners': case_owners,
            'date_filed': self.date_filed,
            'activeStatus': self.activeStatus
        }


# The input of this will be the cleaned XML file Make sure the file structure at this point is
# <trademark-applications-daily><case-file></case-file></trademark-applications-daily> With no other elements in
# between trade-mark-applications and case-file
def make_trademark_objects(filename):
    listOfTrademarks = []
    # Info in files to help classify trademarks further
    code_map = json.load(open("salvusBackend/info/status-codes.json", 'r'))

    file = open(filename, "r")

    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except Exception as e:
        print(e)
        return []

    for caseFile in root:

        newTrademark = Trademark()

        serial = caseFile.find("serial-number")
        mark = caseFile.find("case-file-header/mark-identification")
        date_filed = caseFile.find("case-file-header/filing-date")
        codes = caseFile.findall("classifications/classification/primary-code")
        case_file_statements = caseFile.findall("case-file-statements/case-file-statement")
        case_owners = caseFile.findall("case-file-owners/case-file-owner/party-name")

        # incorporate this data into the trademark object
        status_code = caseFile.find("case-file-header/status-code")

        if mark is not None and serial is not None:
            newTrademark.serial_number = serial.text.lower() if serial is not None else ""
            newTrademark.mark_identification = mark.text.lower() if mark is not None else ""
            newTrademark.date_filed = date_filed.text.lower() if date_filed is not None else ""
            newTrademark.activeStatus = code_map.get(status_code.text.lower()) if status_code is not None else ""

            for code in codes:
                newTrademark.codes.append(code.text)

            for statement in case_file_statements:
                typecode = statement.find("type-code").text
                description = statement.find("text").text

                if typecode is None or description is None:
                    continue

                if typecode[0:2] == "GS":
                    newTrademark.case_file_descriptions.append(description)

            for owner in case_owners:
                newTrademark.case_owners.append(owner.text)

            listOfTrademarks.append(newTrademark)

    return listOfTrademarks
