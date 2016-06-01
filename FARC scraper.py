#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib.error
import urllib.request

import json
import os
import string
import sys
from os.path import normpath, basename

# get archive page
url = "http://farc-ep.co/datos.html"

archive_page = urllib.request.urlopen(url).read()

print(archive_page)

# get links from archive page
soup = BeautifulSoup(archive_page, "html.parser")

# gets all the A tags
communiques = soup.find_all("a", href = True)

links = []

# get relative URLs
for Atag in communiques:
    address = Atag.get("href")
    if address.startswith("/comunicado/"):    
        links.append(address)

shorts = []
# remove the messy prefix to the strings
for link in links:
    short = os.path.basename(os.path.normpath(link))
    shorts.append(short)

print(shorts)

# create output directory if necessary
if not os.path.exists("communiques"):
    os.makedirs("communiques")

# save all communiques
for link in shorts:
    # create the full URL path
    url = "http://farc-ep.co/comunicado/{0}".format(link)
    # save the files
    try:
        urllib.request.urlretrieve(url, os.path.join("communiques", "{0}".format(link)))
        print("Downloaded {0}".format(url))
    except urllib.error.HTTPError:
        print("Error")
