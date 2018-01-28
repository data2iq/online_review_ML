import json
import os
import pandas as pd
import itertools
import sys
import glob
from collections import defaultdict

def reviewData2DF(review_data):
    df = pd.DataFrame.from_dict(review_data)
    df['review'] = df['reviewTitle'] + ' ' + df['reviewComments']
    df = df.drop(['reviewTitle', 'reviewComments'], axis = 1)
    if 'badges' in df:
        df = df.drop(['badges'], axis = 1)
    if 'images' in df:    
        df = df.drop(['images'], axis = 1)
    if 'reviewAuthor' in df:
        df = df.drop(['reviewAuthor'], axis = 1)
    if 'reviewID' in df:
        df = df.drop(['reviewId'], axis = 1)
    return df

def productmeta2DF(meta_data):
    df = pd.DataFrame.from_dict([meta_data])
    
    ## drop fields:
    if 'mediaData' in meta_data:    
        df = df.drop(['mediaData'], axis = 1)
    if 'productUrl' in meta_data:
        df = df.drop(['productUrl'], axis = 1)
    if 'title' in meta_data:
        df = df.drop(['title'], axis = 1)
    if 'subtitle' in meta_data:
        df = df.drop(['subtitle'], axis = 1)
    
    # process 'specs' 
    if 'specs' in meta_data:
        df.loc[0, 'specs'] = u' '.join(df.loc[0, 'specs']).encode('utf-8').strip()
    else:
        df.loc[0, 'specs'] = 'NaN'
    
    # process 'description'
    if 'description' not in meta_data:
        df.loc[0, 'description'] = 'NaN'
    return df

def read_json(json_file):
    # Process Json fields
    review_header = ['rating', 'ratingDate', 'review', 'modelId']
    feature_header = ['description', 'specs', 'rating', 'brand', 'gender', 'price', 'productName', 'modelId']
    df_review = pd.DataFrame(columns=review_header)
    df_productspec = pd.DataFrame(columns=feature_header)
    # Default gender
    gender = 'N' # Neutral
    
    for key,value in json_file.iteritems():
        if key == 'productMeta':
            df_productspec = productmeta2DF(value)
        elif key == 'reviewData':
            if value:
                df_review = reviewData2DF(value)
        elif key == 'rating':
            rating = value
        elif key == 'gender':
            gender = value
        elif key == 'productName':
            productName = value
        elif key == 'brand':
            brand = value
        elif key == 'price':
            price = value
        elif key == 'modelId':
            modelId = value
    
    # Complete product spec data frame fields
    df_productspec['rating'] = rating
    df_productspec['brand'] = brand
    df_productspec['gender'] = gender
    df_productspec['price'] = price
    df_productspec['productName'] = productName
    df_productspec['modelId'] = modelId
    
    # Complete Review data frame fields
    df_review['modelId'] = [modelId] * df_review.shape[0]
    
    return df_productspec, df_review

def main(path):
    
    DATA_PATH = path   
    JSON_PATH = DATA_PATH + '/*/*.json'
    file_list = glob.glob(JSON_PATH) 

    # Create data frame for product features and reviews
    feature_dfs = []
    review_dfs = []

    # Read JSON files
    count = 0
    for json_file in file_list:
        json_data = json.load(open(json_file))
        df_product, df_review = read_json(json_data)
        feature_dfs.append(df_product)
        review_dfs.append(df_review)
        count += 1
    print "Processed total {:d} JSON files".format(count)
    
    # Create product spec DF
    print "Generate product spec data frame ..."
    productspec_df = pd.concat(feature_dfs)
    productspec_df.reset_index(drop=True, inplace=True)
    # Remove duplication
    productspec_df.drop_duplicates
    print "Product Spec DataFrame created with Shape: {}".format(productspec_df.shape)   
    
    # Create review DF
    print "Generate review data frame ..."
    reviewData_df = pd.concat(review_dfs)
    reviewData_df.reset_index(drop=True, inplace=True)
    # remove duplications
    reviewData_df.drop_duplicates
    duplicates = reviewData_df[reviewData_df.duplicated('review', keep=False)]
    duplicates.sort_values(by = ['review'])
    # Need to add back empty rows
    empty_review_rows = reviewData_df[reviewData_df['review'] == ' ']
    empty_review_rows.head(5)
    reviewData_df.drop_duplicates(['review'], keep = 'first', inplace=True)
    reviewData_df = pd.concat([reviewData_df, empty_review_rows])
    print "Review Data DataFrame Created with Shape: {}".format(reviewData_df.shape)

    # Write CSV file for product spect and review dataframe
    reviewData_df.to_csv('product_reviews.csv', encoding='utf-8', index=False)
    productspec_df.to_csv('product_features.csv', encoding='utf-8', index=False)

# How to run
# python JSON2DF.py "path to JSON data"
if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        print("Number of argument is incorrect!!")
    main(path)   
    