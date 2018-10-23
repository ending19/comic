#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:07:52 2018

@author: ending
"""

import requests
import random
from os import path
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

Agents = [
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0b7pre) Gecko/20100921 Firefox/4.0b7pre",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b7) Gecko/20101111 Firefox/4.0b7",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b7) Gecko/20100101 Firefox/4.0b7",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b6pre) Gecko/20100903 Firefox/4.0b6pre",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0b6pre) Gecko/20100903 Firefox/4.0b6pre Firefox/4.0b6pre",
    "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b4) Gecko/20100818 Firefox/4.0b4",
    "Mozilla/5.0 (X11; Linux i686; rv:2.0b3pre) Gecko/20100731 Firefox/4.0b3pre",
    "Mozilla/5.0 (Windows NT 5.2; rv:2.0b13pre) Gecko/20110304 Firefox/4.0b13pre",
    "Mozilla/5.0 (Windows NT 5.1; rv:2.0b13pre) Gecko/20110223 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Linux i686; rv:2.0b12pre) Gecko/20110204 Firefox/4.0b12pre",
    "Mozilla/5.0 (X11; Linux i686; rv:2.0b12pre) Gecko/20100101 Firefox/4.0b12pre",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110131 Firefox/4.0b11pre",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110129 Firefox/4.0b11pre",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0b11pre) Gecko/20110126 Firefox/4.0b11pre",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0b11pre) Gecko/20110126 Firefox/4.0b11pre",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b10pre) Gecko/20110118 Firefox/4.0b10pre",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0b10pre) Gecko/20110113 Firefox/4.0b10pre",
    "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10",
]

ProxyPool = ['118.25.89.245:8080', '118.190.95.35:9001',]



def gethtml(url, headers=None, cookies=None, host=None):
    host = host or urlparse(url).netloc
    if not headers:
        headers = {'User-Agent': random.choice(Agents), 'Host': host}
    #proxies = {'http': random.choice(ProxyPool)}
    proxies = None
    res = requests.get(url, headers= headers, cookies=cookies, proxies=proxies)
    res.raise_for_status()
    if res.encoding == 'ISO-8859-1':
        res.encoding = requests.utils.get_encodings_from_content(res.text)[0]
    return res, host



def _parse_1kkk_index(html):
    root = etree.HTML(html)
    names = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/h2/a/text()")
    index_urls = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/h2/a/@href")
    ranktexts = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/p[@class='zl']/span[@class]/@class")
    status = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/p[@class='chapter']/span/text()")
    latest_urls = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/p[@class='chapter']/a/@href")
    latest_names = root.xpath("//li[not(@class)]/div/div[@class='mh-item-detali']/p[@class='chapter']/a/text()")
    if len(names) == len(latest_urls):
        names = (str(name) for name in names)
        index_urls = (str(url) for url in index_urls)
        rank = (int(text[-1]) for text in ranktexts)
        status = (sta=='完结' for sta in status)
        latest_names = (str(lname) for lname in latest_names)
        latest_urls = (str(lurl) for lurl in latest_urls)
        comics = zip(names, index_urls, rank, status, latest_names, latest_urls)
        return comics
    else:
        raise IndexError("Data length is not aligned.")


#def _parse_1kkk_chapt(html):
#    root = etree.HTML(html)
#    chapt_urls = root.xpath('//div[@id="chapterlistload"]/ul//li/a/@href')
#    if chapt_urls == []:
#        return None, None, None
#    chapt_names = root.xpath('//div[@class="info"]/p[@class="title "]/text()')
#    chapt_index = list(range(1,len(chapt_urls)+1))
#    chapts = zip(chapt_index, chapt_names, chapt_urls)
#    chapt_pay = root.xpath('//div[@class="info"]/span[@class="detail-lock"]')
#    #try:
#    #    date = root.xpath('//div[@id="chapterlistload"]/ul//li[last()]//p[@class="tip"]/text()')[-1]
#    #    chapt_modify = datetime.strptime(date,"%Y-%m-%d")
#    #except:
#    #    print("time error")
#    #    return None,None,None
#    free_num = len(chapt_urls) - len(chapt_pay)
#    #return list(chapts), free_num, chapt_modify
#    return list(chapts), free_num


def _parse_1kkk_chapt(html):
    root = etree.HTML(html)
    chapt_urls = root.xpath('//div[@id="chapterlistload"]/ul//li/a/@href')
    lenth = len(chapt_urls)
    nameflag = root.xpath('//div[@id="chapterlistload"]/ul//li/a/div[@class="cover"]')
    if len(nameflag)==lenth:
        chapt_names = root.xpath('//div[@class="info"]/p[@class="title "]/text()')
    else:
        chapt_names = root.xpath('//div[@id="chapterlistload"]/ul//li/a/text()')
    chapt_names = [name.strip() for name in chapt_names if name.strip() !='']
    lenth = len(chapt_urls)
    if lenth == len(chapt_names):
        chapt_urls = [str(url) for url in chapt_urls]
        chapt_type = []
        for i,v in enumerate(chapt_urls):
            if v[:3]=='/ch':
                chapt_type.append('ch')
            elif v[:3]=='/sp' or v[:3]=='/ot':
                chapt_type.append('other')
            else:
                chapt_type.append(None)
        try:
            chapt_index = [int(url.split('-')[0][3:]) if chapt_type[i]=='ch' else None for i,url in enumerate(chapt_urls)] 
            chapts = zip(chapt_index, chapt_names, chapt_urls, chapt_type)
            chapt_pay = root.xpath('//span[@class="detail-lock"]')
            free_num = lenth - len(chapt_pay)
            return list(chapts), free_num
        except:
            print('parse error')
            return None, None
    else:
        print('error')
        return None, None


def parseindex(url, headers=None, cookies=None, host=None):
    res, host = gethtml(url, headers=headers, cookies=cookies, host=host)
    if host == 'www.1kkk.com':
        _parseindex = _parse_1kkk_index
    return _parseindex(res.text), host


def parsechapt(url, headers=None, cookies=None, host=None):
    res, host = gethtml(url, headers=headers, cookies=cookies, host=host)
    if host == 'www.1kkk.com':
        _parsechapt = _parse_1kkk_chapt
    return _parsechapt(res.text)



def htmltest(url, web=False, headers=None, cookies=None, host=None):
    if not path.exists('test.html') or web:
        res, host = gethtml(url, headers=headers, cookies=cookies, host=host)
        soup = BeautifulSoup(res.text, 'lxml')
        html = soup.prettify()
        with open('test.html','w') as f:
            f.write(html)
    else:
        with open('test.html','r') as f:
            html = f.read()
    root = etree.HTML(html)
    return root, soup


if __name__ == '__main__':
    URL = "http://www.1kkk.com/manhua369/"
    root, soup = htmltest(URL,web=True)





