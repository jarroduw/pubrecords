import os
import requests
from bs4 import BeautifulSoup

target = 'https://www.monroe.wednet.edu/community/committees/school-reopening-committee'
base = 'https://www.monroe.wednet.edu'

#r = requests.get(target)

# if r.status_code == 200:
#     soup = BeautifulSoup(r.text)

with open('temp.html') as fi:
    soup = BeautifulSoup(fi.read(), features='html.parser')

main = soup.find('main', class_="fsPageContent", id="fsPageContent")
links = main.find_all('a')
for link in links:
    href = link['href']
    if 'youtu.be' in href:
        with open('youtube.txt', 'a') as fi:
            fi.write(href + '\n')
    else:
        if not href.startswith('http'):
            fullLink = "%s%s" % (base, link['href'],)
            print(fullLink)
        else:
            fullLink = href
        r = requests.get(fullLink)
        if r.status_code == 200:
            fName = os.path.basename(fullLink).replace("%20", " ")
            print(fName)
            pathToWrite = ("/c/Users/jarro/Documents/MonroePubRecRequest/"+fName)
            with open(pathToWrite, 'wb') as fiOut:
                fiOut.write(r.content)