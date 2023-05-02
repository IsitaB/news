from pymongo import MongoClient
import pandas as pd

from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.environ['MONGO_URI']

def getMainMenuAndInput():
  print('Welcome to the NYT Analysis Dashboard \n')

  print("\n\nNews Search\n \
    \n\t 1 Get articles by topic, year, and month \
    \n\t 2 Get articles by topic and political ideology leaning \
    \n\t 3 Get articles by author and political ideology leaning \
    \n\t 4 Get articles by wordcount \
    \n\t 5 Get articles by headline key terms \
    \n\t 6 Get article headlines by year \
    \n\t 7 Get articles by organization and get polical ideology leaning \
    \n\t 8 Get this week's top articles \
    \n\t 9 Get top articles by topic")

  print("\n\nTrend analysis\n \
    \n\t 10 See breakdown of news coverage by topics over time \
    \n\t 11 Get the coverage breakdown by topics this week")

  print("\n\nMore analysis\n \
    \n\t 12 Contributions by organization analysis \
    \n\t 13 Contributions by author over time analysis \
    \n\t 14 Author's coverage analysis \
    \n\t 15 Analysis of topics covered by high ranking vs low ranking authors \
    \n\t 16 Headline clickbait score")

  print("\n\nMight help you with your search\n \
    \n\t 17 Get all topics \
    \n\t 18 Get the org and authors breakdown")

  return input('\n\n\nEnter the number of a menu option or Q to exit \n')


def case1():
  print('one')


def main():
  '''Connect to mongodb'''

  client = MongoClient()
  client = MongoClient(MONGO_URI)

  db = client['nytdb']
  articles_collection = db['articles']
  print(db.list_collection_names())

  user_input = ''
  while user_input != 'Q':
    user_input = getMainMenuAndInput()
    # throw in some input validation here
    if user_input == 'Q':
      print('Byeee')
      break
    if int(user_input) == 1:
      case1()

    break # for testing


main()
