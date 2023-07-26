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



If we want to use it on Trademark infringement. We may have to get Data of trademark infringement cases and label them
 - But could we get enough data for it to be viable?
 - That's a lot of data we would need to hand process

Ex for this (Pretty sure this falls under a Supervised Learning NLP Model)
Let's say I have an array of word marks
    text = ["Text1", "Text2", ...]

I would need an array of labels that accurately describes the text, an example would be a binary label with 0 being an infringement and 1 being fine
(Although I don't understand how that would work, would the entire model just predict similarity to one wordmark?)

    labels = [0, 1, ...]


Cleaning Data
* Remove any wordmarks with exact texts? Not sure if that would be good but if owned by the same company it should be fine

How To Make Word Mark Searches Efficient

* Obviously we will have a LOT of data and it isn't efficient to compare text against every possible word mark
* We need to really figure out how to shrink the data we are comparing against

A couple ideas:
    1. Separate each mark-identification we have into a JSON file (or separate JSON files because of so much data) that falls under codes
        that way when we have to do a search, we only need to look for the marks that fall under the same or similar codes

    SIDE NOTE: We can train a model to classify a code for any text from the user side since we have so much data on what falls under what code, that will save the user some work.
    We would just use the labeling example from above
    * Well it COULD save the user some work, it depends on the text they are putting in. Is asking the User to put in a description any easier than having them manually choose a code?

    2. Honestly I can't think of anything else

Judging Word Mark Similiarity
    1. Exact Matches Obviously
        - Though for this how do we separate and compare phrases?
    2. More Rough Matches (Fuzzy Search Algorithms?)
    3. Cosine Values, Comparing Semantics Using BERT (Needs more research to see if reliable or not)
    4. Not looking at the word mark itself but rather the people who uses it as that could be an infringement if they are (not sure how this would work)


Models Needed;

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

How To Tell If Mark Is Style Alive Or Not (Double Check That They Are Actually Abandoned)

Dead
<abandonement-date> 
<cancellation-date>
Possible: <trademark-in>
<cancellation-pending-in>

Alive
<republished-12c-date>

Other Important Info:
<concurrent-use-in> a federal trademark registration of the same trademark to two or more unrelated parties, with each party having a registration limited to a distinct geographic area.
<renewal-filed-in> A "T" indicates that a renewal application has been filed for this registration. Otherwise, this field will contain an "F".

TODO: Look more into these, it may be important
<case-file-statements> 
Code D1 - Disclaimer with Predetermined Text (The following Text will appear as part of the disclaimer, “No claim is made to the exclusive right to use…., apart from the mark as shown.”)

<classification><status-code> could be pretty important
