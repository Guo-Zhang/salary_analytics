# -*- coding: utf-8 -*-


import json
import re

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm


def request_html(city):
    r = requests.get('http://salarycalculator.sinaapp.com/report/%s'%(city))
    return r.content

def parse_html(html):
    soup = BeautifulSoup(html, 'html5lib')
    sample_size = soup.find('span', attrs={'class':'report-fyi'}).get_text()
    avg_salary = soup.find('span', attrs={'id':'avg-countup'}).get_text()

    dtb_salary = {}
    for item in soup.find('ul', attrs={'class':'level-list'}).find_all('li'):
        level = item.find('div', attrs={'class':'level pull-left'}).get_text()
        value = item.find('div', attrs={'class':'value pull-right'}).get_text()
        dtb_salary[level] = value

    job_rank = []
    for table in soup.find_all('div',attrs={'class':'col-md-6'}):
        job_table = []
        for tr in table.find_all('tr')[1:]:
            job_info = []
            for td in tr.find_all('td'):
                text = td.get_text()
                job_info.append(text)
            job_table.append(job_info)
        job_rank.append(job_table)
        # print(job_table)

    data = {
        'sample_size': sample_size,
        'avg_salary': avg_salary,
        'salary_distribution': dtb_salary,
        'job_salary_rank': job_rank[0],
        'industry_rank': job_rank[1],
            }
    return data


def save_data(raw):
    data = json.dumps(raw)
    with open('data.json', 'w') as f:
        f.write(data)


def main():

    # request for the city list
    r = requests.get('http://salarycalculator.sinaapp.com/report/%E5%8C%97%E4%BA%AC')
    soup = BeautifulSoup(r.content, "html5lib")
    city_list = [item.get_text() for item in soup.find('div',id="map").find_all('a')]

    # data for each city
    data_raw = []
    for city in tqdm(city_list):
        try:
            html = request_html(city)
            item = parse_html(html)
            item['city'] = city
            data_raw.append(item)
        except Exception as e:
            print(e)
            with open('error.txt','a') as f:
                f.write(city)
                f.write('\n')
    save_data(data_raw)


if __name__=="__main__":
    main()