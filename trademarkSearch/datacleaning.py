import os
import random
import re
import string
import zipfile
from concurrent.futures import ThreadPoolExecutor

import requests
from lxml import etree

# This is used to download files from the USPTO website
# The downloaded files sometimes don't appear in file structure until the program ends, wait for FILE DOWNLOADS FINISHED
# This function does all the downloading, unzipping, and cleaning of the files
def download_and_process_files():
    # url = "https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-10.zip"
    base_url = "https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-"

    urls = [
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc230101.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc230102.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc230103.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc230104.zip',
        'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc230105.zip'
    ]

    with ThreadPoolExecutor(max_workers=5) as executor:
        future = [executor.submit(download_file, url) for url in urls]

    fileNames = []
    for tmp in future:
        fileNames.append(tmp.result())

    print("FILE DOWNLOADS FINISHED")

    print("Starting DataCleaning")

    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, filename in enumerate(fileNames, 1):
            executor.submit(clean_data, filename, "cleaned" + str(i) + ".xml")

    # Removes original filenames as to only leave behind the cleaned files
    for filename in fileNames:
        os.remove(filename)
    print("DataCleaning Finished")


def download_file(url):
    print("starting download in thread: " + url + "\n")

    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
        return

    # This generates a random string name for the zipfile so that the threads do not overwrite each other
    filename = ''.join(random.choice(string.ascii_letters) for i in range(10)) + ".zip"

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

        print("finished extracting zipped file\n")

        # Delete the downloaded zip file after extracting its contents
        os.remove(filename)
    except Exception as e:
        print(e)
        return

    return extracted_file


# This is used to remove elements of any tag from XML file
def remove_elements(element, tags):
    # Removes a lot of needless information from case-file-header - Might consider removing later
    if element.tag == 'case-file-header':
        for child in list(element):
            if child.tag != 'filing-date' and child.tag != 'registration-date' and child.tag and 'status-code' and child.tag != 'status-date' and child.tag != 'mark-identification' and child.tag != 'mark-drawing-code':
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
