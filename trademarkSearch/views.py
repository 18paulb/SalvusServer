from django.shortcuts import render
import textSimilarity as ts
import database as db

# Create your views here.

def main(request):
    inputMark = input("Enter a mark: ")

    infringementList = []

    marks = db.get_trademarks_by_code('014')

    ts.judge_exact_match(marks, inputMark, infringementList)
    ts.judge_ratio_fuzzy(marks, inputMark, infringementList)

    print("Infringement List: \n")

    for (i, infringement) in enumerate(infringementList):
        print(str(i) + ": " + str(infringement) + "\n\n")

main(None)