# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 12:08:54 2018

@author: Administrator
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
import pandas as pd


driver = webdriver.Chrome(executable_path='G:\\chromedriver.exe')
url = 'https://www.fifa.com/worldcup/players/browser/'
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
all_link = soup.find_all('a', class_='fi-p--link ')
data_link = []
for cur_link in all_link:
    data_link.append('https://www.fifa.com' + cur_link['href'].strip())

def get_player_info(link):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=link, headers=headers)
    page = urllib.request.urlopen(req)
    contents = page.read()
    soup = BeautifulSoup(contents, "html.parser")
    cur_player = {}
    cur_player['PlayerName'] = soup.find('div', class_='fi-p__name').get_text().strip()
    cur_player['Nation'] = soup.find('div', class_='fi-p__country').get_text().strip()
    cur_player['Position'] = soup.find('div', class_='fi-p__role').get_text().strip()
    for cur_inx, cur_ele in enumerate(soup.find_all('div', class_='fi-p__profile-number__number')):
        if cur_inx == 0:
            cur_player['Age'] = int(cur_ele.get_text().strip())
        else:
            cur_player['Height'] = float(cur_ele.get_text().strip().split()[0])
    return cur_player

data = []
for cur_inx, cur_link in enumerate(data_link):
    if cur_inx % 50 == 0:
        print('working on :', cur_inx)
    try:
        data.append(get_player_info(cur_link))
    except:
        print('error :', cur_inx)
data = pd.DataFrame(data)
data.to_csv('G:\\player.csv', index=False)