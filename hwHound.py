import requests
import re
from bs4 import BeautifulSoup
import configparser
import getpass

config=configparser.ConfigParser()
config.read('hwHound.ini')
header={       
   'Accept': config['Headers']['Accept'],
   'Accept-Encoding': config['Headers']['Accept-Encoding'],
   'Accept-Language': config['Headers']['Accept-Language'],
   'Connection': config['Headers']['Connection'],
   'User-Agent': config['Headers']['User-Agent']
   }
s=requests.Session()
r=s.get(config['Address']['Link'],headers=header)
soup=BeautifulSoup(r.text,"html.parser")
target=''
for link in soup.find_all('a'):
    if link.text=='Student Log-In':
        target=link.get('href')
r=s.get(target,headers=header)
url_base='https://osc.npu.edu'
username=config['Auth']['Username']
password=config['Auth']['Password']
if username=='':
    username=input('Enter username: ')
if password=='':
    password=getpass.getpass()

r=s.post(url_base+r.history[0].headers.get('Location'),headers=header,data={'username':username,'password':password})

r=s.get('https://stuosc.npu.edu/TALA/Home',headers=header)
soup=BeautifulSoup(r.text,"html.parser")
target=''
for link in soup.find_all('a'):
    if link.text=='Activities':
        target=link.get('href')
url_base='https://stuosc.npu.edu/'
r=s.get(url_base+target,headers=header)
soup=BeautifulSoup(r.text,"html.parser")
list=[]
for banner in soup.find_all('b'):
    if re.match("Homework #",banner.text):
        info=banner.text.split()
        if(len(info)>8):        
            list.append((info[0],info[1],info[2]+info[3]))
        else:                    
            list.append((info[0],info[1],info[2]))

result=-1
result=int(config['Target']['Week'])-1
if result==-1:       
    for i in range(len(list)):
        print('['+str(i)+']'+' '+list[i][2])
    result=int(input('Choose homework: '))
No=''
if result in range(len(list)):
    No=list[result][1][1:-1]

for link in soup.find_all('a'):
    if link.text=='Grade':
        hr=link.get('href')
        if re.match("/TALA/Assignment/Grade/"+No,hr):
            r=s.get(url_base+hr,headers=header)
            
soup=BeautifulSoup(r.text,"html.parser")

pattern=re.compile("/Home/GetFile/")
list=[]
for link in soup.find_all("a",{ "class" : "fancybox" }):
    if(pattern.match(link.get('href'))):
        list.append((link.get('href'),link.text))
path=config['Directory']['Path']
if path=='':
    path=input('Enter a target directory: ')
path+='Week'+str(result+1)+'\\'
    
for link, name in list:
    with open(path+name,"wb") as f:
        r=s.get(url_base+link,headers=header,stream=True)
        f.write(r.content)
    print(name+" Complete.")