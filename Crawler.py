from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urljoin
import json
import time
from plot_data_normal import plot as plot

startTime = time.time()

def getRandomPage():
    req = urllib.request.urlopen('https://en.m.wikipedia.org/wiki/Special:Random') #Grab the smaller mobile page
    soup = BeautifulSoup(req, 'lxml')
    return soup
def getTitle(page):
    try:
        title = page.find("h1", {'id':'section_0'}).text
    except:
        title = page.find("h1", {'id': 'firstHeading'}).text

    return title

def parenText(text): #Finds text between parentheses
    textList = list(str(text))
    parsed = ''
    parens = 0
    startOfParen = False
    endOfParen = False

    for index, char in enumerate(str(text)):
        if char == '(':
            if parens == 0:
                start = index
                startOfParen = True
            parens+=1
            continue

        elif char == ')':
            parens-=1
            if parens ==0:
                end = index
                endOfParen = True

        if startOfParen == True and endOfParen == True:
            capturedString=''.join(textList[start:end+1]) #Converts the list into a string
            if '<a' in capturedString: #Checks if captured string contains a link
                parsed = parsed + capturedString
            startOfParen = False
            endOfParen = False
            continue

    return parsed

def removeLinks(firstParagraph): #Removes links from the parentheses text
    links = firstParagraph.find_all('a')
    goodLinks = []
    badLinkText = parenText(str(firstParagraph))
    parenLinks = parenText(firstParagraph)
    goodLinks = [links[i]['href'] for i in range(len(links))
                 if str(links[i]) not in badLinkText and '.ogg' not in links[i]['href']]

    return goodLinks

def removeElements(body, classes, *element):
    if len(element) > 0:
        for div in body.find_all(element, classes):
            div.decompose() #Decompose recursively removes elements from the DOM tree and their associations
    else:
        for div in body.find_all(classes):
            div.decompose()

def getNextLink(page):
    body = page.find("div", {'id':'mw-content-text'}) #Get the main body text

    removeElements(body, {'class': ['toc', 'toc-mobile'], 'id': 'toc'}, 'div',) #Remove table of contents
    removeElements(body, {'role': 'navigation'}, 'div' )  # Remove navigation boxes
    removeElements(body, {'class': ['new', 'external free', 'external text', 'extiw']},'a') #Remove external links
    removeElements(body, {'class': ['mw-editsection', 'IPA', 'IPA nopopups', 'nowrap']}, 'span') #Remove IPA and edit spans
    removeElements(body, {'class': 'metadata'}, 'small') #Remove metadata links
    removeElements(body, ['table', 'i', 'sup', 'img']) #Remove tables, italics, superscripts

    paragraphs = body.findChildren(['p','ul','li'])
    paraIndex = 0
    firstParagraph = paragraphs[paraIndex]
    goodLinks = removeLinks(firstParagraph)

    try:
        while goodLinks == []: #grabs the next paragraph if the first contains no valid links
            firstParagraph = paragraphs[paraIndex+1]
            goodLinks = removeLinks(firstParagraph)
            paraIndex+=1
    except: #expand link search if no valid links found in any paragraph
        goodLinks = removeLinks(body)

    if goodLinks is not None:
        nextLink = urljoin('https://en.m.wikipedia.org', goodLinks[0])
        return nextLink
    else:
        raise TypeError('404/No Good Links Found ')

def goToNext(page):
    try:
        nextPage=getNextLink(page)
        req = urllib.request.urlopen(nextPage)
        soup = BeautifulSoup(req, 'lxml')
        return soup
    except:
        raise TypeError('404/No Good Links Found ')

def addToDict(list, dict, *val):
    if len(val) > 0:
        distanceFromEnd = val[0]
        for index, element in enumerate(list):
            distance = distanceFromEnd - index  # The distance from the current list element to the end
            dict[element] = distance
    else:
        for index, element in enumerate(list):
            dict[element] = None
    return dict

def mapLinks(list, dict): #Creates a dict of known links and their distances
    distanceFromEnd = list.index(list[-1])+1#The last link before the philosophy page
    addToDict(list, dict,  distanceFromEnd)

def mapFoundLinks(list, dict): #Map links that made it to the Philosophy page
    distanceFromEnd = dict[list[-1]] + (len(list)-1)#Distance from the starting point to the end
    addToDict(list, dict, distanceFromEnd)

def writeToFile(data, fileName): #Write dictionaries to a JSON file
    with open('./results/{}.json'.format(fileName), 'w') as file:
            json.dump(data, file)
    file.close()

def getStats(dict, errors):
    statDict = {}
    average = int(sum(dict.values())/len(dict))
    percentMade = int((1-(len(errors)/len(dict)))*100)
    maxDist = dict[max(dict, key=dict.get)]
    minDist = dict[min(dict, key=dict.get)]

    statDict['average'] = average
    statDict['Percent Made'] = percentMade
    statDict['Maximum Distance'] = maxDist
    statDict['Minimum Distance'] = minDist
    writeToFile(statDict, 'Stats')

    print('\n' + 'The average distance is {} and {} percent of links made it to the Philosophy page.'.format(average, percentMade), flush = True)
    print('The longest distance is {} and the smallest distance is {}.'.format(maxDist, minDist), flush = True)
    print('Check the JSON files in the results folder for more data!', flush = True)

def crawl():
    topics = 1
    stopNumber = 500
    distanceDict = {}
    startingDict = {}
    errorDict = {}
    infLoopDict = {}

    while topics <= stopNumber:
        loopList = []
        try:
            count = 0
            page = getRandomPage()
            startTitle = title = getTitle(page)
            loopList.append(startTitle)
            print('{} - {} of {}'.format(startTitle, topics, stopNumber), flush = True)
        except:
            errorDict['Random Page {}'.format(count)] = '404/No Good Links Found on Random Page {}'.format(count)
            continue

        if str(startTitle) == 'Philosophy':
            distanceDict[startTitle] = 0
            continue

        while str(title) != 'Philosophy': #Page traversal loop
            if title in loopList[1:-1] or title in infLoopDict:  # Catch infinite loops and add to dict
                errorDict[startTitle] = 'Infinite loop'
                addToDict(loopList, infLoopDict)
                break

            elif title in distanceDict: #Stop looping if the link has already been visited
                mapFoundLinks(loopList, distanceDict) #Adds the current link path into the dict
                startingDict[startTitle] = distanceDict[startTitle]
                break

            else:
                try: #Grab the next page
                    page = goToNext(page)
                    title = getTitle(page)
                    loopList.append(title)
                    count += 1
                except Exception as e:
                    errorDict[title] = str(e) #No Good Link Found
                    break

        if len(loopList[1:])> 0 and loopList[-1] == 'Philosophy': #Map distances if Philosophy is reached
            try:
                mapLinks(loopList[:-1], distanceDict)
                startingDict[startTitle] = distanceDict[startTitle]
            except Exception as e:
                errorDict[title] = str(e) #No Good Link Found
                break

        topics+=1
    try:
        writeToFile(errorDict, 'errors')
        writeToFile(distanceDict, 'allLinks')
        writeToFile(startingDict, 'startingLinks')
        getStats(startingDict, errorDict)
    except:
        print('Error writing to files!')

if __name__ == "__main__":
    print('Crawling...', flush = True)
    crawl()
    print('Plotting Results...', flush = True)
    print('--- Finished in {} seconds ---'.format(time.time() - startTime))
    try:
        plot(r'./results/startingLinks.json')
    except:
        print('Plotting Error!', flush = True)
        pass

