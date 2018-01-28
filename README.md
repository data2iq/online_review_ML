# online Product Review

Goals:

1. Process a list of JSON files scraping from the web, each JSON file contains product features and review data
2. Build product features set and review text data
3. Conduct product feature extraction for ML downstream
4. Conduct sentiment ananlysis and create sentiment score for each product based on review data

Notebooks:

* JSON_EDA.ipynb : Process JSON Files

* Sentiment_model_survey.ipynb : Survey the free sentiment libraries.


Standalone Python Program

* JSON2DF.py

		* To run: python JSON2DF.py data/reviews where "data/review" is the path to all JSON files of different shoe brands

		* It produce 2 .csv files: product_features.cv has all the product features, produt_review.csv has all the reviews

* senti_analysis_vader.py

		* To run: python senti_analysis_vader.py product_review.csv

		* It produce senti_analysis.csv which contains the aggregated (mean) sentiment scores per shoe model based on all reviews
