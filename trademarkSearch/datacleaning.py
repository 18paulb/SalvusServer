import os
import random
import re
import string
import zipfile
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from salvusbackend.logger import logger

import requests
from lxml import etree


# This is used to download files from the USPTO website
# The downloaded files sometimes don't appear in file structure until the program ends, wait for FILE DOWNLOADS FINISHED
# This function does all the downloading, unzipping, and cleaning of the files
def download_and_process_files():
    # url = "https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-10.zip"
    # base_url = "https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-"
    urls = [
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-76.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-77.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-78.zip',
    ]

    # Since downloading is I/O multi-threading works perfectly for this
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_results = [executor.submit(download_file, url) for url in urls]

    fileNames = []
    for future in future_results:
        result = future.result()
        if result is not None:
            fileNames.append(result)

    print("FILE DOWNLOADS FINISHED")

    print("Starting DataCleaning")

    # Since this is a CPU bound operation, multi-threading won't work because of the GIL, thus you need to use multi-processing
    with ProcessPoolExecutor(max_workers=5) as executor:
        for i, filename in enumerate(fileNames, 1):
            executor.submit(clean_data, filename, "cleaned-" + filename)

    # Removes original filenames as to only leave behind the cleaned files
    for filename in fileNames:
        os.remove(filename)
    print("DataCleaning Finished")


def download_file(url):
    print("starting download in thread: " + url + "\n")

    try:
        response = requests.get(url)
    except Exception as e:
        logger.error(e)
        return

    # This generates a random string name for the zipfile so that the threads do not overwrite each other
    filename = ''.join(random.choice(string.ascii_letters) for _ in range(10)) + ".zip"

    extracted_file = None

    try:
        with open(filename, 'wb') as file:
            file.write(response.content)

        # Create a ZipFile object
        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                # Extract all the contents of the zip file to current directory
                zip_ref.extractall()

                # Grab [0] because there should only be one file extracted
                extracted_file = zip_ref.namelist()[0]
        else:
            with open('failedUrls.txt', 'a') as file:
                file.write(url + '\n')

        print("finished extracting zipped file\n")

        # Delete the downloaded zip file after extracting its contents
        os.remove(filename)
    except Exception as e:
        logger.error(e)
        return

    return extracted_file


# This is used to remove elements of any tag from XML file
def remove_elements(element, tags):
    # Removes a lot of needless information from case-file-header - Might consider removing later
    if element.tag == 'case-file-header':
        for child in list(element):
            if child.tag != 'filing-date' and child.tag != 'registration-date' and child.tag != 'status-code' and child.tag != 'status-date' and child.tag != 'mark-identification' and child.tag != 'mark-drawing-code':
                element.remove(child)

    # Iterate over a copy of the element's children
    for child in list(element):
        if child.tag in tags:
            # Remove the child
            element.remove(child)
        else:
            # Recursively process child elements
            remove_elements(child, tags)


def remove_non_alphabetical(file_path):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove non-alphabetical characters using regex, keeps new lines and spaces
    content = re.sub(r'[^a-zA-Z\n\s]+', '', content)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)


# This function will take the original unzipped USPTO XML file and clean it, saving it to a new file
# Make sure all paths are correct
def clean_data(source_file_path, destination_file_path):
    parser = etree.XMLParser(remove_comments=True)
    # Get the root element of the XML document
    tree = etree.parse(source_file_path, parser)
    root = tree.getroot()

    case_files = root.findall('.//case-file')

    for case in case_files:
        # Remove Case File from parent
        case_file_parent = case.getparent()
        case_file_parent.remove(case)

        # Add Case File To Root
        root.append(case)

    # Removing Elements
    remove_elements(root, ['version', 'case-file-event-statements', 'correspondent', 'prior-registration-applications',
                           'application-information'])

    # Writes the cleaned file to this file
    tree.write(destination_file_path, pretty_print=True, xml_declaration=True, encoding="utf-8")


# Right now just get the code and descriptions from any case-file that only has one classification
def get_training_data(source_file_path):
    tree = etree.parse(source_file_path)
    root = tree.getroot()
    case_files = root.findall('.//case-file')

    codes_descriptions = []
    code = None
    code_descriptions_map = {}

    for case in case_files:
        try:
            classifications = case.findall('.//classifications/classification')
            case_file_statements = case.findall('.//case-file-statements/case-file-statement')

            # We're not going to worry about if there are multiple classifications for now, still have to figure out how to handle that
            if len(classifications) == 1:

                if classifications[0].find('.//primary-code') is not None:
                    code = classifications[0].find('.//primary-code').text
            else:
                continue

            for file_statement in case_file_statements:
                type_code = None
                description = None
                # TODO: There are issues if there are multiple statements, causes some labels to not be correct
                if file_statement.find(".//type-code") is not None and file_statement.find(".//text") is not None:
                    type_code = file_statement.find(".//type-code").text
                    description = file_statement.find(".//text").text

                    if code not in code_descriptions_map:
                        code_descriptions_map[code] = []

                # Makes sure to only get the GS codes and not the other ones
                if type_code[0:2] == "GS" and description is not None and code is not None:

                    # Right now we are limiting the data for each code to 1000, this can be changed later
                    if len(code_descriptions_map[code]) < 1000:
                        code_descriptions_map[code].append(description)

        except Exception as e:
            logger.error(e)
            continue

    # For each index in the value, return a pair of the key and the value
    for key, value in code_descriptions_map.items():
        for description in value:
            codes_descriptions.append((key, description))

    return codes_descriptions
