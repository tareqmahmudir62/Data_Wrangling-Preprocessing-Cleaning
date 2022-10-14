#!/usr/bin/env python
# coding: utf-8

# # Project: Wrangling and Analyze Data

# In[1]:


import requests as r
import pandas as pd
import numpy as np
import tweepy
import urllib, json
import os
from PIL import Image
from io import BytesIO
import tweepy
from tweepy import OAuthHandler
import json
from timeit import default_timer as timer
import re
import matplotlib.pyplot as plt
import seaborn as sb


# ## Data Gathering
# In the cell below, gather **all** three pieces of data for this project and load them in the notebook. **Note:** the methods required to gather each data are different.
# 1. Directly download the WeRateDogs Twitter archive data (twitter_archive_enhanced.csv)

# In[2]:


df_1= pd.read_csv('twitter-archive-enhanced.csv')


# 2. Use the Requests library to download the tweet image prediction (image_predictions.tsv)

# In[3]:


folder= 'image_prediction'
if not os.path.exists (folder):
    os.makedirs(folder)
    
url= 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'
response= r.get(url)
with open ('image-predictions.tsv', 'wb') as file:
    file.write(response.content)
    
df_2= pd.read_csv('image-predictions.tsv', '\t')


# 3. Use the Tweepy library to query additional data via the Twitter API (tweet_json.txt)

# In[4]:


consumer_key = 'ReaVgydaEm5exW46DiALxP3r1'
consumer_secret = 'Ytk0pqEbhnIXA6R5aod4KpPO4ISXJp8x1hHnLtqQq4Gcus0vcc'
access_token = '150248066-rARUQEAEGugJ6vItNEghr2oBuMgRNJ5ByrW1thrJ'
access_secret = 'buzWzhKx11nta87VDr3XZAjUx9t5Js7Il3WMR8kZ0hLFE'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

'''# NOTE TO STUDENT WITH MOBILE VERIFICATION ISSUES:
# df_1 is a DataFrame with the twitter_archive_enhanced.csv file. You may have to
# change line 17 to match the name of your DataFrame with twitter_archive_enhanced.csv
# NOTE TO REVIEWER: this student had mobile verification issues so the following
# Twitter API code was sent to this student from a Udacity instructor
# Tweet IDs for which to gather additional data via Twitter's API
tweet_ids = df_1.tweet_id.values
len(tweet_ids)

# Query Twitter's API for JSON data for each tweet ID in the Twitter archive
count = 0
fails_dict = {}
start = timer()
# Save each tweet's returned JSON as a new line in a .txt file
with open('tweet_json.txt', 'w') as outfile:
    # This loop will likely take 20-30 minutes to run because of Twitter's rate limit
    for tweet_id in tweet_ids:
        count += 1
        print(str(count) + ": " + str(tweet_id))
        try:
            tweet = api.get_status(tweet_id, tweet_mode='extended')
            print("Success")
            json.dump(tweet._json, outfile)
            outfile.write('\n')
            print (tweet_id, 'success')
        except tweepy.TweepyException  as e:
            print("Fail")
            fails_dict[tweet_id] = e
            pass
end = timer()
print(end - start)
print(fails_dict)
'''
extract_list = []
for line in open('tweet_json.txt', 'r'):
    data= json.loads(line)
    extract_list.append({'twitter_id': data['id_str'],
                         'favorite_count': data['favorite_count'],
                         'retweet_count': data ['retweet_count']})
    
df_3= pd.DataFrame(extract_list, columns = ['twitter_id','retweet_count', 'favorite_count'])


