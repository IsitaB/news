from pymongo import MongoClient
import pandas as pd

from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.environ['MONGO_URI']

'''Connect to mongodb'''

client = MongoClient()
client = MongoClient(MONGO_URI)

db = client['nytdb']
articles_collection = db['articles']
print(db.list_collection_names())

def getMainMenuAndInput():
  print('Welcome to the NYT Analysis Dashboard \n')

  print("\n\nNews Search\n \
    \n\t 1 Get articles by topic, year, and month \
    \n\t 2 Get articles by topic and political ideology leaning \
    \n\t 3 Get articles by author and political ideology leaning \
    \n\t 4 Get articles by wordcount \
    \n\t 5 Get articles by key terms \
    \n\t 6 Get article Investigative headlines by year \
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
  
  print("\n\nAdmin\n \
    \n\t 19 Delete article \
    \n\t 20 Update article \
    \n\t 21 Insert dummy article")

  return input('\n\n\nEnter the number of a menu option or Q to exit \n')


def case1():
  topic = input('Please enter the topic of interest: ')
  year = input('Which year: ')
  month = input('Lastly, in which month? ')

  res = articles_collection.find({"$and": [{'News Desk': {"$in": [topic]}}, {'Year':year, 'Month': month}]})
  for article in res:
    print(article)

def case4():
  wordLimit = int(input("I get that reading takes a while. We'll suggest 10 articles within your word limit. What's your word limit for articles? "))
  articles = articles_collection.find({'Word Count': {"$lte": wordLimit}}).limit(10)
  for article in articles:
    print(article)

def case5():
  keyword = input("Give us a keyword you want to read about: ")
  articles = articles_collection.find({"$and": [{'Keywords': {"$regex": keyword}}, {'Year': {'$gte': 2022}}]}).limit(10)
  for article in articles:
    print(article)

def case6():
  articles = articles_collection.find({'News Desk': 'Investigative'}, {'_id':0, 'Headline':1, 'Year': 1}).sort('Year',-1).limit(1000)
  # clean this up by year
  for article in articles:
    print(article)

def case16():
  headlines = articles_collection.find({'Year': {'$gte': 2022}}, {'_id':0, 'Headline':1}).limit(10)
  for headline in headlines:
    print(headline)
  # throw in clickbait detection model

def case17():
  topics = articles_collection.distinct('News Desk')
  print(topics)


def main():
  user_input = ''
  while user_input != 'Q':
    user_input = getMainMenuAndInput()
    user_input = int(user_input)
    # throw in some input validation here
    if user_input == '00':
      print('Byeee')
      break
    elif user_input == 1:
      case1()
    elif user_input == 4:
      case4()
    elif user_input == 5:
      case5()
    elif user_input == 6:
      case6()
    elif user_input == 16:
      case16()
    elif user_input == 17:
      case17()

    break # for testing


main()
