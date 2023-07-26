import re
import xml.etree.ElementTree as ET
import shutil
import zipfile
import request

# import required module
import os


# This is used to download files from the USPTO website
# Consider using multithreading to see if it speeds up the process of downloading
# Then consider using multiprocessing to see if it speeds up the process of cleaning files
def download_files(filenames):
    return

#This is used to remove elements of any tag from XML file
def remove_elements(element, tags):
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


def clean_data():
    # assign directory
    directory = 'data/original'
    
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):

            #Makes copy of file
            # source_file_path = directory + '/' + filename
            destination_file_path = 'data/cleaned/' + "cleaned" + filename[len(filename)-7 : len(filename)]
            # shutil.copy(source_file_path, destination_file_path)
            # Assume that the XML data is in a file called 'data.xml'


            #edits copied files
            tree = ET.parse(destination_file_path)
            # Get the root element of the XML document
            root = tree.getroot()
            
            #Removing Elements
            remove_elements(root, ['version', 'case-file-event-statements', 'correspondent', 'prior-registration-applications'])

            tree.write(destination_file_path)

# main()


# TODO: Implement

# tree = ET.parse('data.xml')
# root = tree.getroot()

# # 'grandparent' is the new parent for the 'children'
# new_parent = root.find('.//grandparent')

# # Find all 'children' and move them to 'grandparent'
# for child in root.findall('.//child'):
#     # We have to find the parent because the standard ElementTree module doesn't provide a getparent() method
#     # We assume the parent is an immediate child of root here
#     for parent in root:
#         if child in parent:
#             parent.remove(child)
#             new_parent.append(child)
#             break  # No need to check other parents

# # Save the resulting XML
# tree.write('new_data.xml')