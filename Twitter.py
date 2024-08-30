#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
import tweepy
import re
import pymongo
from pymongo import MongoClient
import json
import pandas as pd
import emoji
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
import time


# In[2]:


#set ค่าต่างๆสำหรับการใช้งาน api
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''


# In[25]:


auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
    
hashtag_phrase = '#BLACKPINK' #ค้นหาจากตรงนี้


# In[22]:


client = MongoClient('localhost',27017)
db = client.tweet_db
tweet_collection = db.tweet_collectionV3
tweet_collection.create_index([('id',pymongo.ASCENDING)] , unique = False)


# In[23]:


#เป็น func. ทดลองเวลา
def getDateTime(jsonObj):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(jsonObj._json['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))


# In[26]:


if __name__ == '__main__':
    for tweet in tweepy.Cursor(api.search, q=hashtag_phrase,count = 1000 , tweet_mode="extended" 
                               , lang = "th").items():
            
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ""
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +"/"+entity_hashtag[i]["text"]
                
            try:
                full_text = tweet._json["retweeted_status"]["full_text"].replace('\n',' ')
                fav_count = tweet._json["retweeted_status"]["favorite_count"]
            except:
                full_text = tweet._json["full_text"].replace('\n',' ')
                fav_count = tweet._json["favorite_count"]

            #clean ไม่เอา emoji และ ลิ้งที่ติดมากับ tweet
            allchars = [str for str in full_text]
            emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
            full_text = ' '.join([str for str in full_text.split() if not any(i in str for i in emoji_list)])
            full_text = full_text.replace('"',"")
            full_text = full_text.replace("!","")
            full_text = full_text.replace("​","")
            full_text = full_text.replace("-","")
            full_text = re.sub(r'https?:\/\/.*[\r\n]*', '', full_text, flags=re.MULTILINE)

            data = {
                "user_id" : tweet._json["user"]["screen_name"],
                "full_text" : full_text,
                "favorite_count" : fav_count,
                "retweet_count" : tweet._json["retweet_count"],
                "follower_count" : tweet._json["user"]["followers_count"],
                "all_hashtag" : hashtag,
                "time" : tweet._json["created_at"]
            }
            print(full_text)
            try:
                db.tweet_collectionV3.insert(data)
                print('ok')

            except Exception as e:
                print(e)
                print('error')


# In[ ]:




