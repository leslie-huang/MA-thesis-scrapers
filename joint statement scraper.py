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
for year in range(0, 15):
    url_with_year ="https://www.mesadeconversaciones.com.co/documentos/comunicados-conjuntos?title=&body_value=&page={0}".format(year)
        
    # print(url_with_year)
    
    req = urllib.request.Request(url_with_year, headers = {"User-Agent": "Mozilla/5.0"})

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
    
    # extract the date from the title
    longdate = re.search("\d+ de [a-zA-Z]{1,15} de \d+.*", meta.string)
    
    # get dates when "de" is missing
    if longdate is None:
        longdate = re.search("\d+\s?[a-z]?[a-z]?\s? [a-zA-Z]{1,15} de [0-9].*", meta.string)
    
        if longdate is None:
            longdate = re.search("\d+\s?[de]{0,2} [a-zA-Z]{1,15}[de]{0,2}\s?[0-9].*", meta.string)
            
            # get dates when there's too many letterspaces
            if longdate is None:
                longdate = re.search("\d+ de [a-zA-Z]{1,15}\s{0,2}de\s{0,2}\d+.*", meta.string)
            
                # substitute a string if there's still an error
                if longdate is None:
                    date = "error"
    
    if longdate is not None:
        # print(longdate.group())
        date = longdate.group()
        
    # get rid of punctuation and "de"
    nopunct_date = re.sub("[^a-zA-Z0-9]+", "", date)
    no_de = re.sub("de", "", nopunct_date)
    
    # construct numeric date
    year = re.search("[0-9]{4}", no_de).group()
    day = re.match("[0-9]{1,2}", no_de).group()
    month = re.sub("[^a-zA-Z]+", "", no_de)
    
    meses = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12
    }
    
    for key in meses:
        if month == key:
            nummonth = meses[key]
    
    # make numeric date
    def datemaker(year, month, day):
        return str(year) + "-" + str(month) + "-" + str(day)
    
    numdate = datemaker(year, nummonth, day)
    
    # make it into a dictionary
    doc = {"metadata": meta.string,
    "text": collapsed,
    "doctype": "comunicado conjunto",
    "date": numdate }

    documents_list.append(doc)

    # print(documents_list)


with open("comuniques.csv", "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["metadata", "text", "doctype", "date"])
    
    for document in documents_list:
            metadata = document["metadata"]
            text = document["text"]
            doctype = document["doctype"]
            date = document["date"]
    
            writer.writerow([metadata, text, doctype, date])
