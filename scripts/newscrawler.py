
from decouple import config
import requests
from bs4 import BeautifulSoup
import os
import json

#print(NOTION_KEY)
import deepl

NOTION_KEY = config("NOTION_KEY")
DEEPL_KEY = config("DEEPL_KEY")

#print(DEEPL_KEY)

def get_sciencedaily(url):
    page = requests.get(url)
    #print(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')

    key_list = ['headline','date_posted','abstract','first','text','journal_references']
    text_hash = {}
    for k in key_list:
        text_hash[k] = soup.find(id=k).text
    return text_hash

def translate_paragraph(text, target_lang="KO"):
    result = translator.translate_text(text, target_lang=target_lang)
    return result.text

def format_blocks(p_list2):
    l_block_list = []
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
        l_block_list.append(block)
    return l_block_list

def translate_text(text, target_lang="KO"):
    l_p_list = text.split("\n")
    l_p_list2 = []
    for p in l_p_list:
        #print(p)
        l_p_list2.append(p)
        if len(p) > 0:
            #result = translator.translate_text(p, target_lang="KO")
            trans_p = translate_paragraph(p, target_lang=target_lang)
            l_p_list2.append(trans_p)
    return l_p_list2

translator = deepl.Translator(DEEPL_KEY)

url = 'http://34.64.158.160/marinecroc.html'
notion_headers = {'Authorization': f"Bearer {NOTION_KEY}",
           'Content-Type': 'application/json',
           'Notion-Version': '2022-06-28'}
scidaily_id = "f604567f-9be6-48e0-a31b-42667dec0ae4" # Science Daily page id


text_hash = get_sciencedaily(url)
p_list = translate_text(text_hash['text'])
block_list = format_blocks(p_list)
page_id = scidaily_id

create_page_body = {
    "parent": { "page_id": page_id },
    "properties": {
        "title": {
      "title": [{
          "type": "text",
          "text": { "content": text_hash['headline'] } }]
        }
    },
    "children": block_list
}

create_response = requests.post(
     "https://api.notion.com/v1/pages",
     json=create_page_body, headers=notion_headers)
print(create_response.json())


"""
    search_params = {"filter": {"value": "page", "property": "object"}}
    search_response = requests.post(
        f'https://api.notion.com/v1/search',
        json=search_params, headers=headers)

    print(search_response.json())

    search_results = search_response.json()["results"]
"""