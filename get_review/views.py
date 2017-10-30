from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from bs4 import NavigableString
import re
import json
from textblob import TextBlob

ytSearchTerm = ""
searchTerm = ""
regEx = ""

def index(request):
    try:
        prod = request.GET['prod']
        reviews = {
            'techRadarReviews': getTRR(prod),
            'cnetReviews' : getCR(prod),
            'youtubeReviews' : getYTR(prod)
        }
        return JsonResponse(reviews)
    except Exception:
        return JsonResponse({'error': 'prod value missing'})


def setSearchTerm(product):
    global searchTerm
    searchTerm = product.replace(" ", "+")

def setRegEx(product):
    regExSearchTerm = product.replace(" ", "(.*)")
    global regEx
    regEx = r"(.*){}(.*)".format(regExSearchTerm)

def setYTSearchTerm(product):
    global ytSearchTerm
    ytSearchTerm = product.replace(" ", "%20")

def scrapeData(url):
    response = requests.get(url)
    content = urlopen(url).read()
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def apiRequest(url):
    content = urlopen(url).read()
    return content

def getTRR(prod):
    setSearchTerm(prod)
    setRegEx(prod)
    reviews = {}
    index = 0
    techradarUrl = "http://www.techradar.com/search?searchTerm={}".format(searchTerm)
    soup = scrapeData(techradarUrl)
    results = soup.find_all(class_="listingResult")
    for each in results:
        if each.find(class_="article-name"):
            ratingElement = each.find(class_="rating")
            searchObj = re.search(regEx, each.find(class_="article-name").contents[0], re.M | re.I)
            if ratingElement and searchObj:
                reviews[index] = {
                    'articleName': each.find(class_="article-name").contents[0],
                    'link': each.find('a')['href'],
                    'summary': each.find(class_="synopsis").contents[0].replace("\n",""),
                    'rating': (len(ratingElement.find_all(class_="icon-star")) - (0.5 * len(ratingElement.find_all(class_="half"))))
                }
                index = index + 1
    return reviews

def getTechRadarReviews(request):
    try:
        prod = request.GET['prod']
        return JsonResponse(getTRR(prod))
    except Exception:
        return JsonResponse({'error' : 'prod value missing'})


def getCR(prod):
    setSearchTerm(prod)
    setRegEx(prod)
    reviews = {}
    index = 0
    cnetUrl = "https://www.cnet.com/search/?query={}&page=1".format(searchTerm)
    soup = scrapeData(cnetUrl)
    results = soup.find(class_="resultList").find(class_="items").find_all(class_="searchItem")
    for each in results:
        try:
            itemInfo = each.find(class_="itemInfo")
            searchObj = re.search(regEx, itemInfo.find("a").find("h3").contents[0], re.M | re.I)
            if itemInfo.find(class_="rating") and searchObj:
                reviews[index] = {
                    'articleName': itemInfo.find("a").find("h3").contents[0],
                    'link': "https://www.cnet.com" + itemInfo.find("a")['href'],
                    'summary':itemInfo.find(class_="dek").contents[0],
                    'rating': float(itemInfo.find(class_="rating").find(class_="stars-rating")['class'][3])
                }
                index = index + 1
        except NavigableString:
            pass
    return reviews

def getCnetReviews(request):
    try:
        prod = request.GET['prod']
        return JsonResponse(getCR(prod))
    except Exception:
        return JsonResponse({'error' : 'prod value missing'})


def getYTR(prod):
    setYTSearchTerm(prod)
    setRegEx(prod)
    reviews = {}
    index = 0
    ytUrl = "https://www.googleapis.com/youtube/v3/search?q={}%20reviews&part=snippet&type=video&key=AIzaSyD9SNjRWO_I-5VsW9PbYe_roAWPI7kGd5I".format(ytSearchTerm)
    content = urlopen(ytUrl).read()
    data = json.loads(content)
    for item in data["items"]:
        reviews[index] = {
            'videoId' : item["id"]["videoId"],
            'title' : item["snippet"]["title"],
            'thumbnail' : item["snippet"]["thumbnails"]["medium"]["url"],
            'channel' : item["snippet"]["channelTitle"]
        }
        index = index + 1
    return reviews

def getYoutubeReviews(request):
    try:
        prod = request.GET['prod']
        return JsonResponse(getYTR(prod))
    except Exception:
        return JsonResponse({'error' : 'prod value missing'})

