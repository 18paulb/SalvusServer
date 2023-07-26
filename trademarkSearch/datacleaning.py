import re
import xml.etree.ElementTree as ET
import shutil
import zipfile
from lxml import etree
import requests

# import required module
import os


# This is used to download files from the USPTO website
# Consider using multithreading to see if it speeds up the process of downloading
# Then consider using multiprocessing to see if it speeds up the process of cleaning files
def download_files(filenames):

    url = "https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/apc18840407-20221231-01.zip"

    return

#This is used to remove elements of any tag from XML file
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

    #Removing Elements
    remove_elements(root, ['version', 'case-file-event-statements', 'correspondent', 'prior-registration-applications', 'application-information'])

    #Writes the cleaned file to this file
    tree.write(destination_file_path, pretty_print=True, xml_declaration=True, encoding="utf-8")

clean_data("apc18840407-20221231-10.xml", "cleaned.xml")