# ## Assessing Data
# In this section, detect and document at least **eight (8) quality issues and two (2) tidiness issue**. You must use **both** visual assessment
# programmatic assessement to assess the data.
# 
# **Note:** pay attention to the following key points when you access the data.
# 
# * You only want original ratings (no retweets) that have images. Though there are 5000+ tweets in the dataset, not all are dog ratings and some are retweets.
# * Assessing and cleaning the entire dataset completely would require a lot of time, and is not necessary to practice and demonstrate your skills in data wrangling. Therefore, the requirements of this project are only to assess and clean at least 8 quality issues and at least 2 tidiness issues in this dataset.
# * The fact that the rating numerators are greater than the denominators does not need to be cleaned. This [unique rating system](http://knowyourmeme.com/memes/theyre-good-dogs-brent) is a big part of the popularity of WeRateDogs.
# * You do not need to gather the tweets beyond August 1st, 2017. You can, but note that you won't be able to gather the image predictions for these tweets since you don't have access to the algorithm used.
# 
# 

# ### Quality issues
# 
# 1.	Timestamp in archived_data is in one column, which needs three separate columns for months, days, and year
# 2.	We only need the original tweet. Hence, we can remove all the columns that include data associated with retweets
# 3.	Remove the unnecessary parts from at the end of each row of the 'text' columns
# 4.	It is not necessary to have separate columns of doggo,floofer, pupper,puppo as they include the same information
# 5.	In the 'name' column of the archived_data table, some invalid names that I have assumed can not be any dog's name. Hence, I have removed those names and 'None' entries with an empty string.
# 6.	The denominator should not be more than 10, and Numerator should be <= 10. But there are instances where these conditions were not followed. Because of this, the result it will produce will be invalid
# 
# 8.	It is pertinent to get rid of the HTML from the 'source' column in the archived_data table and replace them with 'Twitter for iPhone', 'Vine - Make a Scene', 'Twitter Web Client', 'TweetDeck.'
# 9.	In the image_data table, we don't need the 'img_num' column. Hence, we can remove that column from the table
# 10.	Remove duplicated rows from the jpg_url column in the 'image_data' table
# 

# ### Tidiness issues
# 1. twitter_id column in the json_data dataset is in object format, convert it to int
# 
# 2. merging all the tables together to make our effort of storing the dataframe easy
# 
# 3. In the image_data dataframe, column: p1,p2 and p3 include the name of the dogs in lower and uppercase letter. 
# 
# 4. renaming the twitter_id to tweet_id in the jason_data table to make make the merging swift

# ## Cleaning Data
# In this section, clean **all** of the issues you documented while assessing. 
# 
# **Note:** Make a copy of the original data before cleaning. Cleaning includes merging individual pieces of data according to the rules of [tidy data](https://cran.r-project.org/web/packages/tidyr/vignettes/tidy-data.html). The result should be a high-quality and tidy master pandas DataFrame (or DataFrames, if appropriate).

# #### Make copies of original pieces of data

# In[5]:


archived_data= df_1.copy()
image_data= df_2.copy()
json_data= df_3.copy()


# In[6]:


archived_data.sample(5)


# In[7]:


image_data.sample(5)


# In[8]:


json_data.sample(5)


# ### Issue #1:
# Time stamp in archived_data is in one column which needs 3 seperate columns for months, days and year

# #### Define:
# Creating four seperate columns for 'year', 'time','month','day' from the 'timestamp' column. Then drop the 'timestamp' column.

# #### Code

# In[9]:


archived_data['year']= pd.to_datetime(archived_data['timestamp']).dt.year
archived_data['time'] = pd.to_datetime(archived_data['timestamp']).dt.time
archived_data['month'] = pd.to_datetime(archived_data['timestamp']).dt.month
archived_data['day'] = pd.to_datetime(archived_data['timestamp']).dt.day
archived_data.drop("timestamp", axis=1,inplace=True)


# #### Test

# In[10]:


archived_data.sample(2)


# ### Issue #2:
# We only need original tweet.Hence,we can remove all the columns that includes data associated with retweets

# #### Define
# Using the drop method on the 'achived_data' dataframe to delete all the following columns (in_reply_to_user_id, in_reply_to_user_id, retweeted_status_id, retweeted_status_user_id,retweeted_status_timestamp,expanded_urls)

# #### Code

# In[11]:


