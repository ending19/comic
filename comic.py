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
from time import ctime
from os import path

# 进程数，默认使用CPU核心数
PROCESSNUMS = cpu_count()
# 线程数
THREADNUMS = 10
# 加锁
lock = Lock()

# 漫画网站前缀
URLs = [
        'http://www.1kkk.com/manhua-list-p',            # 极速漫画
        ]


# 获取漫画名子进程，获取漫画名并存入数据库
def _get_comic_index(url):
    session = Session()
    #print('Get from', url)
    comics, host = parseindex(url)
    if comics:
        index_insert(comics, host, session)
    session.commit()
    

# 获取漫画名总进程，使用进程池
def get_comic_index():
    urlpool = [url+str(i)+'/' for url in URLs for i in range(1,470)]
    print("Crawl index: ", ctime())
    pool = ProcessPool(PROCESSNUMS)
    pool.map(_get_comic_index, urlpool)
    pool.close()
    pool.join
    print('Finished:', ctime())
    
 
# 获取漫画章节子线程，根据数据库的漫画信息，爬取对应的章节，并记录错误
def _thread_update_chapt(queryset):
    session = Session()
    url = 'http://' + queryset.host + queryset.index_url
    chapts, free_num = parsechapt(url)
    if chapts:
        chapt_update(chapts, free_num, queryset, session)
        session.commit()
    elif free_num:
        err_msg = "page lost: %s" % url
        print(err_msg)
        with open('error_msg.log', 'a') as f:
            f.write(err_msg+'\n')
    else:
        err_msg = "parse error: %s" % url
        print(err_msg)
        with open('error_msg.log', 'a') as f:
            f.write(err_msg+'\n')
 
    
# 获取漫画章节子进程，每个子进程里使用多线程
def _process_update_chapt(num):
    print('Process:', num)
    session = Session()
    #chaptnum = session.query(ComicIndex).count()
    chaptnum = 400                                          # 自定义要进行下载的漫画数
    temp = int(chaptnum/PROCESSNUMS)
    partnum = temp if chaptnum%PROCESSNUMS==0 else temp+1
    lock.acquire()
    querysets = session.query(ComicIndex).filter(ComicIndex.id>=num*partnum).filter(ComicIndex.id<(num+1)*partnum)
    lock.release()
    tpool = ThreadPool(THREADNUMS)
    tpool.map(_thread_update_chapt, querysets)
    tpool.close()
    tpool.join()
    

# 获取漫画章节总进程，使用多进程
def update_comic_chapt():
    nowtime = ctime()
    print("Crawl chapt:", nowtime)
    if not path.exists('error_msg.log'):
        with open('error_msg.log', 'w') as f:
            f.write('-----'+str(nowtime)+ '-----\n')
    else:
        with open('error_msg.log', 'a') as f:
            f.write('-----'+ str(nowtime)+ '-----\n')
    pool = ProcessPool(PROCESSNUMS)
    pool.map(_process_update_chapt, range(PROCESSNUMS))
    pool.close()
    pool.join()
    print("Finished:",ctime())


# 主函数
def main():
    print('Begin:',ctime())
    #get_comic_index()                   # 获取漫画信息
    update_comic_chapt()                # 获取漫画章节
    print("End:",ctime())
    

if __name__ == '__main__':
    main()
