import re
import string
import time
import timeit
import itertools
import numpy as np
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer

def pretty_timedelta(fmt="%d:%02d:%02d", since=None, until=None):
    """Pretty-print a timedelta, using the given format string."""
    since = since or time.time()
    until = until or time.time()
    delta_s = until - since
    hours, remainder = divmod(delta_s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return fmt % (hours, minutes, seconds)

## clean up strings
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
def preprocess_stop_stem(text, punct=True, stem=False, stop=True, sent=False):
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
    return preprocess_stop_stem(clean_str(doc), punct=True, stem=False, stop=True, sent=True)

## Text label to sentiment
def create_senti_label_text(row):
    if row['rating'] >= 3.2:
        label = 'pos'
    elif row['rating'] <= 1.8:
        label = 'neg'
    else:
        label = 'neu'
    return label

## numerical label to sentiment
def create_senti_label_num(row):
    if row['rating'] >= 3.2:
        label = 0
    elif row['rating'] <= 1.8:
        label = 2
    else:
        label = 1 
    return label

## Sentiment score
def sentiment_result(score):
    if score >= 0.5:
        return 'pos'
    elif score > -0.5 and score < 0.5:
        return 'neu'
    elif score <= -0.5:
        return 'neg'

def get_train_test_docs(docs, labels, split = 0.8, shuffle=True):
    docs = np.array(docs, dtype=object)
    labels = np.array(labels)
    fmt = (len(docs), sum(map(len, docs)))
    print "Loaded %d docs (%g tokens)" % fmt
    
    if shuffle:
        np.random.seed(10)
        shuffle_indices = np.random.permutation(np.arange(len(labels)))
        docs = docs[shuffle_indices]
        labels = labels[shuffle_indices]
    train_frac = split
    split_idx = int(train_frac * len(labels))
    train_docs = docs[:split_idx]
    train_labels = labels[:split_idx]
    test_docs = docs[split_idx:]
    test_labels = labels[split_idx:]

    fmt = (len(train_docs), sum(map(len, train_docs)))
    print "Training set: %d docs (%d tokens)" % fmt
    fmt = (len(test_docs), sum(map(len, test_docs)))
    print "Test set: %d docs (%d tokens)" % fmt

    return train_docs, train_labels, test_docs, test_labels

def get_train_val_docs(docs, labels, split = 0.75, shuffle=True):
    docs = np.array(docs, dtype=object)
    labels = np.array(labels)
    fmt = (len(docs), sum(map(len, docs)))
    print "Loaded %d docs (%g tokens)" % fmt
    
    if shuffle:
        np.random.seed(10)
        shuffle_indices = np.random.permutation(np.arange(len(labels)))
        docs = docs[shuffle_indices]
        labels = labels[shuffle_indices]
    train_frac = split 
    split_idx = int(train_frac * len(labels))
    train_docs = docs[:split_idx]
    train_labels = labels[:split_idx]
    valid_docs = docs[split_idx:]
    valid_labels = labels[split_idx:]

    fmt = (len(train_docs), sum(map(len, train_docs)))
    print "Training set: %d docs (%d tokens)" % fmt
    fmt = (len(valid_docs), sum(map(len, valid_docs)))
    print "Validation set: %d docs (%d tokens)" % fmt

    return train_docs, train_labels, valid_docs, valid_labels