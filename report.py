import json
import string

with open("report.txt", "w") as report:

    unique_pages = sum(1 for page in open("visited.txt"))
    report.write("Unique Pages: {}\n\n".format(unique_pages))

    for longest_info in open("most_words.txt"):
        report.write(longest_info)
    report.write("\n")

    with open("tokens.json") as token_json:
        tokens_dict = json.load(token_json)

    report.write("50 most common words:\n")
    words_only = {key: value for key, value in tokens_dict.items() if all(char in string.ascii_lowercase + string.punctuation for char in key)}
    for token, count in sorted(words_only.items(), key=lambda x: x[1], reverse=True)[:50]:
        print(token.__repr__())
        report.write(token.strip() + ", " + str(count) + "\n")
    report.write("\n")

    with open("subdomains.json") as subdomains_json:
         subdomains_dict = json.load(subdomains_json)

    report.write("Subdomain Counts:\n")
    for subdomain, count in sorted(subdomains_dict.items()):
        if subdomain:
            report.write(subdomain + ", " + str(count) + "\n")
            

    
