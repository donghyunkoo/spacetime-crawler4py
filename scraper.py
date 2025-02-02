import re
import time
import json
from urllib.parse import urlparse, urldefrag, urljoin
from collections import defaultdict

import string

from nltk.tokenize import TweetTokenizer

from bs4 import BeautifulSoup


new_visitedFile = True
new_subdomainFile = True
new_tokenFile = True

highest_token_count = 0


def scraper(url, resp):
    subdomain_dict = defaultdict(int)
    
    links = extract_next_links(url, resp)
    results = [urldefrag(href).url for href in links]

    for href in results:
        netloc = urlparse(href).netloc
        netloc = netloc.replace("www.", "")

        if ".ics.uci.edu" in netloc:
            subdomain_dict[netloc] += 1

    if subdomain_dict:
        updateSubdomainsCount(subdomain_dict)

    print()

    return [link for link in results if is_valid(link)]


def extract_next_links(url, resp):
    valid_links = []

    if (resp.status==200) or (resp.status==201) or (resp.status==202):
        print(resp.status, "| Scraping |", url)
        bs = BeautifulSoup(resp.raw_response.content, "html.parser") #changed 'resp.raw_resp...' to 'resp.raw_response...' however nothing is happening when running the crawler

        addVisitedLink(url)

        words = bs.get_text()

        tokens = tokenizer(words)
        unique_tokens = set(tokens)

        if len(tokens) < 125 or len(unique_tokens)/len(tokens)<=0.20:
            print("Not Content Rich!!!")
            return []

        else:
            token_counts = computeTokenFrequency(tokens)
            updateTokenCount(token_counts)

            global highest_token_count

            if len(token_counts) > highest_token_count:
                highest_token_count = len(token_counts)

                updateHighestTokenCount(highest_token_count, url)

            # https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python
            start_time = time.time()

            for a in bs.findAll("a"):  #is the syntax supposed to be 'find_all'? The crawler runs tho so ig it doesn't matter lol
                href = a.get("href")

                if urlparse(url).netloc == "":
                    valid_links.append(href)
                else:
                    valid_links.append(urljoin(url, href))

            end_time = time.time()

            if (end_time - start_time) > 7:
                print("Time Limit Exceeded!!!")
                return []
            else:
                print("Returning {} link(s)".format(len(valid_links)))
                return valid_links
        
    else:
        print(resp.status, "| Not Scraping |", url)
        return []

def updateHighestTokenCount(count, url):
    with open("most_words.txt", "w", encoding="utf-8") as f:
        f.write("URL: " + url + "\n")
        f.write("Word Count: " + str(count) + "\n")
        f.flush()

def addVisitedLink(url):
    global new_visitedFile

    if new_visitedFile:
        new_visitedFile = False
        open_permission = "w"
    else:
        open_permission = "a"

    with open("visited.txt", open_permission, encoding="utf-8") as f:
        f.write(url + "\n")
        f.flush()

def is_valid(url):
    try:
        patternA = re.compile(r".*\.(?:ics|cs|informatics|stat)\.uci\.edu")
        patternB = re.compile(r"today\.uci\.edu/department/information_computer_sciences/.*")

        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not re.match(patternA, parsed.netloc):
            return False

        if re.match(patternB, parsed.netloc + parsed.path):
            return False

        # check for Traps
        if checkTrap(url):
            return False

        # check if already visited
        if checkVisited(url):
            return False

        # check later!!!
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|pps|bib|odb|m|psp|py|ppsx|apk|war|img|mpg"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def checkVisited(url):
    try:
        # iterate through text file to see if site has already been visited
        f = open("visited.txt", encoding="utf-8")
        visited = [links.strip() for links in f]
    
    except Exception as e:
        print(e)
        visited = []

    finally:
        f.close()
        return url in visited
        


def checkTrap(url):
    # if the path is too long, it is a good indicator of a trap
    parsed_path = urlparse(url).path
    
    if (len(parsed_path.split("/")) >= 5):
        return True

    # finish writing regular expression
    trapPaths = re.compile(r"(\?page_id\=|\/blog\/|\/tag\/|\/calendar\/|\/events\/|\?replytocom\=|\/pdf\/|\/download\/|mailto:|\?tab_files\=|\?letter\=|\.DS_STORE|\.Z|\.Thesis|\?share\=|\?ical\=|\?rev\=|\?do\=)")
    trapGenome = re.compile(r"\/(cgo|pgo|fgo)\/(p|f|c)[0-9]")

    # check to see if url matches any of the trap patterns
    if re.search(trapPaths, url):
        return True
    if re.search(trapPaths, parsed_path):
        return True
    if re.search(trapGenome, parsed_path):
        return True

    # query paramater indicates trap bc infinite possibilities
    # ? starts a query
    # & separates parameter
    if url.count("?") + url.count("&") > 1:
        return True
    # if url.count("&") > 1:
        # return True
    # if url.count("%") > 0:
        # return True

    return False

def tokenizer(text):
    try:
        tokens = TweetTokenizer().tokenize(text)
        stopwordLst = [line.strip() for line in open("stopwordlist.txt", encoding="utf-8")]
        
        ans = []

        for token in tokens:
            token = token.lower()

            if (token not in stopwordLst) and (token not in string.punctuation) and (len(token) > 1):

                for char in token:
                    if char not in string.digits + string.ascii_lowercase + string.punctuation:
                        break

                ans.append(token)

        return ans

    except Exception as e:
        print(e)
        return []
        
                

def computeTokenFrequency(tokens):
    count_dict = defaultdict(int)

    for token in tokens:
        count_dict[token] += 1

    return count_dict


def updateSubdomainsCount(curr_dict):
    # curr_dict is the default dict {hostname: count}
    # https://www.geeksforgeeks.org/read-json-file-using-python/
    global new_subdomainFile

    if not new_subdomainFile:
        with open("subdomains.json") as f:
            subdomain_dict = json.load(f)

        for domain, count in curr_dict.items():
            if domain in subdomain_dict:
                subdomain_dict[domain] += count
            else:
                subdomain_dict[domain] = count

        with open("subdomains.json", "w") as f:
            json.dump(subdomain_dict, f)

    else:
        new_subdomainFile = False
        print("Opening new JSON file for ICS subdomain...")
        with open("subdomains.json", "w") as f:
            json.dump(curr_dict, f)


def updateTokenCount(curr_dict):
    # curr_dict is the default dict {token: count}
    # https://www.geeksforgeeks.org/read-json-file-using-python/
    global new_tokenFile

    if not new_tokenFile:
        with open("tokens.json") as f:
            token_dict = json.load(f)

        for token, count in curr_dict.items():
            if token in token_dict:
                token_dict[token] += count
            else:
                token_dict[token] = count

        with open("tokens.json", "w") as f:
            json.dump(token_dict, f)

    else:
        new_tokenFile = False
        print("Opening new JSON file for Tokens...")
        with open("tokens.json", "w") as f:
            json.dump(curr_dict, f)


if __name__ == '__main__':
    pass
    

    
    

    


    
