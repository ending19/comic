#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:00:03 2018

@author: ending
"""

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count, Lock
from multiprocessing import Pool as ProcessPool
from dbs import ComicIndex, ComicChapt, Session, index_insert, chapt_update
from parse import parseindex, parsechapt
from functools import partial
from time import ctime


PROCESSNUMS = cpu_count()
THREADNUMS = 5
lock = Lock()

URLs = [
        'http://www.1kkk.com/manhua-list-p',
        ]



def _get_comic_index(url):
    session = Session()
    print('Get from', url)
    comics, host = parseindex(url)
    if comics:
        index_insert(comics, host, session)
    session.commit()
    session.close()
    


def get_comic_index():
    urlpool = [url+str(i)+'/' for url in URLs for i in range(1,470)]
    print("Crawl index: ", ctime())
    pool = ProcessPool(PROCESSNUMS)
    pool.map(_get_comic_index, urlpool)
    pool.close()
    pool.join
    print('Finished:', ctime())
    
    


def _process_update_chapt(num):
    print('Process:', num)
    session = Session()
    #chaptnum = session.query(ComicIndex).count()
    chaptnum = 400
    temp = int(chaptnum/PROCESSNUMS)
    partnum = temp if chaptnum%PROCESSNUMS==0 else temp+1
    lock.acquire()
    querysets = session.query(ComicIndex).filter(ComicIndex.id>=num*partnum).filter(ComicIndex.id<(num+1)*partnum)
    lock.release()
    tpool = ThreadPool(THREADNUMS)
    tpool.map(_thread_update_chapt, querysets)
    tpool.close()
    tpool.join()
    
    


def _thread_update_chapt(queryset):
    session = Session()
    url = 'http://' + queryset.host + queryset.index_url
    chapts, free_num = parsechapt(url)
    if chapts:
        #chapt_update(chapts, free_num, modifytime, queryset, session)
        chapt_update(chapts, free_num, queryset, session)
        session.commit()
    else:
        print("error:",url)


def update_comic_chapt():
    print("Crawl chapt:", ctime())
    pool = ProcessPool(PROCESSNUMS)
    pool.map(_process_update_chapt, [0,1,2,3])
    pool.close()
    pool.join()
    print("Finished:",ctime())




def main():
    print('Begin:',ctime())
    get_comic_index()
    update_comic_chapt()
    print("End:",ctime())
    


if __name__ == '__main__':
    main()