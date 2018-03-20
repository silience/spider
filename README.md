# spider
just a spider

0×01 说明:
为了方便信息安全测评工作，及时收集敏感地址(初衷是爬取api地址)，所以写了这么个小工具。两个简单的功能（目录扫描和url地址爬取）

0×02 使用参数:
python spider.py -u url -s api -o output.txt   #通过爬虫
python spider.py -u url -s dir -f dict.txt -o output.txt   #通过目录扫描

0×03 部分函数说明:
防止因末尾斜线、锚点而重复爬取（http://www.example.com、http://www.example.com、http://www.example.com/index.html#xxoo）
![image](https://github.com/silience/spider/blob/master/image/1.png)
