from pymongo import MongoClient
import pandas as pd
import numpy as np
import datetime
from bson import ObjectId
from pymongo.collection import ReturnDocument
from datetime import timedelta
from bson import SON
from datetime import datetime, timezone
import pytz
import pymongo
import re

from dotenv import load_dotenv
import os
import pickle5 as pickle

load_dotenv()
MONGO_URI = os.environ['MONGO_URI']

'''Connect to mongodb'''

client = MongoClient()
client = MongoClient(MONGO_URI)

db = client['nytdb']
articles_collection = db['articles']
print(db.list_collection_names())
'''Load clickbait model'''
tfidf_reloaded = pickle.load(open('tfidf.pkl', "rb"))
model_reloaded = pickle.load(open('clickbaitmodel.pkl', "rb"))
def getMainMenuAndInput():
  print('Welcome to the NYT Analysis Dashboard \n')

  print("\nNews Search\n \
    \n\t 1 Get articles by news sector, year, and month \
    \n\t 3 Get articles by author \
    \n\t 4 Get articles by wordcount \
    \n\t 5 Get articles by key terms \
    \n\t 6 Get article Investigative headlines by year \
    \n\t 8 Get the top articles of January 2022 \
    \n\t 9 Get top articles by topic \
    \n\t 12 Get total word count by topic")

  print("\n\nTrend analysis\n \
    \n\t 10 See breakdown of news coverage by topics over time \
    \n\t 11 Get the word count for every year and month")

  print("\n\nMore analysis\n \
    \n\t 16 Headline clickbait score")

  print("\n\nMight help you with your search\n \
    \n\t 17 Get all news sectors \
    \n\t 18 Get the org and authors breakdown")
  
  print("\n\nAdmin\n \
    \n\t 19 Insert dummy article \
    \n\t 20 Update article \
    \n\t 21 Delete article"    
        )

  return input('\n\n\nEnter the number of a menu option or Q to exit \n')

def printHelper(article):
  print('Headline:', article['Headline'])
  print('  ', article['Byline'],'|', article['Pub Date'][:10], '\n  ', article['Snippet'])
  print('Access here', article['Web URL'])
  print('\n\n')

def case1():
  topic = input('Please enter the topic of interest: ')
  year = int(input('Which year: '))
  month = int(input('Lastly, in which month? '))

  articles = articles_collection.find({'News Desk': topic, 'Year': year, 'Month': month})
  for article in articles:
    printHelper(article)

def case3():
  author = input('Please enter the name of author of interest: ')
  # check if author contains middlename, or just first and last
  if author == '':
    print("No author provided") 
    return
  elif len(author.split()) == 2:
    author = author.split()
    author.insert(1, 'None')
    author = ' '.join(author)

  regex = re.compile(author, re.IGNORECASE)
  articles = articles_collection.find({ 'Authors': { "$elemMatch": { "$regex": regex } } })
  for article in articles:
    printHelper(article)


def case4():
  wordLimit = int(input("I get that reading takes a while. We'll suggest 10 articles within your word limit. What's your word limit for articles? "))
  articles = articles_collection.find({'Word Count': {"$lte": wordLimit}}).limit(10)
  for article in articles:
    printHelper(article)

def case5():
  keyword = input("Give us a keyword you want to read about: ")
  articles = articles_collection.find({"$and": [{'Keywords': {"$regex": keyword}}, {'Year': {'$gte': 2022}}]}).limit(10)
  for article in articles:
    printHelper(article)
    print('Word Count:', article['Word Count'])

def case6():
  articles = articles_collection.find({'News Desk': 'Investigative'}, {'_id':0, 'Headline':1, 'Year': 1}).sort('Year',-1).limit(1000)
  # clean this up by year
  for article in articles:
    printHelper(article)

def case10():
  articles = articles_collection.aggregate(
     [{"$group": {"_id": {"year": "$Year", "month": "$Month", "topic": "$Keywords"}, 
      "count": {"$sum": 1}}}, 
      {"$project": {"_id": 0, "year": "$_id.year", "month": "$_id.month", "topic": "$_id.topic", "count": 1}}, 
      {"$sort": {"year": 1, "month": 1, "count": -1}}])
  for article in articles:
    print(article)

