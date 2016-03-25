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
t = {0: 'Student', 1: 'Faculty'}[eval(input('Student[0] or Faculty[1]: '))]

target = next(x for x in soupify(r).find_all(
    'a') if x.text == t + ' Log-In').get('href')
'''
Log-In page
'''
print(t + ' Log-in Page')
r = s.get(target, headers=header)
url_base = 'https://osc.npu.edu'
username = input('Enter Username: ')
password = getpass.getpass()
'''
Log-In post
'''
r = s.post(url_base + r.history[0].headers.get('Location'),
           headers=header, data={'username': username, 'password': password})
error = soupify(r).find('span').text
if re.match('Login was unsuccessful.', error):
    print(error)
    exit(1)
print('Log-in succeeded')
'''
Homepage
'''
r = s.get(config[t]['Address'], headers=header)
rows = soupify(r).table.find_all('tr')
courseList = list(filter(lambda y: (y is not None),
                         map(lambda x: grab_link(x, t), rows)))
for idx, item in enumerate(courseList):
    print('[' + str(idx) + ']' + str(item[1]) + '(' + str(item[2]) + ')')
result = eval(input('Choose Course[0-' + str(len(courseList) - 1) + ']: '))
target = courseList[result][-1]
course = str(courseList[result][1]) + str(courseList[result][2])
print('Jump to Activities page...')
'''
Activities Page
'''
r = s.get(url_base + target, headers=header)
actPage = soupify(r)
courseDetailList = list(filter(lambda x: re.match(
    r'.*\#[0-9]{5}\:', x.text), actPage.find_all('b')))
hwList = list(map(lambda x: make_item(x), courseDetailList))
for idx, item in enumerate(hwList):
    print('[' + str(idx) + '] ' + str(item[0]) + str(item[1]) + str(item[2]))
result = eval(input('Choose target[0-' + str(len(hwList) - 1) + ']: '))
No = hwList[result][1]
Week = hwList[result][2]
hr = next(x for x in actPage.find_all('a') if x.text == 'Grade').get('href')
if re.match(config[t]['Pattern'] + "/Assignment/Grade/" + No, hr):
    print('Homework page found, jumping...')
    '''
    Homework Page
    '''
    r = s.get(url_base + hr, headers=header)
else:
    print('Homework page missing.')
    exit(1)
boxes = soupify(r).find_all(
    "a", {"class": "fancybox"})
fileLinks = list(filter(lambda x: re.compile(
    "/Home/GetFile/").match(x.get('href')), boxes))
fileList = list(map(lambda x: (x.get('href'), x.text), fileLinks))

path = config['Directory']['Path']
if not path:
    path = 'C:\\Users\\' + \
        os.getenv('username') + '\\Documents\\' + \
        course + '\\' + str(Week.strip()) + '\\'
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


def soupify(r):
    return BeautifulSoup(r.text, "html.parser")


def grab_link(row, t):
    for link in row.find_all('a'):
        if link.text == config[t]['Activity']:
            result = list(map(lambda x: x.text.strip(), row.find_all('td')))
            return result.append(link.get('href'))


def make_item(x):
    number = str(x).split('<b>')[1].split('#')[0]
    course = str(x).split('#')[1].split(':')[0]
    name = str(x).split(':')[1].split('\r')[0]
    return [number, course, name]
