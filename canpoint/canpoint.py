#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import re
import urllib2
from multiprocessing import Process, Queue
from BeautifulSoup import Tag, BeautifulSoup as Soup

DOMAIN = 'http://gzt.canpoint.cn'

SUBJECTS = range(1, 10)
SUBJECTS_DESC = [u'1 语文', u'2 英语', u'3 数学', u'4 物理', u'5 化学', u'6 生物', u'7 历史', u'8 地理', u'9 政治', ]
DEPOTS = range(1, 3)
DEPOTS_DESC = [u'1 公开题库', u'2 本校题库', ]

tree_nodes = {
    1 : [{"hasChildren":True,"id":"ff8080811fccd305011fd051f15a0476","text":"基础知识"},{"hasChildren":True,"id":"ff8080811fccd305011fd05220d90478","text":"文本阅读"},{"hasChildren":True,"id":"ff8080811fccd305011fd0529008047a","text":"古代诗歌鉴赏"},{"hasChildren":True,"id":"ff8080811fccd305011fd0532026047e","text":"写作"}],
    2 : [{"hasChildren":True,"id":"ff8080811fccd305011fcfe5430a0161","text":"高考听力"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe5a9af0165","text":"单项填空"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe5e4c10167","text":"完形填空"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe60ba80168","text":"广东语法填空"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe63e8f016a","text":"阅读"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe672ff016c","text":"单词拼写"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe74f4f0173","text":"短文改错"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe78f410175","text":"写作或书面表达"},{"hasChildren":True,"id":"ff80808124b90dc1012509de55a200b2","text":"高考口语"},{"hasChildren":False,"id":"ff80808124b90dc1012509df134a00b3","text":"其他未包括类型"}],
    3 : [{"hasChildren":True,"id":"ff8080811fccd305011fcfe904d40181","text":"集合与常用逻辑用语"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe942190183","text":"函数"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe9aaa00186","text":"三角函数"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe9ef38018b","text":"数列"},{"hasChildren":True,"id":"ff8080811fccd305011fcfea0da2018c","text":"极限、导数与定积分"},{"hasChildren":True,"id":"ff8080811fccd305011fcfea376e018e","text":"平面向量"},{"hasChildren":True,"id":"ff8080811fccd305011fcfeb3c4c0198","text":"立体几何"},{"hasChildren":True,"id":"ff8080811fccd305011fcfee33780199","text":"不等式"},{"hasChildren":True,"id":"ff8080811fccd305011fcfee5ec1019a","text":"计数原理与概率、统计"},{"hasChildren":True,"id":"ff8080811fccd305011fcfee8fe6019b","text":"解析几何"},{"hasChildren":True,"id":"ff8080811fccd305011fcfeec092019c","text":"算法与框图"},{"hasChildren":True,"id":"ff8080811fccd305011fcfeeebff019d","text":"复数"},{"hasChildren":True,"id":"ff8080811fccd305011fcfef0a40019e","text":"选修"},{"hasChildren":True,"id":"ff80808124b90dc10124eaff8678004d","text":"数学思想方法"}],
    4 : [{"hasChildren":True,"id":"ff8080811fccd305011fd02692ac0335","text":"运动和力"},{"hasChildren":True,"id":"ff8080811fccd305011fd0277a9e033d","text":"动量和能量"},{"hasChildren":True,"id":"ff8080811fccd305011fd027ad9b033e","text":"电与磁"},{"hasChildren":True,"id":"ff8080811fccd305011fd027dab30341","text":"热学"},{"hasChildren":True,"id":"ff8080811fccd305011fd02802110343","text":"粒子与波"},{"hasChildren":True,"id":"ff8080811fccd305011fd02833390345","text":"原子物理"}],
    5 : [{"hasChildren":True,"id":"ff8080811fccd305011fd0621ae604ef","text":"化学基本概念"},{"hasChildren":True,"id":"ff8080811fccd305011fd0624ba204f0","text":"化学基本理论"},{"hasChildren":True,"id":"ff8080811fccd305011fd06291d604f1","text":"元素及其化合物"},{"hasChildren":True,"id":"ff8080811fccd305011fd062ce2d04f3","text":"有机化合物"},{"hasChildren":True,"id":"ff8080811fccd305011fd063016e04f4","text":"化学实验 "},{"hasChildren":True,"id":"ff8080811fccd305011fd063360304f6","text":"化学计算"},{"hasChildren":True,"id":"ff8080811fccd305011fd06368ed04f8","text":"化学与STSE"},{"hasChildren":True,"id":"ff8080811fccd305011fd063976504fa","text":"选修1《化学与生活》"},{"hasChildren":True,"id":"ff8080811fccd305011fd063ce0204fc","text":"选修2《化学与技术》"}],
    6 : [{"hasChildren":True,"id":"ff8080811fccd305011fcf72130a000a","text":"分子与细胞"},{"hasChildren":True,"id":"ff8080811fccd305011fcf7338e4000c","text":"遗传与进化"},{"hasChildren":True,"id":"ff8080811fccd305011fcf740656000f","text":"稳态与环境"},{"hasChildren":True,"id":"ff8080811fccd305011fcf74491d0010","text":"选修 生物技术实践"},{"hasChildren":True,"id":"ff8080811fccd305011fcf7490990011","text":"选修 生物科学与社会"},{"hasChildren":True,"id":"ff8080811fccd305011fcf74cd320013","text":"选修 现代生物科技专题"},{"hasChildren":True,"id":"ff8080811fccd305011fcfe1322a0149","text":"实验"}],
    7 : [{"hasChildren":True,"id":"ff80808124b90dc101251041cc88041c","text":"政治文明史"},{"hasChildren":True,"id":"ff80808124b90dc101251042166d041f","text":"经济文明史"},{"hasChildren":True,"id":"ff80808124b90dc1012510424fab0421","text":"文化科技文明史"},{"hasChildren":True,"id":"ff80808124b90dc101251042982c0422","text":"选修1  历史上重大改革回眸"},{"hasChildren":True,"id":"ff80808124b90dc101251042ccde0423","text":"选修2 近代社会的民主思想与实践"},{"hasChildren":True,"id":"ff80808124b90dc10125104304bd0424","text":"选修3 20世纪的战争与和平"},{"hasChildren":True,"id":"ff80808124b90dc1012510436f590427","text":"选修4 中外历史人物评说"},{"hasChildren":True,"id":"ff80808124b90dc101251043aff0042a","text":"选修5 探索历史的奥秘"},{"hasChildren":True,"id":"ff80808124b90dc101251043f16a042c","text":"选修6 世界文化遗产荟萃"},{"hasChildren":True,"id":"ff80808124b90dc1012510443457042e","text":"历史能力的综合运用"}],
    8 : [{"hasChildren":True,"id":"ff8080811fccd305011fcf730865000b","text":"自然地理"},{"hasChildren":True,"id":"ff8080811fccd305011fcf7492540012","text":"人文地理"},{"hasChildren":True,"id":"ff8080811fccd305011fcf75a61e0016","text":"区域发展"},{"hasChildren":True,"id":"ff80808124b90dc101250ffacb3802b1","text":"选修地理"},{"hasChildren":True,"id":"ff80808124b90dc101250ffbd5c902b2","text":"区域地理"},{"hasChildren":True,"id":"ff80808124b90dc101250ffc0f4502b3","text":"专题地理"},{"hasChildren":True,"id":"ff80808124b90dc101250ffc4e3002b4","text":"热点地理"}],
    9 : [{"hasChildren":True,"id":"ff80808124b90dc101250aab7481011c","text":"经济生活"},{"hasChildren":True,"id":"ff80808124b90dc101250aabf6e4011d","text":"政治生活"},{"hasChildren":True,"id":"ff80808124b90dc101250aac4ca4011e","text":"文化生活"},{"hasChildren":True,"id":"ff80808124b90dc101250aac9d9f011f","text":"生活与哲学"},{"hasChildren":True,"id":"ff80808124b90dc101250aad26ae0120","text":"选修1  科学社会主义常识"},{"hasChildren":True,"id":"ff80808124b90dc101250aad77c00121","text":"选修2  经济学常识"},{"hasChildren":True,"id":"ff80808124b90dc101250aadca8b0122","text":"选修3  国家和国际组织"},{"hasChildren":True,"id":"ff80808124b90dc101250aae0d9d0123","text":"选修4  科学思维"},{"hasChildren":True,"id":"ff80808124b90dc101250aae4ecf0124","text":"选修5  生活中的法律常识"},{"hasChildren":True,"id":"ff80808124b90dc101250aaea17b0125","text":"选修6  公民道德与伦理常识"},{"hasChildren":False,"id":"ff8080812bd26c07012c04e51d651f4f","text":"时事政治"}],
}

TEMPLATE = """
<html>
<head>
<title>试题管理</title>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta http-equiv="Cache-Control" content="no-store"/>
<meta http-equiv="Pragma" content="no-cache"/>
<meta http-equiv="Expires" content="0"/>
<style>
	a:link,a:visited,a:active{
		text-decoration:none; 
		color:#000000;
	  }
	
	#search_result{
		width:700px;
		position: absolute;
		left: 280px;
		top:220px;
	}
	
	.outer_table{
		background:#CACFF5;
		border:1px solid #CACFF5;
	}
	
	#search_result.inner_table{
		background: #ffffff;
		border:1px solid #CACFF5;
	}
	
	#search_result.inner_table td{
		background: #CACFF5;
	}
	
	.td1{
		background:#6699FF;
	}
	.td2{
		background:#999999;
	}
	.td3{
		background:#ffffff;
	}
	
	#Kuang{width:725px; background:#d7e4ff; padding:10px;}
	.B_K{background:#024c82; line-height:25px; font:"宋体"; color:#000;font-size:12px;}
	.b_j{background:#b1c3f2; text-align:center; font-weight:bold;}
	.b_j1{background:#cedbfd; text-align:center; font-weight:bold;}
	.b_j2{background:#fff; line-height:20px;}
	.b_j2 p{padding:6px;}
	.b_j3{background:#e6edff; text-align:center;}
	.sub{font-weight:bold;}
		
</style>
</head>
<body>
    <div id="Kuang">
        %s
    </div>
</body>
</html>
"""

def save_image(img_url, img_path, retry=3):
    try:
        img_raw = urllib2.urlopen(img_url, timeout=10).read()
    except:
        if retry <= 0:
            print 'Failed to download image: %s' % img_url
        save_image(img_url, img_path, retry-1)
        return
    else:
        if img_raw:
            with open(img_path, 'w') as f:
                f.write(img_raw)
        else:
            print 'Image with empty content: %s' % img_url

def serve_image_downloader(q):
    while True:
        img_url, img_path = q.get()
        if os.path.exists(img_path):
            continue
        img_raw = None
        save_image(img_url, img_path)

def fetch_html(url):
    while True:
        try:
            req = urllib2.Request(url)
            req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
            res = urllib2.urlopen(req, timeout=60)
            content = res.read()
            encoding = res.headers['content-type'].split('charset=')[-1]
        except Exception, e:
            print str(e)
            print 'retrying...'
            continue
        else:
            return unicode(content, encoding, 'ignore')

def get_url(subject, depot='1', page=None):
    str_nodes = '|'.join([node['id'] for node in tree_nodes[subject]])
    kws = [
        'knowledgeStr=|%s' % str_nodes,
        'depot=%s' % depot,
        'cityIds=',
        'cityNames=',
        'provinceIds=',
        'subjectId=%s' % subject,
    ]
    if page:
        kws.append('page.pageNo=%s' % page)
    return "%s/ques/conditionsearch.action?keyword=&%s" % (DOMAIN, '&'.join(kws))

def parse(url, subject, depot):
    content = fetch_html(url)
    # ignore alt text in img tags
    content = re.sub(r'alt=([^"]*?) ', ' ', content)
    soup = Soup(content)
    # find the outer div
    div = soup.find('div', {'id': 'Kuang'})
    for x in div.findAll('div'):
        # show all hidden divs
        try:
            style = x['style']
        except:
            style = ''
        x['style'] = style.replace('display:none', '')

    for tbl in div.findAll('table', {'class': 'B_K'}):
        # ignore the last <tr> (just links)
        trs = tbl.findAll('tr', recursive=False)
        if trs:
            trs[-1].extract()
        # ignore inline styles
        for style in tbl.findAll('style'):
            style.extract()
        # images
        for img in tbl.findAll('img'):
            img_url = img['src']
            img_name = img_url.split('/')[-1]
            fpath = os.path.join(str(subject), depot, img_name)
            img_queue.put((img_url, fpath))
            img['src'] = img_name
        # yield cleaned html
        yield str(tbl).replace("&nbsp;", '')

def get_page_count(subject, depot):
    url = get_url(subject, depot)
    content = fetch_html(url)
    soup = Soup(content)
    pager = soup.find('div', {'id': 'pager'})
    m = re.search(r'共(\d*)页', str(pager))
    if m:
        return int(m.group(1))
    return 1

def save_page(subject, depot, page):
    print 'page %s...' % page,
    fpath = os.path.join(str(subject), depot, '%s.html' % page)
    if os.path.exists(fpath):
        print 'already exists'
        return
    url = get_url(subject, depot, page)
    for rslt in parse(url, subject, depot):
        with open(fpath, 'a') as f:
            f.write(rslt)
    print 'done'

def iter_tempfiles(folder):
    for r, ds, fs in os.walk(folder):
        for fname in fs:
            if os.path.splitext(fname)[-1] != '.html':
                continue
            fpath = os.path.join(r, fname)
            yield open(fpath, 'r').read()

def merge():
    for subject in SUBJECTS:
        for depot in DEPOTS:
            folder = os.path.join(str(subject), str(depot))
            if not os.path.exists(folder):
                continue
            with open(os.path.join(folder, 'index.html'), 'w') as f:
                f.write(TEMPLATE % ''.join(x for x in iter_tempfiles(folder)))

def fetch(subject, depot):
    try:
        os.makedirs('%s/%s' % (subject, depot))
    except OSError:
        pass

    url = get_url(subject, depot)
    print 'fetching %s : %s' % (SUBJECTS_DESC[int(subject) - 1].encode('utf-8'), DEPOTS_DESC[int(depot) - 1]).encode('utf-8'), url
    page_count = get_page_count(subject, depot)
    print page_count, ' pages'
    for page in range(1, page_count + 1):
        save_page(subject, depot, page)
    print 'done'

img_queue = Queue()

def main(options, args):
    p = Process(target=serve_image_downloader, args=(img_queue,))
    p.daemon = True
    p.start()

    if options.subject:
        subject = int(options.subject)
        depot = options.depot or '1'
        fetch(subject, depot)
    else:
        print 'fetching all subjects'
        for subject in SUBJECTS:
            for depot in DEPOTS:
                fetch(subject, str(depot))

if __name__ == '__main__':
    from optparse import OptionParser 
    parser = OptionParser()
    parser.add_option("-s", "--subject", type="choice", action="store", dest="subject",
                        choices=map(str, SUBJECTS), help=' '.join(SUBJECTS_DESC))
    parser.add_option("-d", "--depot", type="choice", default='1', action="store", dest="depot",
                        choices=map(str, DEPOTS), help=' '.join(DEPOTS_DESC))
    parser.add_option("-m", "--merge", action="store_true", dest="merge",
                        help='merge the results into a single page')

    options, args = parser.parse_args()

    if options.merge:
        merge()
        sys.exit()
    else:
        main(options, args)
        merge()

