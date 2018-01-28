import json
import pandas as pd
import numpy as np
import itertools
import sys
import re
from collections import defaultdict
import string
from sklearn.metrics import classification_report, accuracy_score, f1_score
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

## clean up strings (Not used)
def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"(.)\1\1+$", r"\1", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

## preprocess punctutation, stop words, stemming
def preprocess_stop_stem(text, punct=True, stem=False, stop=False, sent=False):
    if punct:
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        text = regex.sub('', text)
    tokens = word_tokenize(text) 
    if stop:
        stop = stopwords.words('english')
        tokens =[word for word in tokens if word not in stop]
        tokens = [word.lower() for word in tokens]
    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]
    if sent:
        tokens = ' '.join(tokens)
    return tokens

## preproces a sentence
def preprocess_doc(doc):
    return preprocess_stop_stem(clean_str(doc), punct=True, stem=False, stop=False, sent=True)

## label to sentiment
def create_senti_label(row):
    if row['rating'] >= 3.7:
        label = 'pos'
    elif row['rating'] <= 1.25:
        label = 'neg'
    else:
        label = 'neu'
    return label

## Sentiment score
## convert to sentiment score between 0 - 10
def sentiment_score(score):
    return (score - (-1.0))*5
    
## Labe based on score range of 0 - 10
## If > 7.5: pos
## if < 2.5: neg
## between 2.5 and 7.5 neu
def sentiment_label(score):
    if score >= 7.5:
        return 'pos'
    elif score > 2.5 and score < 7.5:
        return 'neu'
    elif score <= 2.5:
        return 'neg'

def main(review_table):
    reviewData_df = pd.read_csv(review_table)
    reviewData_df['review'] = reviewData_df['review'].apply(preprocess_doc)
    reviewData_df['rate_label'] = reviewData_df.apply(create_senti_label, axis = 1)
    analyzer = SentimentIntensityAnalyzer()
    
    print "Analyzing Individual Review Sentiment ..."
    senti_score = []
    neg_score = []
    pos_score = []
    neu_score = []
    senti_label = []
    count = 0
    for review in reviewData_df.loc[:, 'review']:
        vs = analyzer.polarity_scores(review)
        senti_score.append(sentiment_score(vs['compound']))
        neg_score.append(sentiment_score(vs['neg']))
        pos_score.append(sentiment_score(vs['pos']))
        neu_score.append(sentiment_score(vs['neu']))
        senti_label.append(sentiment_label(sentiment_score(vs['compound'])))
    reviewData_df['senti_score'] = senti_score
    reviewData_df['senti_label'] = senti_label
    reviewData_df['neg_score'] = neg_score
    reviewData_df['pos_score'] = pos_score
    reviewData_df['neu_score'] = neu_score 
    
    print "Vader Sentiment compared to Product Rating {:f} match".format(accuracy_score(reviewData_df['rate_label'], \
                                                                                    reviewData_df['senti_label']))
    print "Aggregate Review Sentiment by Shoe Model ..." 
    reviewData_df_agg = reviewData_df.groupby('modelId')
    reviewData_agg = reviewData_df_agg['rating', 'senti_score', 'neg_score', 'pos_score', 'neu_score'].apply(np.mean)
    senti_label_agg = []
    for score in reviewData_agg.loc[:, 'senti_score']:
        senti_label_agg.append(sentiment_label(score))
    reviewData_agg['senti_label'] = senti_label_agg
    
    # Write to CSV file
    reviewData_agg.reset_index().to_csv('senti_analysis.csv', encoding='utf-8', index=False)
    
# How to run
# python senti_analysis_vader.py "review_table"
if __name__ == '__main__':
    if len(sys.argv) == 2:
        review_table = sys.argv[1]
    else:
        print("Number of argument is incorrect!!")
    main(review_table) 