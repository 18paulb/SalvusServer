# SalvusServer

Important Links:

Chat GPT link to talk about high level Transformer Process
https://chat.openai.com/share/742e52a7-234c-4620-b1ef-b83e1117a104

Download Bulk Data
https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/

Case File Status-Code Definitions
https://www.uspto.gov/web/offices/com/sol/og/con/files/cons181.htm

Explains XML of Bulk Download
https://www.uspto.gov/sites/default/files/products/applications-documentation.pdf

Trademark Registered Images
https://developer.uspto.gov/product/trademark-24-hour-box-and-supplemental

Models Needed:

1. Model to judge text similarity
    - Train on Trademark cases where infringements have both passed and failed in court

2. Model to classify an image with a code
    - Train on registered in USPTO and the codes they already have, then compare codes to determine likeness of image

3. Model to take description text and give it a classification code (use classifications info as text and labels)

Trademark Object Information That Is Needed From Each Case-file

1. Serial Number
2. Filing Date ?
3. Mark Identification
4. Status Code
5. Classification codes
6. Case File Owners
7. Mark Drawing Code (Eventually)

Other Important Info:
<concurrent-use-in> a federal trademark registration of the same trademark to two or more unrelated parties, with each
party having a registration limited to a distinct geographic area.
<renewal-filed-in> A "T" indicates that a renewal application has been filed for this registration. Otherwise, this
field will contain an "F".

<case-file-statements> 
Code D1 - Disclaimer with Predetermined Text (The following Text will appear as part of the disclaimer, “No claim is made to the exclusive right to use…., apart from the mark as shown.”)
Code GS - The actual description of the product, use in combination with primary code to classify

<classification><status-code> could be pretty important
