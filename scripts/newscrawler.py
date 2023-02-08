
from decouple import config
import requests
from bs4 import BeautifulSoup

NOTION_KEY = config("NOTION_KEY")
DEEPL_KEY = config("DEEPL_KEY")
#print(NOTION_KEY)
import deepl

print(DEEPL_KEY)

translator = deepl.Translator(DEEPL_KEY)


url = 'http://34.64.158.160/marinecroc.html'
page = requests.get(url)
#print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')

key_list = ['headline','date_posted','abstract','first','text','journal_references']
text_hash = {}
for k in key_list:
    text_hash[k] = soup.find(id=k).text

block_list = []
p_list2 = []
p_list = text_hash['text'].split("\n")
for p in p_list:
    #print(p)
    p_list2.append(p)
    if len(p) > 0:
        result = translator.translate_text(p, target_lang="KO")
        p_list2.append(text_hash['result'])


for p in p_list2:
    block =     {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{
            "type": "text",
            "text": {
                "content": p
            }
        }]
      }
    }
    block_list.append(block)

    #print(p)

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

search_results = search_response.json()["results"]
scidaily_id = "f604567f-9be6-48e0-a31b-42667dec0ae4"
#page_id = search_results[0]["id"]
page_id = scidaily_id

create_page_body = {
    "parent": { "page_id": page_id },
    "properties": {
        "title": {
      "title": [{
          "type": "text",
          "text": { "content": headline.text } }]
        }
    },
    "children": block_list
}

create_response = requests.post(
     "https://api.notion.com/v1/pages",
     json=create_page_body, headers=headers)
print(create_response.json())