def case11():
  result = db.command(
      'mapReduce',
      'articles',
      map="function() { emit({ year: this.Year, month: this.Month }, this['Word Count']); }",
      reduce="function(key, values) { return Array.sum(values); }",
      out='word_count_by_month_year'
  )

  articles = db.word_count_by_month_year.find()
  for article in articles:
    print(article)

def case12():
  
  results = articles_collection.aggregate([{'$group': {'_id': '$Keywords', 'word_count': {'$sum': '$Word Count'}}},    
                                                      {'$sort': {'word_count': -1}}])
  for result in results:
    print(result)

def case8():
    top_articles = articles_collection.find({
    "Pub Date": {"$regex": "^2022-01-"}
    }).sort([("Word Count", pymongo.DESCENDING)]).limit(10)

    # Check if there are no articles for January 2022
    if not top_articles:
        print("No articles found for January 2022.")
        return

    # Print the headlines of the top articles
    print("---Headlines of top 10 articles of January 2022:---")
    for article in top_articles:
        print(article['Headline'])

def case9():
    topic = input("Enter a topic: ")
    articles = db.articles.find({"Keywords": {"$regex": f".*{topic}.*"}}).sort([('Word Count', pymongo.DESCENDING)]).limit(10)
    count = db.articles.count_documents({"Keywords": {"$regex": f".*{topic}.*"}})
    if count == 0:
        print("No articles found.")
        return
    print(f"Top {min(10, count)} articles on '{topic}':\n")
    for i, article in enumerate(articles):
        print(f"{i+1}. {article['Headline']}")       

def case16():
  tfidf_reloaded = pickle.load(open('tfidf.pkl', "rb"))
  model_reloaded = pickle.load(open('clickbaitmodel.pkl', "rb"))

  res_df = pd.DataFrame(list(articles_collection.find({'Year': {'$gte': 2022}}, {'_id':0, 'Headline':1}).limit(10)))
  tfidf_res_text = tfidf_reloaded.transform(res_df['Headline'])
  preds = model_reloaded.predict(tfidf_res_text)

  result = np.where(preds == 0, 'Not Clickbait', 'Clickbait')

  res_df['Clickbait'] = result.tolist()
  print(res_df.to_markdown())

def case17():
  topics = pd.DataFrame(list(articles_collection.aggregate([{'$group': {'_id': '$News Desk', 'count': {'$sum':1}}}])))
  topics = topics.rename(columns={'_id':'News Desk'})
  print(topics.to_markdown())

def case19():
    # Insert dummy article
    dummy_article = {
        "Headline": "Dummy Article",
        "Byline": "John Doe",
        "Snippet": "This is a dummy article for testing purposes.",
        "Keywords": ["dummy", "testing"],
        "Web URL": "https://example.com"
    }
    result = db.articles.insert_one(dummy_article)
    print("Dummy article inserted with ID:", result.inserted_id)

def case20():
    # Update article by ID
    article_id = input("Enter the ID of the article you want to update: ")
    result = db.articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"Headline": "Updated Headline", "Byline": "Updated Byline"}}
    )
    if result.modified_count > 0:
        print("Article updated successfully.")
    else:
        print("Article not found.")

def case21():
    # Delete article by ID
    article_id = input("Enter the ID of the article you want to delete: ")
    result = db.articles.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count == 1:
        print("Article deleted successfully.")
    else:
        print("Article not found.")



def main():
  user_input = ''
  while user_input != '00':
    user_input = getMainMenuAndInput()
    user_input = int(user_input)
    # throw in some input validation here
    if user_input == '00':
      print('Byeee')
      break
    elif user_input == 1:
      case1()
    elif user_input == 3:
      case3()
    elif user_input == 4:
      case4()
    elif user_input == 5:
      case5()
    elif user_input == 6:
      case6()
    elif user_input == 10:
      case10()
    elif user_input == 11:
      case11()
    elif user_input == 12:
      case12()
    elif user_input == 8:
      case8()  
    elif user_input == 9:
      case9()  
    elif user_input == 16:
      case16()
    elif user_input == 17:
      case17()
    elif user_input == 19:
      case19()
    elif user_input == 20:
      case20()
    elif user_input == 21:
      case21() 


main()
