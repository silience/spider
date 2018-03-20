# spider
just a spider

0×01 说明:
为了方便信息安全测评工作，及时收集敏感地址(初衷是爬取api地址)，所以写了这么个小工具。两个简单的功能（目录扫描和url地址爬取）

0×02 使用参数:
python spider.py -u url -s api -o output.txt   #通过爬虫
python spider.py -u url -s dir -f dict.txt -o output.txt   #通过目录扫描

0×03 部分函数说明:
防止因末尾斜线、锚点而重复爬取（http://www.example.com、http://www.example.com、http://www.example.com/index.html#xxoo）
#字符串处理
def edit_str(str):
    if str:
        if str.endswith("/"):#消除/引起的重复
                str = str[:-1]
        if '#' in str:#消除锚点引起的重复
            index = str.index('#')
            str = str[:index]
    return str

爬取规则：
第一个无法爬取页面注释中的地址（<!--http://example.com/index.html-->）,第二个无法爬取相对路径和php?id=等类型的地址，古结合两种规则，并排除图片视频类的地址，最后再去重
        pageLinks1 = re.findall(r'(?<=href=\").*?(?=\")|(?<=href=\').*?(?=\')|(?<=src=\").*?(?=\")|(?<=src=\').*?(?=\')',pageSource.lower())
        for m in pageLinks1:
            if ".jpg" not in m and ".jpeg" not in m and ".png" not in m and ".gif" not in m and ".mp4" not in m and ".avi" not in m and ".swf" not in m and ".flv" not in m and ".ico" not in m and "javascript" not in m :#排除媒体文件
                urllinks.append(m)
        
        #无法匹配相对路径的地址和php?id=等类型的地址
        pageLinks2 = re.findall(r'(http[^\s]:*?(\.html|\.js|\.json|\.amsx|\.wsdl|\.xml|\.jsp|\.php|\.asp|\.php|\.aspx))',pageSource.lower())
        for n in xrange(0,len(pageLinks2)):
            if pageLinks2[n][0] not in urllinks:#判断是否已经存在
                urllinks.append(pageLinks2[n][0])

爬取功能
    def get_visitedUrl(self):
        while not self.linkQuence.unvisitedUrlEmpty():
            visitedUrl = self.linkQuence.popUnvisitedUrl()
            print '------------visited------------：'+visitedUrl
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
