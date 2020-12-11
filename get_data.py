from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def tik_info():
    url = 'http://notelections.online/region/region/st-petersburg?action=show&root=1&tvd=27820001217417&vrn=27820001217413&region=78&global=&sub_region=78&prver=0&pronetvd=null&vibid=27820001217417&type=222'
    data = urlopen(url).read()
    soup = BeautifulSoup(data, 'lxml')
    tik_urls = []
    tik_names = []
    for s in soup.form.find_all('option')[1:]:
        tik_urls.append(s['value'])
        tik_names.append(s.text)
    return tik_names, tik_urls

def create_df_from_election_data(column_names, election_data, index):
    df = pd.DataFrame({column_names[i]:election_data[i] for i in range(election_data.shape[0])})
    df.index = index
    return df


def get_column_names(tables):
    columns = tables[7]
    column_names = []
    column_names_raw = columns.find_all('nobr')[1:]
    column_names_raw.pop(33) # drop empty string
    for i in range(0, len(column_names_raw), 3):
        column_names.append(column_names_raw[i+1].text)
    return column_names


def table_data(tables):
    columns = tables[8]
    values = []
    index = []
    for t in columns.find_all('td'):
        if t.find('a'):
            index.append(t.a.text)
        if t.find('b'):
            values.append(t.nobr.b.text)
    values = np.array(values).reshape(14,-1)
    return values, index


def election_results_on_tik(tik_url, tik_name):
    url = 'http://notelections.online/region'+ tik_url
    data = urlopen(url).read()
    soup = BeautifulSoup(data, 'lxml')
    tables = soup.find_all('table')
    column_names = get_column_names(tables)
    election_data, index = table_data(tables)
    df = create_df_from_election_data(column_names, election_data, index)
    df['ТИК'] = [tik_name for i in range(df.shape[0])]
    return df


tik_names, tik_urls = tik_info()
dfs = []
for tik_name, tik_url in zip(tik_names, tik_urls):
    tik_name = '_'.join(tik_name.split()[1:])
    df = election_results_on_tik(tik_url, tik_name)
    dfs.append(df)

df = pd.concat(dfs)
df.to_csv('All_election_results.csv')