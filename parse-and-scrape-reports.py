#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib.error
import urllib.request
import requests

import csv
import json
import os
import re
import string
import sys
from os.path import normpath, basename

links = []
shorts = []
documents_list = []

# get each of the archive pages
for page in range(0, 2):
    url_with_page ="https://www.mesadeconversaciones.com.co/documentos/informes?title=&body_value=&page={0}".format(page)
            
    req = urllib.request.Request(url_with_page, headers = {"User-Agent": "Mozilla/5.0"})

    archive_page = urllib.request.urlopen(req).read()

    # print(archive_page)

    # get links from archive page
    soup = BeautifulSoup(archive_page, "html.parser")
        
    Atags = soup.find_all("a", href = True)
    
    # print(Atags)

    # get relative URLs
    for Atags in Atags:
        address = Atags.get("href")
        if address.startswith("/comunicados/"):    
            links.append(address)
    
# remove the messy prefix to the strings
for link in links:
    short = os.path.basename(os.path.normpath(link))
    shorts.append(short)

# print(shorts)


# save all communiques
for link in shorts:
    # create the full URL path
    url = "https://www.mesadeconversaciones.com.co/comunicados/{0}".format(link)

    # save the files
    r = requests.get(url)
    print("Downloaded {0}".format(url))

    # make the soup!
    ingredients = r.text
    # print(ingredients)
    soup = BeautifulSoup(ingredients, "html.parser")

    # print(soup)

    # get and collapse paragraphs of text
    text = soup.find("div", class_="body")
    # print(text)
    if text is None: continue
    paragraphs = text.find_all("p")
    collapsed = " ".join([p.string for p in paragraphs if p.string is not None])
    # print(collapsed)

    # get metadata
    meta = soup.find("h1")
    
    # make it into a dictionary
    doc = {"title": meta.string,
    "text": collapsed,
    "doctype": "informe",
    "date": "" }

    documents_list.append(doc)

    # print(documents_list)

with open("reports.csv", "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["title", "text", "doctype", "date"])
    
    for document in documents_list:
            title = document["title"]
            text = document["text"]
            doctype = document["doctype"]
            date = document["date"]
    
            writer.writerow([title, text, doctype, date])
