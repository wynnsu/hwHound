# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import configparser
import getpass
import os

config = configparser.ConfigParser()
config.read('hwHound.ini')
header = {
    'Accept': config['Headers']['Accept'],
    'Accept-Encoding': config['Headers']['Accept-Encoding'],
    'Accept-Language': config['Headers']['Accept-Language'],
    'Connection': config['Headers']['Connection'],
    'User-Agent': config['Headers']['User-Agent']
}
s = requests.Session()
'''
NPU main page
'''
r = s.get(config['Address']['Link'], headers=header)
print('Main page...')
soup = BeautifulSoup(r.text, "html.parser")

t=eval(input('Student[0] or Faculty[1]: '))
if t == 0:
    t = 'Student'
if t == 1:
    t = 'Faculty'
target = ''
for link in soup.find_all('a'):
    if link.text == t + ' Log-In':
        target = link.get('href')
'''
Log-In page
'''
print(t + ' Log-in Page')
r = s.get(target, headers=header)
url_base = 'https://osc.npu.edu'
username=input('Enter Username: ')
password=getpass.getpass()
'''
Log-In post
'''
r = s.post(url_base + r.history[0].headers.get('Location'),
           headers=header, data={'username': username, 'password': password})
soup = BeautifulSoup(r.text, "html.parser")
error = soup.find('span').text
if re.match('Login was unsuccessful.', error):
    print(error)
    exit(1)
print('Log-in succeeded')
'''
Homepage
'''
r = s.get(config[t]['Address'], headers=header)
soup = BeautifulSoup(r.text, "html.parser")
target = ''

rows = soup.table.find_all('tr')


def grab_link(row, t):
    for link in row.find_all('a'):
        if link.text == config[t]['Activity']:
            result = list(map(lambda x: x.text.strip(), row.find_all('td')))
            result.append(link.get('href'))
            return result

courseList = list(filter(lambda y: (y is not None), map(lambda x: grab_link(x, t), rows)))

for idx, item in enumerate(courseList):
    print('[' + str(idx) + ']' + str(item[1]) + '(' + str(item[2]) + ')')
result = eval(input('Choose Course[0-' + str(len(courseList) - 1) + ']: '))

target = courseList[result][-1]
course = str(courseList[result][1])+str(courseList[result][2])
print('Jump to Activities page...')
'''
Activities Page
'''
r = s.get(url_base + target, headers=header)

soup = BeautifulSoup(r.text, "html.parser")

courseDetailList = list(filter(lambda x: re.match(
    r'.*\#[0-9]{5}\:', x.text), soup.find_all('b')))


def make_item(x):
    number = str(x).split('<b>')[1].split('#')[0]
    course = str(x).split('#')[1].split(':')[0]
    name = str(x).split(':')[1].split('\r')[0]
    return [number, course, name]
hwList = list(map(lambda x: make_item(x), courseDetailList))

for idx, item in enumerate(hwList):
    print('[' + str(idx) + '] ' + str(item[0]) + str(item[1]) + str(item[2]))
result = eval(input('Choose target[0-' + str(len(hwList) - 1) + ']: '))

No = hwList[result][1]
Week = hwList[result][2]

for link in soup.find_all('a'):
    if link.text == 'Grade':
        hr = link.get('href')

        if re.match(config[t]['Pattern'] + "/Assignment/Grade/" + No, hr):
            print('Homework page found, jumping...')
            '''
            Homework Page
            '''
            r = s.get(url_base + hr, headers=header)

soup = BeautifulSoup(r.text, "html.parser")
pattern = re.compile("/Home/GetFile/")
fileList = list(map(lambda x: (x.get('href'), x.text), list(filter(lambda x: pattern.match(
    x.get('href')), soup.find_all("a", {"class": "fancybox"})))))

path = config['Directory']['Path']
if not path:
    path = 'C:\\Users\\' + os.getenv('username') + '\\Documents\\' + course + '\\' + str(Week.strip()) + '\\'
print(str(len(fileList)) + 'files found...')
print('Downloading to directory: ')
print(path)
if not os.path.exists(path):
    os.makedirs(path)

for link, name in fileList:
    with open(path + name, "wb") as f:
        r = s.get(url_base + link, headers=header, stream=True)
        f.write(r.content)
    print(name + " Complete.")
print('All done.')