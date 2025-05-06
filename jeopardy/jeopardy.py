import requests
import re
from bs4 import BeautifulSoup
import csv
import pandas as pd

game = 6389
r = requests.get('https://j-archive.com/showgame.php?game_id=' + str(game))

mySoup = BeautifulSoup(r.content.decode("utf-8"), 'html.parser')
myList = []

# single jeopardy
for column in range(1, 7):
    activeColumn = mySoup.find_all(class_='category_name')[column-1].get_text()
    for row in range(1, 6):
        questionValue = row*200
        hasMedia = bool(mySoup.find(id=f"clue_J_{column}_{row}").a)
        questionInfo = {
            "game": game,
            "category": activeColumn,
            "question": mySoup.find(id=f"clue_J_{column}_{row}").get_text(),
            "answer": mySoup.find(id=f"clue_J_{column}_{row}_r").em.get_text(),
            "amount": questionValue,
            "media" : mySoup.find(id=f"clue_J_{column}_{row}").a.get('href') if hasMedia else None,
            "dj" : False
        }
        myList.append(questionInfo)

# double jeopardy
for column in range(1, 7):
    activeColumn = mySoup.find_all(class_='category_name')[column+5].get_text()
    for row in range(1, 6):
        questionValue = row*400
        hasMedia = bool(mySoup.find(id=f"clue_DJ_{column}_{row}").a)
        questionInfo = {
            "game": game,
            "category": activeColumn,
            "question": mySoup.find(id=f"clue_DJ_{column}_{row}").get_text(),
            "answer": mySoup.find(id=f"clue_DJ_{column}_{row}_r").em.get_text(),
            "amount": questionValue,
            "media" : mySoup.find(id=f"clue_DJ_{column}_{row}").a.get('href') if hasMedia else None,
            "dj" : True
        }
        myList.append(questionInfo)

myDataFrame = pd.DataFrame(myList)

print(myDataFrame)
# myDataFrame.to_csv("myTable.csv", index=False)

    




# myData = r.content.decode("utf-8")

# myData

# print(myData)
# with open("myFile.html", "w") as file:
#     file.write(myData)

# myCats = re.findall("<td class=\"category_name\">.*</td>", myData)
# myClues = re.findall("<td id=\"clue_._._.\" class=\"clue_text\">.*</td>", myData)
# myAnswers = re.findall("<em class=\"correct_response\">.*</em>", myData)
# myVals = re.findall("<td class=\"clue_value\">.*</td>", myData)

# # print(myCats[0:10])
# # print(myClues[0:10])
# # print(myAnswers[0:10])
# # print(myVals[0:10])
# def replacePhrases(string, vector):
#     for i in vector:
#         string = re.sub(i[0], i[1], string)
#     return string

# phrasesToReplace = [
#     ["<td id=\"clue_._._.\" class=\"clue_text\">", ""],
#     ["<span.*</span>", ""],
#     ["&amp;", "&"],
#     ["\\'", "'"]
# ]

# myCluesCleaned = []
# for aClue in myClues:
#     myMedia = ""
#     myClueNum = re.search("id=\"clue_._._.\"", aClue).group() #search for part of string that contains clue id
#     if re.search("<a href=\".*</a>", aClue): #if there is a link tag, <a>, in the clue (media);
#         myMedia = re.search("<a href=\".*</a>", aClue).group() #isolate that <a> tag
#         myMedia = re.search("\"http:.*\"", myMedia).group() #isolate the link within that <a> tag
#     replacePhrases(aClue, phrasesToReplace)
#     aClue = BeautifulSoup(aClue, "html.parser")
#     aClue = aClue.td.string
#     # aClue = re.sub("<td id=\"clue_._._.\" class=\"clue_text\">", "", aClue) #replace html boilerplate in actual clue
#     # aClue = re.sub("<span.*</span>", "", aClue)
#     # aClue = re.sub("&amp;", "&", aClue)
#     # aClue = re.sub("\\'", "'", aClue)
#     myDict = {
#         "id" : myClueNum,
#         "clue" : aClue,
#         "media" : myMedia
#         }
#     myCluesCleaned.append(myDict)
# myDataFrame = pd.DataFrame(myCluesCleaned)
# print(myDataFrame)
# # myTable = [myClues, myAnswers, myVals]

# # with open('myTable.csv', 'w', newline='') as tableFile:
# #     writer = csv.writer(tableFile)
# #     writer.writerows(myTable)