def techRadarPostParser(request):
    try:
        url = request.GET['url']
        # url = "http://www.techradar.com/reviews/pc-mac/laptops-portable-pcs/laptops-and-netbooks/dell-xps-15-1306282/review"
        soup = scrapeData(url)
        results = soup.find(class_="pro-con")
        procons = {}
        if results:
            for part in results:
                if part.find('h4') != -1:
                    listObj = {}
                    index = 0
                    try:
                        for item in part.find('ul'):
                            if item != "\n":
                                listObj[index] = item.contents[0].replace("\n","")
                                index = index + 1
                        procons[part.find('h4').contents[0].replace("\n","")] = listObj
                    except NavigableString:
                        pass
            return JsonResponse(procons)
        else:
            return JsonResponse({'error': 'no data found'})
    except Exception:
        return JsonResponse({'error' : 'url value missing'})

def cnetPostParser(request):
    try:
        url = request.GET['url']
        # url = "http://www.techradar.com/reviews/pc-mac/laptops-portable-pcs/laptops-and-netbooks/dell-xps-15-1306282/review"
        return JsonResponse(cnetPostParserService(url))
    except Exception:
        return JsonResponse({'error' : 'url value missing'})

def cnetPostParserService(url):
    soup = scrapeData(url)
    results = soup.find(class_="quickInfo")
    if results:
        good = results.find(class_="theGood").find(class_="summary").contents[0]
        bad = results.find(class_="theBad").find("span").contents[0]
        bottomLine = results.find(class_="theBottomLine").find(class_="description").contents[0]
        quickInfo = {}
        ratings = {}
        quickInfo['good'] = good
        quickInfo['bad'] = bad
        quickInfo['bottomLine'] = bottomLine
        if soup.find_all(class_="ratingsBars"):
            for item in soup.find(class_="ratingsBars").find_all(class_="ratingBarStyle"):
                ratings[item.find(class_="categoryWrap").find("span").contents[0]] = float(
                    item.find(class_="categoryWrap").find("strong").contents[0])
        return {
            'quickInfo': quickInfo,
            'ratings': ratings
        }
    else:
        return {'error': 'no data found'}

def sentimentApi(request):
    try:
        text = request.GET['text']
        return JsonResponse(getSentiment(text))
    except Exception:
        return JsonResponse({'error' : 'text value missing'})

def getSentiment(text):
    url = "http://text-processing.com/api/sentiment/"
    data = {'text': (None, text)}
    response = requests.post(url, files=data)
    return response.json()

def getTagsForProduct(request):
    # try:
        prod = request.GET['prod']
        posts = getCR(prod)

        for post in posts:
            post_link = posts[post]['link']
            post_content = cnetPostParserService(post_link)
            quickInfo = post_content['quickInfo']
            calcAverageRating(post_content['ratings'])
            getTags(quickInfo['good'])
            getTags(quickInfo['bad'])
            getTags(quickInfo['bottomLine'])
        return JsonResponse(getPhraseList())
    # except Exception:
        # return JsonResponse({'error' : 'text value missing'})

def getTagPOS(word,tags):
    for tag in tags:
        if tag[0].lower() == word.lower():
            return tag[1]
    return ""

def getTags(text):
    textblob = TextBlob(text)
    tags = textblob.tags
    noun_phrases = textblob.noun_phrases
    for phrase in noun_phrases:
        valid = False
        for word in phrase.split():
            tag = getTagPOS(word,tags)
            if tag.startswith("JJ"):
                valid = True
            if tag.startswith("NN") and valid == True:
                phrase_sentiment = getSentiment(phrase)
                phraseObj = {
                    'phrase': phrase,
                    'sentiment': phrase_sentiment['label'],
                    'posProbability': phrase_sentiment['probability']['pos']
                }
                addPhraseToList(phraseObj)

phraseList = {}
phraseListIndex = 0
def addPhraseToList(obj):
    global phraseListIndex
    phraseList[phraseListIndex] = obj
    phraseListIndex = phraseListIndex + 1

def getPhraseList():
    averageRating = {}
    for param in rating_parameters:
        averageRating[param] = rating_parameters[param][0]/rating_parameters[param][1]
    return {
        'phraseList': phraseList,
        'averageRatings': averageRating
    }

rating_parameters = {}
def calcAverageRating(obj):
    for parameter in obj:
        if parameter in rating_parameters:
            rating_parameters[parameter][0] += obj[parameter]
            rating_parameters[parameter][1] += 1
        else:
            rating_parameters[parameter] = [obj[parameter],1]