import requests
from bs4 import BeautifulSoup

url = 'http://www.sciencedaily.com/releases/2023/01/230125121550.htm'
page = requests.get(url)
print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')
headline = soup.find(id='headline')
date_posted = soup.find(id='date_posted')
abstract = soup.find(id='abstract')
first = soup.find(id='first')
text = soup.find(id='text')
journal_references = soup.find(id='journal_references')

print(headline)