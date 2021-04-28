import re
from urllib.parse import urlparse
from collections import defaultdict

from nltk.tokenize import TweetTokenizer

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    return list()

def is_valid(url):
    try:
        patternA = re.compile(r".*\.(?:ics|cs|informatics|stat)\.uci\.edu")
        patternB = re.compile(r"today\.uci\.edu/department/information_computer_sciences/.*")

        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not re.match(patternA, parsed.netloc):
            return False

        if not re.match(patternB, parsed.netloc):
            return False

        # check for Traps
        if checkTraps(url):
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
    trapPaths = re.compile(r"(\?page_id=|\?replytocom=|\?share=|\.Thesis)")
    trapCalendar = re.compile(r"")
    trapGenome = re.compile(r"")

    # check to see if url matches any of the trap patterns
    if re.search(trapPaths, parsed_path) is not None:
        return True
    if re.search(trapCalendar, parsed_path) is not None:
        return True
    if re.search(trapGenome, parsed_path) is not None:
        return True

    # query paramater indicates trap bc infinite possibilities
    # ? starts a query
    # & separates parameter
    if url.count("?") > 1:
        return True
    if url.count("&") > 1:
        return True
    if url.count("%") > 0:
        return True

    return False

def tokenizer(text):
    try:
        tokens = TweetTokenizer().tokenize(text)
        stopwordLst = [line.strip() for line in open("stopwordlist.txt", encoding="utf-8")]
        return [token.lower() for token in tokens if (token not in stopwordLst) and (token.isalnum()]

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
    try:
        with open("subdomains.json") as f:
            subdomain_dict = json.load(f)

        for domain, count in curr_dict.items():
            if domain in subdomain_dict:
                subdomain_dict += count
            else:
                subdomain_dict = count

        with open("subdomains.json", "w") as f:
            json.dump(subdomain_dict, f)

    except:
        print("Opening new JSON file for ICS subdomain...")
        with open("subdomains.json", "w") as f:
            json.dump(curr_dict, f)


def updateTokenCount(curr):
    # curr_dict is the default dict {token: count}
    # https://www.geeksforgeeks.org/read-json-file-using-python/
    try:
        with open("tokens.json") as f:
            token_dict = json.load(f)

        for domain, count in curr_dict.items():
            if domain in subdomain_dict:
                token_dict += count
            else:
                token_dict = count

        with open("tokens.json", "w") as f:
            json.dump(token_dict, f)

    except:
        print("Opening new JSON file for Tokens...")
        with open("token.json", "w") as f:
            json.dump(curr_dict, f)


if __name__ == '__main__':
    pass
        

    

    
    

    


    
