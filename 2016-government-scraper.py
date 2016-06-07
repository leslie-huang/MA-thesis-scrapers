#!/usr/bin/env python3

import csv
from government_statement_scraping_utilities import get_result_urls, get_links, get_statement

with open("govtstatements2016.csv", "w") as f:
    writer = csv.writer(f)    
    writer.writerow(["title", "text", "date"])
    
    for result_url in get_result_urls():
        for link in get_links(result_url):
            statement = get_statement(link)
            if statement is not None:
            
                writer.writerow([
                    statement["title"],
                    statement["text"],
                    statement["date"]
                ])
