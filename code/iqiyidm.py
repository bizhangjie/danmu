import requests
import re
import os
import xlwt
import zlib
from bs4 import BeautifulSoup
from xml.dom.minidom import parse
import xml.dom.minidom

class IQiyiBarrageDownloader:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}
        self.count = 1

    def get_content(self, url):
        resp = requests.get(url, headers=self.headers)
        return resp

    def parse_html(self, url):
        data = self.get_content(url)
        soup = BeautifulSoup(data.text)
        try:
            vid = re.findall('window.QiyiPlayerProphetData={"tvid":(.*?),', str(soup))[0]
        except:
            vid = re.findall('window.Q.PageInfo.playPageInfo={"cid":2,"tvId":(.*?),', data.text)[0]
        details = soup.find_all('meta')
        title = details[6]['content'].split('，')[0]
        return vid, title

    def download_xml(self, vid, title):
        if not os.path.exists('iqiyi/' + title):
            os.makedirs('iqiyi/' + title)

        for x in range(1, 200):
            url = f'https://cmts.iqiyi.com/bullet/{vid[-4:-2]}/{vid[-2:]}/{vid}_300_' + str(x) + '.z'
            try:
                xml = self.zipdecode(self.get_content(url).content)
                with open(f'./iqiyi/{title}/zx' + str(x) + '.xml', 'a+', encoding='utf-8') as f:
                    f.write(xml)
            except:
                break
        print("弹幕下载完毕....\n接下来开始处理 => ")

    @staticmethod
    def zipdecode(bulletold):
        '对zip压缩的二进制内容解码成文本'
        decode = zlib.decompress(bytearray(bulletold), 15 + 32).decode('utf-8')
        return decode

    def xml_parse(self, worksheet, file_name):
        print(file_name + " 处理中 ...")
        DOMTree = xml.dom.minidom.parse(file_name)
        collection = DOMTree.documentElement
        entrys = collection.getElementsByTagName("entry")
        result = []

        for entry in entrys:
            uid = entry.getElementsByTagName('uid')[0]
            content = entry.getElementsByTagName('content')[0]
            likeCount = entry.getElementsByTagName('likeCount')[0]

            worksheet.write(self.count, 0, label=str(uid.childNodes[0].data))
            worksheet.write(self.count, 1, label=str(content.childNodes[0].data))
            worksheet.write(self.count, 2, label=str(likeCount.childNodes[0].data))
            self.count = self.count + 1
            i = content.childNodes[0].data
            result.append(i)
        print(file_name + " 处理完毕。")
        return result

    def process_barrage(self):
        vid, title = self.parse_html(self.url)
        self.download_xml(vid, title)

        # 创建一个workbook 设置编码
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建一个worksheet
        worksheet = workbook.add_sheet('sheet1')

        # 写入excel
        # 参数对应 行, 列, 值
        worksheet.write(0, 0, label='uid')
        worksheet.write(0, 1, label='content')
        worksheet.write(0, 2, label='likeCount')

        for x in range(1, 100):
            try:
                l = self.xml_parse(worksheet, f"./iqiyi/{title}/zx" + str(x) + ".xml")
            except:
                break

        # 保存
        workbook.save(f'./iqiyi/弹幕数据集-{title}.xls')

if __name__ == "__main__":
    url = 'https://www.iqiyi.com/v_2g3zgt67auk.html?vfrm=pcw_dianying&vfrmblk=711219_dianying_fyb&vfrmrst=711219_dianying_fyb_float_video_area3'
    downloader = IQiyiBarrageDownloader(url)
    downloader.process_barrage()
