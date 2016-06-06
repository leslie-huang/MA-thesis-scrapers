#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib.error
import urllib.request

import json
import os
import re
import string
import sys
from os.path import normpath, basename
import csv

# parse each communique webpage into a dictionary

communique_filenames = [name for name in os.listdir("communiques")]

print(communique_filenames)

articles_list = []

meses = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}

for filename in communique_filenames:
    webpage = open(os.path.join("communiques", filename)).read()
    soup = BeautifulSoup(webpage, "html.parser")
    
    # find metadata and paragraphs of statement
    dateline = soup.find("span", class_="itemDateCreated").string
    title = soup.find("h2", class_="itemTitle")
    author = soup.find("span", class_="itemAuthor")
    text = soup.find("div", class_="itemFullText")
    
    # parse word date into numerical date
    datel = re.search("[0-9]{2} [a-zA-Z]{1,12} [0-9]{4}", dateline).group()
    day = re.search("[0-9]{2}", datel).group()
    month = re.search("[a-zA-Z]{1,12}", datel).group()
    for key in meses:
        if month == key:
            nummonth = meses[key]
    year = re.search("[0-9]{4}", datel).group()
    
    def datemaker(year, nummonth, day):
        return str(year) + "-" + str(nummonth) + "-" + str(day)
    
    date = datemaker(year, nummonth, day)
    
    paragraphs = text.find_all("p")
    
    collapsed = " ".join([p.string for p in paragraphs if p.string is not None])
    
    article = {"date": date,
    "title": title.string,
    "author": author.string,
    "text": collapsed }
        
    articles_list.append(article)

print(articles_list)

# write to CSV
with open("FARC_communiques.csv", "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["date", "title", "author", "text"])
    
    for article in articles_list:
            date = article["date"]
            author = article["author"]
            title = article["title"]
            text = article["text"]
    
            writer.writerow([date, author, title, text])
            