# Sentiment analysis
Sentiment analysis of Tweets using Deep Learning.

## Requirements
Tweeter tokenizer:
`pip install git+https://github.com/erikavaris/tokenizer.git`

## Ideas for improvements
* Lemmatisation
* Include more datasets into training phase
* Better emoticon gestion
* TF-idf, n-grams, skip-grams

## Ressources
**Most interesting:**

* Sentiment140 (neg, neu, pos) {1.6M}: https://www.kaggle.com/kazanova/sentiment140
* Valence (all 7 targets) {< 10000 ?}: Teacher's pdf
* Self-driving cars tweets (very neg, neg, neu, pos, very pos) {7k}: https://www.figure-eight.com/wp-content/uploads/2016/03/Twitter-sentiment-self-drive-DFE.csv


**Slightly less interesting:**

* Twitter airline (neg, neu, pos){14k}: https://www.kaggle.com/crowdflower/twitter-airline-sentiment/home
* Twitter-sentiment-analysis (neg, pos) {100k}: https://www.kaggle.com/c/twitter-sentiment-analysis2/data
* Nuclear energy tweets (neg, neu, pos, unrelated, unsure) {190}: https://www.figure-eight.com/wp-content/uploads/2016/03/1377191648_sentiment_nuclear_power.csv
* Brands & products tweets (neg, neu, pos) {9k}: https://www.figure-eight.com/wp-content/uploads/2016/03/judge-1377884607_tweet_product_company.csv
* Apple tweets (neg, neu, pos) {4k}: https://www.figure-eight.com/wp-content/uploads/2016/03/Apple-Twitter-Sentiment-DFE.csv
* GOP Debate tweets (sentiment and relevance) {14k}: https://www.figure-eight.com/wp-content/uploads/2016/03/GOP_REL_ONLY.csv
