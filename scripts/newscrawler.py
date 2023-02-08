from decouple import config
import requests
from bs4 import BeautifulSoup

NOTION_KEY = config("NOTION_KEY")
print(NOTION_KEY)

url = 'http://34.64.158.160/marinecroc.html'
page = requests.get(url)
#print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')
headline = soup.find(id='headline')
date_posted = soup.find(id='date_posted')
abstract = soup.find(id='abstract')
first = soup.find(id='first')
text = soup.find(id='text')
journal_references = soup.find(id='journal_references')

if False:
    print(headline.text)
    print(date_posted.text)
    print(first.text)
    print(abstract.text)

    print(text.text)
    print(journal_references.text)

import os
import json

headers = {'Authorization': f"Bearer {NOTION_KEY}", 
           'Content-Type': 'application/json', 
           'Notion-Version': '2022-06-28'}
search_params = {"filter": {"value": "page", "property": "object"}}
search_response = requests.post(
    f'https://api.notion.com/v1/search', 
    json=search_params, headers=headers)

print(search_response.json())           