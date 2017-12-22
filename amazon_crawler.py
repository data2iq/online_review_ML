from bs4 import BeautifulSoup
import urllib, pycurl, cStringIO, ast, sys, time
#import urllib, pycurl,  ast, sys, time
from vaderSentiment  import sentiment as vaderSentiment


#amazon crawler
def crawl_amazon():

    p1 = "https://www.amazon.com/product-reviews/B01G92JUGC/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=avp_only_reviews&showViewpoints=1&pageNumber="
    p2 = "&showViewpoints=0&sortBy=byRankDescending"


    #p1 = "http://www.amazon.com/The-Mountain-Three-Short-Sleeve/product-reviews/B00G69KCO8/ref=cm_cr_dp_qt_see_all_top?ie=UTF8&pageNumber="
    #p2 = "&showViewpoints=0&sortBy=byRankDescending"
    posts = []
    # file_name = "nike_reviews.txt"
    file_name = "Little_Blue_Truck_reviews.txt"
    with open(file_name, 'w') as fp:
        for pagenumber in xrange(1, 8):

            amazon_url = p1 + str(pagenumber) + p2
            print ("Processing URL : " + amazon_url)
            ur = urllib.urlopen(amazon_url)
            soup = BeautifulSoup(ur.read(),"lxml")

            print ("Loading the text from the 'span' tags")
            posts_ = soup.select("span.review-text")

            # posts_ = soup.select("div.review-data")
            print (len(posts_))
            for x in posts_: posts.append(x.text)
            for x in posts_: fp.write(x.text.encode('utf-8') + "\n")
            # time.sleep(1)
    #print posts
    print (len(posts))
    return posts

#read amazon/macys reviews from file
def load_reviews(fn):
    posts = []
    with open(fn) as fp:
        for line in fp:
            posts.append(line[:-1])
    return posts

#compute sentiment for comments using text-processing API
def compute_tp_sentiments(posts):
    cnt = 0
    sentiments = []
    for post in posts:
        try:
            cnt += 1
            buf = io.StringIO.StringIO()
            # buf = cStringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://text-processing.com/api/sentiment/')
            c.setopt(c.WRITEFUNCTION, buf.write)
            postdata = ''
            postdata = 'text=' + post
            c.setopt(c.POSTFIELDS, postdata)
            c.perform()
            val = buf.getvalue()
            data = ast.literal_eval(val)
            data["post"] = post
            sentiments.append(data)
            buf.close()
        except (pycurl.error, error):
            errno, errstr = error
            print ("An error occured: ", errstr)
    print ("sentiments computed for %d posts" % cnt)
    return sentiments

#compute sentiments using vaderSentiment
def compute_vader_sentiments(posts):
    cnt = 0
    sentiments = []
    for post in posts:
        cnt += 1
        data = {}
        data["post"] = post
        vs = vaderSentiment(post)
        #print vs
        if vs["neg"] >= vs["neu"] and vs["neg"] >= vs["pos"]:
            data["label"] = "neg"
        elif vs["pos"] >= vs["neu"] and vs["pos"] >= vs["neg"]:
            data["label"] = "pos"
        elif vs["neu"] >= vs["neg"] and vs["neu"] >= vs["pos"]:
            data["label"] = "neutral"
        sentiments.append(data)
    print ("sentiments computed for %d posts" % cnt)
    return sentiments

#overall sentiment summary
def compute_summary(sentiments):
    tot = len(sentiments)
    pos, neg, neu = 0, 0, 0
    for sent in sentiments:
        label = sent['label']
        if label == 'neutral':
            neu += 1
        elif label == 'pos':
            pos += 1
        elif label == 'neg':
            neg += 1
    print ("total posts =", tot, "positives =", pos, ", negatives =", neg, ", neutrals =", neu)

#run experiment
def run(rev_file = None, sent_file = None):
    if rev_file and sent_file:
        #load crawled amazon reviews from file
        posts = load_reviews(rev_file)
        print (len(posts))
        #run sentiment analysis
        sentiments = compute_vader_sentiments(posts)
        with open(sent_file, 'w') as gp:
            for sent in sentiments:
                #print sent
                gp.write(str(sent) + '\n')
        compute_summary(sentiments)
    else:
        posts = crawl_amazon()
        sentiments = compute_vader_sentiments(posts)
        compute_summary(sentiments)

def main():
    #load collected amazon reviews from file and compute their sentimnents
    #run("amazon_reviews.txt", "amazon_sentiments.txt")
    #crawl posts
    run()

if __name__ == "__main__":
    sys.exit(main())
