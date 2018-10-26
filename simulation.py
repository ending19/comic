#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 16:08:08 2018

@author: ending
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Chrome浏览器配置设置
chrome_options = Options()
#chrome_options.add_argument('window-size=1200x600')                # 指定浏览器分辨率
chrome_options.add_argument('--disable-gpu')                        # 谷歌文档提到需要加上这个属性来规避bug
#chrome_options.add_argument('--hide-scrollbars')                   # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('blink-settings=imagesEnabled=false')   # 不加载图片, 提升速度
chrome_options.add_argument('--headless')                           # 无头浏览器，不使用可视化页面. linux下如果系统不支持可视化不加这条会启动失败
# 手动指定使用的浏览器位置
#chrome_options.binary_location = r'/opt/google/chrome/chrome' 


# 对1kkk中的限制级漫画进行浏览器模拟
def web_1kkk_limit(url):
    driver = webdriver.Chrome(options=chrome_options)               # 指定chrome属性
    driver.get(url)                                                 # 访问指定网页
    # 设置隐性超时（全局），在不指定显性超时时，等待元素全部加载完毕的最长等待时间
    driver.implicitly_wait(5)                                                                  
    # 显性超时，每0.5秒查询一次状态，共3秒，最长超时时间以显性和隐性中的较长者计。（感觉不适合多线程）
    # wait = WebDriverWait(driver=driver, timeout=3, poll_frequency=0.5) 
    # adultcheck = (By.ID, 'checkAdult')
    # wait.until(EC.presence_of_element_located(adultcheck))        # 显性等待元素加载完毕，不用等待全部元素加载完毕
    time.sleep(2)                                               # 等待2秒，等元素加载
    driver.find_element_by_id('checkAdult').click()             # 查找某一元素并点击
    time.sleep(2)                                               # 等待2秒，等待JavaScript运行完毕
    html = driver.page_source                                   # 获取此时的HTML
    driver.close()                                              # 关闭该网页
    return html
    



                  
