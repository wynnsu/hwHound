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
   'Cookie': config['Headers']['Cookie'],
   'Host': config['Headers']['Host'],
   'Referer': config['Headers']['Referer'],
   'User-Agent': config['Headers']['User-Agent']
   }
r=requests.get(config['Address']['Link'],headers=header)
soup=BeautifulSoup(r.text)
pattern=re.compile("/Home/GetFile/")
list=[]
for link in soup.find_all("a",{ "class" : "fancybox" }):
    if(pattern.match(link.get('href'))):
        list.append((link.get('href'),link.text))
for link, name in list:
    with open(config['Directory']['Path']+name,"wb") as f:
        r=requests.get(url_base+link,headers=header,stream=True)
        f.write(r.content)
    print(name+" Complete.")