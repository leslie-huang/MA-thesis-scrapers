#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib.error
import urllib.request

import json
import os
import string
import sys
from os.path import normpath, basename
import csv

# parse each communique webpage into a dictionary

communique_filenames = [name for name in os.listdir("communiques")]

print(communique_filenames)

articles_list = []

for filename in communique_filenames:
    webpage = open(os.path.join("communiques", filename)).read()
    soup = BeautifulSoup(webpage, "html.parser")
    
    # find metadata and paragraphs of statement
    date = soup.find("span", class_="itemDateCreated")
    title = soup.find("h2", class_="itemTitle")
    author = soup.find("span", class_="itemAuthor")
    text = soup.find("div", class_="itemFullText")
    
    paragraphs = text.find_all("p")
    
    collapsed = " ".join([p.string for p in paragraphs if p.string is not None])
    
    article = {"date": date.string,
    "title": title.string,
    "author": author.string,
    "text": collapsed }
        
    articles_list.append(article)

print(articles_list)

# write to CSV
with open("comuniques.csv", "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["date", "title", "author", "text"])
    
    for article in articles_list:
            date = article["date"]
            author = article["author"]
            title = article["title"]
            text = article["text"]
    
            writer.writerow([date, author, title, text])
            