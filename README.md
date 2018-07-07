# world_cup_crawler
This is a crawler code that looks up information about footballers
import urllib
import re
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

feature_name = ['PlayerName', 'Rating', 'Position', 'Skills', 'WeakFoot', 'AttackDetense', 'Pace', 'Shooting', 'Passing', 'Dribbling', 'Detending', 'Physicality', 'Height', 'Popularity', 'BaseStats', 'InGameStats']

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
req = urllib.request.Request(url="https://www.futbin.com/18/world-cup/players?page=1&nation=195", headers=headers)
page = urllib.request.urlopen(req)
contents = page.read()
soup = BeautifulSoup(contents, "html.parser")

nation_link = {}
for cur_a in soup.find_all('a', class_='cln_sub_fix'):
    nation_link[cur_a.get_text().strip()] = 'https://www.futbin.com' + cur_a['href']

def get_player_info(nation, link, cur_page_num):
    req = urllib.request.Request(url=link, headers=headers)
    page = urllib.request.urlopen(req)
    contents = page.read()
    soup = BeautifulSoup(contents, "html.parser")
    data = []
    for cur_player in soup.find_all('tr', class_='player_tr_1'):
        cur_player_dic = {}
        cur_player_dic['Nation'] = nation
        if len(cur_player.find_all('td')) == len(feature_name):
            for i, cur in enumerate(cur_player.find_all('td')):
                cur_player_dic[feature_name[i]] = cur.get_text().strip()
            data.append(cur_player_dic)
        else:
            print(nation)
    for cur_player in soup.find_all('tr', class_='player_tr_2'):
        cur_player_dic = {}
        cur_player_dic['Nation'] = nation
        if len(cur_player.find_all('td')) == len(feature_name):
            for i, cur in enumerate(cur_player.find_all('td')):
                cur_player_dic[feature_name[i]] = cur.get_text().strip()
            data.append(cur_player_dic)
        else:
            print(nation)
    next_link = ''
    for cur_a in soup.find_all('a', class_='pagination_a'):
        if int(re.search('page=\d+', cur_a['href']).group().split('=')[1]) == cur_page_num + 1:
            next_link = 'https://www.futbin.com' + cur_a['href']
    return data, next_link

data = []
for cur_nation, cur_link in nation_link.items():
    print('working on:', cur_nation)
    cur_page_num = 1
    while cur_link:
        #print(cur_link)
        cur_data, cur_link = get_player_info(cur_nation, cur_link, cur_page_num)
        data.extend(cur_data)
        cur_page_num += 1

data = pd.DataFrame(data)

data.BaseStats = data.BaseStats.astype(int)
data.Detending = data.Detending.astype(int)
data.Dribbling = data.Dribbling.astype(int)
data.Height = data.Height.apply(lambda x: x.split('cm')[0]).astype(int)
data.InGameStats.replace('-', pd.np.nan, inplace=True)
data.Pace = data.Pace.astype(int)
data.Passing = data.Passing.astype(int)
data.Physicality = data.Physicality.astype(int)
data.Popularity = data.Popularity.astype(int)
data.Rating = data.Rating.astype(int)
data.Shooting = data.Shooting.astype(int)
data.Skills = data.Skills.astype(int)
data.WeakFoot = data.WeakFoot.astype(int)

num_col = data.dtypes[data.dtypes == 'int32'].index
train_data = data.ix[data.InGameStats.notnull(), num_col]
train_label = np.arange(len(train_data))
test_data = data.ix[data.InGameStats.isnull(), num_col]
clf = KNeighborsClassifier(1)
clf.fit(train_data, train_label)
test_label = clf.predict(test_data)
inx = train_data.index[test_label]
for inx1, inx2 in zip(test_data.index, inx):
    data.ix[inx1, 'InGameStats'] = data.ix[inx2, 'InGameStats']
data.InGameStats = data.InGameStats.astype(int)
