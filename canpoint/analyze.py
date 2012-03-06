#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import base64
import itertools
from multiprocessing import Process, Queue
from BeautifulSoup import Tag, BeautifulSoup as Soup
try:
    import simplejson as json
except:
    import json

from canpoint import SUBJECTS, SUBJECTS_DESC, DEPOTS, DEPOTS_DESC, TEMPLATE

from task.formcapture import generate_capture, xvfb

exepath = os.path.abspath('./tools/cutycapt')

@xvfb
def get_capture(content, folder, images):
    try:
        os.makedirs('./tmp')
    except OSError:
        pass

    for img in images:
        with open(os.path.join('./tmp', img['name']), 'wb') as f:
            f.write(base64.b64decode(img['b64']))

    htmlpath = os.path.abspath('./tmp/tmp.html')
    with open(htmlpath, 'w') as f:
        f.write(TEMPLATE % content)

    imgpath = os.path.abspath('./tmp/tmp.png')
    with open(imgpath, 'w') as f:
        f.write('')

    try:
        if not generate_capture(exepath, htmlpath, imgpath):
            return ''
    except:
        return ''
    if not os.path.exists(imgpath):
        return ''
    return base64.b64encode(open(imgpath).read())


def extract_data(fpath):
    """Given a downloaded html page, extracts the data into dicts then yield them """
    soup = Soup(open(fpath).read())
    #div = soup.find('div', {'id': 'Kuang'})
    for tbl in soup.findAll('table', {'class': 'B_K'}):
        rslt = {}
        trs = tbl.findAll('tr', recursive=False)

        # build the json data
        # 知识点: tags
        li = []
        s = trs[0].findAll('td')[-1].text
        s = re.sub(r'\s', '', s)
        for code, desc in re.findall(r'\[(.*?)\|(.*?)\]', s):
            li.append({
                'code': code,
                'desc': desc,
            })
        rslt['tags'] = li
        # 试题来源: source
        rslt['source'] = trs[1].findAll('td')[1].text
        # 试题类别: kind
        rslt['kind'] = trs[1].findAll('td')[-1].text

        tds = trs[2].findAll('td')
        rslt.update({
            # 题型
            'category'  : tds[1].text,
            # 分值
            'point'     : tds[3].text,
            # 难易程度
            'level'     : tds[5].text,
            # 考试时间
            'date'      : tds[7].text,
            # 引用次数
            'cites'     : tds[9].text,
        })

        # 试题题干
        rslt['content'] = str(trs[3].findAll('td')[-1])

        tbl_inner = tbl.find('table', {'class' : 'inner_table'})
        # 试题答案
        rslt['anwser'] = str(tbl_inner.find('td', {'class': 'b_j3'}))
        # 试题解析
        rslt['explanation'] = str(tbl_inner.find('td', {'class': 'b_j2'}))

        # images
        imgs = []
        for img in tbl.findAll('img'):
            img_name = img['src']
            img_path = os.path.join(os.path.dirname(fpath), img_name)
            if not os.path.exists(img_path):
                continue
            with open(img_path, 'rb') as f:
                imgs.append({
                    'name': img_name,
                    'b64': base64.b64encode(f.read())
                })
        rslt['images'] = imgs
        capture_b64 = get_capture(rslt['content'], os.path.dirname(fpath), imgs)
        if not capture_b64:
            print 'failed get capture for %s' % fpath
        rslt['content_capture_b64'] = capture_b64

        yield rslt

def main():
    for subject, depot in itertools.product(SUBJECTS, DEPOTS):
        fpath = os.path.normpath(os.path.join(str(subject), str(depot), 'index.html'))
        print fpath,
        if not os.path.exists(fpath):
            print 'not found'
            continue
        for x in extract_data(fpath):
            yield x
        print 'done'


def test(fpath):
    for x in extract_data(fpath):
        print json.dumps(x, ensure_ascii=False, sort_keys=True, indent=4).encode('utf8')
        with open('test_output', 'w') as f:
            print >>f, json.dumps(x, ensure_ascii=False, sort_keys=True, indent=4).encode('utf8')
        break

if __name__ == '__main__':
    from optparse import OptionParser 
    parser = OptionParser()
    parser.add_option("-t", "--test", action="store_true", dest="test",
                        help='test')
    parser.add_option("-i", "--insert-db", action="store_true", dest="mongo",
                        help='insert into mongodb')
     
    options, args = parser.parse_args()

    if options.test:
        test('3/1/3.html')

    elif options.mongo:
        import pymongo
        conn = pymongo.Connection('localhost', 27017)
        db = conn.test_base

        for x in main():
            db.questions.insert(x)

