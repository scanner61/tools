#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import urllib2
from multiprocessing import Process, Queue
from BeautifulSoup import Tag, BeautifulSoup as Soup
import simplejson as json

from canpoint import SUBJECTS, SUBJECTS_DESC, DEPOTS, DEPOTS_DESC

def get_data(fpath):
    soup = Soup(open(fpath).read())
    #div = soup.find('div', {'id': 'Kuang'})
    for tbl in soup.findAll('table', {'class': 'B_K'}):
        rslt = {}
        trs = tbl.findAll('tr', recursive=False)
        # 知识点
        rslt['zhishidian'] = trs[0].findAll('td')[-1].text
        # 试题来源
        rslt['laiyuan'] = trs[1].findAll('td')[1].text
        # 试题类别
        rslt['leibie'] = trs[1].findAll('td')[-1].text

        tds = trs[2].findAll('td')
        rslt.update({
            # 题型
            'tixing'        : tds[1].text,
            # 分值
            'fenzhi'        : tds[3].text,
            # 难易程度
            'nanyichengdu'  : tds[5].text,
            # 考试时间
            'kaoshishijian' : tds[7].text,
            # 引用次数
            'yinyongcishu'  : tds[9].text,
        })

        # 试题题干
        rslt['tigan'] = str(trs[3].findAll('td')[-1])#.text

        tbl_inner = tbl.find('table', {'class' : 'inner_table'})
        # 试题答案
        rslt['daan'] = tbl_inner.find('td', {'class': 'b_j3'}).text
        # 试题解析
        rslt['jiexi'] = tbl_inner.find('td', {'class': 'b_j2'}).text
        rslt['foo'] = u'ni好'.encode('utf8')

        yield rslt

def main():
    for subject in SUBJECTS:
        for depot in DEPOTS:
            fpath = os.path.normpath(os.path.join(str(subject), str(depot), 'index.html'))
            print fpath,
            if not os.path.exists(fpath):
                print 'not found'
                continue
            for x in get_data(fpath):
                yield x
            print 'done'


if __name__ == '__main__':
    #for x in main():
    for x in get_data('1/1/1.html'):
        #print json.loads(json.dumps(x))
        print x['tigan']
