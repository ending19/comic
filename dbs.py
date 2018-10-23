#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:07:22 2018

@author: ending
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, ForeignKey, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

engine = create_engine('mysql+mysqlconnector://root:12345678@localhost:3306/comic', encoding='utf8', echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

class ComicIndex(Base):
    __tablename__ = 'comic_index'
    id = Column(Integer, Sequence('index_seq'), primary_key=True)
    name = Column(String(50), nullable=False)           # 漫画名
    index_url = Column(String(20), nullable=False)      # 漫画目录页URL
    rank = Column(SmallInteger)                         # 漫画评分
    status = Column(Boolean)                            # 漫画状态（完结/更新）
    latest_name = Column(String(80))                    # 最新章名字
    latest_url = Column(String(30))                     # 最新章URL
    free_chapt = Column(SmallInteger, default=0)        # 免费章节数（-1:全部免费，0：VIP免费，n:免费章节）
    chapt_num = Column(SmallInteger, default=0)         # 章节总数
    host = Column(String(30))                           # 网站host
    update = Column(DateTime)                           # 上次更新时间
    # chapts属性包含了  ComicChapt表中与该条数据相关的所有记录，即comic_insex与ComicChapt之间的关系
    chapts = relationship('ComicChapt', back_populates='comic')
    def __repr__(self):
        return  "<ComicIndex(id='%s' name='%s')>" % (self.id, self.name)
    
    
class ComicChapt(Base):
    __tablename__ = 'comic_chapt'
    id = Column(Integer, Sequence('chapt_seq'), primary_key=True)
    chapt_index = Column(SmallInteger, default=None)                    # 章节索引
    chapt_name = Column(String(80))                                     # 章节名字
    chapt_url = Column(String(30), nullable=False)                      # 章节URL
    chapt_type = Column(String(5), default='ch')                        # 章节类型
    index_id = Column(Integer, ForeignKey("comic_index.id"))
    comic = relationship('ComicIndex', back_populates='chapts')
    def __repr__(self):
        return  "<ComicChapt(comic_id='%s' name='%s')>" % (self.index_id, self.name)



Base.metadata.create_all(engine)



# 处理从漫画目录页获取的数据
def index_insert(comics, host, session):
    cindexs = [ComicIndex(name=name, index_url=iurl, rank=rank, status=status,
           latest_name=lname, latest_url=lurl, host=host) for name,iurl,rank,status,lname,lurl in comics]
    session.add_all(cindexs)


#def chapt_update(chapts, freenum, queryset, modifytime, session, free=True):
def chapt_update(chapts, freenum, queryset, session, free=True):
    index_id = queryset.id
    queryset.free_chapt = freenum
    queryset.chapt_num = len(chapts)
    #queryset.update = modifytime
    if free:
        chapts = chapts[:freenum]
    cchapts = [ComicChapt(chapt_index=index, chapt_name=name, chapt_url=url, chapt_type=ctype, index_id=index_id) for index,name,url,ctype in chapts]
    session.add_all(cchapts)
    