archived_data.drop(['in_reply_to_user_id','in_reply_to_status_id', 'retweeted_status_id', 'retweeted_status_user_id','retweeted_status_timestamp','expanded_urls'], axis=1,inplace=True)


# #### Test

# In[12]:


archived_data.head()


# ### Issue #3:
# Remove the unnecessary parts from at the end of each rows of the 'text' coulmns
# #### Define
# 1. The entire text column was not visible in the workspace, so it was necessary to make it visible using the set_options method
# 2. Then using the str.split method each row was divided into 7 columns
# 3. Then rename the column as the title of each column was integer
# 4. selecting only the first column and remove the last part of each rows which had '10/13' like string part
# 5. Replace the output column with the 'text' column in the achived_data dataframe. 
# #### Code

# In[13]:


pd.set_option('display.max_colwidth',-1)
archived_test= archived_data.text.str.split('/',expand=True)
archived_test= archived_test.rename(columns={0: 'zero',1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven'})
archived_test.drop(['One','Two','Three','Four','Five','Six','Seven'], axis=1, inplace= True)
archived_test['zero']= archived_test.zero.str[:-2]
archived_data['text']= archived_test['zero']


# #### Test

# In[14]:


archived_data.pupper.value_counts()


# ### Issue #4:
# It is not necessary to have separate columns of doggo,floofer, pupper,puppo as they include the same information
# 
# 

# #### Define
# Create a different table (archive_dog) to have a clear view of all the columns together. Then Replace all the None values from each column and creathe a new column 'breed' by adding all the columns ('doggo','pupper','floofer','puppo'). Then drop all the dogs' name column and keep the newly created breed column. At last, add the breed column in the archived_data table
# 
# 

# #### Code

# In[15]:


archive_dog= archived_data [['name','doggo','floofer','pupper','puppo']]
archive_dog['doggo']= archive_dog.doggo.replace('None','')
archive_dog['floofer']= archive_dog.floofer.replace('None','')
archive_dog['pupper']= archive_dog.pupper.replace('None','')
archive_dog['puppo']= archive_dog.puppo.replace('None','')
archive_dog['breed']= (archive_dog['doggo'])+' ' +(archive_dog['floofer'])+' ' +(archive_dog['puppo'])+' ' +(archive_dog['pupper'])
archived_data ['breed']= archive_dog['breed']
archived_data.drop(['doggo','floofer','pupper','puppo'], axis=1, inplace=True)


# #### Test

# In[16]:


archived_data.sample(3)


# ### Issue #5:
# In the 'name' column of archived_data table there are some invalid names which I have assumed can not be the name of any dog. Hence, I have decided to remove those names and 'None' entries with an empty string. 
# #### Define
# To do that, all those invalid vaues were listed into 'invalid_names' list and using a for loop those name were replaced.
# 
# #### Code

# In[17]:


invalid_names= ['a','An','the','all','None','very','one','space','such','quite','unacceptable','this','officially','old','not','my','mad','light','life','just','infuriating','get','incredibly','his','getting','by','an','actually','O',]
for name in invalid_names:
    archived_data.name.replace(name,'',inplace= True)
print(archived_data['name'])





# #### Test

# In[18]:


archived_data.name.sample(5)


# ### Issue #6 and #7:
# Denominator should not be more than 10 and Numerator should be <= 10. But there are instances where these conditins were not followed. Becauyse of this the result it will produce will be invalid
# 
# Lets see in how many cases did not abide by this condition.
# #### Define
# using the min and max on these two columns and then summing up the number where the above condition was not followed.
# 
# #### Code

# In[19]:


sum(archived_data.rating_denominator!= 10)


# In[20]:


sum(archived_data.rating_numerator > 10)


# #### Test

# In[21]:


sum(archived_data.rating_denominator!= 10)
sum(archived_data.rating_numerator > 10)


# ### Issue #8:
# It is pertinent to get rid off the HTML from the 'source' column in the archived_data table and replace them with 
# 'Twitter for iPhone', 'Vine - Make a Scene', 'Twitter Web Client', 'TweetDeck'
# #### Define
# Use the replace method on the 4 HTML to replace them with 'Twitter for iPhone', 'Vine - Make a Scene', 'Twitter Web Client', 'TweetDeck'.
# 
# #### Code

# In[22]:


archived_data.source= archived_data.source.str.replace('<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>','Twitter for iPhone')
archived_data.source= archived_data.source.str.replace('<a href="http://vine.co" rel="nofollow">Vine - Make a Scene</a>','Vine - Make a Scene')
archived_data.source= archived_data.source.str.replace('<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>','Twitter Web Client')
archived_data.source= archived_data.source.str.replace('<a href="https://about.twitter.com/products/tweetdeck" rel="nofollow">TweetDeck</a>','TweetDeck')


# #### Test

# In[23]:


archived_data.source.value_counts()


# ### Issue #9:
# In the image_data table, we dont need the 'img_num' column. Hence, we cam remove that column for the table
# #### Define
# Using the drop method to drop the img_num column from the table
# 
# #### Code

# In[24]:


image_data= image_data.drop(['img_num'], axis=1)


# #### Test

# In[25]:


image_data.sample(2)


# ### Issue #10:
# Remove duplicated rows from the jpg_url column in the 'image_data' table
# #### Define
# use drop_duplicates() method to drop the duplicated rows from the 'jpg_url' column
# 
# #### Code

# In[26]:


image_data= image_data.drop_duplicates(subset ="jpg_url",
                     keep = False)


# #### Test

# In[27]:


image_data.jpg_url.duplicated().sum()


# ### Tidiness issues
# 1.	'twitter_id' column in the 'json_data' table is in object format. Convert it to 'int'
# 2.	Change the column name from twitter_id to tweet_id
# 3.	Only keep the rows where p1_dog, p2_dog and p3_dog is true in the image_data table
# 4.	Change the column name of the respective columns from the image_data table: (p1, p1_conf, p1_dog, p2, p2_conf, p2_dog, p3	p3_conf, p3_dog). Making these column names descriptive would be easier for the reader to grasp what these column titles intend to mean.
# 5.	In the image_data data frame, column: p1,p2 and p3 include the name of the dogs in lower and uppercase letters.
# 6.	Merging tables based on tweet_id as this column exists in all the tables
# 

# ### Issue #1:
# 'twitter_id' column in the 'json_data' table is in object format, convert it to 'int'
# #### Define
# Use the 'astype('int64')' method on 'twitter_id' column of 'json_data' table
# 
# #### Code

# In[28]:


json_data['twitter_id'] = json_data['twitter_id'].astype('int64')


# #### Test

# In[29]:


json_data.info()


# ### Issue #2:
# Change the column name from twitter_id to tweet_id
# #### Define
# Using the dataframe.rename function
# 
# #### Code

# In[30]:


json_data.rename(columns={'twitter_id': 'tweet_id'},inplace= True)


# #### Test

# In[31]:


json_data.info()


# ### Issue #3:
# Only keep the rows where p1_dog, p2_dog and p3_dog is true in the image_data table
# #### Define
# Selecting all the rows (p1_dog, p2_dog and p3_dog) where their values were true
# 
# #### Code

# In[32]:


image_data= image_data [((image_data['p1_dog']== True) & (image_data['p2_dog']== True) & (image_data['p3_dog']== True))]


# #### Test

# In[33]:


image_data [((image_data['p1_dog']== False) & (image_data['p2_dog']== False) & (image_data['p3_dog']== False))]


# ### Issue #4:
# Change the column name of the respective columns from the image_data table: (p1, p1_conf, p1_dog, p2, p2_conf, p2_dog, p3	p3_conf, p3_dog). By making these column names descriptive it would be easier for the reader to grasp what these column title intend to mean. 
# #### Define
# Using the df_rename function on these columns (p1, p1_conf, p1_dog, p2, p2_conf, p2_dog, p3, p3_conf, p3_dog) and change them as follows:
# p1 to prediction_1,
# p2 to prediction_2,
# p3 to prediction_3,
# p1_conf to confidence_1,
# p2_conf to confidence_2,
# p3_conf to confidence_3,
# p1_dog to confidence_result_1,
# p2_dog to confidence_result_2,
# p3_dog to confidence_result_3
# 
# #### Code

# In[34]:


image_data.rename(columns={'p1': 'prediction_1','p2': 'prediction_2', 'p3': 'prediction_3',
                          'p1_conf': 'confidence_1','p2_conf': 'confidence_2','p3_conf': 'confidence_3',
                          'p1_dog': 'confidence_result_1', 'p2_dog': 'confidence_result_2','p3_dog': 'confidence_result_3'},inplace= True)


# In[35]:


image_data


# ### Issue #5:
# In the image_data dataframe, column: p1,p2 and p3 include the name of the dogs in lower and uppercase letter.
# #### Define
# Capitalize the very first letter of all dogs' name in those columns using the str.title() method. 
# 
# #### Code

# In[36]:


image_data ['prediction_1'] = image_data ['prediction_1'].str.title()
image_data ['prediction_2'] = image_data ['prediction_2'].str.title()
image_data ['prediction_3'] = image_data ['prediction_3'].str.title()


# #### Test

# In[37]:


image_data ['prediction_1']
image_data ['prediction_2']
image_data ['prediction_3']


# ### Issue #6:
# Merging tables together based on tweet_id as this column exist in all the tables
# #### Define
# using the pd.merge () to merge the tables together
# 
# #### Code

# In[38]:


we_rate_dogs= archived_data.merge(image_data, on='tweet_id')


# In[39]:


we_rate_dogs_data=we_rate_dogs.merge(json_data, on='tweet_id')


# #### Test

# In[40]:


we_rate_dogs_data.info()


# ## Storing Data
# Save gathered, assessed, and cleaned master dataset to a CSV file named "twitter_archive_master.csv".

# In[41]:


we_rate_dogs_data.to_csv("twitter_archive_master.csv")


# #### Test

# In[42]:


pd.read_csv("twitter_archive_master.csv")


# ## Analyzing and Visualizing Data
# In this section, analyze and visualize your wrangled data. You must produce at least **three (3) insights and one (1) visualization.**

# ### Visualization

# #### The most common tweet source'e name

# In[43]:


common_source= we_rate_dogs_data['source'].value_counts()
common_source


# In[44]:


common_source. plot.bar(color = 'orange', fontsize = 13)
plt.title('Most common Twitter source', color = 'black')
plt.xlabel('Source Name', color = 'black')
plt.ylabel('Tweet counts', color = 'black', fontsize = '13');
plt.show()


# #### Common Dog's name

# In[45]:


Common_dog_name= we_rate_dogs_data.name.value_counts()[1:]
Common_dog_name


# #### Most popular dog's stages

# In[46]:


Common_dog_stage= we_rate_dogs_data.breed.value_counts()[1:]
Common_dog_stage


# ### Insights:
# 1.The most common source of tweet is posted from the iphone users
# 
# 2.The three most popular/common dog's names are: Cooper, Charlie and Oliver
# 
# 3.The most common stage is pupper,doggo,puppo respectively

# 

# In[47]:





# In[79]:


(we_rate_dogs_data.prediction_1.value_counts())


# In[80]:


(we_rate_dogs_data.prediction_2.value_counts())


# In[81]:


(we_rate_dogs_data.prediction_3.value_counts())


# #### The most common predicted dog in the first prediction

# In[89]:


sb.countplot(data=we_rate_dogs_data, y='prediction_1', order=we_rate_dogs_data.prediction_1.value_counts().index[0:15]).set(title="most common predicted dog's breed")


# In[118]:


we_rate_dogs_data['year']= we_rate_dogs_data['year'].astype(str)
we_rate_dogs_data.info()


# In[ ]:




