import requests
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# get each page of the search results
def get_result_urls():
    for resultnum in range(1, 1321, 20):
        yield "http://es.presidencia.gov.co/noticia#ac0bf45e-40db-4415-982a-0c48a1c4fab1={{%22k%22%3A%22%22%2C%22s%22%3A{0}%2C%22r%22%3A[{{%22n%22%3A%22Fecha%22%2C%22t%22%3A[%22range%282016-01-01%2C2016-06-02%29%22]%2C%22o%22%3A%22and%22%2C%22k%22%3Afalse%2C%22m%22%3Anull}}]}}".format(resultnum)
         
# from each page, get the links to press releases
def get_links(url):
    print("Fetching search results at", url)
    
    driver = webdriver.PhantomJS()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.cbs-List")))
        page = driver.page_source
    
        soup = BeautifulSoup(page, "html.parser")
        headers = soup.find("ul", class_="cbs-List").find_all("h1", class_="mtmL-Titulo")
        for header in headers:
            yield header.find("a")["href"]
            
    except Exception as e:
        print("error", e)
                
    finally:
        driver.quit()

def parse_date(dateline):
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
    
    try:
        date_words = dateline.split()
        day = date_words[-5].zfill(2)
        year = date_words[-1]
        month_num = str(meses[date_words[-3]]).zfill(2)

        return "{0}-{1}-{2}".format(year, month_num, day)
    except Exception as e:
        print("Error parsing dateline {0}: {1}".format(dateline, e))
        return "unknown-date"
    
# from link to press release, get press release
def get_statement(statement_url):
    print("Fetching statement at", statement_url)
    
    try:
        page = requests.get(statement_url).text
        soup = BeautifulSoup(page, "html.parser")
    
        # all of the article content is contained in the div with class article
        frame = soup.find("div", class_="article")
    
        dateline = frame.find("div", class_="date fl_left").string
        date = parse_date(dateline)
    
        title = frame.find("h2").string
    
        paragraphs = frame.find_all("p")
        text = " ".join([p.string for p in paragraphs if p.string is not None])
    
        if bool(re.search("paz | la mesa | negociación | conflicto | las Farc ", text)):
            return {
                "date": date,
                "title": title,
                "text": text
            }
        else:
            return None
    
    except Exception as e:
        print("Error souping {0}: {1}".format(statement_url, e))
        return None
        
