import requests
import re
from bs4 import BeautifulSoup
import csv
import pandas as pd
import genanki

myModel = genanki.Model(
  1607392319,
  'Simple Model',
  fields=[
    {'name': 'Game'},
    {'name': 'Category'},
    {'name': 'Question'},
    {'name': 'Answer'},
    {'name': 'Dollar Amount'}
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<h2 style="font-weight:bold;">{{Category}} - ${{Dollar Amount}}</h2><br>{{Question}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br><em>Game {{Game}}<em>',
    },
  ])

games = range(8046, 8236) # season 36
myList = []
for aGame in games:
    r = requests.get(f'https://j-archive.com/showgame.php?game_id={aGame}')
    print(f"started scraping for game {aGame}")

    mySoup = BeautifulSoup(r.content.decode("utf-8"), 'html.parser')

    # single jeopardy
    for column in range(1, 7):
        activeColumn = mySoup.find_all(class_='category_name')[column-1].get_text() # active category
        for row in range(1, 6):
            if mySoup.find(id=f"clue_J_{column}_{row}") == None: # breaks loop for questions that are cut for time
                continue
            questionValue = row*200
            hasMedia = bool(mySoup.find(id=f"clue_J_{column}_{row}").a) # returns true if there is media
            questionInfo = {
                "game": aGame,
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
            if mySoup.find(id=f"clue_DJ_{column}_{row}") == None: 
                continue
            questionValue = row*400
            hasMedia = bool(mySoup.find(id=f"clue_DJ_{column}_{row}").a)
            questionInfo = {
                "game": aGame,
                "category": activeColumn,
                "question": mySoup.find(id=f"clue_DJ_{column}_{row}").get_text(),
                "answer": mySoup.find(id=f"clue_DJ_{column}_{row}_r").em.get_text(),
                "amount": questionValue,
                "media" : mySoup.find(id=f"clue_DJ_{column}_{row}").a.get('href') if hasMedia else None,
                "dj" : True
            }
            myList.append(questionInfo)

myDataFrame = pd.DataFrame(myList)
myDataFrame = myDataFrame.reset_index()
myDataFrame.to_csv("season36.csv", index=False)

# myDeck = genanki.Deck(
#     102031413,
#     'Test'
# )

# for index, row in myDataFrame.iterrows():
#     myNote = genanki.Note(
#         model=myModel,
#         fields=[str(row['game']), row['category'], row['question'], row['answer'], str(row['amount'])]) # ("DJ" if row['dj'] else "")
#     myDeck.add_note(myNote)

# genanki.Package(myDeck).write_to_file('test.apkg')
    