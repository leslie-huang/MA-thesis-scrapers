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

daily_archive_URLs = []

# max year in range is supplied by user in command line
startyear = int(sys.argv[1])
endyear = int(sys.argv[2])

# get each year / month / day webpage of links to press releases
for year in range(startyear, endyear):
    
    for key in meses:
        # force add leading zeros to month
        month_num = str(meses[key]).rjust(2, "0")
        
        for day in range(1, 32):
            # force add leading zeros to day
            day_num = str(day).rjust(2, "0")
            
            date_id = "{0}{1}{2}".format(year, month_num, day_num)
            
            # take account of a change in directory path beginning with 8/7/2014
            if int(date_id) <= 20140806:
                full_url = "http://wsp.presidencia.gov.co/Prensa/{0}/{1}/Paginas/{2}.aspx".format(year, key, date_id)
                # add it to the list of daily archive URLs
                daily_archive_URLs.append(full_url)
            
            elif int(date_id) >= 20140807:
                full_url = "http://wp.presidencia.gov.co/Noticias/{0}/{1}/Paginas/{2}.aspx".format(year, key, date_id)
                # add it to the list of daily archive URLs
                daily_archive_URLs.append(full_url)            

# print(daily_archive_URLs)

# now get just the pages for days that exist
day_archive_pages = []

for url in daily_archive_URLs:
    try:
        req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})

        archive_page = urllib.request.urlopen(req).read()

        day_archive_pages.append(archive_page)
        
        print("success with {0}".format(url))
    
    except urllib.error.HTTPError as error:
        print("error with url {0}: {1}", url, error)

# create a list that will be populated with 1 dictionary per news article
master_list = []
article_dict = {}

# get all links on each day's archive page
for page in day_archive_pages:
    # make the soup
    soup = BeautifulSoup(page, "html.parser")
    
    # get all links to news articles from that day
    news_items = soup.find_all("div", class_="item link-item")
    
    for item in news_items:
        link = item.find("a", href = True)
    
        # extract URL and title of each article from day archive page
        address = link.get("href") # full URL path
        title = link.get_text()
        
        # get the date from the URL path
        date = re.search("\d{8}", address).group()
        hyp_date = date[0:4] + "-" + date[4:6] + "-" + date[6:]
    
        # get each article and make it into soup
        print("attempting to download {0}".format(address))
        article_req = requests.get(address, headers = {"User-Agent": "Mozilla/5.0"})
        article = article_req.text
                
        article_soup = BeautifulSoup(article, "html.parser")
    
        # get the text
        main = article_soup.find("div", id="ctl00_PlaceHolderMain_content__ControlWrapper_RichHtmlField")
        if main is not None:
            paragraphs = main.find_all("p")
            text = collapsed = " ".join([p.string for p in paragraphs if p.string is not None])
        
            # continue only if the text contains the following keywords: "paz", "Farc"
            if bool(re.search("las Farc", text)) & bool(re.search("paz", text)):
    
                # save address, title, text, and date as values in the dictionary
                article_dict["URL"] = address
                article_dict["title"] = title
                article_dict["text"] = text
                article_dict["date"] = hyp_date

                # append dictionary to the list of dictionaries
                master_list.append(article_dict.copy())

        # write to CSV

with open("govtstatements{0}-{1}.csv".format(startyear, endyear), "w") as f:
    writer = csv.writer(f)
    
    writer.writerow(["URL", "title", "text", "date"])
    
    for document in master_list:
        address = document["URL"]
        title = document["title"]
        text = document["text"]
        date = document["date"]

        writer.writerow([address, title, text, date])  
            