# Wiki Cralwer

A Python project to grab random Wikipedia pages and measure their distance from the Philosophy page. 
A Histogram of the Distribution Data is plotted with Pandas, MatPlotLib, NumPy, and SciPy.

## Installing & Running
- Python Version: Anaconda 2.4.1 (Python 3.5.2)
- All libraries used are in the Python Standard Library except:
    - BeautifulSoup4
    - Pandas
    - MatPlotLib 
    - NumPy 
    - SciPy
- The plotting libraries are called from plot_data_normal.py. These libraries (besides BS4) are included with Anaconda.  
- BeautifulSoup4 can be installed via command line with `pip install beautifulsoup4`

## Results

1. *What percentage of pages often lead to philosophy?*
    - In my test run (included in the example folder), 96% (483) of random pages led to philosophy. The remaining 20 ended in infinite looping between pages. 

2. *What is the distribution of path lengths for 500 pages who made it to philosophy?*
    - The average path length is 11 pages. The shortest distance was 2 pages and the longest is 25 pages. 

3. *How can the number of http requests be reduced for 500 random starting pages*?
    - The program maintains a hashmap of known links and their distances, which signifcantly reduces the amount of redundant link traversals and requests upon finding already visited pages.
        - See the optimization section for further detail. 
    - Tangentially, the program will only request and construct Wikipedia mobile links. Mobile pages can contain over 90% less data than full-sized pages while still retaining the necessary information.

## Design

### Overview
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), with lxml as the HTML parser, is used to navigate and modify the DOM tree of each random Wikipedia mobile page(from /wiki/Special:Random).
- After grabbing the page's body content from the DOM tree, the crawler program preprocesses the text by removing unnecessary elements/ then selects the first valid link that is not in parentheses or italicized. 
- The crawler will keep grabbing links until an exception is raised or the Philosophy page is reached. If successful, the distance from the starting page to the Philosophy is calculated. 
- Distribution data and an error log are dumped into JSON files. A Histogram of the Distribution Data is plotted with Pandas, MatPlotLib, NumPy, and SciPy.

#### Preprocessing, Bad Link Removal and Good Link Selection
- A Good Link is defined as the first link in the main body of the Wikipedia page that is not contained in parentheses or italicised. 

- The main body text is contained in the `mw-content-text` div of each Wikipedia page. In order to reduce the amount of erroneous links and HTML elements from the body, the crawler scrubs the text using Beautifulsoup's [decompose()](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#decompose) function. 
    - Elements such as the Table of Contents, Navigation items, external links, [IPA text](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet), italic text, metadata and others are removed. 
    - The only remaining links in the body text are either Good Links or links contained within parentheses. 

- Paragraph, list and unordered list elements are then selected from the body and stored in a Python list. The first item from the list is passed into a function which returns the text contained within parentheses. 
    - The function  returns a single string containing all of the captured parentheses text. 

- The parentheses text and the first selected text element from the scrubbed HTML body are then passed into a function to remove invalid links. 
    - This function will gather all of the remaining links in the scrubbed paragraph, place them into a list, and compare the list elements to the links contained in the parentheses text. 

- After scrubbing and removing the links contained within the parentheses, a list containing only Good Links is produced. 
    - If that text element contains no Good Links, the process will repeat with the next text element
    
- The first link from this list is used to form a new Wikipedia link using Python's [urllib2](https://docs.python.org/2/library/urllib2.html) library. 

- *What if no Good Links are found in the paragraph elements?*
    - The program will first expand it's search to all links contained in the scrubbed body, not just paragraph, list and unordered list elements. 
    - If the expanded search yields no Good Links, the program will raise an exception, which will be caught by the crawling function, logged in the error dictionary, and outputted as a JSON file upon program completion. 
    
#### Traversing Wikipedia Pages and Distance Calculation

##### Traversal

- The crawler traverses Wikipedia pages by first grabbing a random page: 
    - It will first check if the random page is the Philosophy page (pretty lucky as there are over 5 million possible articles).
    - If the random page is not the Philosophy page, the crawler will find the next Good Link and go to that page. The title of each link traversed is stored in a list called loopList. 
    - The program will repeat this process until the Philosophy Page is reached or an exception occurs. A common exception is an infinite looping error, where the sequence of pages will continually loop over itself. 
        - Exceptions will not end the program prematurely- the error is logged and a new random page is grabbed. 

##### Distance Calculation

- If the random page successfully reaches the philosophy page, the loopList is passed to a function which calculates the distance from each link in the travel path to the philosophy page. 

#### Optimization

#####*Why use mobile pages?*
- Mobile pages can contain over 90% less data than full-sized pages while still retaining the necessary information. On average, requesting a mobile page is up to one second faster. 
    
##### Distance Calculation Optimization
- Many random pages will follow the similar paths towards the philosophy page. 
- Storing these pages and their distances to the philosophy page in a dictionary allows the program to greatly increase it's speed by substituting link grabbing with finding and retrieving values from the dictionary.
- Because dictionaries in Python are implemented using hash tables, getting, setting and checking for items are O(1) operations. 

######How it works:
- The distanceDict is checked for each new link grabbed. If the link is contained in the dictionary, the page traversal ends and the value returned from the distanceDict is used to calculate the distances for each link in the loopList. 
- These distances are then added to the distanceDict.

#### Plotting and Output
- Page distance data is outputted to the results folder as a JSON file. 
- Pandas read_json() function is an easy way to create a data frame with minimal code.
- Matplotlib is used to plot the distribution data as a normalized histogram.
- A best-fit line is added using SciPy and NumPy. 

### Discussion and Improvements

##### Performance
1. Preprocessing and scrubbing unnecessary elements from the DOM tree is implemented in a cumbersome way
    - Each call to the BeautifulSoup decompose() function must traverse the entire body text tree
    - Can be faster - ideas
        - Use a different library which can more efficiently scrub multiple HTML elements at once
        - Create a custom scrubbing function and directly pass it the parsed tree from LXML
        - Initially request just the  `mw-content-text` element and not the entire DOM tree
2. Each random page is traversed one page at a time
    - Using asynchronous tools such as Pythons asyncio or multiprocessing may add a significant performance boost

##### Code improvements
1. Crawl function could be further broken up
2. Error throwing and exception raising could be more descriptive
3. Matplotlib and Pandas are both large libraries with many dependencies
    - Utilizing a more lightweight plotting library may be appropriate
    - D3.js can easily read JSON files and run in-browser with no user configuration

