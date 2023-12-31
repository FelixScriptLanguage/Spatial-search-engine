import os
import requests
import threading
import re
import socket
from bs4 import BeautifulSoup as bs
import jieba
def getWebsite(ip):
    try:
        return requests.get('http://ip-api.com/json/'+ip,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'}).json()
    except:
        return 'error'
lock = threading.Lock();threads = list()
ports_list = list();nr = []
def judge_hostname_or_ip(target_host):
    result = re.match(r"^(\d|[1-9]\d|1\d\d|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.(\d|[1-9]\d|1\d\d|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\."
        "(\d|[1-9]\d|1\d\d|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.(\d|[1-9]\d|1\d\d|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$",target_host)
    if result:
        return result.group()
    else:
        try:
            socket.setdefaulttimeout(1);IP = socket.gethostbyname(target_host)
            return IP
        except Exception as e:
            pass
def parse_port(ports):
    if ports:
        global nr
        try:
            res = re.match(r'(\d+)-(\d+)', ports)
            if res:
                if int(res.group(2)) > 65535:
                    pass
                return range(int(res.group(1)), int(res.group(2)))
        except:
            pass
    else:
        return [19, 21, 22, 23, 25, 31, 42, 53, 67, 69, 79, 80, 88, 99, 102, 110, 113, 119, 220, 443]
def test_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect((host, port))
        lock.acquire()  # 加线程锁
        global nr;nr.append(port)
        ports_list.append(port)
    except:
        lock.acquire()
    finally:
        lock.release();s.close()
def duankou(ipdizhi):
    ip = judge_hostname_or_ip(ipdizhi);l = parse_port('')
    socket.setdefaulttimeout(3)
    for port in l:
        t = threading.Thread(target=test_port, args=(ip, port));threads.append(t)  # 添加到等待线程列表里面
        t.start()
    for t in threads:
        t.join()  # 等待线程全部执行完毕
    global nr;jl = nr;nr = []
    return jl
def shibiexitong(ip):
    if ip == None:
        return 'error'
    system = os.popen('.\\scan\\python.exe ./scan/zplbscan.py '+ip).read()
    for i in system.split('\n'):
        if 'OS' in i:
            return i
def getUrl(url):
    code = getCode('https://' + url)
    jl = 'https://' + url
    if code == 'error':
        code = getCode('http://' + url)
        if code != 'error':
            jl = 'http://' + url
        else:
            return 'error'
    return jl
def getTitle(code):
    try:
        soup = bs(code,'html.parser')
        return '<'.join('>'.join(str(soup.find_all('title')[0]).split('>')[1:]).split('<')[:-1])
    except:
        return 'error'
def getCode(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'}
        return requests.get(url,headers=headers,timeout=10).text
    except:
        return 'error'
def getStateCode(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'}
        return str(requests.get(url,headers=headers).status_code)
    except:
        return 'error'
def getText(nr,code):
    sentence = nr
    words = jieba.cut(sentence)
    lst = []
    for i in words:
        lst.append(i)
    words = lst
    jl = 0
    for i in words:
        if i in code:
            jl += 1
    if jl == 0:
        return 'no'
    else:
        return jl
def read(wz):
    if '/' in wz:
        wz = ''.join(wz.split('/')[1:][1])
    with open('./db/'+wz+'.txt','r',encoding='utf-8') as r:
        return eval(r.read())
def write(wz,content):
    if '/' in wz:
        wz = ''.join(wz.split('/')[1:][1])
    with open('./db/'+wz+'.txt','w',encoding='utf-8') as w:
        w.write(str(content))
def addNewSublinks(url,sublinks):
    db = read(url)
    cd = getCode(sublinks)
    db[1].append([sublinks,getTitle(cd),cd])
    write(url,db)
def isIn(url):
    if os.path.isfile('./db/'+url+'.txt'):
        return True
    else:
        return False
def isInSublinks(url,sublinks):
    db = read(url)
    #print('yessss!:',open('./db/'+url+'.txt','r',encoding='utf-8').read())
    if os.path.isfile('./db/'+url+'.txt'):
        for i in db[1]:
            if i[0] == sublinks:
                return True
        return False
def addNewlink(url):
    #open('./db/' + url + '.txt', 'w', encoding='utf-8').write('[]')
    #{'status': 'success', 'country': 'China', 'countryCode': 'CN', 'region': 'GD', 'regionName': 'Guangdong', 'city': 'Shenzhen', 'zip': '', 'lat': 22.5431, 'lon': 114.058, 'timezone': 'Asia/Shanghai', 'isp': 'China Mobile', 'org': 'China Mobile', 'as': 'AS9808 China Mobile Communications Group Co., Ltd.', 'query': '39.156.66.18'}
    ip = judge_hostname_or_ip(url)
    config = getWebsite(ip)
    code = getCode('https://'+url)
    if code == 'error':
        code = getCode('http://'+url)
    if config == 'error':
        config = {'country':'error','city':'error'}
    try:
        dk = duankou(ip)
    except:
        dk = ['error']
    db = [[config['country'],config['city'],getStateCode(code),getTitle(code),code,str(ip),shibiexitong(ip), dk],[]]
    write(url,db)
    if dk[0] != 'error':
        for i in dk:
            if str(i) == '80':
                continue
            elif str(i) == '443':
                continue
            else:
                wz = getUrl(url+':'+str(i))
                if wz == 'error':
                    continue
                else:
                    spider(wz)
def spider(url):
    try:
        wz = url
        if '/' in url:
            wz = ''.join(url.split('/')[1:][1])
        #open('./db/'+wz+'.txt','w',encoding='utf-8').write('[]')
        print(wz)
        code = getCode(url)
        soup = bs(code, 'html.parser')
        sp = soup.find_all('a')
        jl = 0
        for j in sp:
            if str(j) == 'None':
                continue
            elif str(j) == '#':
                continue
            else:
                jl += 1
        print('len:',jl)
        jl = 0
        for i in sp:
            jl += 1
            i = str(i.get('href'))
            if i.startswith('http'):
                pass
            elif i.startswith('//'):
                i = 'https://'+wz+i[1:]
            elif i.startswith('/'):
                i = 'https://'+wz+i
            elif 'javascript' in i:
                continue
            if str(i) != 'None' and str(i) != '#':
                print('yes:',i,jl)
            else:
                print('no!!!', i,jl)
            if str(i) != 'None' and str(i) != '#':
                print(i)
                zgwz = ''.join(i.split('/')[1:][1])
                if zgwz != wz:
                    if isIn(zgwz):
                        if isInSublinks(zgwz,i):
                            pass
                        else:
                            addNewSublinks(zgwz,i)
                            spider(zgwz)
                    else:
                        addNewlink(zgwz)
                        addNewSublinks(zgwz,i)
                        spider(zgwz)
                else:
                    if isIn(zgwz):
                        pass
                    else:
                        addNewlink(zgwz)
                    if isInSublinks(zgwz, i):
                        pass
                    else:
                        addNewSublinks(zgwz, i)
    except Exception as a:
        print('error',a)
def ipToUrl(ip):
    code = getCode('https://site.ip138.com/'+ip)
    spider(getUrl(ip))
    soup = bs(code, 'html.parser')
    sp = soup.find_all('div')
    code = ''
    for i in sp:
        if i.get('class') == ['result', 'result2']:
            code = str(i)
            break
    soup = bs(code, 'html.parser')
    sp = soup.find_all('a')
    for i in sp:
        i = str(i.get('href'))
        url = getUrl(i[1:][:-1])
        if url == 'error':
            continue
        else:
            print('find:', url)
            spider(url)
def see():
    while True:
        for a in range(1,256):
            for b in range(0,256):
                for c in range(0,256):
                    for d in range(0,256):
                        ip = str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)
                        ipToUrl(ip)
                        #for i in lst:
                        #    spider(i)
see()
#addNewSublinks('www.baidu.com','https://www.baidu.com/s?wd=%E7%99%BE%E5%BA%A6%E7%83%AD%E6%90%9C&sa=ire_dl_gh_logo_texing&rsv_dl=igh_logo_pc')
#print(spider('https://blog.csdn.net/'))
#port,text,title,os,url,city,country,status_code
#{'www.baidu.com':[ ['country','city','code','title','text','ip','os',[port] ,'is ok'], [['url','title','text']] ]}
#{'www.baidu.com':[ ['country','city','code','title','text','ip','os',[80] ,'is ok'], [['url','title','text']] ]}