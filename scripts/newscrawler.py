import sys
from decouple import config
import requests
from bs4 import BeautifulSoup
import os
import json
import urllib.request
import time
import deepl
import googletrans
from datetime import datetime

NOTION_KEY = config("NOTION_KEY")
DEEPL_KEY = config("DEEPL_KEY")

PAPAGO_ID = config("PAPAGO_ID")
PAPAGO_SECRET = config("PAPAGO_SECRET")

deepl_translator = deepl.Translator(DEEPL_KEY)
notion_headers = {'Authorization': f"Bearer {NOTION_KEY}",
           'Content-Type': 'application/json',
           'Notion-Version': '2022-06-28'}

scidaily_id = "f604567f-9be6-48e0-a31b-42667dec0ae4" # Science Daily page id

def get_html_article(url):
    #page = requests.get(url)
    page = requests.get(url,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    retry_count = 0
    while page.status_code != 200:
        print("retrying...",page.status_code)
        page = requests.get(url,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        retry_count += 1
        if retry_count > 10:
            return None
        time.sleep(10)
    return page.content

def get_sciencedaily_article(url):
    page_content = get_html_article(url)
    if not page_content:
        return None

    soup = BeautifulSoup(page_content, 'html.parser')

    key_list = ['headline','date_posted','abstract','first','text','journal_references']
    text_hash = {}
    for k in key_list:
        print(k)
        obj = soup.find(id=k)
        if obj:
            text_hash[k] = soup.find(id=k).text
        else:
            text_hash[k] = ''
    return text_hash


def get_physorg_article(url):

    page_content = get_html_article(url)
    if not page_content:
        return None

    soup = BeautifulSoup(page_content, 'html.parser')
    article = soup.find(class_='news_article')
    article_info = soup.find(class_='article__info-item')
    article_main = soup.find(class_='article-main')
    article_img = soup.find(class_='article-img').img['src']   
    article_h1 = soup.find('h1')

    #print( article_info.text)
    #print( article_img)
    #print( article_h1.text)
    #print( article_main.text)
    text_hash={}

    text_hash['headline'] = article_h1.text
    text_hash['date_posted'] = article_info.text.strip()
    text_hash['abstract'] = ''
    text_hash['first'] = ''
    l_p_list=[]
    for p in article_main.text.split('\n'):
        if len(p.strip()) > 0:
            l_p_list.append(p.strip())
            #break
    text_hash['text'] = "\n".join(l_p_list)
    text_hash['journal_references'] = ''
    
    return text_hash    

def translate_paragraph_papago(text, target_lang="KO"):
    #result = translator.translate_text(text, target_lang=target_lang)
    #return result.text

    encText = urllib.parse.quote(text)
    data = "source=en&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",PAPAGO_ID)
    request.add_header("X-Naver-Client-Secret",PAPAGO_SECRET)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        result = response_body.decode('utf-8')
        #print(result)
        result = json.loads(result)

        #print(result['translatedText'])
        #print(result['message']['result'])
        result_text = result['message']['result']['translatedText']
        #print(result_text)
        return result_text
    else:
        print("Error Code:" + rescode)
        return ''

def translate_paragraph_google(text, target_lang="KO"):
    translator = googletrans.Translator()
    result = translator.translate(text, dest=target_lang)
    return result.text

    #str1 = "나는 한국인 입니다."
    #str2 = "I like burger."
    #result1 = translator.translate(str1, dest='en')
    #result2 = translator.translate(str2, dest='ko')

    #print(f"나는 한국인 입니다. => {result1.text}")
    #print(f"I like burger. => {result2.text}")    

def translate_text(p_list, target_lang="KO"):
    l_p_list2 = []
    for p in p_list:
        #print(p)
        l_p_list2.append(p)
        if len(p) > 0:
            
            trans_papago_p = translate_paragraph_papago(p, target_lang=target_lang)
            l_p_list2.append("[파파고]: " + trans_papago_p)

            trans_google_p = translate_paragraph_google(p, target_lang=target_lang)
            l_p_list2.append("[구글]: " + trans_google_p)

            time.sleep(3)
    return l_p_list2

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

n = len(sys.argv)
url = ''

if n > 1:
    url = sys.argv[1] #'''https://www.sciencedaily.com/releases/2023/02/230208125147.htm'
    print("url: ", url)
else:
    print("no url")
    sys.exit()

paragraph_list=[]
source_name = ''

''' begin time '''
begin_time = "Begin time: "+ datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if url.find('phys.org') > 0:
#text_hash = get_sciencedaily_article(url)
    source_name = "Phys.org"
    text_hash = get_physorg_article(url)
elif url.find('sciencedaily.com') > 0:
    source_name = "사이언스 데일리"
    text_hash = get_sciencedaily_article(url)
else:
    print("Can't handle url", url)
    sys.exit()

if not text_hash:
    print("no text_hash")
    sys.exit()

for k in ['headline','date_posted','abstract','first']:
    paragraph_list.append(text_hash[k])

paragraph_list.append("("+translate_paragraph_papago(text_hash['date_posted'], target_lang="KO")+" <a href='"+url+"'>" + source_name + " 기사</a> 번역)")
#paragraph_list.append(url)
paragraph_list.extend(text_hash['text'].split('\n'))
#paragraph_list = translate_text(paragraph_list)
paragraph_list.append(text_hash['journal_references'])

''' end time '''
end_time = "End time: "+ datetime.now().strftime("%Y-%m-%d %H:%M:%S")
paragraph_list.append(begin_time)
paragraph_list.append(end_time)

block_list = format_blocks(paragraph_list)
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

create_response = requests.post("https://api.notion.com/v1/pages",json=create_page_body,headers=notion_headers)