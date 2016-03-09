import requests
import re
from bs4 import BeautifulSoup
import configparser
import getpass
import os

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
'''
NPU main page
'''
r=s.get(config['Address']['Link'],headers=header)
print('Main page...')
soup=BeautifulSoup(r.text,"html.parser")

t=input("Student[0] or Faculty[1]: ")
if t=='0':
    t='Student'
if t=='1':
    t='Faculty'
target=''
for link in soup.find_all('a'):
    if link.text==t+' Log-In':
        target=link.get('href')
'''
Log-In page
'''
print('Log-in Page...')
r=s.get(target,headers=header)
url_base='https://osc.npu.edu'
username=input('Enter username: ')
password=getpass.getpass()
'''
Log-In post
'''
r=s.post(url_base+r.history[0].headers.get('Location'),headers=header,data={'username':username,'password':password})
print('Log-in succeeded, hopefully...')
'''
Homepage
'''
r=s.get(config[t]['Address'],headers=header)
soup=BeautifulSoup(r.text,"html.parser")
target=''

for tab in soup.find_all('table'):
    for row in tab.find_all('tr'):
        for col in row.find_all('td'):
            if re.match(config['Target']['Course'],col.text):
                for link in row.find_all('a'):
                    if link.text==config[t]['Activity']:
                        target=link.get('href')
                        break
print('Jump to Activities page...')
'''
Activities Page
'''
r=s.get(url_base+target,headers=header)

soup=BeautifulSoup(r.text,"html.parser")
list=[]
for banner in soup.find_all('b'):
    if re.match(r'.*\#[0-9]{5}\:',banner.text):
        name=banner.text.split('#')[0]
        number=banner.text.split('#')[1].split(':')[0]
        list.append([name,number])
        
for idx,item in enumerate(list):
    print('['+str(idx)+']',item[0],item[1])
result=int(input('Choose target[0-'+str(len(list)-1)+']: '))

No=list[result][1]

for link in soup.find_all('a'):
    if link.text=='Grade':
        hr=link.get('href')
        
        if re.match(config[t]['Pattern']+"/Assignment/Grade/"+No,hr):
            print('Homework page found, jumping...')
            '''
            Homework Page
            '''
            r=s.get(url_base+hr,headers=header)
                
soup=BeautifulSoup(r.text,"html.parser")
pattern=re.compile("/Home/GetFile/")
list=[]
for link in soup.find_all("a",{ "class" : "fancybox" }):
    if(pattern.match(link.get('href'))):
        list.append((link.get('href'),link.text))
path=''
path=config['Directory']['Path']
if path=='':
    path='C:\\Users\\'+os.getenv('username')+'\\Documents\\'+config['Target']['Course']+'\\Week'+str(result+1)+'\\'
print(str(len(list))+'files found...')
print('Downloading to directory: ')
print(path)
if not os.path.exists(path):
    os.makedirs(path)
    
for link, name in list:
    with open(path+name,"wb") as f:
        r=s.get(url_base+link,headers=header,stream=True)
        f.write(r.content)
    print(name+" Complete.")
print('All done.')