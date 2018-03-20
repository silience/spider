#!/usr/bin/python    
#-*- coding:utf8 -*- 

import getopt
import sys    
import threading
import requests
import re
import urllib
import time

target = ""
searchtype = ""
dict_file = ""
dest_file = ""
urlprotocol = ""
domain_url = ""
th_number = 1
threads = []

#用法         
def usage():
    print    
    print "Usage: python spider.py -u url -s dir -f dict.txt -o output.txt -t"    
    print "-s              - search api or dir"    
    print "-f              - dict file"    
    print "-o              - output the result"
    print "-t              - thread number"     
    sys.exit(0)

#字符串处理
def edit_str(str):
    if str:
        if str.endswith("/"):#消除/引起的重复
                str = str[:-1]
        if '#' in str:#消除锚点引起的重复
            index = str.index('#')
            str = str[:index]
    return str

#判断目标地址是否有效
def get_url(target):
    try:
        r = requests.get(target,timeout=2)
        status_code = r.status_code
        if status_code == 200:
            #print "target : %s is ok" % target
            return target
    except:
        return ""

def get_domain(target):
    proto, rest = urllib.splittype(target)
    host, rest = urllib.splithost(rest)
    return host

#righturl = get_url(target)

#获取url地址的协议
def url_protocol(target):
    return re.findall(r".*(?=://)",target)[0]

#urlprotocol = url_protocol(righturl)

#限定同一网站
def same_url(target):
    #去除协议头部
    target = target.replace(urlprotocol+"://","")
    #判断url是否有www，没有则加上www
    if re.findall(r"^www",target) == []:
        sameurl = "www." + target
        if sameurl.find("/") != -1:
            sameurl = re.findall(r"(?<=www.).*?(?=/)", sameurl)[0]
        else:
            sameurl = sameurl + "/"
            sameurl = re.findall(r"(?<=www.).*?(?=/)", sameurl)[0]
    else:
        if target.find("/") != -1:
            sameurl = re.findall(r"(?<=www.).*?(?=/)", target)[0]
        else:
            sameurl = target + "/"
            sameurl = re.findall(r"(?<=www.).*?(?=/)", sameurl)[0]
    return sameurl


class linkQuence:
    def __init__(self):
        self.visited = []    #已访问过的url初始化列表
        self.unvisited = []  #未访问过的url初始化列表
    def getVisitedUrl(self):  #获取已访问过的url
        return self.visited   
    def getUnvisitedUrl(self):  #获取未访问过的url
        return self.unvisited
    def addVisitedUrl(self,target):  #添加已访问过的url
        if target != '' and target not in self.visited:
            return self.visited.append(target)
    def addUnvisitedUrl(self,target):   #添加未访问过的url
        if target != '' and target not in self.visited and target not in self.unvisited:
            return self.unvisited.insert(0,target)
    def popUnvisitedUrl(self):    #从未访问过的url中取出一个url
        try:                      #pop动作会报错终止操作，所以需要使用try进行异常处理
            return self.unvisited.pop()
        except:
            return None
    def unvisitedUrlEmpty(self):   #判断未访问过列表是不是为空
        return len(self.unvisited) == 0

