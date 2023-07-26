from django.db import models
import xml.etree.ElementTree as ET
import json

# Create your models here.

#This is not a django model, but it is a model for the trademark object
class Trademark:

    def __init__(self, mark_identification=None, serial_number=None, codes=None, case_file_descriptions=None, case_owners=None, date_filed=None, activeStatus=None):
        self.mark_identification = mark_identification if mark_identification is not None else ""
        self.serial_number = serial_number if serial_number is not None else ""
        self.codes = codes if codes is not None else []
        self.case_file_descriptions = case_file_descriptions if case_file_descriptions is not None else []
        self.case_owners = case_owners if case_owners is not None else []
        self.date_filed = date_filed if date_filed is not None else ""
        self.activeStatus = activeStatus if activeStatus is not None else ""
    
    def __str__(self):
        return "Case Owners: " + "\n".join(self.case_owners) + "\nDate Filed: " + self.date_filed + "\nactiveStatus: " + self.activeStatus + "\nSerial Number: " + self.serial_number + "\nMark Identification: " + self.mark_identification + "\nCodes: " + " ".join(self.codes) + "\nDescriptions: " + "\n".join(self.case_file_descriptions) + "\n\n"
    
# The input of this will be the cleaned XML file
# Make sure the file structure at this point is <trademark-applications-daily><case-file></case-file></trademark-applications-daily>
# With no other elements in between trade-mark-applications and case-file
def make_trademark_objects(file):

    listOfTrademarks = []
    #Info in files to help classify trademarks further
    code_map = json.load(open("salvusbackend/trademarkSearch/info/status-codes.json", 'r'))

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
        case_file_descriptions = caseFile.findall("case-file-statements/case-file-statement/text")
        case_owners = caseFile.findall("case-file-owners/case-file-owner/party-name")

        #incorporate this data into the trademark object
        status_code = caseFile.find("case-file-header/status-code")

        if (mark != None and serial != None):
            newTrademark.serial_number = serial.text.lower() if serial is not None else ""
            newTrademark.mark_identification = mark.text.lower() if mark is not None else ""
            newTrademark.date_filed = date_filed.text.lower() if date_filed is not None else ""
            newTrademark.activeStatus = code_map.get(status_code.text.lower()) if status_code is not None else ""


            for code in codes:
                newTrademark.codes.append(code.text) 

            for description in case_file_descriptions:
                newTrademark.case_file_descriptions.append(description.text)
            
            for owner in case_owners:
                newTrademark.case_owners.append(owner.text)

            listOfTrademarks.append(newTrademark)

    return listOfTrademarks
