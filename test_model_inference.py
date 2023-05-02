from pymongo import MongoClient
import pandas as pd
import numpy as np
import pickle5 as pickle


client = MongoClient()
client = MongoClient('')

db = client['nytdb']
articles_collection = db['articles']
print(db.list_collection_names())

tfidf_reloaded = pickle.load(open('tfidf.pkl', "rb"))
model_reloaded = pickle.load(open('clickbaitmodel.pkl', "rb"))

res_df = pd.DataFrame(list(articles_collection.find({'Year': {'$gte': 2022}}, {'_id':0, 'Headline':1}).limit(10)))
tfidf_res_text = tfidf_reloaded.transform(res_df['Headline'])
preds = model_reloaded.predict(tfidf_res_text)

result = np.where(preds == 0, 'Not Clickbait', 'Clickbait')

res_df['Clickbait'] = result.tolist()
print(res_df.to_markdown())
