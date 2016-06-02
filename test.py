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

documents_list = []

url = "https://www.mesadeconversaciones.com.co/comunicados/comunicado-conjunto-72-la-habana-cuba-25-de-mayo-de-2016"

print(url)

r = requests.get(url)

ingredients = r.text

soup = BeautifulSoup(ingredients, "html.parser")

metadata = soup.find("h1")
print(metadata.string)

date = re.search("\d+ de [a-zA-Z]{1,8} de \d+", metadata.string)
print(date.group())


text = soup.find("div", class_="body")
paragraphs = text.find_all("p")
collapsed = " ".join([p.string for p in paragraphs if p.string is not None])
print(collapsed)

doc = {"metadata": metadata.string, "text": collapsed }
    
documents_list.append(doc)

print(documents_list)

with open("comuniques.csv", "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["metadata", "text"])
    
    for document in documents_list:
            metadata = document["metadata"]
            text = document["text"]
    
            writer.writerow([metadata, text])