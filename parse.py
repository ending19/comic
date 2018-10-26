#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:07:52 2018

@author: ending
"""

import requests
import random
import re
from os import path
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from simulation import web_1kkk_limit


# 浏览器标识头
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
# 代理池
ProxyPool = ['118.25.89.245:8080', ]
# 用于获取1kkk网站的漫画章节索引的正则表达式
re_1kkk_chapt = re.compile(r'/ch(\d+).*-')


# 用于获取HTML网页
def gethtml(url, headers=None, cookies=None, host=None):
    host = host or urlparse(url).netloc             # 获取网址的host信息
    if not headers:
        headers = {'User-Agent': random.choice(Agents), 'Host': host}
    proxies = {'http': random.choice(ProxyPool)}
    #proxies = None                                  # 此处不使用代理
    res = requests.get(url, headers= headers, cookies=cookies, proxies=proxies)
    res.raise_for_status()
    if res.encoding == 'ISO-8859-1':                # 网页编码处理
        res.encoding = requests.utils.get_encodings_from_content(res.text)[0]
    return res, host


# 对1kkk网站的漫画信息的解析
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


# 对1kkk网站的正常的漫画章节的解析
def _1kkk_chapt_normal(root):
    chapt_urls = root.xpath('//div[@id="chapterlistload"]/ul//li/a/@href')
    nameflag = root.xpath('//div[@id="chapterlistload"]/ul//li/a/div[@class="cover"]')
    if nameflag:                        # 针对不同的网页类型
        chapt_names = root.xpath('//div[@class="info"]/p[@class="title "]/text()')
    else:
        chapt_names = root.xpath('//div[@id="chapterlistload"]/ul//li/a/text()')
    chapt_names = [name.strip() for name in chapt_names if name.strip() !='']
    chapt_pay = root.xpath('//span[@class="detail-lock"]')
    chapt_discount = root.xpath('//div[@id="chapterlistload"]/ul//span[@class="view-discount-red"]')
    order = root.xpath('//span[@class="s"]/a[@class="order "]/text()')
    order = order[0].strip()=='正序' if order else False
    return chapt_urls, chapt_names, len(chapt_pay)+len(chapt_discount), order
    

# 对1kkk网站的某些限制级漫画进行解析，使用模拟浏览器，加载JavaScript  
def _1kkk_chapt_limit(url):
    html = web_1kkk_limit(url)
    root = etree.HTML(html)
    return _1kkk_chapt_normal(root)


# 对1kkk的漫画章节进行解析
def _parse_1kkk_chapt(html, url):
    root = etree.HTML(html)
    chapt_warning = root.xpath('//div[@class="warning-bar"]')
    if not chapt_warning:
        chapt_urls, chapt_names, chapt_pay, order =  _1kkk_chapt_normal(root)
    elif root.xpath('//div[@class="warning-bar"]/a'):
        chapt_urls, chapt_names, chapt_pay, order =  _1kkk_chapt_limit(url)
    else:                                       # 由于政策原因，该漫画被屏蔽了
        print('lost')
        return None, True
    lenth =len(chapt_urls)
    if lenth == len(chapt_names):
        chapt_urls = [str(curl) for curl in chapt_urls]
        # 对漫画章节类型进行分类，主线还是番外
        chapt_type = []
        for i,v in enumerate(chapt_urls):
            if v[:3]=='/ch':
                chapt_type.append('ch')
            elif v[:3]=='/sp' or v[:3]=='/ot':
                chapt_type.append('other')
            else:
                chapt_type.append(None)
        # 为漫画章节添加索引
        last_url = chapt_urls[-1] if order else chapt_urls[0]
        if set(chapt_type)=={'ch'} and lenth==int(re_1kkk_chapt.search(last_url).group(1)):
            chapt_index = range(1,lenth+1) if order else range(lenth,0,-1)
        else:
            indexs = [re_1kkk_chapt.search(curl) for curl in chapt_urls]
            chapt_index = [int(index.group(1)) if index else None for index in indexs]
        # 将章节信息打包并返回
        try:    
            chapts = zip(chapt_index, chapt_names, chapt_urls, chapt_type)
            free_num = lenth - chapt_pay
            return list(chapts), free_num
        except:
            return None, False
    else:
        return None, False


# 解析漫画信息
def parseindex(url, headers=None, cookies=None, host=None):
    res, host = gethtml(url, headers=headers, cookies=cookies, host=host)
    if host == 'www.1kkk.com':
        _parseindex = _parse_1kkk_index
    return _parseindex(res.text), host


# 解析章节信息
def parsechapt(url, headers=None, cookies=None, host=None):
    res, host = gethtml(url, headers=headers, cookies=cookies, host=host)
    if host == 'www.1kkk.com':
        _parsechapt = _parse_1kkk_chapt
    return _parsechapt(res.text, url)


# 用于HTML测试
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
    return root, soup, html



if __name__ == '__main__':
    URL = "http://www.1kkk.com/manhua369/"
    root, soup, html = htmltest(URL,web=True)
    #chapt_urls, chapt_names, chapt_pay = _1kkk_chapt_normal(root)
    chapts, free = _parse_1kkk_chapt(html,URL)




