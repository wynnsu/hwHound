import requests
import re
from bs4 import BeautifulSoup
import configparser

config=configparser.ConfigParser()
config.read('hwHound.ini')
url_base='https://stuosc.npu.edu/'
header={       
   'Accept': config['Headers']['Accept'],
   'Accept-Encoding': config['Headers']['Accept-Encoding'],
   'Accept-Language': config['Headers']['Accept-Language'],
   'Connection': config['Headers']['Connection'],
   'User-Agent': config['Headers']['User-Agent']
   }
r=requests.get('http://www.npu.edu/',headers=header)
soup=BeautifulSoup(r.text,"html.parser")
target=''
for link in soup.find_all('a'):
    if link.text=='Student Log-In':
        target=link.get('href')
r=requests.get(target,headers=header)
print(r.headers)
print(r.request.headers)