class Spider():
    def __init__(self,target):
        self.linkQuence = linkQuence()   #引入linkQuence类
        self.linkQuence.addUnvisitedUrl(target)   #并将需要爬取的url添加进linkQuence对列中
        self.current_deepth = 1    #设置爬取的深度
    def getPageLinks(self,target):
        urllinks = []
        #domainlink1 = ""
        #domainlink2 = ""
        pageSource = requests.get(target).text
        pageLinks1 = re.findall(r'(?<=href=\").*?(?=\")|(?<=href=\').*?(?=\')|(?<=src=\").*?(?=\")|(?<=src=\').*?(?=\')',pageSource.lower())
        for m in pageLinks1:
            #只爬取html|js|json|amsx|wsdl|xml
            #if m.endswith(".html") or m.endswith(".xml") or m.endswith(".js") or m.endswith(".json") or m.endswith(".amsx") or m.endswith(".wsdl") or m.endswith(".php") or m.endswith(".asp") or m.endswith(".aspx") or m.endswith(".jsp"):
            if ".jpg" not in m and ".jpeg" not in m and ".png" not in m and ".gif" not in m and ".mp4" not in m and ".avi" not in m and ".swf" not in m and ".flv" not in m and ".ico" not in m and "javascript" not in m :#排除媒体文件
                urllinks.append(m)
        
        #无法匹配相对路径的地址和php?id=等类型的地址
        pageLinks2 = re.findall(r'(http[^\s]:*?(\.html|\.js|\.json|\.amsx|\.wsdl|\.xml|\.jsp|\.php|\.asp|\.php|\.aspx))',pageSource.lower())
        for n in xrange(0,len(pageLinks2)):
            if pageLinks2[n][0] not in urllinks:#判断是否已经存在
                urllinks.append(pageLinks2[n][0])

        return urllinks
        
        
    def processUrl(self,target):
        #判断正确的链接及处理相对路径为正确的完整url，判断是否为同一域名或者子域名，防止爬出站外，然后导致无限尝试爬取

        true_url = []
        process_domain = ""
        process_target = "" 
        for l in self.getPageLinks(target):
            l = edit_str(l)
            if l not in true_url:
                process_domain = get_domain(l)
                if process_domain:
                    if domain_url in process_domain:#判断是否为相同域名或者是子域名
                        try:
                            r = requests.get(process_target,timeout=2)
                            status_code = r.status_code
                            if status_code == 200:
                                true_url.append(l)
                        except:
                            pass
                
                else:#域名为空，则判断为相对路径或者无法访问的
                    if '://' not in l:#判断为相对路径
                        process_target = urlprotocol + '://' + 'www.'+domain_url +'/'+ l
                        try:
                            r = requests.get(process_target,timeout=2)
                            status_code = r.status_code
                            if status_code == 200:
                                true_url.append(process_target)
                        except:
                            pass
        return true_url

    def get_visitedUrl(self):
        while not self.linkQuence.unvisitedUrlEmpty():
            visitedUrl = self.linkQuence.popUnvisitedUrl()
            print visitedUrl+'------------visited++++++++++++++'
            if visitedUrl is None or visitedUrl == '':
                continue
            if dest_file:
                save_file(visitedUrl,dest_file)
            links = self.processUrl(visitedUrl)
            self.linkQuence.addVisitedUrl(visitedUrl)
            for link in links:
                self.linkQuence.addUnvisitedUrl(link)

    def crawler(self,crawl_deepth=1):
        #正式的爬取，并依据深度进行爬取层级控制
        while self.current_deepth <= crawl_deepth:

            for i in xrange(th_number):
                t = threading.Thread(target=self.get_visitedUrl)
                threads.append(t)
            for i in xrange(th_number):
                threads[i].start()
                time.sleep(1)
            for i in xrange(th_number):
                threads[i].join()
            self.current_deepth += 1
        #print(self.linkQuence.visited)
        return self.linkQuence.visited

#目录扫描
def dir_scan(target,dict_file):
    if len(target):
        with open(dict_file,"r") as myfiles:
            for myfileurl in myfiles.readlines():
                myfileurl = myfileurl.strip("\n")
                target =edit_str(target)
                myfileurl = target+"/"+myfileurl
                myfileurl = get_url(myfileurl)
                if myfileurl:
                    print 'exist url--------：'+myfileurl
                    if dest_file:
                        save_file(myfileurl,dest_file)

#写入文件
def save_file(target,dest_file):
    with open (dest_file,'a') as savefile:
        target = target+'\n'
        savefile.write(target)

def main():
    global target
    global searchtype
    global dest_file
    global dict_file
    global urlprotocol
    global domain_url
    global th_number
    global threads
    try:
        opts,args =getopt.getopt(sys.argv[1:],"hu:s:f:o:t:",["help","url","search","dictfile","output","thread"])
    except getopt.GetoptError as err:    
        print str(err)    
        usage()
    for o,a in opts:
        if o in ("-h","--help"):    
            usage()
        elif o in ("-u","--url"):
            target = a
        elif o in ("-s","--seach"):
            searchtype = a
        elif o in ("-f","--dictfile"):
            dict_file = a
        elif o in ("-o","--output"):
            dest_file = a
        elif o in ("-t","--thread"):
            th_number = int(a)
        else:
            assert False,"Unhandled Option"
    righturl = get_url(target)
    urlprotocol = url_protocol(righturl)
    domain_url = same_url(righturl)#去除www

    print domain_url
    if len(righturl) and searchtype == "api":
        spider = Spider(righturl)
        spider.crawler(2)
    if len(target) and searchtype == "dir":
        dir_scan(target,dict_file)

main()